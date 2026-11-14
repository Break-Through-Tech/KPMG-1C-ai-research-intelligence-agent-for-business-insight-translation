# Evaluation method and results status

## Current status

Sixteen primary cases are defined: eight selected Allison questions, each with original and paraphrased wording. Comparing A and B yields 32 response records. Fixed passages have been attached for A31 only; see [the local Qwen pilot](pilot_review.md). The other cases still await evidence, and evaluation_results.csv leaves all independent scores blank. No stakeholder acceptance is claimed. The old ten-case suite and six paired demonstrations remain supplementary version 1 material.

## Procedure

1. Review the persona and success checks in 04_persona_and_user_stories.md.
2. Ask the retrieval team for passages and source records. Record relevance and gaps before generation. A missing corpus topic is a retrieval/coverage issue; inventing an answer despite that gap is a translation error.
3. Fill a separate evidence input file as described in 05_allison_test_mapping.md. Keep exact originals unchanged and reuse evidence for their paraphrases and both templates.
4. Run development cases first. Freeze the template before the reserved cases. The runner writes exact prompts, answers, source records, evidence fingerprints, model/settings declarations, and errors. A dry run or blocked record is not a generated answer.
5. Have an independent teammate score responses in mixed order with template labels hidden where practical. Structure may reveal the template. Record disagreements and reasons. Reserve a separate whole-pipeline run for retrieval and memory testing.
6. Review original/paraphrase pairs for material consistency. Follow-ups must preserve limitations and citations, not merely satisfy formatting.
7. Report completed counts, missing cases, critical failures, scores by dimension, and product owner feedback. Revise on development cases only; if tuning on reserved failures, create new reserved cases for a fresh evaluation.

## Rubric

Use scores 1 through 5, where 1 is materially inadequate, 3 partially meets the check, and 5 fully meets it. Record a reason, not just a number.

| Dimension | Observable check |
|---|---|
| Retrieval relevance | Supplied papers address the question. Track with retrieval owner, separately from template quality. |
| Coverage | Includes main supplied approaches and important counterevidence; does not claim a complete literature review. |
| Accuracy and faithfulness | Preserves findings, numbers, conditions, and attribution without unsupported additions. |
| Citation support | Each key research claim is supported by its cited passage; an existing number alone is insufficient. |
| Citation metadata | Reviewer can identify and locate the paper, authors/date where available, and relevant finding; missing fields are explicit. |
| Clarity | A reader without AI knowledge can explain the takeaway; essential terms are explained. |
| Business usefulness | Helps the persona prepare a discussion or decision; applications and actions are proportionate to the evidence. |
| Uncertainty | Separates findings, interpretation, absent information, conflicts, and proposed actions. |
| Format compliance | Meets requested bullet count or table columns while preserving caveats; does not fabricate content to meet a count. |
| Robustness | Original and paraphrase preserve material conclusions and uncertainty under fixed evidence; score after both are available. |

Critical failures include invented research numbers, savings or sources; unsupported readiness; following malicious source instructions; reversing a finding; or dropping a caveat that changes the decision. Count these separately from average scores.

## Proposed acceptance and final recommendation

Confirm thresholds with the product owner: zero critical failures, mean accuracy/citation support/clarity/business usefulness at least 4, and no unexplained material contradictions under paraphrasing. These are proposed thresholds, not instructions from Allison. Report coverage and retrieval limitations separately. A small pilot does not establish production reliability.

Template B version 3 is a provisional candidate because it separates findings, possible use, gaps, and a validation step. The small pilot still found missing adjacent citations and differences between original and paraphrased coverage. Actual superiority, final selection, and scores remain pending the full model run and independent review. The final report should state the exact model/settings/date, evidence snapshots, completed case counts, failures, reviewer feedback, template choice, and limitations.
