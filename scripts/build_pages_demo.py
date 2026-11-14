"""Build a static, saved-results version of the browser UI for GitHub Pages.

Run from anywhere with: python scripts/build_pages_demo.py
This only exports committed benchmark answers; it does not call a model.
"""

import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontend_server import bootstrap, make_insight  # noqa: E402


RUN = "answers_after_parser_integrated.json"
SOURCE = ROOT / "frontend"
DEST = ROOT / "docs" / "demo"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def replace_exact(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"Expected exactly one occurrence of {old!r} in frontend/index.html")
    return source.replace(old, new)


def main() -> None:
    data = bootstrap()
    if RUN not in data["runs"]:
        raise ValueError(f"Saved run {RUN} is missing")
    if not all(question["saved_answer_available"] for question in data["questions"]):
        raise ValueError("Every published question must have a saved answer")

    DEST.mkdir(parents=True, exist_ok=True)
    html = (SOURCE / "index.html").read_text(encoding="utf-8")
    for old, new in (
        ('<html lang="en">', '<html lang="en" data-static-demo="true">'),
        ('href="/favicon.svg"', 'href="favicon.svg"'),
        ('href="/styles.css"', 'href="styles.css"'),
        ('src="/app.js"', 'src="app.js"'),
        ('src="/kpmg-logo.png"', 'src="kpmg-logo.png"'),
        ("Local research prototype", "Saved research demo"),
    ):
        html = replace_exact(html, old, new)
    (DEST / "index.html").write_text(html, encoding="utf-8")
    for name in ("app.js", "styles.css", "favicon.svg"):
        shutil.copyfile(SOURCE / name, DEST / name)
    shutil.copyfile(ROOT / "assets" / "kpmg-logo.png", DEST / "kpmg-logo.png")

    data["runs"] = [RUN]
    data["default_run"] = RUN
    data["models"] = []
    data["live_configured"] = False
    write_json(DEST / "data" / "bootstrap.json", data)

    insights = DEST / "data" / "insights"
    if insights.exists():
        shutil.rmtree(insights)
    for persona in data["personas"]:
        for question in data["questions"]:
            result = make_insight(
                {"mode": "saved", "run": RUN, "persona": persona["id"], "id": question["id"]}
            )
            write_json(insights / persona["id"] / f"{question['id']}.json", result)

    (ROOT / "docs" / ".nojekyll").touch()
    (ROOT / "docs" / "index.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta http-equiv="refresh" content="0; url=demo/">'
        '<title>Research Intelligence Demo</title></head><body>'
        '<p><a href="demo/">Open the saved research demo</a></p></body></html>\n',
        encoding="utf-8",
    )
    print(f"Built GitHub Pages demo: {len(data['questions'])} questions × {len(data['personas'])} perspectives")


if __name__ == "__main__":
    main()
