import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "notebooks"))
from ingest import build_documents, build_vector_store, chunk_documents, chunk_ids  # noqa: E402
from test_retrieval import KeywordEmbeddings  # noqa: E402

PAPERS = [
    {"id": "p1", "title": "Paper One", "authors": ["Ann", "Bo"], "published": "2026-08-01T00:00:00+00:00",
     "source_url": "http://arxiv.org/abs/p1", "primary_category": "cs.AI", "categories": ["cs.AI", "cs.LG"],
     "collection_areas": ["workflow_automation"]},
    {"id": "p2", "title": "Paper Two", "authors": [], "published": None,
     "source_url": "http://arxiv.org/abs/p2", "primary_category": "cs.CL", "categories": ["cs.CL"],
     "collection_areas": []},
]
PARSED = {
    "Paper One": {"all": "...", "Abstract": "agent audit", "1 Introduction": "  ", "2 Method": "agent " * 40},
    "Paper Two": {"all": "...", "Abstract": "routing cost"},
}
words = lambda text: len(text.split())  # noqa: E731


def test_build_documents_metadata_and_order():
    docs = build_documents(PARSED, PAPERS)
    assert [d.metadata["section"] for d in docs] == ["Abstract", "2 Method", "Abstract"]  # empty section skipped
    assert [d.metadata["section_order"] for d in docs] == [0, 2, 0]
    meta = docs[0].metadata
    assert meta["authors"] == "Ann, Bo"
    assert meta["published"] == "2026-08-01"
    assert meta["categories"] == "cs.AI, cs.LG"
    assert meta["collection_areas"] == "workflow_automation"
    assert docs[2].metadata["published"] == ""
    assert all(isinstance(v, (str, int)) for d in docs for v in d.metadata.values())  # Chroma needs scalars


def test_build_documents_rejects_unknown_title():
    with pytest.raises(ValueError):
        build_documents({"Unknown": {"Abstract": "x"}}, PAPERS)


def test_chunk_ids_are_unique_and_stable():
    chunks = chunk_documents(build_documents(PARSED, PAPERS), chunk_size=10, chunk_overlap=2,
                             length_function=words)
    ids = chunk_ids(chunks)
    assert len(ids) == len(set(ids))
    assert ids[0] == "p1_0_1" and "p1_2_2" in ids


def test_build_vector_store_uses_cosine_and_is_idempotent(tmp_path):
    for _ in range(2):
        store = build_vector_store(PARSED, PAPERS, KeywordEmbeddings(), persist_directory=tmp_path,
                                   collection_name="test_ingest", length_function=words)
    assert store._collection.metadata["hnsw:space"] == "cosine"
    assert store._collection.count() == len(chunk_ids(chunk_documents(
        build_documents(PARSED, PAPERS), length_function=words)))


class CountingEmbeddings(KeywordEmbeddings):
    def __init__(self):
        self.embedded = 0

    def embed_documents(self, texts):
        self.embedded += len(texts)
        return super().embed_documents(texts)


def test_build_vector_store_resumes_without_reembedding(tmp_path, capsys):
    total = len(chunk_documents(build_documents(PARSED, PAPERS), length_function=words))
    first = CountingEmbeddings()
    build_vector_store(PARSED, PAPERS, first, persist_directory=tmp_path,
                       collection_name="test_resume", length_function=words)
    assert first.embedded == total

    second = CountingEmbeddings()
    store = build_vector_store(PARSED, PAPERS, second, persist_directory=tmp_path,
                               collection_name="test_resume", length_function=words)
    assert second.embedded == 0
    assert store._collection.count() == total
    assert f"Resuming: {total} chunks already stored, 0 to embed." in capsys.readouterr().out
