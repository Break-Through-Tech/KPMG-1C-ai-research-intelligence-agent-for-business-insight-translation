"""UI helpers and actual Streamlit rendering, offline with tiny service fakes."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "notebooks"))

import app
from answer_validation import ABSTENTION, answer_issues
from personas import PERSONAS, selectable_personas
from retrieval import ResearchRetriever, RetrievedChunk


def test_personas_have_context_and_exclude_anti_persona():
    assert len(PERSONAS) == 4
    assert len(selectable_personas()) == 3
    assert "jordan" not in selectable_personas()
    assert all("Your current user" in persona.context for persona in selectable_personas().values())


def test_load_committed_benchmark_and_all_passages():
    papers, records = app.load_demo_data()
    assert len(papers) == 5
    assert len(records) == 25
    assert len({r["id"] for r in records}) == 25
    assert all(r["saved_answer_available"] for r in records)
    for record in records:
        chunks = app.demo_chunks(record, papers)
        assert [chunk.rank for chunk in chunks] == list(range(1, len(chunks) + 1))
        assert isinstance(answer_issues(record["answer"], chunks), list)


def test_demo_metadata_is_not_invented():
    papers, records = app.load_demo_data()
    chunks = app.demo_chunks(records[0], papers)
    assert chunks[0].authors == []
    assert chunks[0].published == ""
    assert not app.math.isfinite(chunks[0].score)
    assert chunks[0].source_url.startswith("https://arxiv.org/abs/")
    enriched = app.demo_chunks(records[0], papers, {chunks[0].paper_id: {"authors": ["A"], "published": "2026-01-01"}})
    assert enriched[0].authors == ["A"]


def test_missing_demo_files_report_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        app.load_demo_data(tmp_path)


def test_missing_saved_answer_joins_by_id_and_abstains(tmp_path):
    (tmp_path / "evaluation/results").mkdir(parents=True)
    (tmp_path / "evaluation/benchmark.json").write_text(json.dumps({
        "papers": {}, "queries": [{"id": "q1", "query": "Unknown?", "relevant_papers": []}],
    }))
    (tmp_path / "evaluation/results/answers_grounded.json").write_text(json.dumps({
        "answers": [{"id": "q2", "answer": "Must not match q1", "passages": []}],
    }))
    _, records = app.load_demo_data(tmp_path)
    assert records[0]["answer"] == ABSTENTION
    assert not records[0]["saved_answer_available"]


def test_missing_live_index_fails_before_service_or_model_load(tmp_path):
    with pytest.raises(FileNotFoundError):
        app.load_live_retriever(tmp_path)


@pytest.mark.parametrize("url,valid", [
    ("https://arxiv.org/abs/2608.20316", True),
    ("javascript:alert(1)", False),
    ("https://arxiv.org.evil.test/abs/paper", False),
])
def test_safe_source_links(url, valid):
    assert bool(app.safe_arxiv_url(url)) == valid


class FakeRetriever:
    def __init__(self, chunks):
        self.chunks = chunks

    def retrieve(self, query, **kwargs):
        self.query, self.kwargs = query, kwargs
        return self.chunks

    format_context = ResearchRetriever.format_context


def test_live_answer_rewrites_reserves_filters_and_attaches_quotes(monkeypatch):
    chunk = RetrievedChunk(1, 0.5, "The survey collected 92 commuters and 454 observations.",
                           "p1", "Travel", "Results", "https://arxiv.org/abs/p1")
    retriever = FakeRetriever([chunk])
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return json.dumps({"response": "The survey collected 92 commuters [1]."}).encode()

    def generate(request, timeout):
        captured.update(json.loads(request.data))
        assert timeout == 45
        return Response()

    monkeypatch.setattr(app, "urlopen", generate)
    answer, chunks = app.live_answer(retriever, "Compare Pandora and Travel Behavior survey", "Reviewer", collection_area="operations_supply_chain")
    assert retriever.kwargs["min_papers"] == 2
    assert retriever.kwargs["collection_area"] == "operations_supply_chain"
    assert "Retrieval terms:" in retriever.query
    assert "Reviewer" in captured["prompt"]
    assert captured["model"] == "llama3.2"
    assert not answer_issues(answer, chunks)


def test_no_results_abstains_without_generation(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("No generation expected for an empty context")
    monkeypatch.setattr(app, "urlopen", unexpected)
    assert app.live_answer(FakeRetriever([]), "Question?", "Reviewer", rewrite=False) == (ABSTENTION, [])


def test_generation_failure_falls_back(monkeypatch):
    def fail(*args, **kwargs):
        raise TimeoutError("service unavailable")
    monkeypatch.setattr(app, "live_answer", fail)
    result, error = app.try_live_answer(FakeRetriever([]), "Question?", "Reviewer")
    assert result is None
    assert "saved benchmark" in error


def test_streamlit_offline_ui_and_persona_switch():
    from streamlit.testing.v1 import AppTest

    ui = AppTest.from_file(str(ROOT / "app.py")).run(timeout=15)
    assert not ui.exception
    assert len(ui.tabs) == 3
    benchmark = next(item for item in ui.selectbox if item.label == "Benchmark question")
    assert len(benchmark.options) == 25
    ui.sidebar.selectbox[0].select("marcus").run()
    assert not ui.exception
    assert any("Marcus" in str(item.value) for item in ui.sidebar.markdown)
    next(item for item in ui.selectbox if item.label == "Benchmark question").select_index(24).run()
    assert not ui.exception
    assert any(ABSTENTION in str(item.value) for item in ui.markdown)


def test_streamlit_live_initialization_failure_returns_demo(monkeypatch):
    from streamlit.testing.v1 import AppTest

    def unavailable():
        raise ConnectionError("Offline fixture")

    monkeypatch.setattr(app, "load_live_retriever", unavailable)
    ui = AppTest.from_string("import app; app.main()").run(timeout=15)
    ui.sidebar.radio[0].set_value("Live RAG + Local Ollama").run()
    assert not ui.exception
    assert any("saved benchmark" in str(item.value) for item in ui.warning)
    assert len(next(item for item in ui.selectbox if item.label == "Benchmark question").options) == 25


@pytest.mark.parametrize("failed", [False, True])
def test_streamlit_live_generation_and_failure_ui(monkeypatch, failed):
    from streamlit.testing.v1 import AppTest

    def fake_retriever():
        return FakeRetriever([])

    def generate(*args, **kwargs):
        if failed:
            return None, "Live mode unavailable; browsing saved benchmark answers."
        return (ABSTENTION, []), None

    monkeypatch.setattr(app, "load_live_retriever", fake_retriever)
    monkeypatch.setattr(app, "try_live_answer", generate)
    ui = AppTest.from_string("import app; app.main()").run(timeout=15)
    ui.sidebar.radio[0].set_value("Live RAG + Local Ollama").run()
    ui.text_input[0].set_value("An unsupported question").run()
    ui.button[0].click().run()
    assert not ui.exception
    assert len(ui.tabs) == 3
    if failed:
        assert any(item.label == "Benchmark question" for item in ui.selectbox)
    else:
        assert any(ABSTENTION in str(item.value) for item in ui.markdown)
