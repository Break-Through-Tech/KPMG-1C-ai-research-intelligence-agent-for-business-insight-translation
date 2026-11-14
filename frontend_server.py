"""Local, same-origin frontend adapter. Existing research modules stay unchanged.

Run: python frontend_server.py --port 8765
Live mode is opt-in: --live-root PATH (an existing notebook index; never builds one).
"""

import argparse
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import threading
from urllib.parse import urlsplit

import app

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "frontend"


def bootstrap():
    papers, records = app.load_demo_data()
    runs = app.available_evaluation_runs()
    return {
        "papers": [{"id": key, "title": title, "url": f"https://arxiv.org/abs/{key}",
                    "area": app.infer_collection_area(title),
                    "questions": [r["id"] for r in records if key in r["relevant_papers"]]}
                   for key, title in papers.items()],
        "questions": [{k: row[k] for k in ("id", "query", "relevant_papers", "saved_answer_available")}
                      for row in records],
        "personas": [{"id": key, "name": p.name, "role": p.role}
                     for key, p in app.selectable_personas().items()],
        "runs": runs,
        "default_run": runs[0],
        "models": [model for model in app.MODELS if not model.startswith("gemini-")],
        "areas": list(app.KPMG_COLLECTION_AREAS),
    }


def make_insight(payload, live_root=None, live_lock=None):
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object.")
    personas = app.selectable_personas()
    persona_key = payload.get("persona", "allison")
    if not isinstance(persona_key, str) or persona_key not in personas:
        raise ValueError("Choose an available review perspective.")
    persona = personas[persona_key]
    mode = payload.get("mode", "saved")
    if mode == "saved":
        runs = app.available_evaluation_runs()
        run = payload.get("run", runs[0] if runs else None)
        if not isinstance(run, str) or run not in runs:
            raise ValueError("Choose an available saved run.")
        papers, records = app.load_demo_data(answers_name=run)
        record = next((r for r in records if r["id"] == payload.get("id")), None)
        if not record or not record["saved_answer_available"]:
            raise ValueError("No saved answer is available for this question.")
        question, answer = record["query"], record["answer"]
        chunks = app.demo_chunks(record, papers)
    elif mode == "live":
        if live_root is None:
            raise ConnectionError("Live research is not connected in this preview. You can continue browsing the saved research collection.")
        question = payload.get("question")
        if not isinstance(question, str) or not 1 <= len(question.strip()) <= 2000:
            raise ValueError("Enter a research question of 1–2,000 characters.")
        model = payload.get("model", app.MODEL)
        if model not in [m for m in app.MODELS if not m.startswith("gemini-")]:
            raise ValueError("Choose a supported local model.")
        # Serialize model access; a preview must not flood a shared local service.
        if live_lock is None or not live_lock.acquire(blocking=False):
            raise ConnectionError("Another research request is running. Try again when it finishes.")
        try:
            retriever = app.load_live_retriever(live_root)
            result, error = app.try_live_answer(retriever, question.strip(), persona.context, model=model)
            if error:
                raise ConnectionError("The local model is unavailable. Saved research remains available.")
            answer, chunks = result
        finally:
            live_lock.release()
        run = None
    else:
        raise ValueError("Choose saved or live research.")
    insight = app.format_structured_business_insight(question, answer, chunks, persona.context)
    sources = []
    for chunk in chunks:
        source = asdict(chunk)
        source["score"] = chunk.score if math.isfinite(chunk.score) else None
        source["source_url"] = app.safe_arxiv_url(chunk.source_url)
        sources.append(source)
    return {"id": payload.get("id") if mode == "saved" else None,
            "mode": mode, "run": run, "persona": persona_key, "persona_name": persona.name,
            "question": question, "answer": answer, "insight": asdict(insight), "sources": sources,
            "checks": app.answer_issues(answer, chunks),
            "markdown": app.export_executive_brief_markdown(insight, persona.name)}


class FrontendServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, live_root=None):
        super().__init__(address, Handler)
        self.live_root = live_root
        self.live_lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # Questions and research content do not belong in access logs.

    def respond(self, status, content, content_type="application/json; charset=utf-8"):
        data = json.dumps(content, allow_nan=False).encode() if content_type.startswith("application/json") else content
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(data)

    def valid_host(self):
        return self.headers.get("Host") in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

    def do_GET(self):
        if not self.valid_host():
            return self.respond(403, {"error": "Local access only."})
        path = urlsplit(self.path).path
        try:
            if path == "/api/bootstrap":
                return self.respond(200, {**bootstrap(), "live_configured": self.server.live_root is not None})
            static = {
                "/": (WEB / "index.html", "text/html; charset=utf-8"),
                "/app.js": (WEB / "app.js", "text/javascript; charset=utf-8"),
                "/styles.css": (WEB / "styles.css", "text/css; charset=utf-8"),
                "/kpmg-logo.png": (ROOT / "assets/kpmg-logo.png", "image/png"),
                "/favicon.svg": (WEB / "favicon.svg", "image/svg+xml"),
            }
            if path not in static:
                return self.respond(404, {"error": "Not found."})
            file, mime = static[path]
            return self.respond(200, file.read_bytes(), mime)
        except (OSError, ValueError, KeyError, TypeError):
            return self.respond(503, {"error": "Research files are missing or malformed. Restore the committed evaluation files and try again."})

    def do_POST(self):
        origin = self.headers.get("Origin")
        if not self.valid_host() or (origin and origin != f"http://{self.headers.get('Host')}"):
            return self.respond(403, {"error": "Same-origin local access only."})
        if urlsplit(self.path).path != "/api/insight":
            return self.respond(404, {"error": "Not found."})
        if self.headers.get_content_type() != "application/json":
            return self.respond(415, {"error": "Send application/json."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16000:
                return self.respond(413, {"error": "Request must be between 1 and 16,000 bytes."})
            self.connection.settimeout(10)
            payload = json.loads(self.rfile.read(length))
            result = make_insight(payload, self.server.live_root, self.server.live_lock)
            return self.respond(200, result)
        except (ValueError, TypeError, UnicodeError):
            return self.respond(400, {"error": "Invalid request. Choose an available question, run and perspective."})
        except ConnectionError as error:
            return self.respond(503, {"error": str(error)})
        except Exception:
            return self.respond(503, {"error": "Research is temporarily unavailable. Check the index and local model; saved research remains available."})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--live-root", type=Path)
    args = parser.parse_args()
    server = FrontendServer(("127.0.0.1", args.port), args.live_root)
    print(f"Research Intelligence: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
