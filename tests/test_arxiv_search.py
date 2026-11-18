"""Check arXiv provenance and live wiring without contacting the network."""

import threading

import arxiv_search
import frontend_server


FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry><id>https://arxiv.org/abs/2401.12345v2</id>
    <title>Retrieval for Factual Answers</title>
    <summary>Retrieval supplies evidence for factual answers.</summary>
    <published>2024-01-20T00:00:00Z</published>
    <author><name>Researcher One</name></author><category term="cs.CL" />
  </entry>
  <entry><id>https://not-arxiv.example/abs/2401.99999</id>
    <title>Untrusted</title><summary>Wrong origin.</summary>
  </entry>
</feed>"""


def test_search_uses_arxiv_ids_and_broadens_only_when_needed(monkeypatch):
    calls = []

    def fake_request(url, limit):
        calls.append(url)
        return b'<feed xmlns="http://www.w3.org/2005/Atom"></feed>' if len(calls) == 1 else FEED

    monkeypatch.setattr(arxiv_search, "request_bytes", fake_request)
    papers = arxiv_search.search_arxiv("How does retrieval improve factual answers?", 5)
    assert len(calls) == 2
    assert "AND" in calls[0] and "AND" in calls[1]
    assert len(papers) == 1
    assert papers[0].paper_id == "2401.12345"
    assert papers[0].authors == ["Researcher One"]
    assert papers[0].categories == ["cs.CL"]


def test_retriever_returns_citable_arxiv_passages(monkeypatch, tmp_path):
    papers = [
        arxiv_search.Paper("2401.12345", "Retrieval for Factual Answers",
                           "Retrieval supplies evidence for factual answers.", [], "2024-01-20", []),
        arxiv_search.Paper("2401.23456", "Factuality Benchmark",
                           "The benchmark tests factual answers with sources.", [], "2024-01-21", []),
    ]
    monkeypatch.setattr(arxiv_search, "search_arxiv", lambda *args: papers)
    retriever = arxiv_search.ArxivRetriever(tmp_path, pdf_papers=0)

    class Reranker:
        def predict(self, pairs, **kwargs):
            return [2.0, 1.0]

    retriever._reranker = Reranker()
    chunks = retriever.retrieve("How does retrieval support factual answers?", k=2, min_papers=2)
    assert [chunk.paper_id for chunk in chunks] == ["2401.12345", "2401.23456"]
    assert [chunk.rank for chunk in chunks] == [1, 2]
    assert all(chunk.section == "Abstract" for chunk in chunks)
    assert all(chunk.source_url.startswith("https://arxiv.org/abs/") for chunk in chunks)
    assert "[1]" in retriever.format_context(chunks)


def test_live_server_uses_arxiv_retriever(monkeypatch):
    sentinel = object()
    monkeypatch.setattr(frontend_server.app, "load_arxiv_retriever", lambda: sentinel)

    def answer(retriever, question, context, **kwargs):
        assert retriever is sentinel
        assert question == "A research question?"
        return (frontend_server.app.ABSTENTION, []), None

    monkeypatch.setattr(frontend_server.app, "try_live_answer", answer)
    result = frontend_server.make_insight(
        {"mode": "live", "question": "A research question?"},
        live_lock=threading.Lock(), arxiv_live=True,
    )
    assert result["scope"] == "arxiv"
    assert result["sources"] == []
    assert "## Sources" in result["markdown"]
    assert "Proposed business" not in result["markdown"]
