# Translating research into business insights

Revised November 1, 2026 for the product owner.

## Purpose and recommendation

Help a professional-services user understand research and decide what to investigate next. The reader should not need AI knowledge. Use Template B version 2 as a candidate for testing, not a proven winner. It separates findings, potential business implications, uncertainty, and proposed actions while supporting the requested format.

## Basis for this revision

Allison's Sample User Prompts supplies realistic questions, a recommended answer pattern, and testing guidance. Her Personas and User Stories guide supplies optional tools for choosing the user and defining observable success. This package adopts one draft persona and four stories; neither document mandates a separate persona research project or testing all 46 questions. The selection and numerical acceptance thresholds here are team proposals, not requirements stated by Allison. See 04_persona_and_user_stories.md and 05_allison_test_mapping.md.

## Design and comparison

Both templates receive the same original business question, research passages, source records, topic, and, for follow-ups, prior answer. Template A gives concise general instructions. Template B provides explicit evidence boundaries and decision-oriented structure. They are new templates, not verbatim copies of the existing generation prompt. Both now have the same default 300-word limit to avoid confounding length with structure. Explicit formats and audiences take precedence.

The default audience remains a product owner with no AI knowledge. Explain terms when needed, connect evidence to professional-services decisions when relevant, and avoid assumptions about KPMG or a particular client. Separate reported findings from proposed business uses. Identify the most relevant papers, explain why they matter, and attach usable references. Do not invent missing metadata, benefits, timelines, or adoption readiness.

## Scope of this task

The prompt owner designs and evaluates business translation from supplied evidence. Retrieval owners supply relevant public-paper passages and source metadata. Fix the evidence when comparing templates or question paraphrases. Separately assess the complete pipeline when retrieval is rerun; a changed source set is a confounding factor, not automatically a prompt failure.

## Test design

The primary suite uses Allison's questions 29, 30, 31, 32, 34, and 40, plus follow-ups 41 and 42. Each has an original and a proposed paraphrase, giving 16 cases and 32 template responses. These exact originals were extracted from the supplied Word document. The paraphrases are proposed test inputs, not quotations from Allison. No evidence is fabricated to fill those cases. Relevant passages and metadata must be supplied before model calls are made.

Use questions 29, 30, 31, 32 and follow-ups 41 and 42 for development; reserve 34 and 40 for a final check. Original questions run before their paraphrases. The runner uses a shared saved A31 answer for follow-ups so both templates receive identical history. This checks follow-up translation, not the application's memory implementation. The original ten transport/synthetic cases are retained in stress_cases.json as supplementary checks; the old demonstrations do not count as results for version 2.

## Current results and limits

Model runs, independent scoring, robustness results, and product owner acceptance remain pending. The six worked comparisons are version 1 demonstrations drafted in conversation, not captured Gemini or Llama outputs. Input rendering and blocked-case handling can be verified without model access, but cannot establish answer quality. The suite is small, and example source metadata still needs retrieval-team input. Latest and maturity claims require supporting evidence rather than compliance with an unsupported question premise.

## Next actions

1. Confirm the draft persona and priority questions with the product owner.
2. Obtain relevant public research passages, metadata, and a stable evidence identifier from the retrieval team.
3. Populate a separate evidence input file, including the topic and saved prior answer for follow-ups.
4. Run the development cases on the team's approved model and record exact settings.
5. Independently score and revise; then run the reserved cases and record limitations honestly.
6. Select the final template from actual results and stakeholder feedback. Human review remains necessary before business or client-facing use.
