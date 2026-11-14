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

## November 13 local pilot

After the revision above, fixed excerpts from the five-paper corpus became available for A31. A local `qwen2.5:7b` run compared the two phrasings and both templates. Template B was shortened to version 3 after the first run used inconsistent source notation; a further version 4 attempt regressed on sentence-level citations and was archived. See [pilot review](pilot_review.md) for outputs and limits. The statement above that no real model was called describes the November 1 revision only. The full business suite and independent scoring are still pending.
