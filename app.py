"""Streamlit research review UI with a model-free saved-benchmark fallback.

Run from the repository root: streamlit run app.py
Importing helpers neither imports Streamlit nor initializes models or services.
"""

import json
import math
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "notebooks"))

from answer_validation import ABSTENTION, answer_issues, attach_evidence
from business_translator import (
    KPMG_COLLECTION_AREAS, build_business_insight_prompt, format_structured_business_insight,
    infer_collection_area, recommend_min_papers, reformat_prompt,
)
from personas import selectable_personas
from retrieval import ResearchRetriever, RetrievedChunk, load_paper_metadata

OLLAMA_HOST = "http://127.0.0.1:11434"
MODEL = "llama3.2"


def load_demo_data(root: Path = ROOT) -> tuple[dict, list[dict]]:
    """Join saved answers to the benchmark by ID, never by list position.

    Bad/missing files produce an actionable UI message, not an uncaught exception.
    """
    benchmark = json.loads((root / "evaluation/benchmark.json").read_text(encoding="utf-8"))
    report = json.loads((root / "evaluation/results/answers_grounded.json").read_text(encoding="utf-8"))
    papers = benchmark["papers"]
    if not isinstance(papers, dict) or not isinstance(report["answers"], list):
        raise ValueError("Malformed benchmark or saved answers.")
    answers = {row["id"]: row for row in report["answers"]}
    records = []
    for query in benchmark["queries"]:
        saved = answers.get(query["id"], {})
        answer = saved.get("answer", ABSTENTION)
        passages = saved.get("passages", [])
        if not isinstance(answer, str) or not isinstance(passages, list):
            raise ValueError(f"Malformed saved answer for {query['id']}.")
        records.append({**saved, **query, "answer": answer, "passages": passages,
                        "saved_answer_available": bool(saved)})
    return papers, records


def demo_chunks(record: dict, papers: dict, metadata: dict | None = None) -> list[RetrievedChunk]:
    """Rehydrate saved passages; unavailable metadata and scores stay explicit."""
    metadata = metadata or {}
    chunks = []
    for number, passage in enumerate(record["passages"], 1):
        paper_id = passage["paper_id"]
        meta = metadata.get(paper_id, {})
        chunks.append(RetrievedChunk(
            rank=number, score=float("nan"), text=passage["text"], paper_id=paper_id,
            title=papers.get(paper_id, paper_id), section=passage.get("section", ""),
            source_url=f"https://arxiv.org/abs/{paper_id}", chunk_id=passage.get("chunk_id", ""),
            authors=meta.get("authors", []), published=(meta.get("published") or "")[:10],
            collection_areas=meta.get("collection_areas", []),
        ))
    return chunks


def load_live_retriever(root: Path = ROOT) -> ResearchRetriever:
    """Open an existing populated collection and locally cached models only."""
    directory = root / "arxiv_data/chroma_db"
    if not (directory / "chroma.sqlite3").is_file():
        raise FileNotFoundError("Build the notebook's citable Chroma index to enable live mode.")
    tags = json.loads(urlopen(OLLAMA_HOST + "/api/tags", timeout=2).read())
    if not any(item["name"].split(":")[0] == MODEL for item in tags.get("models", [])):
        raise RuntimeError("Install the local llama3.2 model to enable live mode.")
    import chromadb
    from langchain_huggingface import HuggingFaceEmbeddings

    collection = chromadb.PersistentClient(path=str(directory)).get_collection(
        "research_mpnet_cosine_v3_citable"
    )
    if not collection.count():
        raise ValueError("The citable Chroma collection is empty.")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={"local_files_only": True}, encode_kwargs={"normalize_embeddings": True},
    )
    retriever = ResearchRetriever.from_persisted(
        embeddings, persist_directory=directory, metadata_path=root / "arxiv_data/metadata/papers.jsonl",
        max_chunks_per_paper=4, rerank_model="cross-encoder/ms-marco-MiniLM-L6-v2",
        max_rerank_gap=8, order_by_vector=True,
    )
    # Avoid downloading the reranker during a presentation.
    from sentence_transformers import CrossEncoder
    retriever._reranker = CrossEncoder(retriever.rerank_model, local_files_only=True)
    return retriever


def live_answer(
    retriever: ResearchRetriever, question: str, persona_context: str,
    k: int = 5, min_papers: int | None = None, collection_area: str | None = None,
    rewrite: bool = True,
) -> tuple[str, list[RetrievedChunk]]:
    """Retrieve with synthesis reservations, generate locally, and attach quotes."""
    query = reformat_prompt(question) if rewrite else question
    chunks = retriever.retrieve(
        query, k=k, fetch_k=60, collection_area=collection_area,
        min_papers=min_papers if min_papers is not None else recommend_min_papers(question),
    )
    if not chunks:
        return ABSTENTION, []
    prompt = build_business_insight_prompt(question, retriever.format_context(chunks), persona_context)
    prompt += "\nReturn only the technical evidence answer. The UI adds business framing separately."
    payload = json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "options": {"temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": 550},
    }).encode("utf-8")
    request = Request(OLLAMA_HOST + "/api/generate", data=payload,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=45) as response:
        answer = json.loads(response.read())["response"]
    return attach_evidence(answer, chunks, question), chunks


def try_live_answer(retriever: ResearchRetriever, question: str, persona_context: str, **kwargs) -> tuple[tuple | None, str | None]:
    """Contain service failures at the presentation boundary so saved demo stays usable."""
    try:
        return live_answer(retriever, question, persona_context, **kwargs), None
    except Exception as error:
        return None, f"Live mode unavailable ({type(error).__name__}); browsing saved benchmark answers."


def safe_arxiv_url(url: str) -> str | None:
    """Only expose direct arXiv links from provenance metadata."""
    parsed = urlparse(url)
    return url if parsed.scheme in {"https", "http"} and parsed.netloc == "arxiv.org" else None


def render_answer(st, question: str, answer: str, chunks: list[RetrievedChunk], persona_context: str) -> None:
    """Present business hypotheses, mechanical checks, and original passages separately."""
    insight = format_structured_business_insight(question, answer, chunks, persona_context)
    business, technical, sources = st.tabs([
        "KPMG Business Insight Translation", "Grounded Technical Answer & Mechanical Verification",
        "Retrieved Source Passages & Provenance",
    ])
    with business:
        st.caption("Business framing is a proposed application for review, not a paper finding.")
        for title, body in (("What the Study Found", insight.what_study_found),
                            ("Why It Matters to KPMG", insight.why_it_matters_to_kpmg),
                            ("What KPMG Could Consider · Proportionate Guardrails", insight.what_kpmg_could_consider)):
            st.subheader(title)
            st.write(body)
    with technical:
        st.write(answer)
        issues = answer_issues(answer, chunks)
        if issues:
            for issue in issues:
                st.warning(issue)
        else:
            st.success("Mechanical checks passed (or clean abstention).")
        st.info("Citation and verbatim-quote checks do not establish semantic correctness. Human review required.")
        st.code(insight.sources_block or "No retrieved sources.", language=None)
    with sources:
        for chunk in chunks:
            with st.expander(f"[{chunk.rank}] {chunk.title} · {chunk.section}"):
                st.write({"Paper ID": chunk.paper_id, "Chunk ID": chunk.chunk_id,
                          "Cosine/rerank score": chunk.score if math.isfinite(chunk.score) else "Not saved",
                          "Authors": chunk.authors or "Not saved", "Date": chunk.published or "Not saved",
                          "Collection areas": chunk.collection_areas or "Not saved"})
                st.caption("Live scores are cross-encoder scores, not cosine probabilities.")
                url = safe_arxiv_url(chunk.source_url)
                if url:
                    st.link_button("Open arXiv paper", url)
                st.text(chunk.text)


def main() -> None:
    """Start a resilient review UI; model imports occur only on live-mode selection."""
    import streamlit as st

    st.set_page_config(page_title="KPMG Research Insights", layout="wide")
    st.title("KPMG Research Insights")
    personas = selectable_personas()
    key = st.sidebar.selectbox("KPMG Stakeholder Persona", list(personas),
                               format_func=lambda key: personas[key].name)
    persona = personas[key]
    st.sidebar.write(persona.context)
    mode = st.sidebar.radio("Execution mode", ["Offline benchmark demo", "Live RAG + Local Ollama"])
    area = st.sidebar.selectbox("KPMG Business Area Filter", ["Auto", "All"] + list(KPMG_COLLECTION_AREAS))
    k = st.sidebar.slider("Top-k chunks", 3, 10, 5)
    synthesis = st.sidebar.selectbox("Cross-paper synthesis (minimum papers)", ["Auto", "1", "2", "3"])
    rewrite = st.sidebar.checkbox("Rewrite business queries for retrieval", value=True)
    retriever = None
    if mode == "Live RAG + Local Ollama":
        try:
            retriever = st.cache_resource(load_live_retriever)()
        except Exception as error:
            st.warning(f"Live mode unavailable ({type(error).__name__}); using saved benchmark demo.")
    if retriever is not None:
        question = st.text_input("Ask a research question")
        if st.button("Generate insight"):
            if not question.strip():
                st.warning("Enter a research question.")
            else:
                selected_area = infer_collection_area(question) if area == "Auto" else None if area == "All" else area
                with st.spinner("Retrieving and checking evidence..."):
                    result, error = try_live_answer(
                        retriever, question, persona.context, k=k,
                        min_papers=None if synthesis == "Auto" else int(synthesis),
                        collection_area=selected_area, rewrite=rewrite,
                    )
                if error:
                    st.warning(error)
                    retriever = None
                else:
                    st.session_state["live_result"] = (question, *result)
        if retriever is not None:
            if "live_result" in st.session_state:
                question, answer, chunks = st.session_state["live_result"]
                render_answer(st, question, answer, chunks, persona.context)
            return
    st.info("Saved benchmark demo: 25 fixed questions. Retrieval controls apply only in live mode; "
            "saved answers and passage order are unchanged. These are diagnostic outputs, not validated business advice.")
    try:
        papers, records = load_demo_data()
        metadata = load_paper_metadata(ROOT / "arxiv_data/metadata/papers.jsonl")
        if not records:
            st.warning("No saved benchmark questions are available.")
            return
        record = st.selectbox("Benchmark question", records, format_func=lambda row: f"{row['id']}: {row['query']}")
        if not record["saved_answer_available"]:
            st.warning("No saved answer for this question.")
        render_answer(st, record["query"], record["answer"], demo_chunks(record, papers, metadata), persona.context)
        st.subheader("Five sample paper insights")
        for paper_id, title in papers.items():
            sample = next((row for row in records if row["relevant_papers"] == [paper_id]), None)
            with st.expander(title):
                if sample:
                    insight = format_structured_business_insight(
                        sample["query"], sample["answer"], demo_chunks(sample, papers, metadata), persona.context
                    )
                    st.write(insight.what_study_found)
                    st.write(insight.why_it_matters_to_kpmg)
                    st.write(insight.what_kpmg_could_consider)
                    for warning in insight.validation_warnings:
                        st.warning(warning)
    except (OSError, ValueError, KeyError, TypeError) as error:
        st.error(f"Saved demo files are missing or malformed ({type(error).__name__}). "
                 "Restore evaluation/benchmark.json and evaluation/results/answers_grounded.json from the repository.")


if __name__ == "__main__":
    main()
