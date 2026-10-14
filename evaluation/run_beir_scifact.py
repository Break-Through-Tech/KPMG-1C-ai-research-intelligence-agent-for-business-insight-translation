"""Evaluate the repo's MPNet/Chroma retriever on a tiny BEIR SciFact subset.

Downloads the official BEIR archive, selects 20 test claims and 500 articles
including all relevant ones. This is a diagnostic subset, not a standard
full-corpus BEIR score. SciFact qrels assess document relevance only.
"""

import csv
import hashlib
import json
import math
import random
import sys
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "notebooks"))
from ingest import build_vector_store  # noqa: E402
from retrieval import ResearchRetriever  # noqa: E402

DATASET_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"
DATASET_MD5 = "5f7d1de60b170fc8027bb7898e2efca1"
CACHE = ROOT / ".evaluation_cache/beir"
SAMPLE_SIZE = 20
CORPUS_SIZE = 500
SEED = 42


def dataset_paths():
    archive = CACHE / "scifact.zip"
    CACHE.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        partial = archive.with_suffix(".part")
        urllib.request.urlretrieve(DATASET_URL, partial)
        partial.rename(archive)
    digest = hashlib.md5(archive.read_bytes()).hexdigest()  # BEIR's published integrity check
    if digest != DATASET_MD5:
        raise RuntimeError(f"SciFact checksum mismatch: {digest}")
    dataset = CACHE / "scifact"
    names = ["corpus.jsonl", "queries.jsonl", "qrels/test.tsv"]
    with zipfile.ZipFile(archive) as source:
        for name in names:
            target = dataset / name
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read(f"scifact/{name}"))
    return dataset


def read_jsonl(path):
    with path.open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def load_data(dataset):
    corpus = read_jsonl(dataset / "corpus.jsonl")
    queries = {item["_id"]: item["text"]
               for item in read_jsonl(dataset / "queries.jsonl")}
    qrels = {}
    with (dataset / "qrels/test.tsv").open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            score = int(row["score"])
            if score > 0:
                qrels.setdefault(row["query-id"], {})[row["corpus-id"]] = score
    if not set(qrels) <= set(queries):
        raise RuntimeError("Test judgments contain unknown query IDs")
    if not {doc for labels in qrels.values() for doc in labels} <= {p["_id"] for p in corpus}:
        raise RuntimeError("Test judgments contain unknown corpus IDs")
    return corpus, queries, qrels


def ingest_adapter(corpus):
    """One title-plus-abstract section per SciFact article for ingest.py."""
    title_counts = Counter(p["title"] for p in corpus)
    parsed, metadata = {}, []
    for item in corpus:
        title = item["title"]
        # build_documents keys by title; disambiguate the two duplicate titles.
        unique_title = f"{title} [BEIR:{item['_id']}]" if title_counts[title] > 1 else title
        parsed[unique_title] = {"Abstract": f"{title} {item['text']}"}
        metadata.append({"id": item["_id"], "title": unique_title})
    if len(parsed) != len(corpus):
        raise RuntimeError("Lost articles while adapting SciFact for ingestion")
    return parsed, metadata


def select_corpus(corpus, qrels, query_ids):
    gold_ids = {doc_id for query_id in query_ids for doc_id in qrels[query_id]}
    if len(gold_ids) > CORPUS_SIZE:
        raise RuntimeError("Relevant article count exceeds corpus subset size")
    distractors = [item["_id"] for item in corpus if item["_id"] not in gold_ids]
    selected_ids = gold_ids | set(random.Random(SEED + 1).sample(
        distractors, CORPUS_SIZE - len(gold_ids)))
    selected = [item for item in corpus if item["_id"] in selected_ids]
    if len(selected) != CORPUS_SIZE:
        raise RuntimeError("SciFact corpus subset has an unexpected size")
    return selected, len(gold_ids)


def score_query(ranked_ids, relevance):
    relevant = set(relevance)
    ranks = [i + 1 for i, doc_id in enumerate(ranked_ids) if doc_id in relevant]
    def recall(k):
        return sum(doc_id in relevant for doc_id in ranked_ids[:k]) / len(relevant)
    def dcg(scores):
        return sum((2 ** score - 1) / math.log2(rank + 2)
                   for rank, score in enumerate(scores))
    ndcg_ideal = dcg(sorted(relevance.values(), reverse=True)[:10])
    return {
        "hit_at_1": int(bool(ranks and ranks[0] <= 1)),
        "hit_at_5": int(bool(ranks and ranks[0] <= 5)),
        "hit_at_10": int(bool(ranks and ranks[0] <= 10)),
        "recall_at_5": recall(5),
        "recall_at_10": recall(10),
        "mrr_at_10": 1 / ranks[0] if ranks else 0,
        "ndcg_at_10": dcg([relevance.get(doc_id, 0) for doc_id in ranked_ids[:10]]) / ndcg_ideal,
    }


def main():
    from langchain_huggingface import HuggingFaceEmbeddings

    dataset = dataset_paths()
    corpus, queries, qrels = load_data(dataset)
    selected_ids = random.Random(SEED).sample(sorted(qrels, key=int), SAMPLE_SIZE)
    corpus_subset, gold_count = select_corpus(corpus, qrels, selected_ids)
    parsed, metadata = ingest_adapter(corpus_subset)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        encode_kwargs={"normalize_embeddings": True},
    )
    store = build_vector_store(
        parsed, metadata, embeddings,
        persist_directory=CACHE / "scifact_20q_500d_mpnet_cosine",
        collection_name="beir_scifact_20q_500d_mpnet_cosine",
    )
    retriever = ResearchRetriever(store, max_chunks_per_paper=2)
    rows = []
    for index, query_id in enumerate(selected_ids, start=1):
        chunks = retriever.retrieve(queries[query_id], k=10, fetch_k=30)
        ranked_ids = list(dict.fromkeys(chunk.paper_id for chunk in chunks))
        metrics = score_query(ranked_ids, qrels[query_id])
        rows.append({"query_id": query_id, "query": queries[query_id],
                     "relevant_ids": qrels[query_id], "retrieved_ids": ranked_ids,
                     "metrics": metrics})
        if index % 20 == 0:
            print(f"Scored {index}/{SAMPLE_SIZE} test queries", flush=True)
    names = rows[0]["metrics"]
    summary = {key: sum(row["metrics"][key] for row in rows) / SAMPLE_SIZE
               for key in names}
    result = {
        "dataset": "BEIR SciFact", "split": "test",
        "dataset_url": DATASET_URL, "archive_md5": DATASET_MD5,
        "full_corpus_documents": len(corpus),
        "indexed_corpus_documents": len(corpus_subset),
        "labeled_relevant_documents_in_subset": gold_count,
        "test_queries_available": len(qrels),
        "sampled_test_queries": SAMPLE_SIZE, "sample_seed": SEED,
        "sample_method": "random.Random(42).sample(numerically sorted test query IDs, 20)",
        "corpus_method": "all judged relevant articles for selected claims plus random.Random(43) distractors to 500 total",
        "model": "sentence-transformers/all-mpnet-base-v2",
        "index": "title plus abstract, chunked at 350 MPNet tokens with 50-token overlap; cosine Chroma",
        "retriever": "ResearchRetriever, k=10, fetch_k=30, max_chunks_per_paper=2; paper IDs deduplicated",
        "summary": summary, "queries": rows,
    }
    output = ROOT / "evaluation/results/beir_scifact_20q_500d.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
