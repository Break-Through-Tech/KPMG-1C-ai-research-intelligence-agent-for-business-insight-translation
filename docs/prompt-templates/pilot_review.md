# Small local business-prompt pilot

## Data and setup

This pilot uses three saved passages (abstract, conclusion, discussion) from the travel-behavior paper in the project's five committed arXiv PDFs. The passages and paper metadata are frozen in [`evidence_pilot_five_papers.json`](evidence_pilot_five_papers.json). Only Allison case A31 was run, using its original wording and one paraphrase. Both phrasings used the same evidence. This tests a translation prompt with supplied passages; it does **not** test retrieval or the live browser business panel.

The model was local Ollama `qwen2.5:7b` with temperature 0, seed 42, context 8192, and output cap 700. The provider adapter is [`ollama_adapter.py`](ollama_adapter.py). The runner saves exact prompts, outputs, evidence fingerprints, and settings. Model settings are declared by the adapter, not independently confirmed by the runner.

## What happened

| Candidate | Two-phrasing result | Decision |
| --- | --- | --- |
| Template A and B version 2 | A gave useful summaries but put source information at the end, leaving research sentences without passage citations. B separated possible applications and gaps, but used `Source: 1` style or source lists instead of the requested inline `[1]` citations. Some business language was broader than the supplied study. | Keep only as a baseline in [`archive/didnt_work/pilot_qwen_a31_ab_v2.json`](archive/didnt_work/pilot_qwen_a31_ab_v2.json). |
| B version 3 | Both phrasings used bracketed passage citations and gave a clearly proposed pilot. They retained the study sample and key weather/prediction findings. **Neither response cited every research sentence**; the sentence with 92 commuters and 454 observations had no adjacent citation. Several `[1][2][3]` groups were broader than needed, and one proposed business application carried a paper citation that could look like direct study evidence. | Keep as a provisional prompt, with outputs in [`pilot_qwen_a31_b_v3.json`](pilot_qwen_a31_b_v3.json). Require human citation review before reuse. |
| B version 4 | The original wording regressed: several research sentences had no citation until the last sentence of the paragraph. The paraphrase cited more consistently. | Archive this run in [`archive/didnt_work/pilot_qwen_a31_b_v4.json`](archive/didnt_work/pilot_qwen_a31_b_v4.json); restore version 3. |

The revised template is useful for *drafting* a business brief, but this pilot does not prove the answer is fully supported. The two phrasings were generated with the same model and passages, so they are not independent validation. In the version 3 outputs, the paraphrase omitted the 69.9% zero-shot LLM comparison that the original included; that is a coverage difference, even though the numbers that did appear match the supplied passage. The supplied excerpts end mid-sentence because they are fixed retrieval chunks; source metadata is present but authors/date fields were unavailable in this snapshot.

## Before using this for a decision

1. Attach fixed passages and source records for the remaining business cases, then run both templates on the development split without changing evidence between variants.
2. Add a sentence-level citation and claim-support review. A bracketed citation somewhere in a paragraph does not support every sentence; business suggestions should be labeled as proposals rather than treated as paper findings.
3. Ask an independent teammate and KPMG reviewer to score accuracy, usefulness, caveats, and whether the output helps them make a decision. Keep the reserved cases for a later clean check.

The [`evaluation_results.csv`](evaluation_results.csv) primary score sheet remains blank: this two-phrasing pilot has not been independently scored and does not fill the planned 32 A/B rows.
