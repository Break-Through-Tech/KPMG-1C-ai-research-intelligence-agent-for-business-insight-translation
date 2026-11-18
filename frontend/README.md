# Research Intelligence frontend

This browser UI builds on Raghul's Streamlit persona and insight work and his browser preview. The chat is the main screen. The five-paper benchmark is kept as a separate set of examples and tests.

## Start with saved research

From the repository root, install the Python dependencies and run:

```bash
python -m pip install -r evaluation/requirements.txt
python frontend_server.py --port 8765
```

Open `http://127.0.0.1:8765`. This starts with the 25 recorded example answers and does not need Ollama.

For the GitHub Pages version, build the [static files](../docs/demo/) with `python scripts/build_pages_demo.py` from the repository root. To enable live Ask arXiv on that site, deploy and connect the separate API described in the [hosting guide](../docs/hosting.md).

## Ask arXiv with the local model

Start Ollama in one terminal and make sure the evaluated model is installed:

```bash
ollama pull qwen2.5:7b
ollama serve
```

Start the browser server in another terminal:

```bash
python frontend_server.py --port 8765 --arxiv
```

The chat starts in **Ask arXiv** mode. Each question searches arXiv's catalog, reads up to three top matching PDFs when available, ranks short passages, and asks local Qwen to answer from those passages. PDFs are cached locally. The UI links back to the original paper and shows verbatim excerpts and source checks. The hosted path uses the server-selected Gemini model and a lighter retrieval fallback; its answers need separate evaluation. The five-paper and BEIR numbers do **not** measure either live path's accuracy or recall across arXiv.

To rerun the fixed five-paper evaluation path instead, use `python frontend_server.py --port 8765 --live-root .`. The local server listens only on `127.0.0.1`; it has no account system and is meant for local review, not public hosting. The Gemini option remains in the Streamlit app and notebook, not this browser UI.

## What the evidence signal means

Raghul's evidence breakdown combines retrieval, citation, quote and numeric, and source-diversity indicators. It is a reviewer aid, **not a calibrated probability that the answer is correct**. Missing saved retrieval scores are shown as missing, not invented. A warning can withhold a proposed business action while leaving the technical answer visible for inspection. Human reviewers still need to judge whether each claim follows from its cited passage and whether the proposed application is useful.

## Files and verification

`frontend_server.py` adapts the existing `app.py` helpers to a small same-origin HTTP API. `frontend/` contains plain HTML, CSS, and JavaScript; there is no build step or Node dependency. The server serves an explicit asset list, checks Host and Origin, limits request size, does not log questions, and escapes research text before HTML insertion.

```bash
python -m pytest -q
node --check frontend/app.js
```

The browser UI was checked at desktop size for saved-question navigation, source inspection, and live-answer flow. Evaluation details and limitations are in [`evaluation/results/branch_evaluation.md`](../evaluation/results/branch_evaluation.md).
