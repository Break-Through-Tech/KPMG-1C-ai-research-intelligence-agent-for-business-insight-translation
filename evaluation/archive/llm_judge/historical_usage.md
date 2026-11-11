## Explanatory LLM-as-a-judge review

For an interactive workflow, open
[`notebooks/judge_answers.ipynb`](../notebooks/judge_answers.ipynb). It checks
Ollama, runs the script with live progress, and displays the formatted report
inline. It defaults to all saved answers with repair retries disabled; set
`LIMIT = 1` in its configuration cell for a quicker one-question pilot.

`judge_answers.py` adds an optional model review of the saved answers. It prints
readable per-question assessments and writes a JSON checkpoint plus a Markdown
report. It uses the passages already saved with each answer, without retrieving
again or changing the generated answers. No additional Python packages are needed.

Start Ollama and select an installed judge model with `ollama list`, then run:

```bash
python evaluation/judge_answers.py \
  --answers evaluation/results/answers_ordered_frozen.json \
  --model qwen3.5:9b
```

The default judge is `qwen3.5:9b`; it must already be installed. Use `--model` to
select another installed model. The script does not download models. A different
judge from the answer generator avoids direct self-evaluation, but does not
guarantee reliable judgments. Compare the judge with human reviews before using
its ratings to choose an optimization.

For each question the report explains:

- Whether the retrieved context is sufficient, and why each passage is relevant,
  partly relevant, or irrelevant.
- Answer relevance, faithfulness, completeness, citation support, and whether the
  decision to answer or abstain is appropriate.
- Specific failures, answer excerpts, and supporting passage quotations.
- A suggested concise revision, explicitly marked as not independently verified.
- The separate mechanical citation, quote, and number checks.

The judge returns structured JSON. Its evidence quotes are checked against the
actual passages, and its proposed citation numbers must exist. Invalid output
gets one repair attempt; persistent failures are reported as `JUDGE ERROR`, not
scored as successful reviews. Quote validation does not establish that the
judge's interpretation is correct. The script returns a nonzero exit status for
judge errors; a valid negative judgment (`NEEDS REVIEW`) is a successful evaluation.

By default, outputs are `answers_ordered_frozen_judge.json` and
`answers_ordered_frozen_judge.md` alongside the answers file. Use `--output` with
a new `.json` path to compare another judge or configuration. Compatible runs
resume; changing answers, benchmark, judge weights, options, rubric, or evaluator
code requires a new output file. Failed judge calls are retried on the next run.
Use `--limit 3` for a pilot; omit it to review all answers currently in the file.
`--num-ctx`, `--num-predict`, and `--timeout` control the local model request.

For a quicker single-question check, disable the automatic repair request:

```bash
.venv/bin/python evaluation/judge_answers.py \
  --answers evaluation/results/answers_ordered_frozen.json \
  --model qwen3.5:9b --limit 1 --retries 0 \
  --output evaluation/results/judge_single_attempt.json
```

This saves a second generation when validation fails, at the cost of leaving
that review as `JUDGE ERROR`. It does not speed up the first generation. The CLI
prints each attempt and elapsed generation time. A lower `--num-predict` is only
an output ceiling: it can truncate the JSON rather than produce a shorter valid
review. Use a fresh output path after changing evaluator code or settings.

Content verdicts and citation support remain separate: a factually correct answer
with no citations may receive `full` content but still `NEEDS REVIEW`. A `PASS`
is an automated assessment, not a verified ground-truth label. The benchmark's
fact snippets are treated as reference anchors rather than required exact wording.

### Initial live calibration

The saved [Qwen3.5 pilot](results/answers_ordered_frozen_judge_qwen35.md)
tested the three existing answers. It produced two `JUDGE ERROR` results because
evidence quotations failed literal source matching after a repair attempt. The
third review correctly flagged missing citations while accepting the domain list.
The run took approximately 7.5 minutes locally, including retries.

The rejected raw reviews also rated the first two answers too generously compared
with the [earlier qualitative review](results/answer_review_ordered_frozen.md):
they missed method confusion and an incomplete comparison. Raw attempts are kept
in the JSON checkpoint for diagnosis. This establishes that the script runs, but
does **not** establish that this judge is reliable enough to rank optimizations.
Calibrate alternative judge models against reviewed examples before using their
verdicts as an acceptance gate; exact quote checks alone cannot fix semantic errors.

The readable judge report uses a concise business summary for each answer: what
went well, what needs fixing, and the next step. If a review fails, it explains
the failure in plain language and labels any model impressions as unverified.
Complete raw responses, evidence, and technical errors remain in the JSON checkpoint.

## Checklist-based review (recommended workflow)

Open [`notebooks/judge_answers.ipynb`](../notebooks/judge_answers.ipynb), or run:

```bash
.venv/bin/python evaluation/review_answers.py \
  --answers evaluation/results/answers_ordered_frozen.json \
  --output evaluation/results/checklist_review.json
```

This replaces the notebook's broad, all-in-one judge with three separate layers:

1. **Required answer points:** `answer_checklists.json` covers all 25 benchmark
   questions, including comparisons, numerical results, cross-paper answers, and
   unsupported questions. Each requirement has a stable ID and reference PDF/page.
   The checklists were prepared by the assistant from the local papers and are
   **pending human approval**, not a human-reviewed gold standard. Review these
   requirements before treating them as acceptance criteria.
2. **Automatic checks:** body citations (excluding appended sources/evidence),
   valid citation IDs, numerical values against cited passages, expected figures,
   and a configurable word-count target. These are surface checks, not proof of
   factual accuracy. Numbers spelled as words or calculated from evidence may need
   human interpretation. Existing quote diagnostics remain in JSON; an appended
   quotation is no longer required for a business answer to pass these checks.
   Retrieval is measured independently using recall, reciprocal rank, and binary
   NDCG over deduplicated paper IDs in first-appearance order, compared with the
   benchmark's labeled papers. These are **paper-level**, not passage-level,
   relevance metrics. Unsupported questions have no retrieval score.
3. **Focused content decisions:** the model independently marks each requirement
   yes/no/uncertain, with a short reason and source-location IDs. Requirements for
   one answer are batched in one request. Missing source support requires an
   uncertain assessment (except explicitly unsupported benchmark questions).
   The model does not write source quotes or a replacement answer. This checks
   the listed requirements, not all possible hallucinations.

The short report shows strengths, problems, next steps, and a requirement table.
At most two source excerpts (240 characters each) are copied directly from saved
passages, with whitespace normalized and truncation marked. The model selects
locations; this does not certify their relevance. Full original passages, span
positions, check results, and raw responses remain in the JSON checkpoint. The
answer and automatic-check details are collapsed in the notebook report.

For a fast run with **no model call**, use a separate output file:

```bash
.venv/bin/python evaluation/review_answers.py \
  --answers evaluation/results/answers_ordered_frozen.json \
  --checks-only --output evaluation/results/checklist_automatic.json
```

In the notebook, set `CHECKS_ONLY = True` and change `OUTPUT` accordingly.
Content is explicitly labeled pending in this mode. The default focused review
uses all saved answers, `qwen3.5:9b`, no retries, and a 1,400-token output ceiling.
Use `--limit 1` for a pilot, `--max-words` to change the readability target, and
`--retries 1` for one repair attempt. A smaller output ceiling can truncate JSON.

Compatible runs resume completed answers. Changes to inputs, model weights,
checklists, code, or settings require a new output filename. Existing broad-judge
reports are preserved and are not compatible with this report format. Review
failures stay separate from answer defects; failed model ratings are not accepted.

Before using scores to rank optimizations, compare the focused reviewer with
independent human labels, including wrong-but-plausible answers, missing
comparison points, correct paraphrases, and insufficient evidence. Passing
structural checks or a three-answer pilot does not establish judge reliability.

The [first focused live pilot](results/checklist_review.md) completed three valid
reviews in about 58 seconds of model time. It caught missing comparison points
but still overcredited two requirements. See the
[calibration notes](results/checklist_calibration.md) before interpreting its
ratings. The [automatic-only report](results/checklist_automatic.md) is also
available without running Ollama.

### Three-question AI example in the notebook

The notebook currently selects **q08 (AI4AI-Bench), q09 (Task Model Induction),
and q18 (G-CARL)**. Fresh `llama3.2` answers are saved separately in
`results/answers_ai_three.json`, using the existing frozen retrieval passages.
The checklist report is `results/checklist_ai_three.md`.

To generate a specific subset without changing the benchmark:

```bash
.venv/bin/python evaluation/run_answers.py \
  --retrieval evaluation/results/retrieval_ordered_frozen.json \
  --ids q08 q09 q18 --model llama3.2 \
  --output evaluation/results/answers_ai_three.json
```

`--ids` preserves the supplied order, rejects unknown/duplicate IDs, and cannot
be combined with `--limit`. The selected IDs are recorded in the run configuration.
Earlier answer sets and reports are preserved. The notebook's final cell displays
the saved report without regenerating answers or rerunning the model.
