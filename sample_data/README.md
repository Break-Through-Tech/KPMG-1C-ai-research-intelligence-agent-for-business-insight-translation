# Starter dataset for trying the research assistant

This sample comes from the five public arXiv PDFs already committed in [`data/`](../data/), plus seven questions selected from the project's fixed 25-question [`evaluation/benchmark.json`](../evaluation/benchmark.json). It is small enough to inspect by hand and requires no download or account. The questions, relevance labels, and check hints were drafted for this project and checked against the PDFs; they have **not** had an independent human annotation pass.

## Files

| File | What it contains |
| --- | --- |
| [`papers.csv`](papers.csv) | Five paper IDs, titles, paths to the committed PDFs, and arXiv links. The PDFs are the actual documents searched by the RAG system. |
| [`questions.csv`](questions.csv) | Seven starter questions: five direct answers, one two-paper search, and one question that should be declined. |

Both files are UTF-8 CSV and open in a text editor, spreadsheet, or Python's standard `csv` module. `paper_id` and `expected_paper_ids` join the two files. A blank `expected_paper_ids` cell means the question is intentionally outside the corpus; multiple IDs are separated by `|`. `check_hint` is a quick manual check, **not** a verified reference answer or a score.

## Try it

From the repository root, follow the [setup instructions](../README.md#setup-and-use), then run:

```bash
python frontend_server.py --port 8765
```

Open `http://127.0.0.1:8765`, choose **Evidence & evaluation**, and open a question by its ID from `questions.csv`. This uses saved answers and does not need a model. Check the original answer, source passages, and review warnings. The full 25-question benchmark is available in the same view.

To ask one of these questions again with the live local model, start Ollama with `qwen2.5:7b` as described in the root README, then run:

```bash
python frontend_server.py --port 8765 --live-root .
```

Choose **Ask a question**, paste a question from the CSV, and inspect the cited passages. Use a different port if the saved-mode server is still running. The first live question may build the five-paper index, which takes longer. No KPMG or client data is needed.

The sample tests a narrow public research corpus. The source labels help check retrieval and traceability; they do not establish that every generated sentence is accurate, complete, or useful for a business decision. The [evaluation guide](../evaluation/README.md) explains the full benchmark and the separate tiny BEIR SciFact retrieval run.
