"""On-demand arXiv retrieval for the local research chat.

Search the arXiv catalog for each question, read a few matching PDFs, then
return citable passages. This is separate from the five-paper evaluation index.
"""

from dataclasses import dataclass
from io import BytesIO
import math
from pathlib import Path
import re
import threading
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from notebooks.retrieval import RetrievedChunk, looks_like_bibliography


ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_API = "https://export.arxiv.org/api/query"
ARXIV_ID = re.compile(r"(?:\d{4}\.\d{4,5}|[a-z][a-z.\-]+/\d{7})(?:v\d+)?", re.I)
WORDS = re.compile(r"[a-z][a-z0-9]+", re.I)
STOPWORDS = {"about", "after", "among", "and", "are", "can", "could", "does", "for", "from",
             "have", "how", "improve", "into", "many", "much", "papers", "research", "results", "study",
             "that", "the", "their", "these", "this", "those", "using", "was", "were", "what",
             "when", "where", "which", "with", "would"}
_request_lock = threading.Lock()
_last_request = 0.0


@dataclass(frozen=True)
class Paper:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    published: str
    categories: list[str]


def terms(question: str) -> list[str]:
    return list(dict.fromkeys(word.lower() for word in WORDS.findall(question)
                              if len(word) > 2 and word.lower() not in STOPWORDS))[:8]


def search_expression(question: str, broad: bool = False) -> str:
    words = terms(question)
    if not words:
        raise ValueError("Ask a more specific research question.")
    return " AND ".join(f"all:{word}" for word in words[:2 if broad else 4])


def request_bytes(url: str, limit: int) -> bytes:
    """Bound downloads and observe arXiv's three-second request spacing."""
    global _last_request
    host = urlparse(url).hostname
    if host not in {"arxiv.org", "export.arxiv.org"}:
        raise ValueError("Only arXiv URLs may be fetched.")
    with _request_lock:
        pause = 3.1 - (time.monotonic() - _last_request)
        if pause > 0:
            time.sleep(pause)
        _last_request = time.monotonic()
        request = Request(url, headers={"User-Agent": "KPMG-1C-research-prototype/0.1 (academic research demo)"})
        with urlopen(request, timeout=30) as response:
            if urlparse(response.geturl()).hostname not in {"arxiv.org", "export.arxiv.org"}:
                raise ValueError("arXiv redirected outside its domain.")
            data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("arXiv response exceeded the size limit.")
    return data


def parse_feed(xml: bytes) -> list[Paper]:
    feed = ET.fromstring(xml)
    papers = []
    for entry in feed.findall(f"{ATOM}entry"):
        url = (entry.findtext(f"{ATOM}id") or "").strip()
        parsed = urlparse(url)
        if parsed.hostname != "arxiv.org" or not parsed.path.startswith("/abs/"):
            continue
        paper_id = parsed.path.removeprefix("/abs/")
        if not ARXIV_ID.fullmatch(paper_id):
            continue
        paper_id = re.sub(r"v\d+$", "", paper_id)
        title = " ".join((entry.findtext(f"{ATOM}title") or "").split())
        summary = " ".join((entry.findtext(f"{ATOM}summary") or "").split())
        if not title or not summary:
            continue
        authors = [" ".join((author.findtext(f"{ATOM}name") or "").split())
                   for author in entry.findall(f"{ATOM}author")]
        published = (entry.findtext(f"{ATOM}published") or "")[:10]
        categories = [item.attrib["term"] for item in entry.findall(f"{ATOM}category")
                      if item.attrib.get("term")]
        papers.append(Paper(paper_id, title, summary, authors, published, categories))
    return papers


def search_arxiv(question: str, max_results: int = 20) -> list[Paper]:
    """Use arXiv relevance search; broaden once if the precise query is empty."""
    if not 1 <= max_results <= 50:
        raise ValueError("Choose 1–50 search results.")
    expressions = list(dict.fromkeys((search_expression(question), search_expression(question, True))))
    for expression in expressions:
        query = urlencode({"search_query": expression, "start": 0,
                           "max_results": max_results, "sortBy": "relevance",
                           "sortOrder": "descending"})
        papers = parse_feed(request_bytes(f"{ARXIV_API}?{query}", 2_000_000))
        if papers:
            return papers
    return []


def pdf_passages(pdf: bytes, paper: Paper, max_pages: int = 25) -> list[RetrievedChunk]:
    """Extract overlapping page chunks, preserving page provenance."""
    reader = PdfReader(BytesIO(pdf))
    passages = []
    for page_no, page in enumerate(reader.pages[:max_pages], 1):
        text = " ".join((page.extract_text() or "").split())
        words = text.split()
        if len(words) < 40 or looks_like_bibliography(text):
            continue
        for start in range(0, len(words), 210):
            chunk = " ".join(words[start:start + 260])
            if len(chunk.split()) < 35:
                continue
            passages.append(RetrievedChunk(
                rank=0, score=0.0, text=chunk, paper_id=paper.paper_id,
                title=paper.title, section=f"Page {page_no}",
                source_url=f"https://arxiv.org/abs/{paper.paper_id}",
                chunk_id=f"{paper.paper_id}_p{page_no}_{start}",
                authors=paper.authors, published=paper.published,
                categories=paper.categories,
            ))
    return passages


def relevance(question: str, chunk: RetrievedChunk) -> float:
    wanted = set(terms(question))
    text = set(WORDS.findall(chunk.text.lower()))
    title = set(WORDS.findall(chunk.title.lower()))
    return (sum(1.5 if word in title else 1 for word in wanted if word in text or word in title)
            / max(len(wanted), 1))


class ArxivRetriever:
    """Small per-question passage set from the whole searchable arXiv catalog."""

    def __init__(self, cache: Path, max_results: int = 20, pdf_papers: int = 3):
        self.cache = Path(cache)
        self.max_results = max_results
        self.pdf_papers = pdf_papers
        self._reranker = None

    def _pdf(self, paper: Paper) -> bytes:
        path = self.cache / f"{paper.paper_id.replace('/', '_')}.pdf"
        if path.is_file():
            return path.read_bytes()
        data = request_bytes(f"https://arxiv.org/pdf/{paper.paper_id}", 12_000_000)
        if not data.startswith(b"%PDF"):
            raise ValueError("arXiv did not return a PDF.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return data

    def retrieve(self, query: str, k: int = 5, fetch_k: int = 60,
                 collection_area: str | None = None, min_papers: int = 1,
                 **_ignored) -> list[RetrievedChunk]:
        if not query.strip():
            raise ValueError("Query is empty.")
        papers = search_arxiv(query, self.max_results)
        candidates = [RetrievedChunk(
            rank=0, score=0.0, text=paper.summary, paper_id=paper.paper_id,
            title=paper.title, section="Abstract",
            source_url=f"https://arxiv.org/abs/{paper.paper_id}",
            chunk_id=f"{paper.paper_id}_abstract", authors=paper.authors,
            published=paper.published, categories=paper.categories,
        ) for paper in papers]
        for paper in papers[:self.pdf_papers]:
            try:
                candidates.extend(pdf_passages(self._pdf(paper), paper))
            except (OSError, ValueError, IndexError, TypeError, PdfReadError):
                pass  # An abstract is still a traceable source when a PDF cannot be read.
        if not candidates:
            return []
        candidates.sort(key=lambda chunk: relevance(query, chunk), reverse=True)
        candidates = candidates[:max(fetch_k, k)]
        paper_order = {paper.paper_id: index for index, paper in enumerate(papers)}

        def blended_score(chunk, semantic):
            search_rank = 1 - paper_order.get(chunk.paper_id, len(papers)) / max(len(papers), 1)
            return 0.7 * semantic + 0.3 * search_rank

        try:
            if self._reranker is None:
                from sentence_transformers import CrossEncoder
                self._reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2", local_files_only=True)
            scores = self._reranker.predict([(query, chunk.title + " " + chunk.text) for chunk in candidates],
                                            batch_size=16, show_progress_bar=False)
            ranked = [(chunk, blended_score(
                chunk, 1 / (1 + math.exp(-max(-30, min(30, float(score)))))))
                for chunk, score in zip(candidates, scores)]
            ranked.sort(key=lambda item: item[1], reverse=True)
        except (ImportError, OSError, RuntimeError, ValueError):
            ranked = [(chunk, blended_score(chunk, min(1.0, relevance(query, chunk))))
                      for chunk in candidates]
            ranked.sort(key=lambda item: item[1], reverse=True)
        selected = []
        used = set()
        counts = {}
        if min_papers > 1:
            for chunk, score in ranked:
                if chunk.paper_id not in used:
                    selected.append((chunk, score))
                    used.add(chunk.paper_id)
                    counts[chunk.paper_id] = 1
                if len(used) >= min(min_papers, k):
                    break
        for chunk, score in ranked:
            if len(selected) >= k:
                break
            if any(chunk is prior for prior, _ in selected):
                continue
            if counts.get(chunk.paper_id, 0) >= 2:
                continue
            selected.append((chunk, score))
            counts[chunk.paper_id] = counts.get(chunk.paper_id, 0) + 1
        for rank, (chunk, score) in enumerate(selected, 1):
            chunk.rank = rank
            chunk.score = score
        return [chunk for chunk, _ in selected]

    @staticmethod
    def format_context(results: list[RetrievedChunk]) -> str:
        return "\n\n".join(f"[{chunk.rank}] {chunk.title} — {chunk.section} "
                           f"(chunk {chunk.chunk_id})\n{chunk.text}" for chunk in results)

    def format_focused_context(self, query: str, results: list[RetrievedChunk]) -> str:
        return self.format_context(results)
