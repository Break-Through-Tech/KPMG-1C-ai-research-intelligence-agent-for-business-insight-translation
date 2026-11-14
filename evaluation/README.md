# Evaluation guide

## What the two datasets are

The **five-paper arXiv set** is the five PDFs committed in `data/`. Its 25 questions and relevance labels in [`benchmark.json`](benchmark.json) were drafted by Codex (GPT-6-Sol), then checked against the PDFs during preparation. Twenty questions ask about one paper, three ask across papers, and two have no answer in the papers. There is no documented independent human annotation pass. This set is useful for finding specific failures, not estimating how the assistant will perform on every research topic.

New users can start with the seven-question [sample dataset](../sample_data/README.md), which points to the committed PDFs and gives short manual checks without requiring a full benchmark run.

The **BEIR SciFact subset** comes from the official [BEIR SciFact dataset](https://github.com/beir-cellar/beir). We sample 20 test claims with seed 42, include all 19 distinct relevant articles for them, then add fixed random distractors to make 500 articles. We index each title and abstract. Because the corpus is reduced, these numbers cannot be compared with published full-corpus BEIR scores. SciFact tests retrieval relevance only; it does not test generated answers or business usefulness.

## Try the assistant in the notebook

Install `evaluation/requirements.txt` and JupyterLab. Start [Ollama](https://ollama.com/) in a separate terminal and pull `qwen2.5:7b`. Open [`notebooks/eda_workbook.ipynb`](../notebooks/eda_workbook.ipynb) from `notebooks/`, then scroll to **“Run the research assistant on the five committed papers.”** Run the next two setup cells and edit the example question. The first setup cell builds the five-paper index if it is missing. The earlier EDA cells are separate and are not needed for this demo.

The notebook checks citation IDs and requires a literal quote from every cited passage. If a generated answer fails those checks, it shows source matches for review instead of presenting the unchecked draft. “Which papers” questions return labeled search matches with excerpts. These mechanical checks do **not** prove that the cited passage supports every claim, and the paper-match keyword gate can miss relevant papers with different wording.

## Reproduce retrieval checks

From the repository root:

```bash
python -m pip install -r evaluation/requirements.txt
python evaluation/run_retrieval.py --output evaluation/results/retrieval_after_parser_integrated.json --per-paper 4 --fetch-k 60 --rerank-model cross-encoder/ms-marco-MiniLM-L6-v2 --max-rerank-gap 8 --order-by-vector
python evaluation/run_beir_scifact.py --output evaluation/results/beir_scifact_after_integration.json --rerank-model cross-encoder/ms-marco-MiniLM-L6-v2 --max-rerank-gap 8 --order-by-vector
python -m pytest -q
```

The arXiv script parses the five PDFs with the notebook's `process_paper` function, uses `notebooks/ingest.py` to make MPNet embeddings in cosine Chroma, and runs `notebooks/retrieval.py`. The cached index lives under `.evaluation_cache/`; its fingerprint changes when the parser, ingestion code, or PDFs change. The BEIR script verifies the downloaded archive's published MD5 checksum and uses the same ingestion and retrieval code on the sampled titles and abstracts.

On the five PDFs, the current retriever finds all labeled relevant papers for **23/23 answerable questions**, and **23/28** labeled fact snippets appear literally in selected chunks. `evidence_coverage` is an exact wording check, not answer accuracy. The teammate's PDF parser fix removed repeated page headers and false table-caption headings; the integrated index has 288 chunks, one fewer than before. On the tiny SciFact subset, the relevant article ranks first for **18/20** claims and appears in the first five for **20/20**; MRR@10 is **0.950** and nDCG@10 is **0.963**. SciFact does not use the PDF parser, so the parser fix did not change its results.

## Reproduce answer checks

With Ollama running and `qwen2.5:7b` installed:

```bash
python evaluation/run_answers.py --retrieval evaluation/results/retrieval_after_parser_integrated.json --output evaluation/results/answers_after_parser_integrated.json
python evaluation/check_answers.py --answers evaluation/results/answers_after_parser_integrated.json --output evaluation/results/answer_checks_after_parser_integrated.json
```

`run_answers.py` resumes finished questions in its output file. The output records the raw model draft, final response, retrieved passages, generation time, and whether the response is a direct answer, source-only paper list, source review, or abstention. `check_answers.py` checks citation numbers, verbatim quotes in their cited passages, numbers absent from cited passages, and the fixed abstention phrase. It counts direct answers separately from source-only results. It cannot verify semantic support, factual accuracy, or completeness by itself.

For a content review, compare every material claim with its cited passage and check all parts of the question. The [original manual review](results/answer_review.md) records early failures. The [branch evaluation](results/branch_evaluation.md) compares the fresh baseline, the updated notebook, and the parser follow-up. In the post-parser run, all 20 direct answers passed the mechanical source checks, but q01 omitted the Router's explicit stopping rule. [`notebooks/evaluation.ipynb`](../notebooks/evaluation.ipynb) displays the earlier runs and source passages.
