# Research Intelligence frontend

This local browser UI builds on Raghul's Streamlit persona and insight work and his browser preview. It keeps the paper library, saved briefs, source dialogs, review perspectives, and evidence breakdowns. The current design uses KPMG's navy header, clear typography, and generous whitespace as a reference, with quieter blue and gray colors.

## Start with saved research

From the repository root, install the Python dependencies and run:

```bash
python -m pip install -r evaluation/requirements.txt
python frontend_server.py --port 8765
```

Open `http://127.0.0.1:8765`. The current complete Qwen evaluation is selected by default. You can browse 25 benchmark questions and five papers, inspect their exact saved answers and passages, switch review perspectives, save briefs for this browser tab, and export a Markdown brief. Saved answers are not regenerated when the perspective changes.

## Ask a new question locally

Start Ollama in one terminal and make sure the evaluated model is installed:

```bash
ollama pull qwen2.5:7b
ollama serve
```

Start the browser server in another terminal:

```bash
python frontend_server.py --port 8765 --live-root .
```

Choose **Ask a question** in the UI. The first live question builds the five-paper Chroma index from the committed PDFs if it is missing; this can take a little while. Later questions reuse the cached index. Live answers use the notebook's Qwen prompt, passage retrieval settings, focused excerpts for numeric or comparison questions, exact passage citations, and verbatim quote checks. If the draft fails a source check, the UI shows inspectable source matches instead of treating it as a verified answer. Business applications stay separate from paper findings.

Live mode searches the five public papers committed under `data/`. It does not access KPMG or client documents. The local server listens only on `127.0.0.1`; it has no account system and is meant for local review, not public hosting. The Gemini option remains in the Streamlit app and notebook, not this browser UI.

## What the evidence signal means

Raghul's evidence breakdown combines retrieval, citation, quote and numeric, and source-diversity indicators. It is a reviewer aid, **not a calibrated probability that the answer is correct**. Missing saved retrieval scores are shown as missing, not invented. A warning can withhold a proposed business action while leaving the technical answer visible for inspection. Human reviewers still need to judge whether each claim follows from its cited passage and whether the proposed application is useful.

## Files and verification

`frontend_server.py` adapts the existing `app.py` helpers to a small same-origin HTTP API. `frontend/` contains plain HTML, CSS, and JavaScript; there is no build step or Node dependency. The server serves an explicit asset list, checks Host and Origin, limits request size, does not log questions, and escapes research text before HTML insertion.

```bash
python -m pytest -q
node --check frontend/app.js
```

The browser UI was checked at desktop size for saved-question navigation, source inspection, and live-answer flow. Evaluation details and limitations are in [`evaluation/results/branch_evaluation.md`](../evaluation/results/branch_evaluation.md).
