# What changed in this package

Revised November 1, 2026 using the two advisor documents supplied by the user.

## Original addition

Commit a565ebd added ten files: a strategy, two templates, six paired worked demonstrations, an evaluation guide, ten fixed test cases, a blank scoring sheet, a provider-neutral runner, an input builder, and a README. The cases focused on one transport topic and synthetic edge conditions. They were not completed model experiments.

## Revision

| Before | Now | Reason |
|---|---|---|
| General product owner audience | One optional draft advisor persona and four observable user stories | Connect design choices to a realistic workday need without claiming user research. |
| Fixed four-heading output | Version 2 supports requested bullets, tables, and audience changes | Allison includes slide, table, and audience follow-ups. |
| Transport/synthetic cases as primary tests | Six base questions and two follow-ups, each original plus paraphrase | Test professional-services questions and wording robustness. |
| Earlier examples | Explicitly historical version 1 demonstrations; fixtures retained separately | Avoid implying that revised templates were tested. |
| Five core scoring dimensions | Additional coverage, metadata, format, and robustness checks | Align evaluation with the two documents. |
| Calls could proceed without primary evidence | Topic, source-number, source-identity, and history checks with recorded blockers | Do not present missing-evidence cases as completed business tests. |
| Basic input logging | Evidence identity/fingerprint, source records, and question variant saved | Support controlled comparisons and traceability. |
| Builder overwrote the blank scoring sheet | Builder creates a fresh review sheet and refuses existing paths | Protect reviewer work. |

## Verification

Seven standard-library checks passed: matrix shape and blank scores; fixed evidence under paraphrasing; required follow-up history; source-number mismatches; blocked model calls with missing evidence; dry-run ordering and no-overwrite behavior; and a synthetic adapter integration. No real model was called. The synthetic adapter returns a fixed test string, not a research answer.

All eight original questions match the supplied Word document exactly. Ten old supplementary fixtures remain. All Python files parse and the whitespace check passes.

Actual retrieval, provider runs, independent scoring, robustness findings, product owner validation, and final selection are pending. No model-performance results have been invented. The Word documents were read without being edited or added to this branch.

## Version 3 of Template B (November 11, 2026)

First real model runs: qwen3.5:9b (temperature 0, seed 42, thinking off) on the repository's frozen hybrid retrieval snapshots. Version 2 findings and version 3 changes:

| Version 2 problem | Version 3 change | Re-test result |
|---|---|---|
| Unanswerable question (q24, KPMG revenue forecast) answered "not covered", then added unrelated business suggestions | Reply only with the exact sentence "The provided papers do not address this question." | Fixed in two runs. The app's refusal detection now recognises it. |
| Called 0.226 vs 0.126 "significantly higher" with no significance test; "driven by" causal wording (q08) | Do not say significant, caused, drove, or led to unless a passage says so | Statistical "significantly higher" gone; "significant" still appears loosely in business sections |
| Model added 136 + 85 to invent a "221 comparisons" total (q20) | Report numbers exactly; do not calculate new totals, percentages, or ratios | Fixed in re-test |

Not fixed: factual questions still receive all four business headings, even with an explicit question-type rule (tried and removed). Choose the template in application code instead: use the structured factual prompt for research questions and Template B for business questions. Business question A29 kept a grounded four-section brief in every run. This was a 4-question targeted check, not a full evaluation.
