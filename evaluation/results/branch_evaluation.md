# RAG evaluation and fixes — November 13, 2026

This review started on `codex/rag-answer-evaluation` and was completed on `codex/sparkle-ui-and-evaluation`. The notebook is a small research assistant over five public papers. It answers one question at a time; it has no conversation memory or business-usefulness rating.

## Dataset 1: five arXiv papers

This project-specific dataset comes from the five PDFs committed in `data/`, with 25 questions and relevance labels drafted by Codex (GPT-6-Sol) and checked against the PDFs during preparation.

Twenty questions ask about one paper, three ask which papers cover a topic, and two ask for information absent from the corpus. The labels have not had a documented independent human annotation pass. We kept the question set fixed while diagnosing the system. The final retrieval run is [`retrieval_branch_confirmed.json`](retrieval_branch_confirmed.json); the answer runs are [`answers_branch_baseline.json`](answers_branch_baseline.json) for `llama3.2`, [`answers_qwen_branch_baseline.json`](answers_qwen_branch_baseline.json) for the old Qwen path, and [`answers_qwen_branch_final.json`](answers_qwen_branch_final.json) for the final notebook path.

### Retrieval

The retriever found the labeled relevant paper for **23/23 answerable questions**. All 28 labeled fact snippets were checked for literal presence in the selected chunks; **23/28** appeared. Five snippets missed the exact wording check (q01, q02, q10, q12, q19), although some selected chunks carried the same fact in different words. This is an evidence-availability diagnostic, not a measure of answer correctness. Both unsupported questions still retrieved some passages, so the answer layer must decide when to abstain.

The earlier result file used a different cache fingerprint from the fresh run. We verified that both caches contain the same 289 chunk IDs, text, and metadata, and that the 25 questions select the same chunk ID order. The fresh run built a new cache because the fingerprint changed; the notebook now opens the fresh result and rebuilds an empty cache automatically.

### What went wrong in generated answers

| Problem | What we observed | Change made |
| --- | --- | --- |
| Missing citations | The interactive `llama3.2` answer gave the correct 92/454 figures without a citation. The fresh 25-question `llama3.2` run had citations and literal quotes in only 18/23 answerable responses. | `qwen2.5:7b` is now the local default. An unchecked draft is withheld and replaced with inspectable source matches. |
| Missed facts inside long passages | `llama3.2` declined the normalization and held-out-gain questions even though the selected passages contained the answers. | The Qwen comparison improved these answers. Comparison and “how much” questions now put short, query-ranked source windows first while keeping original passage IDs for checking. |
| Wrong comparison target | Both first-pass models emphasized submission counts for q08 instead of the paper's 0.226-versus-0.126 result. The first focused answer called the figures an “improvement” rather than average scores. | Focused source windows and a metric-label prompt rule now report the paper's average scores. |
| Cross-paper synthesis errors | The models sometimes declined or contradicted themselves on q21–q23 even though both labeled papers were retrieved. | “Which papers” questions now return a labeled, quoted paper-match list. A keyword gate declines the unsupported stock-price question. This is a search result, not a generated synthesis. |
| Quotes could come from the wrong passage | The old quote helper could cite a quote from passage [4] while the answer cited only [1][2] from the same paper. | The helper now attaches one literal quote from **each passage cited in the answer body**. The checker requires that exact passage match. |
| Numeric source check missed a wrong citation | The old check removed punctuation before looking for `74.9`; unrelated nearby digits in q11's cited passage happened to form that sequence. | Numeric values are now compared as complete values, tolerating PDF spacing such as `0 .126` without joining unrelated numbers. “How much” questions get focused excerpts; q11's correct 74.9% passage is then cited. |
| Notebook setup depended on earlier cells | Running the example loop in a fresh kernel raised `NameError` for `test_query`, and the saved-index cell used an older cache fingerprint. | The notebook's five-paper demo now has a self-contained setup and an editable example question. It builds the current index from the PDFs if needed. |

The first local Qwen run produced citations and at least one literal quote in **22/23** answerable responses, versus **18/23** for `llama3.2`; both models declined the two unsupported questions. Those old quote counts were only *per paper*. Under the stricter current rule that every cited **passage** needs its own quote, only 6/23 old `llama3.2` responses and 7/23 old Qwen responses pass all mechanical source checks. That is a change in the checking rule, so these figures are not a clean model-quality comparison. In the old runs, the checker also flagged four mixed answer-and-abstention outputs from `llama3.2` and one Qwen answer with a number absent from its cited passage. The more serious semantic errors needed manual review; a valid citation number alone did not catch them.

### Final answer review

The final run uses Ollama `qwen2.5:7b` (model digest and prompt hash are saved in the JSON), temperature 0 and seed 42, with the same five-paper retrieval settings. The summary and question-by-question review below were prepared after reading the final answers and the cited excerpts. This is one reviewer, using a small AI-drafted question set; it is not a blinded study or a KPMG acceptance test.

| Item | Result |
| --- | --- |
| Direct answers on single-paper questions | 20/20 |
| Direct answers passing mechanical source checks | 20/20 |
| Paper-list questions returning both labeled papers | 3/3 |
| Unsupported questions with correct abstention | 2/2 |
| Review against the fixed answer labels | 20/20 direct answers contained the expected facts; one reviewer checked the output and displayed excerpts, so this is a diagnostic review rather than independent adjudication. |

| Question | Content review | Note |
| --- | --- | --- |
| q01 | Matches label | Router queries when value of information exceeds cost. |
| q02 | Matches label | Distinguishes centralized Router from decentralized Bidder. |
| q03 | Matches label | Lists all three evaluation domains. |
| q04 | Matches label | Names the noisy-competitor limitation. |
| q05 | Matches label | Ten repositories and ten algorithm families. |
| q06 | Matches label | Four-hour agent and twelve-hour replay budgets. |
| q07 | Matches label | Gives the 0, 0.1, and 1.0 normalization anchors. |
| q08 | Matches label | Calls 0.226 and 0.126 average scores, not gains. |
| q09 | Matches label | Names objective and procedure models. |
| q10 | Matches label | Gives 0.974 grouping agreement. |
| q11 | Matches label | Gives 74.9% and cites the passage containing it. |
| q12 | Matches label | Gives the 30% relative held-out accuracy gain. |
| q13 | Matches label | Gives 92 commuters and 454 valid observations. |
| q14 | Matches label | Notes cycling sensitivity and the snowy transit increase. |
| q15 | Matches label | Gives 69.6% versus 69.9% five-class accuracy. |
| q16 | Matches label | Gives 71.5% vision-based accuracy. |
| q17 | Matches label | Describes patient-oriented report interpretation. |
| q18 | Matches label | Describes retrieval-based claim checks and weighted checklist coverage. |
| q19 | Matches label | Names MMedReport and subjective/objective evaluation dimensions. |
| q20 | Matches label | Reports clinician preference for G-CARL. |
| q21 | Both labeled papers listed | Computer-use and travel-survey papers; this is a source list. |
| q22 | Both labeled papers listed | AI4AI-Bench and Pandora papers; this is a source list. |
| q23 | Both labeled papers listed | Task-model and G-CARL papers; this is a source list. |
| q24 | Appropriate abstention | KPMG revenue is absent. |
| q25 | Appropriate abstention | NVIDIA stock price is absent. |

## Dataset 2: BEIR SciFact subset

This retrieval dataset comes from BEIR's official SciFact test split, sampled here to 20 claims and 500 title-plus-abstract articles, including every judged relevant article for those claims.

The branch rerun in [`beir_scifact_branch_confirmed.json`](beir_scifact_branch_confirmed.json) got the relevant article at rank one for **18/20** claims and in the top five for **20/20**. MRR@10 was **0.950**, and nDCG@10 was **0.963**. These match the prior tiny-subset result. The dataset is mostly scientific and biomedical, and the reduced article pool makes this an easier diagnostic than the full BEIR corpus. It does not test answer writing, citation quality, or KPMG usefulness.

## What still needs work

1. **Independent labels and broader data.** The five-paper questions were AI drafted. Ask teammates or KPMG reviewers to label new questions without seeing the system answers, and expand beyond five papers and a 500-article retrieval subset.
2. **Claim support beyond exact matching.** The current checker verifies passage IDs, literal quotes, and exact numeric values. It cannot prove that a cited passage entails the sentence or that every factual sentence has its own citation. A second reviewer or a separately validated claim-level evaluator is needed.
3. **Paper-search relevance.** The “which papers” path is deliberately an inspectable search list and uses a conservative keyword gate. It can miss relevant papers that use different vocabulary, and a lexical match alone is not proof of relevance.
4. **PDF text quality and page tracing.** Extracted text can join words and decimals (`average0.226 against0 .126`), and citations identify chunks rather than exact pages. Improve PDF normalization and page offsets before asking reviewers to rely on quotations at scale.
5. **Real use and business value.** The notebook handles one question at a time. It has no evaluated conversation memory, deployed answer service, or KPMG reviewer score for usefulness and trust. The business-translation helper is separate from this answer test.

To reproduce all commands and open the notebook, see [`evaluation/README.md`](../README.md).
