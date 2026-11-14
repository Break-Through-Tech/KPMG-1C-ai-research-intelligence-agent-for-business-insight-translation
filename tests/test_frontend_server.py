"""Exercise the frontend contract and HTTP boundary without models or new packages."""

from http.client import HTTPConnection
import json
from pathlib import Path
import sys
import threading

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import frontend_server as frontend


def test_catalog_uses_committed_data_and_selectable_personas():
    data = frontend.bootstrap()
    assert len(data["papers"]) == 5
    assert len(data["questions"]) == 25
    assert len(data["personas"]) == 3
    assert {p["id"] for p in data["personas"]} == set(frontend.app.selectable_personas())
    assert data["default_run"] == data["runs"][0]
    assert data["default_run"] != "answers_grounded.json"


@pytest.mark.parametrize("run", frontend.app.available_evaluation_runs())
def test_all_saved_answers_preserve_sources_checks_and_exports(run):
    papers, records = frontend.app.load_demo_data(answers_name=run)
    for record in records:
        result = frontend.make_insight({"id": record["id"], "run": run})
        assert result["answer"] == record["answer"]
        assert [s["text"] for s in result["sources"]] == [p["text"] for p in record["passages"]]
        assert all(s["score"] is None for s in result["sources"])
        assert all(s["source_url"].startswith("https://arxiv.org/abs/") for s in result["sources"])
        chunks = frontend.app.demo_chunks(record, papers)
        assert result["checks"] == frontend.app.answer_issues(record["answer"], chunks)
        assert record["query"] in result["markdown"]
        if result["insight"]["validation_warnings"]:
            assert result["insight"]["confidence"]["tier"] == "Abstained"
        json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("payload", [[], None, {"id": "missing"}, {"id":"q01", "persona":"jordan"},
                                    {"id":"q01", "run":"../../.env"}, {"mode":"unknown"},
                                    {"id":"q01", "persona":[]}])
def test_invalid_requests_are_rejected(payload):
    with pytest.raises(ValueError):
        frontend.make_insight(payload)


def test_live_disabled_does_not_initialize_models(monkeypatch):
    monkeypatch.setattr(frontend.app, "load_live_retriever", lambda *a: pytest.fail("Model initialized"))
    with pytest.raises(ConnectionError, match="not connected"):
        frontend.make_insight({"mode":"live", "question":"Research question?"})


def test_live_adapter_uses_existing_pipeline_and_releases_lock(monkeypatch, tmp_path):
    captured = {}
    sentinel = object()
    def load(root):
        assert root == tmp_path
        return sentinel
    def answer(retriever, question, context, **kwargs):
        assert retriever is sentinel
        captured.update(question=question, context=context, **kwargs)
        return (frontend.app.ABSTENTION, []), None
    monkeypatch.setattr(frontend.app, "load_live_retriever", load)
    monkeypatch.setattr(frontend.app, "try_live_answer", answer)
    lock = threading.Lock()
    result = frontend.make_insight({"mode":"live", "question":"  Unknown question?  ", "persona":"marcus"}, tmp_path, lock)
    assert captured["question"] == "Unknown question?"
    assert "Risk Assurance" in captured["context"]
    assert result["mode"] == "live" and result["run"] is None
    assert result["insight"]["confidence"]["tier"] == "Abstained"
    assert not lock.locked()
    monkeypatch.setattr(frontend.app, "try_live_answer", lambda *a, **k: (None,"Unavailable"))
    with pytest.raises(ConnectionError):
        frontend.make_insight({"mode":"live", "question":"Question?"}, tmp_path, lock)
    assert not lock.locked()


@pytest.fixture
def http_server():
    server = frontend.FrontendServer(("127.0.0.1", 0))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def request(server, method, path, body=None, headers=None):
    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    status, data, response_headers = response.status, response.read(), response.headers
    connection.close()
    return status, data, response_headers


def test_http_static_allowlist_and_same_origin_boundary(http_server):
    status, body, headers = request(http_server, "GET", "/")
    assert status == 200 and b"Research Intelligence" in body
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"
    for path in ("/.env", "/../app.py", "/%2e%2e/app.py", "/evaluation/benchmark.json"):
        assert request(http_server, "GET", path)[0] == 404
    assert request(http_server,"GET","/api/bootstrap",headers={"Host":"evil.example"})[0] == 403
    status, body, _ = request(http_server,"GET","/api/bootstrap")
    assert status == 200 and json.loads(body)["live_configured"] is False
    payload = json.dumps({"id":"q18"})
    headers = {"Content-Type":"application/json"}
    assert request(http_server,"POST","/api/insight",payload,headers)[0] == 200
    assert request(http_server,"POST","/api/insight",payload,{**headers,"Origin":"https://evil.example"})[0] == 403
    assert request(http_server,"POST","/api/insight","{",headers)[0] == 400
    assert request(http_server,"POST","/api/insight",payload,{"Content-Type":"text/plain"})[0] == 415
    assert request(http_server,"POST","/api/insight","x"*16001,headers)[0] == 413
    assert request(http_server,"POST","/api/insight",json.dumps({"mode":"live","question":"test"}),headers)[0] == 503
