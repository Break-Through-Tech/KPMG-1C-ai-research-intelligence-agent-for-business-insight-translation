"""Run a small, labeled retrieval benchmark against the five checked-in PDFs.

Uses the notebook's actual process_paper function and the repo's ingest and
retrieval modules. It does not invoke an answer generator.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "notebooks"))
from ingest import build_vector_store  # noqa: E402
from retrieval import ResearchRetriever, needs_multiple_papers  # noqa: E402


def compact(text):
    """Tolerate PDF spacing, punctuation, and hyphenation in fact checks."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def notebook_parser():
    notebook = json.loads((ROOT / "notebooks/eda_workbook.ipynb").read_text())
    cells = ["".join(c.get("source", [])) for c in notebook["cells"] if c["cell_type"] == "code"]
    parser_cells = [source for source in cells if "def process_paper(" in source]
    if len(parser_cells) != 1:
        raise RuntimeError("Expected exactly one notebook process_paper definition")
    namespace = {"re": re}
    exec(compile(parser_cells[0], "eda_workbook.ipynb:process_paper", "exec"), namespace)
    return namespace["process_paper"], parser_cells[0]


def load_corpus(benchmark, parser):
    pdfs = sorted((ROOT / "data").glob("*.pdf"))
    if len(pdfs) != len(benchmark["papers"]):
        raise RuntimeError("The PDF count differs from the benchmark catalog")
    parsed, metadata, full_text = {}, [], {}
    for path in pdfs:
        paper_id = path.name.split("v", 1)[0]
        title = benchmark["papers"].get(paper_id)
        if not title:
            raise RuntimeError(f"PDF is not labeled in benchmark.json: {path.name}")
        pages = [page.extract_text() or "" for page in PdfReader(path).pages]
        full_text[paper_id] = compact(" ".join(pages))
        parsed[title] = parser(pages)
        metadata.append({"id": paper_id, "title": title,
                         "source_url": f"https://arxiv.org/abs/{paper_id}"})
    for item in benchmark["queries"]:
        if not set(item["relevant_papers"]) <= set(full_text):
            raise RuntimeError(f"Unknown relevant paper in {item['id']}")
        for phrase in item["evidence"]:
            if not any(compact(phrase) in full_text[paper_id]
                       for paper_id in item["relevant_papers"]):
                raise RuntimeError(f"Evidence for {item['id']} absent from gold PDF: {phrase}")
    return parsed, metadata


def run(benchmark_path, output_path, k, fetch_k, per_paper, rerank_model=None,
        max_rerank_gap=None, rank_fusion=False):
    from langchain_huggingface import HuggingFaceEmbeddings

    benchmark = json.loads(benchmark_path.read_text())
    parser, parser_source = notebook_parser()
    parsed, metadata = load_corpus(benchmark, parser)
    corpus_fingerprint = hashlib.sha256(parser_source.encode())
    corpus_fingerprint.update((ROOT / "notebooks/ingest.py").read_bytes())
    for path in sorted((ROOT / "data").glob("*.pdf")):
        corpus_fingerprint.update(path.read_bytes())
    fingerprint = corpus_fingerprint.hexdigest()[:12]
    cache = ROOT / ".evaluation_cache" / fingerprint
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        encode_kwargs={"normalize_embeddings": True},
    )
    store = build_vector_store(parsed, metadata, embeddings,
                               persist_directory=cache,
                               collection_name="evaluation_mpnet_cosine")
    retriever = ResearchRetriever(store, max_chunks_per_paper=per_paper,
                                  rerank_model=rerank_model,
                                  max_rerank_gap=max_rerank_gap,
                                  rank_fusion=rank_fusion)
    rows = []
    for item in benchmark["queries"]:
        chunks = retriever.retrieve(item["query"], k=k, fetch_k=fetch_k,
                                    min_papers=2 if needs_multiple_papers(item["query"]) else 1)
        ids = list(dict.fromkeys(chunk.paper_id for chunk in chunks))
        gold = item["relevant_papers"]
        hits = [paper_id for paper_id in gold if paper_id in ids]
        evidence_hits = [any(compact(phrase) in compact(chunk.text)
                             for chunk in chunks if chunk.paper_id in gold)
                         for phrase in item["evidence"]]
        rows.append({"id": item["id"], "query": item["query"],
                     "relevant_papers": gold, "retrieved_papers": ids,
                     "retrieved_chunks": [
                         {"paper_id": c.paper_id, "section": c.section,
                          "chunk_id": c.chunk_id,
                          "score": round(c.score, 4), "source_url": c.source_url}
                         for c in chunks],
                     "recall": len(hits) / len(gold) if gold else None,
                     "reciprocal_rank": 1 / (min(ids.index(p) for p in hits) + 1) if hits else 0,
                     "evidence_hits": evidence_hits})
    positive = [row for row in rows if row["relevant_papers"]]
    negatives = [row for row in rows if not row["relevant_papers"]]
    evidence = [hit for row in rows for hit in row["evidence_hits"]]
    all_chunks = [c for row in rows for c in row["retrieved_chunks"]]
    summary = {
        "positive_queries": len(positive), "negative_queries": len(negatives),
        "macro_recall_at_k": sum(r["recall"] for r in positive) / len(positive),
        "hit_at_k": sum(r["recall"] > 0 for r in positive) / len(positive),
        "mrr_at_k": sum(r["reciprocal_rank"] for r in positive) / len(positive),
        "evidence_coverage": sum(evidence) / len(evidence) if evidence else None,
        "evidence_facts": len(evidence),
        "unsupported_queries_with_results": sum(bool(r["retrieved_chunks"]) for r in negatives),
        "citation_metadata_complete": sum(bool(c["paper_id"] and c["source_url"])
                                          for c in all_chunks) / len(all_chunks),
    }
    result = {"benchmark": str(benchmark_path.relative_to(ROOT)),
              "corpus_fingerprint": fingerprint,
              "model": "sentence-transformers/all-mpnet-base-v2",
              "k_chunks": k, "fetch_k": fetch_k, "max_chunks_per_paper": per_paper,
              "rerank_model": rerank_model,
              "max_rerank_gap": max_rerank_gap,
              "rank_fusion": rank_fusion,
              "summary": summary, "queries": rows}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"Detailed results: {output_path}")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--benchmark", type=Path, default=ROOT / "evaluation/benchmark.json")
    argparser.add_argument("--output", type=Path, default=ROOT / "evaluation/results/retrieval.json")
    argparser.add_argument("--k", type=int, default=5, help="Number of retrieved chunks")
    argparser.add_argument("--fetch-k", type=int, default=30)
    argparser.add_argument("--per-paper", type=int, default=2)
    argparser.add_argument("--rerank-model", default=None)
    argparser.add_argument("--max-rerank-gap", type=float, default=None)
    argparser.add_argument("--rank-fusion", action="store_true")
    args = argparser.parse_args()
    run(args.benchmark.resolve(), args.output.resolve(), args.k, args.fetch_k,
        args.per_paper, args.rerank_model, args.max_rerank_gap,
        args.rank_fusion)
