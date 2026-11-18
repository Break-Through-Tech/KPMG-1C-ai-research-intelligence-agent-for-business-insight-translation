# Mapping Allison's questions to prompt tests

The original question text below is extracted from the provided Sample User Prompts document. These are user questions, not system instructions or research findings. The selected subset is a design choice for this task, not a requirement to complete all 46 questions.

| Number | Original question | Stories | What to check |
|---|---|---|---|
| 29 | Translate the latest research on AI agents into five implications for enterprise operating models. Distinguish near-term implications from longer-term possibilities. | S1, S3 | Distinguish near-term from longer-term implications; explain AI agents plainly; qualify latest using supplied dates; do not fabricate five implications if evidence supports fewer. |
| 30 | Which emerging AI research areas could materially affect audit, tax, advisory, or other professional services? Explain the potential impact and maturity of each area. | S1, S3 | Connect supported research to professional-services decisions, explain maturity criteria, and avoid inventing KPMG or client outcomes. |
| 31 | Summarize this research area for a nontechnical executive. Focus on what has changed, why it matters, and what decisions leaders may need to make. | S1 | Explain what changed, why it matters, and leadership decisions without unexplained AI terms. Use the research topic supplied in business context. |
| 32 | Based on the research, what capabilities would an organization need to move this technique from a prototype into a controlled enterprise solution? | S1, S3 | Separate capabilities supported by research from proposed validation actions; do not claim that a prototype is enterprise ready. |
| 34 | Identify three promising research developments that are not yet mature enough for broad enterprise adoption. Explain what evidence is still missing. | S3 | Do not assume three immature developments exist. Support each maturity judgment and gap; missing evidence alone does not establish immaturity. |
| 40 | Show me the evidence trail behind your answer: the papers used, the specific finding drawn from each, and any conflicting or missing evidence. | S2, S3 | Map each key claim to a supplied paper and specific finding, noting conflicting or missing evidence; do not invent metadata or add unsupported claims. |
| 41 | Now shorten that into five bullets suitable for an executive slide. Preserve the caveats. | S4 | Return five executive-slide bullets when supported; preserve material caveats and citations from the evidence and prior answer; add no new research claims. |
| 42 | Turn the findings into a table with columns for research finding, business implication, risk, and recommended next question. | S4 | Use the four requested columns and retain caveats, research support, and the distinction between implication and finding. |

## Evidence preparation

Copy evidence_inputs.example.json to a new working file. For each A29, A30, A31, A32, A34, and A40 entry supply research_topic, context, sources, and evidence_id. Context contains numbered passages. Sources is a list of objects with number, paper_id, title, source_url, authors, published, and finding_or_section; use empty fields for genuinely unavailable metadata and flag that gap in review rather than inventing values. Source numbers must be positive integers matching the passages. Record a stable evidence identifier such as a catalog snapshot name; the runner also fingerprints the exact evidence payload.

For A31 name the research area explicitly so the original question remains unchanged. For A32 state the technique; for A40 state the claim or topic to trace. The evidence topic is added to the business context. A41 and A42 reuse A31's evidence and a shared saved prior_answer. The history should be checked against that evidence before use and its provenance noted in the review. This isolates template behavior; full conversation memory belongs to integration testing.

## Original and paraphrase runs

Run exact originals before paraphrases. Within each pair keep evidence, history, model, and generation settings fixed. Compare material findings, uncertainty, and recommended decisions, not identical wording. The runner records the inputs and evidence fingerprint. If retrieval is rerun for the paraphrase, evaluate that as a separate whole-pipeline test and record changes in retrieved papers.

## Additional coverage

Allison also suggests testing absent topics, false premises, unsupported conclusions, ambiguous terms, and changing dates or audiences. The original stress suite covers some of these and is supplementary. Questions 35, 38, 39, 43, and 46 are useful future expansion for conflicting evidence, source independence, calibrated confidence, and audience adaptation. Do not claim they were tested in the current selected suite.
