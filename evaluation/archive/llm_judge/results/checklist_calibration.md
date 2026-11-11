# Focused reviewer: initial calibration notes

This is an assistant comparison with the earlier qualitative review, **not an
independent human calibration or an accuracy estimate**. Only three answers from
one paper were tested. Checklists still need human approval.

The final live run in `checklist_review.json` used Qwen3.5:9b, no repair retry,
and the saved answer passages. All three reviews passed structural validation;
model calls took 19.6, 18.8, and 19.1 seconds (57.5 seconds total). These timings
are local observations, not performance guarantees. The report does not ask the
model to copy quotations; displayed source text is copied by the code.

| Answer | Useful findings | Remaining disagreement |
| --- | --- | --- |
| Router decision rule | Identifies the missing inspection order/stopping rule. Automatic checks flag excessive length. | Approves the method distinction, despite the earlier review finding distracting Bidder material and policy confusion. |
| Router versus Bidder | Identifies missing centralized/decentralized decision-making and global-welfare/local-surplus distinctions. | Incorrectly approves the high-cost options: the answer says the bidder declines, omitting the alternative of using the cheap estimate. |
| Evaluation domains | Recognizes all three domains. Automatic checks flag missing citations. | No disagreement on these checklist points. |

All three answers receive “Needs attention”, but some individual “Covered” labels
remain too generous. Do not treat valid JSON, source IDs, or checklist completion
as evidence that the judge is calibrated. Use this as a diagnostic assistant,
with human spot-checks and a broader set of independently labeled examples before
ranking optimizations. Source excerpts are selected aids, not independent proof.

The initial focused pilot is preserved in `checklist_review_initial.json`; it
included a conflicting source-support field that was removed from the final
one-decision-per-requirement format. Earlier broad-judge reports remain unchanged.
