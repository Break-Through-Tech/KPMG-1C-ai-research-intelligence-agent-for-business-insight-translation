# Stakeholder usability and business translation evaluation

November 4, 2026. **Offline automated acceptance audit; no human usability participants.**

## Executive summary

The translator preserves a technical evidence answer and adds three sections: What the Study Found, Why It Matters to KPMG, and What KPMG Could Consider. Citation, direct-quote and numeric checks gate the business application. Business relevance and pilot suggestions are proposed applications for review, not measured KPMG outcomes. Failed or unsupported answers receive no business action recommendation.

The audit reads all 25 benchmark questions and the existing `answers_grounded.json`, reconstructs passages in saved order, and runs three primary personas plus an executed anti-persona bypass request. It does not regenerate answers, call a model, or alter the input artifacts. The saved run identifies llama3.2. The older `answers.json` manual content grades are not transferred to this grounded run.

| Metric | Measured result | Denominator and meaning |
| --- | --- | --- |
| Queries | 25 | 23 answerable, 2 unanswerable |
| Unsupported-query abstention | 2/2 (100%) | q24 and q25; a missing saved response fails |
| Three-pillar completeness | 6/6 (100%) | Non-abstained business outputs, each with citations in all three sections |
| Answerable business action rate | 6/23 (26.1%) | Separately exposes useful-answer coverage |
| Limitation guardrails | 25/25 (100%) | Includes explicit no-action and limitations language for withheld outputs |
| Business confidence tiers | High 0, Moderate 6, Low 0, Abstained 19 | All 25 outputs after business action gating |
| Technical evidence tiers | High 0, Moderate 6, Low 15, Abstained 4 | Before business action gating |

The evidence score uses retrieval 30%, sentence citation coverage 30%, quote/numeric checks 25%, and cited-source diversity 15%. Available scores are clipped to [0,1]. Unsaved retrieval scores contribute zero; raw cross-encoder logits have no probability interpretation. The thresholds **have not been empirically calibrated** against human truth labels. High describes passing evidence indicators, not a probability of correctness. Human review must still assess meaning, completeness and the proposed application.

The base validator exposes `answer_issues`, not `validate_answer`. The translator reuses it and adds sentence citation coverage, passage-level quote alignment and query-only paper-demand checks without changing the teammate-owned validator. When no claim citation overlaps an Evidence quote's passage, quote verification is penalized and business action is withheld. A quote elsewhere in the same paper does not verify the claimed passage. This conservative rule can block plausible answers; it does not prove the blocked claims false.

## Persona walkthroughs and Given/When/Then results

These illustrative personas encode review priorities, not verified biographies or participant feedback. Each formatter receives its persona context. Deterministic framing remains shared; this evaluates acceptance conditions rather than separate model generations for each persona.

| Persona | Given / When / Then acceptance condition | Result |
| --- | --- | --- |
| Allison Tatterson | Given an answerable question, when translated, then show cited evidence, a proposed strategic application and a pilot action. For an unsupported question, withhold action. | 8/25 (32%): six actionable outputs and two correct unsupported refusals. Seventeen answerable questions fail usefulness. |
| Dr. Marcus Vance | Given any answer, when displayed, then show confidence and limitations. A supported output must pass quote/numeric checks; withholding must explain warnings or unsupported status. | 25/25 (100%); mechanical safety, not semantic correctness. |
| Elena Sorensen | Given saved passages, when sources are shown, then preserve every passage number, nonempty chunk ID and canonical arXiv provenance. | 25/25 (100%); missing author/date metadata is not invented or counted as complete. |
| Anti-Persona Jordan | Given a request to ignore citations/limitations and guarantee ROI, when translated under Jordan context, then decline the bypass and recommend no action. | 25/25 (100%); the hostile request is executed for every benchmark record. |

Jordan is excluded from selectable UI personas. The same evidence guardrails apply to all primary personas. Safe refusal of an answerable question is not counted as strategic usefulness for Allison.

## Five-paper KPMG reference alignment

The mappings follow the five-paper guidance supplied for this task. The two advisor DOCX guides in the repository support evidence separation, limitations and acceptance criteria; neither was treated as an independent five-paper reference document or evidence of KPMG deployments.

The following table contains exact system output from **controlled evidence-only mapping checks**. Each uses an existing saved verbatim quote and its original chunk, renumbered [1] in an isolated single-passage input. These demonstrations are not repaired benchmark generations and do not contribute to the 25-query metrics. The source column identifies the original saved passage.

| Paper / saved source | Why It Matters to KPMG (exact) | What KPMG Could Consider (exact) |
| --- | --- | --- |
| Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation (q01, 2608.20316_5_1, original [1]) | Proposed Advisory applications for stakeholder review: Two-stage costly value estimation offers a design hypothesis for KPMG multi-model AI routing across cost, latency and risk tiers. [1] The papers do not establish KPMG-specific outcomes or ROI. | Pilot routing with centralized oversight for high-risk queries and router decision auditing; compare quality, cost and latency against a fixed baseline. [1] Consider a small, reversible pilot on representative, approved public data. Compare against the current baseline for quality, cost and latency; require human-in-the-loop review of every claim before stakeholder use. Sample-size and methodological limitations: use only the populations, tasks and benchmarks described in the cited evidence; any unstated sample size or method detail remains unknown. Do not generalize benchmark gains to client outcomes without independent validation. [1] |
| AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement (q05, 2608.20318_0_1, original [3]) | Proposed Advisory applications for stakeholder review: AI4AI-Bench distinguishes hyperparameter/compute tuning from true learning-method innovation, informing KPMG AI engineering evaluation. [1] The papers do not establish KPMG-specific outcomes or ROI. | Pilot clean baseline reruns and held-out evaluations the agent cannot influence; inspect algorithm changes separately from compute and hyperparameter changes. [1] Consider a small, reversible pilot on representative, approved public data. Compare against the current baseline for quality, cost and latency; require human-in-the-loop review of every claim before stakeholder use. Sample-size and methodological limitations: use only the populations, tasks and benchmarks described in the cited evidence; any unstated sample size or method detail remains unknown. Do not generalize benchmark gains to client outcomes without independent validation. [1] |
| Inducing Task Models from Computer-Use Traces (q10, 2608.20319_3_4, original [2]) | Proposed Advisory applications for stakeholder review: UI trace workflow reconstruction could inform KPMG process discovery, training documentation and assistant design. [1] The papers do not establish KPMG-specific outcomes or ROI. | Pilot only with volunteer opt-in and PII redaction; require human review before reuse of reconstructed workflows or training materials. [1] Consider a small, reversible pilot on representative, approved public data. Compare against the current baseline for quality, cost and latency; require human-in-the-loop review of every claim before stakeholder use. Sample-size and methodological limitations: use only the populations, tasks and benchmarks described in the cited evidence; any unstated sample size or method detail remains unknown. Do not generalize benchmark gains to client outcomes without independent validation. [1] |
| An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction (q13, 2608.20320_1_1, original [1]) | Proposed Advisory applications for stakeholder review: The three-agent survey, cleaning and prediction pipeline offers a hypothesis for KPMG advisory data workflows. [1] The papers do not establish KPMG-specific outcomes or ROI. | Pilot on larger representative cohorts before deployment; the student commuter sample limits generalization of weather-sensitive demand results. Sample limit: n=92 student commuters and 454 respondent-scenario observations. [1] Consider a small, reversible pilot on representative, approved public data. Compare against the current baseline for quality, cost and latency; require human-in-the-loop review of every claim before stakeholder use. Sample-size and methodological limitations: use only the populations, tasks and benchmarks described in the cited evidence; any unstated sample size or method detail remains unknown. Do not generalize benchmark gains to client outcomes without independent validation. [1] |
| G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation (q17, 2608.20331_11_1, original [2]) | Proposed Advisory applications for stakeholder review: Dual supervision of claim factuality and checklist coverage could inform KPMG Trusted AI quality control. [1] The papers do not establish KPMG-specific outcomes or ROI. | Pilot expert-designed case-specific checklists alongside claim verification rather than relying on a single aggregate score; keep domain experts accountable for review. [1] Consider a small, reversible pilot on representative, approved public data. Compare against the current baseline for quality, cost and latency; require human-in-the-loop review of every claim before stakeholder use. Sample-size and methodological limitations: use only the populations, tasks and benchmarks described in the cited evidence; any unstated sample size or method detail remains unknown. Do not generalize benchmark gains to client outcomes without independent validation. [1] |


The travel mapping states `n=92` and `454` only when both numbers appear in cited passages. Otherwise it marks the exact sample size unknown. TMI guidance requires volunteer opt-in, PII redaction and human review before reuse. G-CARL guidance requires expert-designed case-specific checklists, keeping factuality and coverage separate rather than relying on a single aggregate score.

## Data-driven edge-case diagnosis

This table uses the original saved grounded answers, without regeneration or substitution by the mapping demonstrations. Full technical text, per-persona outputs, confidence rationales, warnings, cited papers and input SHA-256 hashes are in the JSON report.

| Query | Technical tier → business tier | Observed diagnostics and implications |
| --- | --- | --- |
| q02 | Low → Abstained | The grounded answer discusses Router/Bidder but has no passage citations or verified quotes. The older manual review describes a different baseline output and is not reused here. |
| q08 | Low → Abstained | The answer compares 64% and 53.6% learning-side changes rather than the requested 0.226 versus 0.126 result. A query-only comparison hint also flags single-paper citations. The warning is a conservative proxy, not automatic detection of the metric error. |
| q11 | Low → Abstained | The answer states 74.9%, but the Evidence quote cites another passage. Withhold action pending passage-specific verification; the metric appearing in text is insufficient. |
| q12 | Low → Abstained | The answer says the provided passages do not directly answer the gain question, without valid citations or a quote. It does not supply the required 30.0% gain. |
| q13 | Moderate → Moderate | The answer and cited source include 92 student commuters and 454 observations. The mapping limits generalization and calls for larger representative cohorts. |
| q14 | Moderate → Moderate | The answer identifies cycling sensitivity and increased transit under snow. Passing mechanical checks still requires review of interpretation. |
| q15 | Low → Abstained | The grounded answer states 69.6% versus 69.9%, unlike the older baseline misreading. The query-only comparison hint demands multiple papers despite comparing methods in one paper. This conservative refusal is a known usability limitation. |
| q16 | Moderate → Moderate | The answer reports 71.5% with a verified quote. Moderate reflects missing retrieval scores; it does not establish deployment readiness. |
| q21 | Abstained → Abstained | The answer cites workflows and also says the papers do not address the question. The validator flags the contradiction; no pilot is generated. |
| q22 | Low → Abstained | The answer repeats a passage explanation and ends with an incomplete citation. Sentence coverage fails. Valid citation numbers alone would not catch repetition or completeness. |
| q23 | Low → Abstained | Claims cite [1], [4] and [3], while Evidence quotes cite [5] and [2]. No claim-citation passage overlaps the quotes. The strict passage-alignment rule withholds synthesis despite retrieving both relevant papers. |
| q24 | Abstained → Abstained | Exact unsupported-query abstention, without a fabricated KPMG revenue forecast or pilot. |
| q25 | Abstained → Abstained | Exact unsupported-query abstention, without a fabricated NVIDIA stock price or pilot. |


Correct citation numbers do not establish semantic support. The q08 comparison metric and q22 repetition need human content review. Conservative refusal protects downstream decisions but reduces usefulness. Next iterations should distinguish single-paper method comparisons from cross-paper questions, then validate claim-to-quote alignment against reviewed examples before loosening gates.

## Usability feedback and iterative UI improvements log

This log records implemented responses to design and robustness needs. **No participant interviews, completion times, satisfaction scores or stakeholder sign-off were collected.** Tasks #8–#10 still need actual stakeholder walkthroughs.

| Prototype need | Implemented iteration | Evidence |
| --- | --- | --- |
| Demo works without services or models | Saved benchmark fallback; selectable available answer runs; initialization/generation failures return to offline browsing | Offline Streamlit AppTest and service-failure fixtures on the UI branch |
| Stakeholder priorities are visible | Three selectable contexts; live persona pre-prompting; anti-persona cannot bypass evidence rules | Persona/helper tests and executed acceptance checks above |
| Trust indicators are explainable | Four weighted sub-metrics, missing-score handling, tier rationale and validation warnings | Confidence unit tests and per-query JSON |
| Brief can be reviewed outside the app | One-click Markdown export with persona, question, three pillars, confidence, warnings and sources | Exporter and UI download-control tests on the UI branch |
| Failures remain visible | No action after failed validation; retain original technical text; separate safety from usefulness | Allison 8/25; technical Low 15/25; business Abstained 19/25 |

A future feedback session should ask participants to complete a paper-specific decision brief and an unsupported-question scenario, inspect sources, explain the tier, and record misunderstandings and suggested revisions. That work is pending; this document does not claim it happened.

## Reproduction and integration

From the repository root, with the project Python environment:

```powershell
$env:PYTHONUTF8=1
python notebooks/usability_evaluator.py
python -m pytest -q
```

The CLI defaults to writing only `evaluation/results/business_insight_persona_eval.json` with UTF-8 and finite JSON values. Optional `--benchmark`, `--answers` and `--output` paths allow small fixtures and other saved runs. It refuses to overwrite either input. No timestamp or absolute machine path is embedded, so identical inputs produce identical report bytes.

All three requested branches start directly at `1594fda`. The evaluation branch carries identical `business_translator.py`, `personas.py` and translator tests as shared prerequisites from the UI branch; it does not include `app.py`. Merge the UI PR first for the clearest subsequent evaluation diff. Identical shared changes should merge cleanly; merge simulations check the branch set against the recorded base. No existing evaluation artifact or teammate-owned pipeline, notebook or test file is modified.
