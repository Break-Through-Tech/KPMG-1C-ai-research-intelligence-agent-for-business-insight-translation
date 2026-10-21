# Fresh answer review

October 14, 2026. One reviewer compared all 25 fresh `llama3.2` answers in
[answers.json](answers.json) with the retrieved passages and the labeled facts
in `benchmark.json`. The run used the notebook's prompt and model, the newer
`ResearchRetriever` context and paper citation formatting, temperature 0,
and seed 42. This is an initial manual assessment, not a blinded or
multi-reviewer study.

**Content rubric:** *full* answers all parts correctly; *partial* contains
correct relevant material but omits a requested part; *fail* gives a wrong or
contradictory answer, or declines an answerable question. Citation and direct
quote checks are separate, so a full content answer may still fail issue #5's
traceability requirement.

| ID | Content | Review note |
| --- | --- | --- |
| q01 | Full | Correct value-of-information rule. |
| q02 | Fail | Declines a Router-versus-Bidder question. Bidder passage was absent from context. |
| q03 | Full | Correctly names MATH, RAG, and EmbedLLM domains. |
| q04 | Full | Correct noisy-competitor limitation. |
| q05 | Full | Correctly reports ten repositories and ten families. |
| q06 | Full | Correctly reports four-hour agent and twelve-hour replay budgets. |
| q07 | Full | Correctly gives the 0, 0.1, and 1.0 scale anchors. |
| q08 | Fail | Gives the correct 0.226-versus-0.126 result, then says the papers do not address that same question. |
| q09 | Full | Identifies objective and procedure models, but has no citation. |
| q10 | Full | Correctly reports 0.974 adjusted Rand index. |
| q11 | Fail | Declines the 74.9% reconstruction question because the relevant passage was not retrieved. |
| q12 | Fail | Reports 18.57 absolute accuracy as the *gain*; the requested gain was 30% relative. |
| q13 | Fail | Declines the 92-commuter, 454-observation question. |
| q14 | Partial | Names cycling and transit, but omits the increased transit use under snow and has no citation. |
| q15 | Fail | Says random forest scored 71.5%; the paper reports 69.6% for random forest and 71.5% for the best vision setup. Citation points to a passage with the correct values. |
| q16 | Fail | Declines the 71.5% best vision accuracy question. |
| q17 | Partial | Gives task constraints but not the full patient-oriented report interpretation task. |
| q18 | Partial | Explains atomic-claim verification but omits the weighted checklists used for response coverage. |
| q19 | Full | Correctly identifies MMedReport and the three evaluation dimensions. |
| q20 | Full | Correctly describes clinician preferences, but has no citation. |
| q21 | Fail | Declines despite retrieved passages about both computer-use and travel-survey workflows. |
| q22 | Fail | Declines despite naming the two relevant papers in its explanation. |
| q23 | Partial | Describes the task-model paper but omits G-CARL. |
| q24 | Appropriate abstention | Does not invent KPMG revenue data. |
| q25 | Appropriate abstention | Does not invent an NVIDIA stock price. |

Among 23 answerable queries: **10 full, 4 partial, 9 fail**. Both unsupported
queries received the notebook's abstention phrase. Mechanical checks in
[answer_checks.json](answer_checks.json) found a citation in 14/23 answerable
responses, no out-of-range citation numbers, and **zero verified direct quotes**.
Valid citation numbers do not imply that the cited passage supports the claim:
q15 is a clear counterexample.

The answer failures have different causes. q02, q11, and q13 lacked the
requested fact in retrieved context; q15 had the correct values in context but
misread them; q08 had a self-contradictory output. Improving passage selection
alone will therefore not resolve every failure. The current notebook prompt
does not request the direct non-paraphrased quote required by issue #5.
