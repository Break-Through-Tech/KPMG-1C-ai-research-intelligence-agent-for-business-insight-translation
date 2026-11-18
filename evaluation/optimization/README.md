# Optimization control loop

Priority: complete, source-supported answers; avoid wrong group/metric attribution,
false causal/significance claims, and unsupported answers. Brevity/latency are
secondary. Schema validity is not factual correctness.

1. Implement structured claim/citation generation and local validity checks.
2. Screen policies on q01/q02/q08/q18 plus citation, cross-paper and abstention
   regressions; assess against the existing source-backed checklist, then run
   the strongest policy on all 25 development questions.
3. Compare retrieval/ranking configurations, screen by evidence coverage and
   inspect actual generated answers. Retain the same generator/policy for a
   controlled retrieval comparison.
4. Evaluate the selected configuration and baseline on 15 additional questions
   labeled from the local PDFs before inspecting generated answers. These are
   same-corpus held-out questions, not an external independent test.

Acceptance threshold chosen before experiments: at least two net additional
complete answers out of 25 development questions, without a new major factual
error or incorrect unsupported answer. Smaller gains may break a tie only if
supported by held-out performance and fewer errors. Retrieval changes require
at least two net additional complete answers (or removal of two material errors)
without losing unsupported-query behavior; retrieval scores alone do not qualify.
An unchanged or worse result is recorded and rejected, not hidden.

Assistant source reviews are the primary quality assessment. Mechanical checks
only flag invalid IDs, mismatched literal quotes and potential unsupported
numbers; they are not an LLM judge. Preserve every candidate output and its
configuration. Failed structured output is a generation failure, not evidence
that the source cannot answer the question.

## Time-limited checkpoint

The user requested wrapping up before full validation. See
`../results/optimization_loop_summary.md` for completed pilots and the strongest
observed Qwen generator examples. No candidate met the full-benchmark adoption
threshold because no new full run completed. The active notebook remains on
Llama 3.1 8B with grouping alone and the earlier short prompt.

Structured experiments: `../optimize_answers.py`; implementation:
`../../notebooks/structured_answers.py`. These are experimental and are not wired
into `ask_llm`. The optional hybrid retriever remains disabled. The prepared
`../retrieval_sweep.py` has not been run; no retrieval improvement is claimed.

Fifteen new questions and source-backed criteria are in `benchmark_holdout.json`
and `answer_checklists_expanded.json` in the parent directory. Only baseline
retrieval has run for these questions; generated answers have not been assessed.

## Completed 25-question and hybrid comparison (2026-11-04)

The historical checkpoint above is superseded by
[`qwen_hybrid_assessment.md`](../results/qwen_hybrid_assessment.md), displayed first
in `notebooks/answer_review.ipynb`. Qwen/vector: 18 Complete, 3 Partial, 2 Major
issue, 2 Correct abstention. Qwen/hybrid: 20 Complete, 2 Partial, 1 Major issue,
2 Correct abstention. Citation defects are recorded separately. q21 is Partial
under the existing paper-name criterion; accepting correct paper IDs increases
both complete counts by one, leaving the paired gain unchanged.

Hybrid meets the +2 threshold against Qwen/vector, but the configuration does
not qualify to replace the existing Llama default: versus that baseline it adds
only one complete answer and introduces a major numerical-attribution error.
The default notebook is unchanged. Holdout answer generation remains pending.

Reproduce from the repository root (local Ollama must be running):

```sh
.venv/bin/python evaluation/optimize_answers.py --model qwen3.5:9b --policy coverage --evidence-mode citation --output evaluation/results/opt_qwen_coverage_full.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=2 .venv/bin/python evaluation/retrieval_sweep.py --variants baseline hybrid
.venv/bin/python evaluation/optimize_answers.py --model qwen3.5:9b --policy coverage --evidence-mode citation --retrieval evaluation/results/opt_retrieval_sweep/hybrid.json --output evaluation/results/opt_qwen_hybrid_changed.json --ids q03 q05 q07 q09 q11 q12 q13 q14 q15 q18 q19 q21 q22 q23 q24 q25
.venv/bin/python evaluation/optimization/assemble_hybrid_run.py
```

The runner resumes matching existing files; use new output paths for a fresh
repeat and preserve historical outputs. Nine hybrid inputs are exactly identical
to vector inputs; assembly verifies question, grouped context, source list,
evidence text/metadata, and model/policy/settings before reusing their answers.
The combined file records per-answer provenance. No prompt or generator change
was made between the paired runs. Hybrid also changes final presentation order
from dense rank to fused rank; it is a complete hybrid-configuration comparison.
All 140 repository tests passed.

## Adopted notebook default

Following the user's explicit selection, the live notebook now uses Qwen 3.5 9B
with hybrid retrieval and the exact tested coverage/citation-only generation
policy. The assessment's recommendation and old default statements are
historical; benchmark results have not been revised. No tighter policy has
been silently substituted. Rerun the retriever setup and answer-definition
cells to update an existing kernel. The Google path remains separate.

## Prompt, tables and rewriting experiments (completed)

Results: [`prompt_tables_rewrite_assessment.md`](../results/prompt_tables_rewrite_assessment.md).
No new candidate met the +2-complete-answer or two-major-errors-removed threshold.
Qwen + hybrid + coverage remains the live configuration. Selective rewriting
adds one complete answer and is retained as experimental. The 15-question
holdout remains pending.

The focused policy full run used the baseline hybrid snapshot. The second
policy, focused_v2, was stopped after q01/q08/q20/q21 because q20 introduced an
attribution error. Its checkpoint is `opt_focused_v2_pilot_stopped.json`; it is
not a 25-question result. The first two table snapshots are extraction-debug
artifacts; only **v3** is used in answer-quality conclusions.

Reproduce into **new output paths** to preserve snapshots (local Ollama required):

```sh
python -m pip install -r evaluation/requirements-tables.txt
python evaluation/optimize_answers.py --model qwen3.5:9b --policy focused --evidence-mode citation --retrieval evaluation/results/opt_retrieval_sweep/hybrid.json --output /tmp/focused_answers.json
python evaluation/experimental_retrieval.py --mode tables --output /tmp/tables_retrieval.json
python evaluation/optimize_answers.py --model qwen3.5:9b --policy coverage --evidence-mode citation --retrieval /tmp/tables_retrieval.json --output /tmp/table_answers.json
python evaluation/rewrite_queries.py --output /tmp/rewrites.json
python evaluation/experimental_retrieval.py --mode rewrite --rewrites /tmp/rewrites.json --output /tmp/rewrite_retrieval.json
python evaluation/optimize_answers.py --model qwen3.5:9b --policy coverage --evidence-mode citation --retrieval /tmp/rewrite_retrieval.json --output /tmp/rewrite_answers.json
```

These commands regenerate all answers. The completed comparison saved compute
by generating only eight changed table contexts and four changed rewrite
contexts. The other 17/21 answers are verified exact-input reuses. A fresh
control retrieval run reproduced all original hybrid contexts exactly.
`assemble_paired_run.py` also proves that the coverage engine matches the
original fingerprint after removing only the two added, unused policy
assignments; it does not broadly ignore code mismatches.

Table extraction is deliberately limited to confident ruled numeric tables
and does not solve chart/figure interpretation, scanned tables, or every
complex multi-row header. Eight tables produced 21 chunks. Two pages were
rendered and visually checked; tests assert specific row/column and judge-group
associations. New chunks can alter lexical corpus statistics and ordering even
when no table is ultimately selected. The experiment clones the baseline
collection into a separate cache and does not modify the production index.

The rewrite selector uses broad-question phrasing only, never expected answers
or benchmark IDs. All eight generated rewrites are saved along with their
prompt, model digest and timing. No generated answer text is used as evidence.

150 tests passed. The code and trial artifacts are retained; none of these
three techniques is silently enabled in the live assistant.
