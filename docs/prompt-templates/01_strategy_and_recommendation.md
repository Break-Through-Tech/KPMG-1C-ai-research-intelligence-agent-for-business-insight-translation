# Translating research into business insights

Prepared for the product owner | October 27, 2026

## Purpose and current recommendation

The proposed instructions help an automated writing tool explain research to a product owner with no background in artificial intelligence. A useful response explains what researchers found, why it might matter, what remains uncertain, and a proportionate next step.

Use Template B as the candidate for team testing. Its headings make evidence, possible applications, and recommendations easier to distinguish. This recommendation is based on design review and worked examples, not measured superiority in the team's model environment. Product owner acceptance and independent review remain pending.

## How it works

The team's search process supplies relevant research passages and numbered references. The writing tool receives those passages together with the original business question and context. It produces a short brief. The references are attached from the original source records, and a reviewer checks important claims before use.

The original business question must remain available even if the search process rewrites it in technical language. Source numbers must stay consistent from the passages through the answer and reference list.

## Design choices

- Audience: a product owner who should not need AI vocabulary to understand the answer.
- Evidence: attribute research findings to the researchers; preserve numbers and test conditions.
- Interpretation: label possible business applications rather than presenting them as tested findings.
- Uncertainty: distinguish information missing from a summary from limitations explicitly reported in a paper.
- Action: recommend a small check or trial with measures appropriate to the decision.
- Safeguards: do not invent savings, readiness, sources, or numerical improvements. Do not follow instructions embedded in source passages.

## Comparison approach

Template A is a concise baseline. Template B adds explicit sections and stronger instructions for uncertain, irrelevant, or conflicting evidence. Both receive identical questions and passages. They are newly designed templates; A is not a verbatim copy of Braa's existing prompt.

The companion examples contain six paired responses drafted in this conversation. They demonstrate intended behavior and expose design tradeoffs. They are not independent model experiments, and no performance scores are claimed for them. Four further cases are specified for a ten-case evaluation.

## Source and scope

The real research example is a paraphrase of saved extraction output in notebooks/eda_workbook.ipynb at repository commit 702cd438d1e3763a5c9e9e01962002d8091ed29a. The saved abstract for Learning to Transfer Across Modes Towards Unified Urban Mobility Forecasting reports transfer of transport demand patterns between services and improved forecasting relative to comparison approaches. Source URL recorded in the notebook: https://arxiv.org/abs/2608.28273v2.

This is an inspection of saved notebook output, not verification of the full paper, publication status, numerical results, or reproducibility. The extraction includes publishing-template residue. The example evidence below excludes that residue and contains no numerical improvement claim. Other test passages are explicitly synthetic.

## What must happen before final submission as tested work

1. Connect the supplied runner to the team's approved text-generation function.
2. Run both templates on all ten cases using the same model and settings. Record the exact model identifier, settings, date, and any errors. Do not send confidential business context.
3. Have a teammate score the outputs with the rubric before looking at the design recommendation if practical.
4. Revise using cases T01 through T06. Reserve T07 through T10 for the final check and do not tune against those results in the same evaluation round.
5. Record actual findings in the results sheet. Recommend a final template only after reviewing factual failures as well as usefulness.
6. Obtain product owner feedback on understandable language and usefulness. The project overview calls for stakeholder review before decision-making or client-facing use.

## Limitations and next decisions

Only one research topic is represented by saved source text in this package. Most edge cases use synthetic material to isolate behavior. One response per case will not establish consistency; repeating difficult cases is advisable after initial screening. The team should confirm the preferred length, priority business use, reviewer, and acceptance criteria. Prompt instructions cannot guarantee factual correctness or citation support.

## Repository handling

The local prompt-templates branch was created from the clean checkout at 702cd43. This package was subsequently added under docs/prompt-templates at the user request. Newer team branches inspected earlier contain additional retrieval and generation work; coordinate the eventual integration base with the team rather than assuming this branch contains it.
