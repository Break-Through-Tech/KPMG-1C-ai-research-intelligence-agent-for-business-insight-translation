"""
Retrieval layer for the research RAG pipeline (Task #5).

Sits on top of the Chroma collection built in `eda_workbook.ipynb` and turns a
question into a small, citable set of chunks for the summarizer.

What it adds over a plain `vector_store.similarity_search`:
- Drops boilerplate sections (references, acknowledgements) that match queries
  on keywords but carry no findings, plus chunks whose text reads like a
  bibliography (catches reference entries the parser mislabels as headings,
  e.g. "8 Amin Jalali").
- Caps chunks per paper so one long paper can't fill every slot (the EDA found
  papers ranging from ~2,900 to ~46,500 words).
- Returns each chunk with the paper's full metadata (authors, published date,
  categories, collection areas) for citations: read from the chunk when it was
  built by `ingest.py`, otherwise looked up in `papers.jsonl`.
- Formats retrieved chunks as a numbered context block plus a source list, so
  the summarizer can cite [1], [2], ... and we can trace every claim.

Usage from `notebooks/` (after the Chroma collection has been built):

    from retrieval import ResearchRetriever

    retriever = ResearchRetriever.from_persisted(embeddings=embeddings)
    results = retriever.retrieve("How can AI agents automate audit workflows?")
    context = retriever.format_context(results)
    sources = retriever.format_sources(results)
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_PERSIST_DIRECTORY = "arxiv_data/chroma_db"
DEFAULT_COLLECTION_NAME = "research_mpnet_cosine_v2"  # built by ingest.py
DEFAULT_METADATA_PATH = "arxiv_data/metadata/papers.jsonl"

# Sections that match queries on vocabulary alone but hold no findings.
EXCLUDED_SECTIONS = {
    "references", "bibliography",
    "acknowledgment", "acknowledgments", "acknowledgement", "acknowledgements",
}


def normalize_section(section: str) -> str:
    """'7 References' -> 'references', 'B.2 Acknowledgments' -> 'acknowledgments'"""
    section = re.sub(r"^(\d{1,2}|[A-H])(\.\d{1,2})*\.?\s+", "", section.strip())
    return section.lower().rstrip(".:")


YEAR = re.compile(r"\b(?:19|20)\d{2}[a-z]?\b")
AUTHOR_INITIAL = re.compile(r"\b[A-Z]\.(?:\s?[A-Z]\.)*\s")
VENUE = re.compile(
    r"et al\.|arXiv|doi|Proceedings|Conference|Journal|Transactions|pp\.|In:|URL|https?://|Preprint|Vol\.",
    re.IGNORECASE,
)


def looks_like_bibliography(text: str) -> bool:
    """True if `text` reads like a reference list rather than findings.

    Uses densities per 100 words. Calibrated on real chunks: reference lists
    have author initials plus dense years/venues; citation-heavy prose such as
    Related Work has years and venues but no initials, and venue density <= ~6.
    """
    words = len(text.split())
    if words < 30:
        return False
    years = 100 * len(YEAR.findall(text)) / words
    initials = 100 * len(AUTHOR_INITIAL.findall(text)) / words
    venues = 100 * len(VENUE.findall(text)) / words
    return (
        initials >= 4
        or (initials > 0 and years >= 2.5 and venues >= 3.5)
        or (years >= 3 and venues >= 7)
    )


def split_list(value) -> list:
    """Chunk metadata stores lists as 'a, b, c' (see ingest.py)."""
    if isinstance(value, list):
        return value
    return [item.strip() for item in value.split(",") if item.strip()] if value else []


def load_paper_metadata(metadata_path=DEFAULT_METADATA_PATH) -> dict:
    """Map paper id -> metadata record from the saved papers.jsonl catalog."""
    path = Path(metadata_path)
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as file:
        records = [json.loads(line) for line in file if line.strip()]
    return {record["id"]: record for record in records}


@dataclass
class RetrievedChunk:
    rank: int
    score: float
    text: str
    paper_id: str
    title: str
    section: str
    source_url: str
    authors: list = field(default_factory=list)
    published: str = ""
    categories: list = field(default_factory=list)
    collection_areas: list = field(default_factory=list)


class ResearchRetriever:
    def __init__(
        self,
        vector_store,
        paper_metadata: dict | None = None,
        excluded_sections=EXCLUDED_SECTIONS,
        max_chunks_per_paper: int = 2,
        min_score: float | None = None,
        drop_bibliography: bool = True,
    ):
        self.vector_store = vector_store
        self.paper_metadata = paper_metadata or {}
        self.excluded_sections = set(excluded_sections)
        self.max_chunks_per_paper = max_chunks_per_paper
        self.min_score = min_score
        self.drop_bibliography = drop_bibliography

    @classmethod
    def from_persisted(
        cls,
        embeddings,
        persist_directory=DEFAULT_PERSIST_DIRECTORY,
        collection_name=DEFAULT_COLLECTION_NAME,
        metadata_path=DEFAULT_METADATA_PATH,
        **kwargs,
    ):
        """Open the Chroma collection built in the notebook. `embeddings` must be
        the same model used at ingestion (all-mpnet-base-v2, normalized)."""
        from langchain_chroma import Chroma

        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(persist_directory),
        )
        return cls(vector_store, load_paper_metadata(metadata_path), **kwargs)

    def retrieve(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 30,
        paper_ids: list[str] | None = None,
        collection_area: str | None = None,
    ) -> list[RetrievedChunk]:
        """
        Return up to `k` chunks for `query`, best first.

        Fetches `fetch_k` candidates, then drops excluded sections, bibliography-like
        text, low scores,
        papers outside `collection_area`, and chunks beyond the per-paper cap.
        """
        if not query.strip():
            raise ValueError("Query is empty.")

        where = None
        if paper_ids:
            where = {"paper_id": {"$in": list(paper_ids)}}

        candidates = self.vector_store.similarity_search_with_relevance_scores(
            query, k=max(fetch_k, k), filter=where
        )

        results = []
        chunks_per_paper = {}

        for doc, score in candidates:
            meta = doc.metadata
            paper_id = meta.get("paper_id", "")
            paper = self.paper_metadata.get(paper_id, {})

            if normalize_section(meta.get("section", "")) in self.excluded_sections:
                continue
            if self.drop_bibliography and looks_like_bibliography(doc.page_content):
                continue
            if self.min_score is not None and score < self.min_score:
                continue
            areas = split_list(meta.get("collection_areas")) or paper.get("collection_areas", [])
            if collection_area and collection_area not in areas:
                continue
            if chunks_per_paper.get(paper_id, 0) >= self.max_chunks_per_paper:
                continue

            chunks_per_paper[paper_id] = chunks_per_paper.get(paper_id, 0) + 1
            results.append(RetrievedChunk(
                rank=len(results) + 1,
                score=float(score),
                text=doc.page_content,
                paper_id=paper_id,
                title=meta.get("title", paper.get("title", "")),
                section=meta.get("section", ""),
                source_url=meta.get("source_url", paper.get("source_url", "")),
                authors=split_list(meta.get("authors")) or paper.get("authors", []),
                published=(meta.get("published") or paper.get("published") or "")[:10],
                categories=split_list(meta.get("categories")) or paper.get("categories", []),
                collection_areas=areas,
            ))
            if len(results) == k:
                break

        return results

    @staticmethod
    def citation_numbers(results: list[RetrievedChunk]) -> dict:
        """Map paper id -> citation number, in order of first appearance."""
        numbers = {}
        for chunk in results:
            numbers.setdefault(chunk.paper_id, len(numbers) + 1)
        return numbers

    def format_context(self, results: list[RetrievedChunk]) -> str:
        """Numbered context block for the summarizer prompt. Chunks from the same
        paper share a citation number so the LLM cites papers, not chunks."""
        numbers = self.citation_numbers(results)
        blocks = [
            f"[{numbers[chunk.paper_id]}] {chunk.title} — {chunk.section}\n{chunk.text}"
            for chunk in results
        ]
        return "\n\n".join(blocks)

    def format_sources(self, results: list[RetrievedChunk]) -> str:
        """Source list matching the citation numbers in `format_context`."""
        numbers = self.citation_numbers(results)
        lines = []
        for paper_id, number in numbers.items():
            chunk = next(c for c in results if c.paper_id == paper_id)
            authors = ", ".join(chunk.authors[:3]) + (" et al." if len(chunk.authors) > 3 else "")
            details = ", ".join(part for part in (authors, chunk.published) if part)
            lines.append(f"[{number}] {chunk.title}" + (f" ({details})" if details else "") + f" — {chunk.source_url}")
        return "\n".join(lines)
