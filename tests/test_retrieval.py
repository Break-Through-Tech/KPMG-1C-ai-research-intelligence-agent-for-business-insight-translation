import sys
from pathlib import Path

import pytest
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "notebooks"))
from retrieval import ResearchRetriever, normalize_section  # noqa: E402

VOCAB = ["agent", "audit", "supply", "chain", "routing", "cost", "thanks", "et", "al"]


class KeywordEmbeddings(Embeddings):
    """Tiny deterministic embedding: normalized counts over a fixed vocabulary."""

    def _embed(self, text):
        words = text.lower().split()
        vector = [float(words.count(word)) + 1e-3 for word in VOCAB]
        norm = sum(x * x for x in vector) ** 0.5
        return [x / norm for x in vector]

    def embed_documents(self, texts):
        return [self._embed(text) for text in texts]

    def embed_query(self, text):
        return self._embed(text)


def chunk(paper_id, section, text):
    return Document(text, metadata={
        "paper_id": paper_id, "title": f"Paper {paper_id}", "section": section,
        "source_url": f"http://arxiv.org/abs/{paper_id}", "section_order": 0,
    })


PAPER_METADATA = {
    "p1": {"id": "p1", "authors": ["Ann", "Bo", "Cy", "Di"], "published": "2026-08-01T00:00:00",
           "collection_areas": ["workflow_automation"], "categories": ["cs.AI"]},
    "p2": {"id": "p2", "authors": ["Eve"], "published": "2026-08-02T00:00:00",
           "collection_areas": ["ai_reliability_governance"], "categories": ["cs.LG"]},
}


@pytest.fixture
def retriever(tmp_path):
    store = Chroma(collection_name="test_retrieval", embedding_function=KeywordEmbeddings(),
                   persist_directory=str(tmp_path),
                   collection_metadata={"hnsw:space": "cosine"})
    store.add_documents([
        chunk("p1", "1 Introduction", "agent audit agent audit"),
        chunk("p1", "3 Method", "agent audit agent"),
        chunk("p1", "4 Results", "agent audit"),
        chunk("p1", "7 References", "agent audit et al agent audit"),
        chunk("p2", "Abstract", "audit agent routing"),
        chunk("p2", "Acknowledgments", "thanks agent audit agent audit"),
    ])
    return ResearchRetriever(store, PAPER_METADATA, max_chunks_per_paper=2)


def test_normalize_section():
    assert normalize_section("7 References") == "references"
    assert normalize_section("B.2 Acknowledgments") == "acknowledgments"
    assert normalize_section("2.1 Related Work") == "related work"
    assert normalize_section("Abstract:") == "abstract"


def test_excludes_boilerplate_sections(retriever):
    results = retriever.retrieve("agent audit", k=10)
    sections = {normalize_section(r.section) for r in results}
    assert "references" not in sections
    assert "acknowledgments" not in sections


def test_caps_chunks_per_paper_and_ranks(retriever):
    results = retriever.retrieve("agent audit", k=10)
    assert sum(r.paper_id == "p1" for r in results) == 2
    assert [r.rank for r in results] == list(range(1, len(results) + 1))
    assert results == sorted(results, key=lambda r: -r.score)


def test_filters(retriever):
    by_area = retriever.retrieve("agent audit", collection_area="ai_reliability_governance")
    assert {r.paper_id for r in by_area} == {"p2"}
    by_id = retriever.retrieve("agent audit", paper_ids=["p1"])
    assert {r.paper_id for r in by_id} == {"p1"}


def test_enriches_metadata(retriever):
    result = retriever.retrieve("routing", k=1)[0]
    assert result.paper_id == "p2"
    assert result.authors == ["Eve"]
    assert result.published == "2026-08-02"
    assert result.collection_areas == ["ai_reliability_governance"]


def test_context_and_sources_share_citation_numbers(retriever):
    results = retriever.retrieve("agent audit", k=3)
    context = retriever.format_context(results)
    sources = retriever.format_sources(results).splitlines()
    numbers = retriever.citation_numbers(results)
    assert sorted(numbers.values()) == list(range(1, len({r.paper_id for r in results}) + 1))
    for paper_id, number in numbers.items():
        assert f"[{number}] Paper {paper_id}" in context
        assert sources[number - 1].startswith(f"[{number}] Paper {paper_id}")
    assert "Ann, Bo, Cy et al." in retriever.format_sources(retriever.retrieve("agent audit", paper_ids=["p1"]))


def test_empty_query_rejected(retriever):
    with pytest.raises(ValueError):
        retriever.retrieve("   ")


BIBLIOGRAPHY = (
    "A. Jalali, M. T. Alam, and L. Nguyen. 2024. Decision checkpoints for process automation. "
    "In Proceedings of the International Conference on Business Process Management, pp. 112-128. "
    "J. Smith and K. Lee. 2023. Agent oversight at scale. arXiv preprint arXiv:2301.01234. "
    "R. Patel, S. Kim, and T. Wu. 2025. Auditing LLM agents. Journal of AI Research 12(3):45-67. "
    "D. Bhusal and P. Rao. 2022. Zero trust for autonomous agents. Transactions on Security, Vol. 9."
)
RELATED_WORK = (
    "Prior work on agent oversight has focused on logging and human review (Smith et al., 2023; "
    "Lee and Park, 2024). Process mining approaches reconstruct workflows from event logs, while "
    "recent studies evaluate how large language model agents handle long-horizon tasks in enterprise "
    "settings (Chen et al., 2025). Unlike these approaches, we ground each oversight decision in "
    "evidence collected during execution and compare it against the declared plan of the agent."
)


def test_looks_like_bibliography():
    from retrieval import looks_like_bibliography
    assert looks_like_bibliography(BIBLIOGRAPHY)
    assert not looks_like_bibliography(RELATED_WORK)
    assert not looks_like_bibliography("A. B. 2020. arXiv.")  # too short to judge


def test_drops_bibliography_under_mislabeled_section(tmp_path):
    store = Chroma(collection_name="test_bibliography", embedding_function=KeywordEmbeddings(),
                   persist_directory=str(tmp_path), collection_metadata={"hnsw:space": "cosine"})
    store.add_documents([
        chunk("p1", "8 Amin Jalali", "agent audit " + BIBLIOGRAPHY),
        chunk("p1", "2 Related Work", "agent audit " + RELATED_WORK),
    ])
    sections = [r.section for r in ResearchRetriever(store, PAPER_METADATA).retrieve("agent audit")]
    assert sections == ["2 Related Work"]
    kept = ResearchRetriever(store, PAPER_METADATA, drop_bibliography=False).retrieve("agent audit")
    assert {r.section for r in kept} == {"8 Amin Jalali", "2 Related Work"}
