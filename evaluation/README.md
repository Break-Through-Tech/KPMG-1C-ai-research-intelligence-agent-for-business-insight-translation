# Evaluation guide

## What the two datasets are

The **five-paper arXiv set** is the five PDFs committed in `data/`. Its 25 questions and relevance labels in [`benchmark.json`](benchmark.json) were drafted by Codex (GPT-6-Sol), then checked against the PDFs during preparation. Twenty questions ask about one paper, three ask across papers, and two have no answer in the papers. There is no documented independent human annotation pass. This set is useful for finding specific failures, not estimating how the assistant will perform on every research topic.

New users can start with the seven-question [sample dataset](../sample_data/README.md), which points to the committed PDFs and gives short manual checks without requiring a full benchmark run.

The **BEIR SciFact subset** comes from the official [BEIR SciFact dataset](https://github.com/beir-cellar/beir). We sample 20 test claims with seed 42, include all 19 distinct relevant articles for them, then add fixed random distractors to make 500 articles. We index each title and abstract. Because the corpus is reduced, these numbers cannot be compared with published full-corpus BEIR scores. SciFact tests retrieval relevance only; it does not test generated answers or business usefulness.

## Current default: Qwen + hybrid retrieval

The notebook uses **Qwen 3.5 9B**, BM25 + dense reciprocal-rank fusion, the
cross-encoder reranker (`k=5`, `fetch_k=60`, at most 4 passages per paper,
rerank gap 8, vector ordering), and paper-grouped context. Local answers use
`notebooks/structured_answers.py`: coverage policy, citation-only schema, no
repair, thinking disabled, temperature 0, seed 42, context 12,288 and output
limit 1,800. The optional Gemini path keeps its separate plain-text prompt.

Two routing rules from the earlier `qwen2.5:7b` pipeline are kept on top:
"Which papers..." questions return labeled paper matches with excerpts and no
model call (q21–q23, q25), and comparison or "how much" questions receive short
focused excerpts (q08, q11, q15).

**Scores and their limits.** The 25-question hybrid assessment
([`qwen_hybrid_assessment.md`](results/qwen_hybrid_assessment.md)) scored
20 Complete, 2 Partial, 1 Major issue, 2 Correct abstentions. That run used the
corpus from **before** the PDF parser fix (fingerprint `ca5f3c8351d1`; the
integrated index is `bda9f4863bbe`) and did **not** include the routing rules
above. Rerun it on the integrated index before quoting it for the current
notebook. Citation placement and numerical attribution still require review.
No LLM judge or additional repair call is enabled.

To generate fresh artifacts with the structured configuration:

```bash
ollama pull qwen3.5:9b
# Start ollama serve separately if the local server is not already running.
python evaluation/retrieval_sweep.py --variants hybrid --output-dir evaluation/results/current_hybrid_retrieval
python evaluation/optimize_answers.py --model qwen3.5:9b --policy coverage --evidence-mode citation --retrieval evaluation/results/current_hybrid_retrieval/hybrid.json --output evaluation/results/current_qwen_hybrid_answers.json
```

`optimize_answers.py`, rather than `run_answers.py`, reproduces the notebook's
structured local generation path. Evaluation artifacts store the raw answer;
the notebook additionally attaches source excerpts and references. Use new
output paths when changing configurations.

## Try the assistant in the notebook

Install `evaluation/requirements.txt` and JupyterLab. Start [Ollama](https://ollama.com/) in a separate terminal and pull `qwen3.5:9b`. Open [`notebooks/eda_workbook.ipynb`](../notebooks/eda_workbook.ipynb) from `notebooks/`, then scroll to **“Run the research assistant on the five committed papers.”** Run the next two setup cells and edit the example question. The first setup cell opens the cached five-paper index (building it if missing) and enables hybrid retrieval. The earlier EDA cells are separate and are not needed for this demo. After editing the notebook or rebuilding the index, rerun both setup cells; the retriever caches its keyword corpus.

The notebook checks citation IDs and requires a literal quote from every cited passage. If a generated answer fails those checks, it shows source matches for review instead of presenting the unchecked draft. These mechanical checks do **not** prove that the cited passage supports every claim, and the paper-match keyword gate can miss relevant papers with different wording.

## Latest experiments: prompt, tables and selective rewriting

See [`prompt_tables_rewrite_assessment.md`](results/prompt_tables_rewrite_assessment.md)
for the completed comparisons: Qwen/hybrid 20 complete answers, focused prompt
19, table-aware retrieval 18, selective rewriting 21 (25 questions each,
including two correct abstentions). The focused policy removes a major factual
error but sacrifices completeness; rewriting's +1 is below the +2 adoption
threshold, so the default is unchanged. Reviews and raw answers are displayed
first in `notebooks/answer_review.ipynb`.

Experimental implementations:

- `notebooks/structured_answers.py`: opt-in `focused` and `focused_v2` policies;
  neither is the default. The second variant was stopped after four cases.
- `notebooks/table_documents.py`: conservative numeric-table extraction with
  repeated captions, headers, row labels and group labels. Install optional
  dependencies with `python -m pip install -r evaluation/requirements-tables.txt`.
- `evaluation/rewrite_queries.py` and `experimental_retrieval.py`: query-only
  selective rewriting, original-plus-rewritten hybrid candidate fusion, and
  reranking against the original question. This is distinct from the notebook's
  optional `rewrite_query` flag, which remains off by default.
- `evaluation/assemble_paired_run.py`: verified reuse for identical inputs,
  recording source hashes per answer.

## Reproduce retrieval checks

From the repository root:

```bash
python -m pip install -r evaluation/requirements.txt
python evaluation/run_retrieval.py --output evaluation/results/retrieval_integrated_frozen.json --per-paper 4 --fetch-k 60 --rerank-model cross-encoder/ms-marco-MiniLM-L6-v2 --max-rerank-gap 8 --order-by-vector
python evaluation/run_beir_scifact.py --output evaluation/results/beir_scifact_after_integration.json --rerank-model cross-encoder/ms-marco-MiniLM-L6-v2 --max-rerank-gap 8 --order-by-vector
python -m pytest -q
```

The arXiv script parses the five PDFs with the notebook's `process_paper` function, uses `notebooks/ingest.py` to make MPNet embeddings in cosine Chroma, and runs `notebooks/retrieval.py` (vector + reranker; the hybrid variant is produced by `retrieval_sweep.py`). The cached index lives under `.evaluation_cache/`; its fingerprint changes when the parser, ingestion code, or PDFs change. New reports are **frozen snapshots**: they include the exact selected passage text, metadata, scores, ordering, formatted context, source list, and benchmark hash. Keep each report unchanged when comparing answer models or prompts. The BEIR script verifies the downloaded archive's published MD5 checksum and uses the same ingestion and retrieval code on the sampled titles and abstracts.

On the five PDFs, the vector + reranker retriever finds all labeled relevant papers for **23/23 answerable questions**, and **23/28** labeled fact snippets appear literally in selected chunks (the original baseline found 7/28). `evidence_coverage` is an exact wording check, not answer accuracy. The PDF parser fix removed repeated page headers and false table-caption headings; the integrated index has 288 chunks, one fewer than before. On the tiny SciFact subset, the relevant article ranks first for **18/20** claims and appears in the first five for **20/20**; MRR@10 is **0.950** and nDCG@10 is **0.963**. SciFact does not use the PDF parser, so the parser fix did not change its results.

## Reproduce plain-text answer checks

`run_answers.py` is the plain-text runner. It uses the notebook's `PROMPT`
(the Gemini-path prompt), the same paper-search and focused-context routing as
the notebook, and the fallback to source review when checks fail. It **replays a
frozen retrieval snapshot**: it does not open Chroma, load embeddings, or search
again. First create a snapshot with the `run_retrieval.py` command above, then:

```bash
python evaluation/run_answers.py --model qwen2.5:7b --retrieval evaluation/results/retrieval_integrated_frozen.json --output evaluation/results/answers_integrated_frozen.json
python evaluation/check_answers.py --answers evaluation/results/answers_integrated_frozen.json --output evaluation/results/answer_checks_integrated_frozen.json
```

Reuse the same `--retrieval` file with a new `--output` for each model or prompt
comparison. `--ids`, `--group-by-paper` and `--selection-order` change which
questions run and how passages are presented, never the passages themselves.

Each answer records the raw model draft, its issues, the final response, the
exact generation context, the passages used, generation time, and whether it is
a direct answer, source-only paper list, source review, or abstention.

**Resuming.** Completed questions resume only when the stored run fingerprint
matches the model name and Ollama digest, prompt, generation options, benchmark,
full retrieval snapshot, presentation flags, and answer pipeline code.
Checkpoints are replaced atomically after each answer. A mismatch fails before
generation and leaves the previous answers intact; choose a new output file.

**Historical files.** Retrieval reports without `snapshot_version` (including
`retrieval_after_parser_integrated.json`) do not store formatted context and
must be regenerated to a new file before `run_answers.py` can use them. Answer
files without `run_config` cannot be resumed; preserve them and use a new
output path. `check_answers.py` still reads historical answer files, falling
back to `benchmark.json` when a file does not embed its benchmark.

**What `check_answers.py` checks.** Citation numbers, verbatim quotes in their
cited passages (allowing PDF whitespace differences), numbers absent from cited
passages, and the fixed abstention phrase. Numeric matching compares whole
values: it preserves decimals, signs and percentage units (92 ≠ 192, 30 ≠ 30%)
while accepting equivalent formats such as `1,000` / `1000`, `30.0%` / `30%`,
and PDF spacing like `0 .126`. Evidence quotes cannot supply missing numbers for
the answer body. These are review signals: calculations and unit conversions are
not inferred, and the checks cannot verify semantic support, factual accuracy,
or completeness. Each result records `claim_support_status: "not_evaluated"`.

## Manual answer review

For a content review, compare every material claim with its cited passage and check all parts of the question:

| Dimension | Pass condition |
| --- | --- |
| Citation validity | Every cited number maps to a supplied paper and the cited passage supports the claim. |
| Factual accuracy | Every material claim is supported by its cited passage; numbers, direction, and caveats are correct. |
| Completeness | All fact snippets required by the benchmark question are answered, or missing evidence is stated explicitly. |
| Direct quote | A verbatim quote from the cited paper is present when required by issue #5. |
| Abstention | Questions 24–25 are declined without invented KPMG or market facts. |

Report claim accuracy as `supported material claims / all material claims`,
completeness as `answered required facts / all required facts`, and the number
of answers with a valid citation and direct quote. Do not treat a citation or
quote by itself as proof of accuracy.

Open [`notebooks/answer_review.ipynb`](../notebooks/answer_review.ipynb) to see
answers, required checklist points, short source excerpts, and expandable full
passages. It runs citation, number, length, and paper-level retrieval checks
without Ollama, model downloads, or LLM reviewer calls:

```bash
.venv/bin/python evaluation/manual_review.py \
  --answers evaluation/results/answers_ai_three.json \
  --output evaluation/results/manual_review_ai_three.json
```

The checklists in `answer_checklists.json` cover all 25 benchmark questions and
are assistant-prepared, pending human approval. Source previews use word overlap
and are navigation aids; inspect the full passages to establish support.

The [original manual review](results/answer_review.md) records early failures.
The [branch evaluation](results/branch_evaluation.md) compares the fresh
`qwen2.5:7b` baseline, the updated notebook, and the parser follow-up: in the
post-parser run, all 20 direct answers passed the mechanical source checks, but
q01 omitted the Router's explicit stopping rule.
[`notebooks/evaluation.ipynb`](../notebooks/evaluation.ipynb) displays the earlier
runs and source passages. The [LLM-judge experiment is archived](archive/llm_judge/README.md);
its ratings are not part of the active workflow.

## Earlier configurations (history)

These were the notebook default at the time and are kept for traceability.

- **`qwen2.5:7b`, vector + reranker, plain-text prompt** (before this merge):
  results in `answers_after_parser_integrated.json`,
  `answer_checks_after_parser_integrated.json`, and
  [`branch_evaluation.md`](results/branch_evaluation.md).
- **Llama 3.1 8B, vector ordering + paper grouping, concise prompt**:
  `results/prompt_grouped_concise.txt`, `results/grouped_concise_assessment.md`,
  `answers_grouped_concise_full.json` (selected), `answers_grouped_compliance_full.json`
  (rejected longer revision), and `answers_grouped_compliance_aborted.json`.
  Average answer length decreased, but some required details and claim-level
  citations were missing.
- **Passage presentation pilot**: `run_answers.py --group-by-paper --selection-order`
  on `retrieval_ordered_frozen.json` (q08, q21, q23); its output was not committed.
- The full 25-answer `results/answers_grounded.json` used an earlier passage order.
