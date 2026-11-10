# Research Intelligence frontend

Local frontend preview for the existing Break Through Tech × KPMG research agent.
No build step, Node packages, database migration, or changes to the existing Streamlit app.

From this worktree's root:

```powershell
python frontend_server.py --port 8765
```

Open http://127.0.0.1:8765. The server binds only to loopback and serves an explicit
asset allowlist. It is a local preview server, not an authenticated production server.

## Working features

- Search the committed benchmark questions and filter the five-paper research library.
- Open saved answers with business framing, original technical answers, clickable
  citations, source passages, provenance, confidence breakdowns and validation warnings.
- Choose a stakeholder perspective and inspect either committed answer run.
- Save briefs in the current browser tab's session and export the existing executive
  brief Markdown. Closing the tab clears session storage; export to keep a copy.
- Responsive navigation and layouts, keyboard-accessible tabs and native source dialogs.
- Optional local generation through the existing retrieval and Ollama pipeline.

Saved answers are not regenerated when the perspective changes. The existing formatter
applies the chosen review context without changing the technical answer or passage order.
Research themes come from the existing title-based inference helper and are project
labels, not official KPMG classifications. No synthetic business metrics are displayed.

## Integration boundary

`frontend_server.py` imports the existing `app.py` helpers. It reuses
`load_demo_data`, `demo_chunks`, `selectable_personas`,
`format_structured_business_insight`, `answer_issues`, and
`export_executive_brief_markdown`. The UI sends JSON to `POST /api/insight` and reads
`GET /api/bootstrap`. NaN saved retrieval scores become explicit `null` values.

All research text is escaped before insertion into HTML. Direct arXiv links pass the
existing URL validator. The local adapter checks Host and Origin, limits request size,
does not log prompts, and serves no arbitrary repository files. There is no remote
telemetry, CDN dependency, cloud generation, or new runtime dependency. Prettier was
run as a temporary formatting tool; no Node manifest or dependency tree is added.

To connect a prepared index, explicitly opt in:

```powershell
python frontend_server.py --port 8765 --live-root "C:\path\to\prepared-repository"
```

That directory must contain the existing `arxiv_data/chroma_db` collection and metadata.
The existing Python retrieval dependencies, locally cached embedding/reranker models,
and a supported Ollama model must already be available. The adapter does not create an
index, download models, or start Ollama. Live requests are serialized. Saved research
remains available after a service error. Opening a persistent Chroma client may touch
its database; use a dedicated copy of an index when another teammate/process owns it.

The cloud Gemini path stays in the existing Streamlit app; this frontend deliberately
offers only local generation. Future hosted delivery needs an authenticated application
server, request lifecycle handling, and an agreed shared persistence layer.

## Design reference

The visual system follows [Astryx's design conventions](https://github.com/meta/astryx/wiki/Design-Conventions):
intentional spacing, clear hierarchy, restrained elevation, consistent interaction states,
and accessible controls. It uses plain CSS tokens and the repository's KPMG logo,
with KPMG blue (`#00338d`) and supporting blue (`#005eb8`). Astryx is inspiration;
its React library is not installed into the Python project.

## Verification

```powershell
python -m pytest -q tests/test_frontend_server.py tests/test_business_translator.py tests/test_answer_validation.py tests/test_personas_and_ui_helpers.py -k "not streamlit"
node --check frontend/app.js
```

The adapter tests cover every answer in both saved runs, unchanged evidence and export
content, abstention, input validation, local-only HTTP boundaries, and mocked live success
and failure. Browser QA covers research navigation, search, filters, brief tabs, source
dialogs, session saving, export, live-unavailable handling, and responsive layouts.
Result: 98 tests passed; five Streamlit rendering tests were deselected because
Streamlit is not installed. The downloaded Markdown matched the backend export exactly.
Desktop (1440 px) and mobile (390 px) layouts were inspected, including horizontal
overflow checks, keyboard tab switching, empty search results and error recovery.

## Isolation and repository review — November 10, 2026

Fetched all remote refs with pruning. The original checkout was clean at `cccf3a3` on
`raghul-ui-and-insight-upgrade`, matching its remote. `main` and `origin/main` remained
at `1594fda`; no pull was needed. The new `origin/Baraa-confidence-score` ref also pointed
at `1594fda`. Parser, evaluation and prompt-template branches remain independent.

This work lives on local branch `raghul-frontend-preview-20261110` in the sibling
`kpmg-frontend-preview` worktree. No existing tracked source, notebook, corpus, prompt,
test, CI, requirements or configuration file is modified. The frontend changes are staged locally for review; no merge into main is included.
Only `frontend/`, `frontend_server.py`, and `tests/test_frontend_server.py` are added.

The full retrieval/ingestion suite requires `langchain_chroma`, which is unavailable in
the current Python environment. Live model generation and scientific validity are not
verified by this frontend work. Existing saved-output problems are surfaced rather than
rewritten or hidden.
