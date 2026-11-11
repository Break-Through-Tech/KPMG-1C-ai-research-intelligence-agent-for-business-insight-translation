# Evaluation on the committed research papers

`benchmark.json` contains 25 manually labeled questions about the five PDFs in
`data/`: 20 single-paper questions, three cross-paper questions, and two
questions the papers cannot answer. The fact snippets in the labels were
checked against the source PDFs. This is a small project-specific diagnostic
set, not a population-level estimate of RAG quality or a BEIR benchmark.

## Latest experiments: prompt, tables and selective rewriting

See [`prompt_tables_rewrite_assessment.md`](results/prompt_tables_rewrite_assessment.md)
for the completed comparisons: current Qwen/hybrid 20 complete answers, focused
prompt 19, table-aware retrieval 18, selective rewriting 21 (25 questions each,
including two correct abstentions). The focused policy removes a major factual
error but sacrifices completeness; rewriting's +1 is below the +2 adoption
threshold. The live default remains unchanged. The source-backed reviews and
raw answers are displayed first in `notebooks/answer_review.ipynb`.

Experimental implementations:

- `notebooks/structured_answers.py`: opt-in `focused` and `focused_v2` policies;
  neither is the live default. The second variant was stopped after four cases.
- `notebooks/table_documents.py`: conservative numeric-table extraction with
  repeated captions, headers, row labels and group labels. Install optional
  dependencies with `python -m pip install -r evaluation/requirements-tables.txt`.
- `evaluation/rewrite_queries.py` and `experimental_retrieval.py`: query-only
  selective rewriting, original-plus-rewritten hybrid candidate fusion, and
  reranking against the original question. This experiment is distinct from
  the notebook's older optional rewrite flag, which remains off by default.
- `evaluation/assemble_paired_run.py`: verified reuse for identical inputs,
  recording source hashes per answer. See the experiment protocol below for
  exact commands and known limitations.

## Current default: Qwen + hybrid retrieval

The notebook now uses **Qwen 3.5 9B**, BM25 + dense reciprocal-rank fusion,
the existing cross-encoder reranker, and paper-grouped context. Local answers
use `notebooks/structured_answers.py`: coverage policy, citation-only schema,
no repair, thinking disabled, temperature 0, seed 42, context 12,288 and output
limit 1,800. These are the settings tested in the full hybrid comparison.
The optional Gemini path retains its separate concise plain-text prompt.

After pulling `qwen3.5:9b`, rerun the notebook's retriever setup cell and answer
definition cell before asking questions. Recreate the retriever after rebuilding
the corpus so its cached lexical documents are refreshed.

To generate fresh evaluation artifacts with the selected configuration:

```bash
ollama pull qwen3.5:9b
# Start ollama serve separately if the local server is not already running.
python evaluation/retrieval_sweep.py --variants hybrid --output-dir evaluation/results/current_hybrid_retrieval
python evaluation/optimize_answers.py --model qwen3.5:9b --policy coverage --evidence-mode citation --retrieval evaluation/results/current_hybrid_retrieval/hybrid.json --output evaluation/results/current_qwen_hybrid_answers.json
```

The structured runner, rather than the older `run_answers.py`, reproduces the
current notebook's local generation path. Evaluation artifacts store the raw
answer; the notebook additionally attaches source excerpts and references.
Use new output paths when changing configurations. Reports are in
[`qwen_hybrid_assessment.md`](results/qwen_hybrid_assessment.md), and the review
notebook displays them first. User-selected adoption does not change those
historical scores: 20 Complete, 2 Partial, 1 Major issue, 2 Correct abstentions.
Citation placement and numerical attribution still require review. No LLM judge
or additional repair call was enabled.

## Use the changes in the team notebook

Open [`notebooks/eda_workbook.ipynb`](../notebooks/eda_workbook.ipynb) and run
its metadata, PDF extraction, parser, and embeddings cells, followed by the
shared-index and research-assistant cells. The notebook now calls
`notebooks/ingest.py`, `notebooks/retrieval.py`, and
`notebooks/answer_validation.py` directly. It builds a resumable Chroma index,
skips reference sections, reranks candidate passages, shows stable chunk IDs
with citations, and checks that any attached quote appears in its cited chunk.
The notebook has its own step-by-step setup note immediately above the answer
cell. Install `evaluation/requirements.txt`; the answer cell uses a local
Ollama server with `qwen3.5:9b` by default. It writes a new
`research_mpnet_cosine_v3_citable` collection so an older index cannot hide
the parser and citation-metadata changes.

## Run the retrieval evaluation

From the repository root:

```bash
python -m pip install -r evaluation/requirements.txt
python evaluation/run_retrieval.py --output evaluation/results/retrieval_frozen.json
python -m pytest -q
```

The script reads the checked-in PDFs, executes the `process_paper` parser from
`notebooks/eda_workbook.ipynb`, calls `notebooks/ingest.py` to build a cosine
Chroma index with the notebook's MPNet model, and calls
`notebooks/retrieval.py`. The index is cached under `.evaluation_cache/` and is
invalidated when a PDF or the parser changes. Results go to
the selected output file (`retrieval.json` is the CLI default). New reports
include the exact selected passage text, metadata, scores, ordering, formatted
context, source list, and benchmark hash. Keep each report as an immutable
snapshot when comparing answer models or prompts.

Paper-level `macro_recall_at_k` averages the fraction of labeled relevant
papers found per answerable question. `mrr_at_k` uses the rank of the first
relevant **paper**. `evidence_coverage` is the share of labeled fact snippets
found literally (ignoring PDF punctuation and whitespace) in the retrieved
chunks. It measures whether the generator received specific evidence, **not**
whether its answer was factual. The two unanswerable questions are counted
separately. `citation_metadata_complete` checks paper IDs and source URLs on
returned chunks; it does not validate generated citations.

To reproduce the earlier vector-only retrieval baseline on the five PDFs:

```bash
python evaluation/run_retrieval.py --output evaluation/results/retrieval_ordered_frozen.json --per-paper 4 --fetch-k 60 --rerank-model cross-encoder/ms-marco-MiniLM-L6-v2 --max-rerank-gap 8 --order-by-vector
```

That vector-only run found all labeled relevant papers and 23/28 labeled snippets
literally in selected chunks. The original baseline found 7/28 snippets. This
strict wording check does not measure answer correctness.

## BEIR SciFact relevance test

```bash
python evaluation/run_beir_scifact.py
```

For the earlier vector-only retrieval settings on the **same** tiny subset:

```bash
python evaluation/run_beir_scifact.py --output evaluation/results/beir_scifact_20q_500d_ordered.json --rerank-model cross-encoder/ms-marco-MiniLM-L6-v2 --max-rerank-gap 8 --order-by-vector
```

This downloads the [official BEIR SciFact dataset](https://github.com/beir-cellar/beir)
and verifies its published MD5 checksum. It samples **20 claims** from the
official 300-query test split (seed 42), includes every judged relevant article
for those claims, and adds fixed random distractors for a **500-article**
corpus. Each article's title and abstract form its indexed text. Duplicate
titles receive an ID suffix in metadata so the repo's title-keyed ingestion
can keep both articles.

The report in `evaluation/results/beir_scifact_20q_500d.json` gives document-level
hit@1/5/10, recall@5/10, MRR@10, and nDCG@10 against BEIR's test qrels.
Results at five papers are obtained from the first five **distinct** article
IDs returned by the retriever. SciFact consists of scientific claims and
article abstracts, with many biomedical topics. This is a small diagnostic
subset; because the search corpus is reduced, its scores are **not comparable
to published full-corpus BEIR scores**. It tests retrieval relevance, not
answer accuracy or business usefulness.

## Review generated answers

The following is the legacy plain-text evaluation path. `run_answers.py` uses
the notebook's separate `PROMPT` template, with `llama3.2` as its CLI default;
it does not reproduce the selected structured Qwen path described above.
Start a local Ollama server and pull the model, then run:

```bash
ollama serve  # separate terminal
ollama pull llama3.2
python evaluation/run_answers.py --retrieval evaluation/results/retrieval_ordered_frozen.json --output evaluation/results/answers_ordered_frozen.json
python evaluation/check_answers.py --answers evaluation/results/answers_ordered_frozen.json --output evaluation/results/answer_checks_ordered_frozen.json
```

First create `retrieval_ordered_frozen.json` using the current-settings command
above. The answer runner reads that snapshot directly; it does not open Chroma,
load embeddings, or perform another search. Reuse the same `--retrieval` file
with a new answer `--output` path for each model or prompt comparison.

Completed queries resume only when the stored run fingerprint matches the model
name and Ollama digest, prompt, generation options, benchmark, full retrieval
snapshot (including corpus fingerprint and retrieval settings), and answer
pipeline code. `--limit` may be increased to finish a pilot. Checkpoints are
replaced atomically after each answer. A mismatch fails before generation and
leaves the previous answers intact; choose a new output file for the changed run.
The answer file also stores its benchmark and the exact passages used.

**Historical files:** checked-in retrieval reports without `snapshot_version`
do not contain full passages and must be regenerated to a new file. Answer files
without `run_config` cannot be safely resumed; preserve them and use a new output
path. Historical answers remain readable by `check_answers.py`.

The full
25-answer result in `results/answers_grounded.json` used an earlier passage
order; the final ordering has a full retrieval test and a one-answer pilot,
not a full answer-quality run.
`check_answers.py` verifies citation numbers, quotes against the retrieved
passages (allowing whitespace differences), numeric tokens, and the notebook
prompt's abstention phrase. Numeric matching preserves decimals, signs and
percentage units while accepting equivalent formats such as `1,000` / `1000`
and `30.0%` / `30%`. Evidence-only citations cannot supply missing numbers for
the answer body. Numeric checks remain review signals: calculations and other
unit conversions are not inferred.

These checks cannot verify claim support or method/metric associations. Each
result explicitly records `claim_support_status: "not_evaluated"`, independently
of quote verification. For each answer, inspect the source passages and record:

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
quote by itself as proof of accuracy. The retrieval report does not supply
these answer metrics. The first completed [manual review](results/answer_review.md)
uses a full/partial/fail rubric for each answer and records the observed
generation failures. `notebooks/evaluation.ipynb` provides a notebook view of
both runs and the source passages.

## Automatic checks and manual answer review

Open [`notebooks/answer_review.ipynb`](../notebooks/answer_review.ipynb). It displays
answers, required checklist points, short source excerpts, and expandable full
passages. It runs citation, number, length, and paper-level retrieval checks
without Ollama, model downloads, or LLM reviewer calls. Content remains explicitly
marked as awaiting manual review.

```bash
.venv/bin/python evaluation/manual_review.py \
  --answers evaluation/results/answers_ai_three.json \
  --output evaluation/results/manual_review_ai_three.json
```

The default notebook uses q08 (AI4AI-Bench), q09 (Task Model Induction), and q18
(G-CARL). Change its answers path to review another saved run. The checklists in
`answer_checklists.json` cover all 25 benchmark questions and are assistant-prepared,
pending human approval. Source previews use word overlap and are navigation aids;
inspect the full passages to establish support. Numerical warnings can include
section references or PDF extraction artifacts and require interpretation.

The [LLM-judge experiment is archived](archive/llm_judge/README.md), including its
code, executed notebook, reports, and tests. Its ratings are not part of the
active workflow. Answer generation and retrieval remain available independently.

### Passage presentation experiment

`ResearchRetriever.format_context(..., group_by_paper=True)` groups passages
under paper titles without changing their citation IDs. The notebook enables
this in `ask_llm`; restart its kernel after editing `retrieval.py` and rerun setup.
The adopted grouping-only setup uses `order_by_vector=True` in cell 77 and
`group_by_paper=True` in `ask_llm`. The notebook generator defaults to
`llama3.1:8b`, matching the evaluated model. Grouping keeps each paper’s passages
adjacent while preserving citation IDs. Pass `--model llama3.1:8b --group-by-paper`
to the benchmark runner; omit `--selection-order` for this setup.

To test presentation on identical saved evidence:

```sh
.venv/bin/python evaluation/run_answers.py \
  --retrieval evaluation/results/retrieval_ordered_frozen.json \
  --model llama3.1:8b --ids q08 q21 q23 \
  --group-by-paper --selection-order \
  --output evaluation/results/answers_context_both_pilot.json
```

Omit either flag to isolate its effect. Use a separate output per variant.
`--selection-order` reconstructs reserved-paper selection order from saved
reranker scores; original citation IDs are preserved for comparison (live
retrieval assigns IDs after ordering). It does not retrieve new passages.
Grouping also makes same-paper passages adjacent, so it changes layout and can
change display order. Each answer saves its exact `generation_context`; both
flags are included in the resume fingerprint. Existing frozen snapshots remain
valid, while older answer checkpoints must use a new output after code changes.

### Adopted grouping and concise prompt

The notebook now uses Llama 3.1 8B, vector ordering followed by paper grouping,
and the shorter prompt saved as `results/prompt_grouped_concise.txt`.
The 25-question comparison is in `results/grouped_concise_assessment.md` and
at the top of `notebooks/answer_review.ipynb`. Average answer length decreased,
but some required details and claim-level citations remain missing. Citation
presence checks do not establish factual support.

Reproduce this configuration with a new output path:

```sh
.venv/bin/python evaluation/run_answers.py \
  --retrieval evaluation/results/retrieval_ordered_frozen.json \
  --model llama3.1:8b --group-by-paper \
  --output evaluation/results/answers_grouped_concise_repeat.json
```

`answers_grouped_compliance_full.json` records the rejected longer revision;
`answers_grouped_compliance_aborted.json` preserves three completed answers
from the stopped literal-template experiment. Their prompt snapshots are saved
alongside them. The selected full run is `answers_grouped_concise_full.json`.
No LLM judge or automatic repair call is part of the active pipeline.
