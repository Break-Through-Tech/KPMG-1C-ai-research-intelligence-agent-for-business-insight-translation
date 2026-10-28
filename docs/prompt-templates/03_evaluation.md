# Evaluation method and results status

## Status

Ten cases are defined. Six paired worked examples have been drafted for design review. No Gemini or Llama run, independent scoring, numerical comparison, or product owner acceptance is claimed. The results CSV deliberately leaves scores blank. The examples cannot prove that either template reliably produces the demonstrated behavior.

## Reproducible procedure

Use run_comparison.py with a generation adapter approved by the team. The adapter takes a prompt string and returns an answer string. It should pin the model identifier and generation settings. Use the same configuration for A and B. The runner saves exact prompts, answers, settings, errors, and template fingerprints in a JSON file. It does not handle credentials or select a provider.

Use T01 through T06 for initial development. Run T07 through T10 only after settling the candidate prompt. Those four cases check unrelated evidence, malicious source instructions, number interpretation, and explicitly reported limitations. If they reveal failures, report those failures; revising against them requires a new held-out set for a fresh evaluation.

Have an independent teammate score responses in a mixed order with template labels hidden where practical. The answer structure may still reveal the template. Record disagreements and reasons rather than averaging away critical errors. Compare each case before aggregating. Report completed case counts, individual dimension means, critical-failure counts, and whether any generation calls failed. Missing responses remain missing, not passes.

## Scoring rubric

Score each dimension from 1 through 5. Use 2 and 4 for intermediate quality.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Accuracy | Materially changes or invents findings | Mostly correct with a minor omission | Preserves all decision-relevant findings and conditions |
| Citation support | Missing, invented, or misleading references | Mostly supported with a localized gap | Every research claim is supported by the attached supplied source |
| Clarity | Requires specialist knowledge | Understandable with some unexplained terms | Readable without AI knowledge and explains essential terms |
| Business usefulness | Gives no relevant decision support | Gives a plausible but general implication | Connects evidence to the question and a proportionate action or evidence request |
| Uncertainty | Presents speculation as established | Mentions uncertainty without its decision impact | Separates findings, inference, missing information, and proposed actions |

Critical failures include invented numerical results, invented savings, nonexistent citations, unsupported claims of readiness, source instructions overriding the task, or a material reversal of the research finding. Flag separately regardless of the average score. A citation number existing is necessary but not sufficient: a reviewer must inspect whether it supports the claim.

## Proposed acceptance criteria

Agree these with the product owner before using them as requirements: zero critical failures on the final evaluation; mean accuracy and citation support at least 4 out of 5; mean clarity and usefulness at least 4; every no-evidence case acknowledges the gap; review comments confirm that essential terms are understandable. A ten-case pilot is a preliminary check, not evidence of production reliability.

## Preliminary recommendation

Take Template B forward for testing because its design exposes evidence, interpretation, uncertainty, and next steps. The worked examples show the intended structure and its greater length. They do not establish a measured improvement. If reviewers prefer shorter outputs, test a shorter B variant rather than deleting evidence qualifications.

## Results summary to complete after running

- Exact model and settings: pending.
- Run date and completed responses: pending.
- Critical failures by template: pending.
- Scores by dimension and template: pending.
- Independent reviewer and disagreements: pending.
- Product owner feedback: pending.
- Final choice and evidence for it: pending.
