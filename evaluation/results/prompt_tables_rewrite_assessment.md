# Prompt, table and query-rewriting experiments

**Selective query rewriting is the most promising candidate, but none of these changes clears the existing adoption threshold.** It raises complete answers from 20 to 21 and adds no new major errors. The tighter prompt removes the existing major error but drops completeness to 19; adding table chunks drops completeness to 18. Keep the accepted Qwen + hybrid coverage configuration as the default. Preserve rewriting as an opt-in experiment for broader validation, and use table chunks selectively in a future test rather than enabling them globally.

| Configuration | Complete | Partial | Major error | Correct abstention | Mean answer words |
|---|---:|---:|---:|---:|---:|
| Current Qwen + hybrid | 20 | 2 | 1 | 2 | 101.6 |
| Focused prompt | 19 | 4 | 0 | 2 | 40.5 |
| Table-aware retrieval | 18 | 4 | 1 | 2 | 88.7 |
| Selective rewriting | 21 | 1 | 1 | 2 | 102.7 |

**Interpretation:** 23 questions are answerable and two intentionally unsupported. Complete requires the requested content without a material factual defect; citation placement is tracked separately. Paper IDs without recognizable names remain Partial under the established presentation criterion. These are assistant source reviews on a small development set, not independent human ratings or statistically significant estimates.

## What each experiment showed

1. **Tighter answer policy — mixed, not adopted.** The full run is shorter and avoids the clinician-preference count attribution error, but a comparison caveat changes stronger *systems* to stronger *submissions*, and a cross-paper answer becomes too vague about costs. A feedback-adjusted second policy still ignores some instructions and attributes non-expert comprehensibility ratings to clinicians. That candidate was stopped after four completed cases; the interrupted fifth response is not counted.
2. **Table-aware extraction/chunking — better extraction, worse overall answers, not adopted.** Visual review confirms that table headers, row labels, percentages and judge groups are recovered correctly for the inspected tables. The TMI accuracy answer now includes the correct baseline and improved values explicitly. However, new table chunks also alter ranking on non-table questions: the PMRI definition answer cites an unrelated results table and conflates task definition with training supervision; another cross-paper answer loses paper names and compute-budget detail. Clearer source formatting alone does not guarantee better selection or generation.
3. **Selective rewriting — modest positive signal, still experimental.** Eight short rewrites change four questions' retrieved contexts. The Router answer now covers ordering, stopping and final selection without explicitly describing specialist execution as the computation of reservation prices; it remains repetitive. The other three changed answers retain their previous grades. Rewrite generation takes 16.5 seconds in total (about 2.1 seconds per selected query) in this warm local run, excluding retrieval and answer generation; this is not a controlled latency benchmark.
4. **Remaining issues:** The accepted baseline's clinician-preference numerical attribution error remains in the table and rewrite variants because those inputs are unchanged. Paper-ID-only answers and misplaced citations also remain. None of these trials enables an LLM judge, corrective loop or HyDE.

**Recommended next decision:** validate selective rewriting on the 15 additional questions before making it the default. For output quality, a deterministic mapping from known cited paper IDs to their titles is a lower-risk way to improve business readability than adding more prompt instructions. For tables, first try routing only explicit metric/comparison questions to table chunks while preserving explanatory prose.

## Controls and limits

- Qwen 3.5 9B, temperature 0, seed 42, citation-only schema, thinking disabled, no repair, context 12,288 and output limit 1,800 throughout. Five retrieved passages maximum, fetch 60, per-paper cap 4 and reranker gap 8.
- Prompt experiment: all 25 answers were freshly generated on exactly the baseline hybrid evidence. Only the prompt policy changed. A second prompt variant was stopped after four completed regression cases; it is not counted as a full run.
- Table and rewriting experiments independently retain the accepted coverage policy. They are not stacked on the rejected focused prompt. A fresh control retrieval run reproduced all 25 original hybrid contexts byte-for-byte.
- Table experiment: eight confident numeric tables produce 21 additional chunks across two PDFs. Captions, header context, row labels and group labels are preserved. Unsupported layouts are skipped; original prose is retained. Three questions retrieve a table chunk, but eight contexts change because new corpus entries also affect hybrid rankings. Only those eight answers were regenerated.
- Rewriting: a fixed question-text rule selects broad mechanisms, comparisons and multi-paper questions. Eight rewrites produce four changed contexts. Original and rewritten hybrid candidates are fused, then reranked against the original question. Only real source passages go to the answer generator. Four changed answers are regenerated; unchanged answers are reused.
- Assembly verifies identical questions, grouped context, citation IDs, source lists and generation settings before reuse. The baseline engine hash was reproduced exactly after removing only the two added, unused experimental policy assignments; generation code for coverage is unchanged.
- Literal evidence-phrase coverage: baseline 25/28, tables 24/28, rewriting 25/28. These are wording checks, not correctness scores.
- Acceptance threshold remains +2 complete answers or removal of two major errors, without new major errors or unsupported answers. No automatic production promotion is based on shorter output or more matching phrases alone.
- The 15-question holdout was not run here: this task tested the requested items 1, 2 and 4. No HyDE or corrective-RAG calls were added.
- 150 tests passed, including original-query reranking, table row/header/group association, and strict checks for reusing prior outputs.

## Source-table example

The layout-aware extractor stores explicit metric/value pairs, for example:

```text
Workflow summary: Cov.=54.07; Exec.=59.35; Safe.=91.74; Align.=66.18; Acc.=14.29
Ours: Cov.=54.95; Exec.=67.65; Safe.=90.57; Align.=67.99; Acc.=18.57
```

The chunk repeats the caption defining Acc. as held-out task accuracy and the values as percentages. This extraction improvement did not produce a net answer-quality gain when added indiscriminately to retrieval.

## Question-by-question outcomes

| Question | Current | Focused | Tables | Rewriting |
|---|---|---|---|---|
| q01 | Partial | Partial | Partial | Complete |
| q02 | Complete | Complete | Complete | Complete |
| q03 | Complete | Complete | Complete | Complete |
| q04 | Complete | Complete | Complete | Complete |
| q05 | Complete | Complete | Complete | Complete |
| q06 | Complete | Complete | Complete | Complete |
| q07 | Complete | Complete | Complete | Complete |
| q08 | Complete | Partial | Complete | Complete |
| q09 | Complete | Complete | Complete | Complete |
| q10 | Complete | Complete | Complete | Complete |
| q11 | Complete | Complete | Complete | Complete |
| q12 | Complete | Complete | Complete | Complete |
| q13 | Complete | Complete | Complete | Complete |
| q14 | Complete | Complete | Complete | Complete |
| q15 | Complete | Complete | Complete | Complete |
| q16 | Complete | Complete | Complete | Complete |
| q17 | Complete | Complete | Partial | Complete |
| q18 | Complete | Complete | Complete | Complete |
| q19 | Complete | Complete | Complete | Complete |
| q20 | Major issue | Complete | Major issue | Major issue |
| q21 | Partial | Partial | Partial | Partial |
| q22 | Complete | Partial | Partial | Complete |
| q23 | Complete | Complete | Complete | Complete |
| q24 | Correct abstention | Correct abstention | Correct abstention | Correct abstention |
| q25 | Correct abstention | Correct abstention | Correct abstention | Correct abstention |

## Explanations and raw outputs

The following details preserve model outputs; no generated answers were edited to improve their grades.

### Focused prompt

<details><summary>q01 — Partial: How does Pandora's Router decide when an expensive specialist estimate is worth paying for?</summary>

Still conflates running a specialist with calculating reservation prices, and omits explicit ordering and final selection.

- Pandora's Router decides when an expensive specialist estimate is worth paying for by computing reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate. [2]
- The system computes reservation prices by running the specialist for a few reasoning tokens and checking if it is on the right track. [2]
- Pandora's Router stops querying expensive estimates when no remaining query is worth its cost. [2]

Citation concern: The first claim cites [2][4] rather than the explicit mechanism in [1].

</details>

<details><summary>q02 — Complete: What is the difference between Pandora's Router and Pandora's Bidder?</summary>

Explains centralized Router versus decentralized Bidder and global welfare versus local surplus, without turning high costs into automatic refusal.

- Pandora's Router queries the costly specialist only when the value of information exceeds the cost, interpolating between baselines that either always query or never query. [2][3]
- Pandora's Bidder operates in a decentralized setting where specialists face posted prices and must decide whether to invest in more accurate self-assessments before claiming queries. [3]
- In Pandora's Bidder, maximizing local surplus does not always lead to better overall allocative efficiency because strategic bidders may capture higher surplus at the cost of global welfare. [3]
- The tension between local surplus maximization and global allocative efficiency is absent in Pandora's Router, where the router internalizes all costs and optimizes global welfare directly. [3]
- Pandora's Bidder corresponds to a single stage of an ascending-price mechanism with costly preference elicitation, isolating core components of decentralized prompt allocation under private value estimation with profit incentives. [4]

</details>

<details><summary>q03 — Complete: In which three domains was the costly-value-estimation routing policy evaluated?</summary>

Names all three evaluation domains.

- The costly-value-estimation routing policy was evaluated across three domains: a multi-LLM routing benchmark (EmbedLLM), retrieval-augmented specialists for factoid QA, and inference-time computation for mathematical reasoning. [2][3]

</details>

<details><summary>q04 — Complete: What limitation appears when competing specialists' estimates are noisy?</summary>

Correctly states that noisy competing estimates can benefit one specialist at others' expense.

- When competing estimates are noisy, value-of-information reasoning can increase the strategic specialist's utility at the expense of others. [2]

Citation concern: The statement is supported by passage [1], but cites [2].

</details>

<details><summary>q05 — Complete: How many frozen repositories and training algorithm families are in AI4AI-Bench?</summary>

Correct ten repositories and ten algorithm families.

- AI4AI-Bench contains ten frozen research repositories. [2][3]
- These ten repositories cover ten distinct families of training algorithms. [3]

</details>

<details><summary>q06 — Complete: What is the AI4AI-Bench time budget for an agent and for the replay?</summary>

Correct four-hour agent budget on one B300 and up-to-twelve-hour replay.

- The agent has a time budget of 4 hours on one B300 GPU to rewrite the training algorithm. [2][4]
- The replay (rerun) has a time budget of up to 12 hours. [2][4]

</details>

<details><summary>q07 — Complete: How are the incommensurable AI4AI-Bench task metrics normalized?</summary>

Correct 0, 0.1 and 1.0 anchors, but the cited passage is wrong.

- The incommensurable AI4AI-Bench task metrics are normalized such that 0 represents an uninformative model, 0.1 represents the algorithm the repository ships, and 1.0 represents the task optimum. [2]

Citation concern: The only answer claim cites unrelated passage [2] rather than the scale definition in [4].

</details>

<details><summary>q08 — Partial: How do submissions that change the learning algorithm compare with those that do not?</summary>

Correct 0.226 versus 0.126, but changes the caveat from stronger systems to stronger submissions. This preserves a factual attribution imprecision.

- Submissions that change the learning algorithm achieve a mean score of 0.226, while those that do not change it achieve a mean score of 0.126. [2][3]
- The algorithmic layer is where the distance to a better algorithm is closed, and most submissions never go there. [3]
- Submissions that reach the learning procedure more often are the stronger ones to begin with. [2][3]

Citation concern: No numeric warning, but semantic caveat attribution is wrong.

</details>

<details><summary>q09 — Complete: What two kinds of task structure does TMI recover from computer-use traces?</summary>

Correct objective hierarchy and execution-control-flow model.

- TMI recovers task models that pair a hierarchical objective model of recursive goal decomposition with a procedure model of the control flow that organized the execution. [2][3]

</details>

<details><summary>q10 — Complete: How well does task model induction group interleaved tasks?</summary>

Correct 0.974 grouping agreement.

- The method recovers interleaved tasks with 0.974 agreement against ground-truth task groupings. [2]

</details>

<details><summary>q11 — Complete: How much of observed execution does TMI reconstruct?</summary>

Correct 74.9% of observed execution steps.

- TMI reconstructs 74.9% of the observed execution steps. [2][4]

</details>

<details><summary>q12 — Complete: What was the held-out task accuracy gain from skills derived from TMI?</summary>

Correct 30.0% held-out accuracy improvement, without unrelated table statistics.

- Skills derived from TMI's task models improve held-out task accuracy by 30.0% over the strongest baseline. [2][5]

</details>

<details><summary>q13 — Complete: How many commuters and respondent-scenario observations did the weather travel survey collect?</summary>

Correct 92 commuters and 454 respondent-scenario observations.

- The weather travel survey collected mode choices from 92 student commuters. [2][3]
- The survey yielded 454 respondent–scenario observations across five predefined weather scenarios. [1][3]

</details>

<details><summary>q14 — Complete: Which travel modes responded most clearly to adverse weather and snow?</summary>

Correct cycling sensitivity and increased transit use under snow.

- Cycling was particularly sensitive to adverse weather, while public transit use increased substantially under the Snowy scenario. [2][4]

</details>

<details><summary>q15 — Complete: How did random forest and the best text-only zero-shot LLM compare on five-class travel prediction?</summary>

Correct 69.6% versus 69.9% without asserting statistical significance.

- Random forest achieved the highest trained-model accuracy of 69.6% five-class accuracy, while the best text-only zero-shot LLM produced a comparable point estimate of 69.9% without task-specific fitting to the survey records. [2][3]

</details>

<details><summary>q16 — Complete: What was the best vision-based travel mode prediction accuracy?</summary>

Correct best observed vision accuracy of 71.5%.

- The best vision-based configuration reached a five-class accuracy of 71.5%. [2][3]

</details>

<details><summary>q17 — Complete: What is the patient-oriented medical report interpretation task introduced with G-CARL?</summary>

Correct patient-facing multimodal interpretation using the user query and dialogue history.

- Patient-oriented Medical Report Interpretation (PMRI) is a novel open-ended multimodal generation task that requires models to explain medical reports in accurate and accessible language based on a user's query and dialogue history. [2][3]
- PMRI must align professional medical knowledge with patient-centered communication by transforming report evidence into accessible explanations, addressing user-specific concerns, and offering clinically cautious guidance. [4]
- Unlike short, deterministic outputs of medical VQA or conventional report generation, PMRI produces long-form, patient-facing explanations grounded in multimodal reports and extended patient-doctor dialogue. [4]

</details>

<details><summary>q18 — Complete: How does G-CARL supervise factuality and response coverage?</summary>

Explains multi-source verification and weighted checklists in two distinct claims.

- G-CARL supervises factuality through a retrieval-grounded branch that verifies report-grounded medical claims against evidence retrieved from a multi-source medical datastore. [2][4]
- G-CARL supervises response coverage through a case-specific checklist branch that constructs a weighted checklist via MLLM generation followed by clinician-guided refinement to evaluate checklist coverage of the generated response. [2][4]

</details>

<details><summary>q19 — Complete: What benchmark and evaluation dimensions accompany G-CARL?</summary>

Names MMedReport and all three dimensions; extra factual evaluation details are supported.

- G-CARL is evaluated on the MMedReport benchmark, which contains 2,450 instances of real-world multimodal patient-oriented medical report interpretation tasks. [2][4]
- The evaluation protocol for G-CARL includes three clinician-defined subjective dimensions: Medical Accuracy, Demand Satisfaction, and Expression Quality. [1]
- In addition to subjective evaluation, G-CARL is assessed using an external benchmark called CMB, which evaluates medical QA accuracy and the professionalism of open-ended clinical interpretation under an LLM-as-a-judge protocol. [1]
- Objective evaluation metrics are also reported alongside holistic assessment for G-CARL. [1]

Citation concern: The 2,450-instance claim cites [2][4] instead of supporting [1]. The subjective/objective protocol claim cites [4] rather than [1].

</details>

<details><summary>q20 — Complete: What did clinician pairwise preferences find about G-CARL?</summary>

Correct clinician preference direction and dimensions; omits the earlier unsupported count-to-baseline mapping.

- Clinician pairwise preferences found that G-CARL is consistently preferred over both SFT and MLLM-as-a-Judge, particularly in medical accuracy and demand satisfaction. [2][1]

</details>

<details><summary>q21 — Partial: Which papers address auditable AI workflows derived from user activity or survey responses?</summary>

Identifies the correct two paper IDs and relevance, but still omits recognizable paper titles.

- Paper ID 2608.20320 addresses auditable AI workflows derived from survey responses by defining agents as software components that produce structured and auditable outputs. [2][3]
- Paper ID 2608.20319 addresses auditable AI workflows derived from user activity by introducing TASKMODELINDUCTION(TMI) to derive symbolic, auditable, and reusable models of how everyday work is done from naturalistic computer-use traces. [1]

Citation concern: Paper-ID numeric warnings are metadata false positives, not fabricated result numbers.

</details>

<details><summary>q22 — Partial: Which papers evaluate AI agents or model specialists using benchmark tasks and costs?</summary>

Names both papers but largely repeats the question, without explaining the agent compute/time budget or specialist estimation-cost trade-off.

- Pandora's AI Model Routing Box evaluates model specialists using benchmark tasks and costs. [2][5]
- AI4AI-Bench evaluates AI agents using benchmark tasks. [3]

</details>

<details><summary>q23 — Complete: Which papers discuss evidence-grounded explanations and auditable task models?</summary>

Names TMI and G-CARL and correctly assigns their distinct relevance.

- The paper Inducing Task Models from Computer-Use Traces discusses auditable task models. [2][4]
- The paper G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation discusses evidence-grounded explanations. [3]

</details>

<details><summary>q24 — Correct abstention: What is KPMG's 2026 revenue forecast?</summary>

Correctly declines to invent a KPMG forecast.

The provided papers do not address this question.

</details>

<details><summary>q25 — Correct abstention: Which of these papers reports the stock price of NVIDIA on October 14, 2026?</summary>

Correctly declines to invent a NVIDIA stock price.

The provided papers do not address this question.

</details>

### Table-aware retrieval

<details><summary>q09 — Complete: What two kinds of task structure does TMI recover from computer-use traces?</summary>

Correct objective hierarchy and procedure/control-flow structure; repeated definitions remain.

- TMI recovers two complementary task structures: an objective model that hierarchically decomposes the task's goal into subobjectives, and a procedure model that composes control-flow operators to specify how execution is organized through sequencing and iteration. [2][4]
- The objective model represents a hierarchical decomposition of the task's objective into subobjectives that the user pursues. [4]
- The procedure model represents a trace-grounded composition of control-flow operators that specify how the execution of the task is organized through sequencing and iteration. [4]
- The final task model is structured as a tree where every node pairs an objective with a control-flow operator over its children. [4]

</details>

<details><summary>q12 — Complete: What was the held-out task accuracy gain from skills derived from TMI?</summary>

Correct 30% relative improvement and explicit 14.29% to 18.57% comparison. The cleaner table is retrieved, but the baseline already answered this correctly.

- Skills derived from TMI's task models improve held-out task accuracy by 30.0% over the strongest baseline. [2][5]
- The held-out accuracy improved from 14.29% for the strongest baseline (Workflow summary) to 18.57% for TMI, representing a 30% relative accuracy gain. [1][2]

</details>

<details><summary>q17 — Partial: What is the patient-oriented medical report interpretation task introduced with G-CARL?</summary>

Correct PMRI definition and user/dialogue context, but an extra claim assigns the framework's structured reward supervision to the task itself.

- The patient-oriented medical report interpretation task is defined as an open-ended multimodal generation task that requires models to explain medical reports in accurate and accessible language based on a user's query and dialogue history. [2]
- This task requires both evidence-grounded medical factuality and context-dependent patient communication, which existing medical vision-language tasks do not adequately capture. [2]
- The task involves two objectives that differ fundamentally in their verifiability but remain tightly coupled, making them difficult to optimize jointly under conventional supervised fine-tuning and holistic reinforcement learning paradigms. [2]
- The task aims to provide structured supervision for factuality, user-demand satisfaction, and expression quality without constraining response diversity. [2]

Citation concern: Every claim cites [2], which is a CMB results table. The actual task definition is in [4].

</details>

<details><summary>q18 — Complete: How does G-CARL supervise factuality and response coverage?</summary>

Correct multi-source claim verification and weighted checklist coverage in two clear claims.

- G-CARL supervises factuality by verifying report-grounded medical claims against evidence retrieved from a multi-source medical datastore to produce a factuality reward. [2][4]
- G-CARL supervises response coverage by constructing a case-specific weighted checklist through MLLM generation followed by clinician refinement to produce a checklist reward. [2][4]

</details>

<details><summary>q19 — Complete: What benchmark and evaluation dimensions accompany G-CARL?</summary>

Includes MMedReport, CMB and the three requested evaluation dimensions. Extra study details are supported, though it leads with the secondary benchmark.

- G-CARL is evaluated on the CMB benchmark, which assesses both medical QA accuracy and the professionalism of open-ended clinical interpretation under an LLM-as-a-judge protocol. [2][3]
- The evaluation dimensions for PMRI responses include Medical Accuracy, Demand Satisfaction, and Expression Quality, each scored according to a clinician-authored rubric ranging from -2 to 3. [1]
- In addition to the subjective dimensions, G-CARL also undergoes objective evaluation alongside holistic assessment on the MMedReport benchmark. [1]
- Human preference evaluation involves three professional clinicians comparing anonymized responses across the three evaluation dimensions and overall preference, with majority voting used for the final decision. [3]
- A separate group of 50 participants without medical training evaluates the comprehensibility of the generated interpretations to ensure patient understandability. [3]

Citation concern: The CMB protocol claim cites [2][3], while the full protocol is described in [1].

</details>

<details><summary>q21 — Partial: Which papers address auditable AI workflows derived from user activity or survey responses?</summary>

Correct two paper IDs and relevance, but still omits recognizable titles.

- Paper ID 2608.20320 addresses an auditable AI workflow derived from survey responses by defining agents as goal-directed, researcher-supervised software components that produce structured and auditable outputs. [2][3]
- Paper ID 2608.20319 addresses an auditable AI workflow derived from user activity by introducing TASKMODELINDUCTION (TMI), which derives symbolic, auditable, and reusable models of how everyday work is done from naturalistic computer-use traces. [1]

Citation concern: Paper-ID warnings are metadata false positives.

</details>

<details><summary>q22 — Partial: Which papers evaluate AI agents or model specialists using benchmark tasks and costs?</summary>

Gives paper IDs instead of titles and does not explain the fixed compute/time budget for the agent benchmark; specialist estimation costs are described.

- Paper ID 2608.20318 evaluates AI agents using benchmark tasks that measure their ability to design training algorithms for recursive self-improvement, where each task involves rewriting a training algorithm within a frozen repository and scoring the rerun against an original baseline. [2][4]
- Paper ID 2608.20316 evaluates model specialists by routing queries to them based on estimated value, where the cost of estimation varies between cheap noisy predictors and expensive accurate ones, and the system trades off these costs to achieve allocative performance. [1][3][5]

Citation concern: Paper-ID numeric warnings are metadata false positives.

</details>

<details><summary>q23 — Complete: Which papers discuss evidence-grounded explanations and auditable task models?</summary>

Identifies both TMI and G-CARL and their distinct relevance, but repeats TMI across five claims.

- The paper titled Inducing Task Models from Computer-Use Traces discusses auditable task models derived from naturalistic computer-use traces. [2][1]
- The paper titled Inducing Task Models from Computer-Use Traces discusses inducing symbolic, auditable, and reusable models of how everyday work is done. [2][1]
- The paper titled Inducing Task Models from Computer-Use Traces discusses inducing task models that are auditable and reusable. [2][1]
- The paper titled Inducing Task Models from Computer-Use Traces discusses inducing task models that are symbolic and auditable. [2][1]
- The paper titled Inducing Task Models from Computer-Use Traces discusses inducing task models that are reusable. [2][1]
- The paper titled G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation discusses evidence-grounded explanations. [3]
- The paper titled G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation discusses evidence-grounded medical factuality. [4]

</details>

### Selective rewriting

<details><summary>q01 — Complete: How does Pandora's Router decide when an expensive specialist estimate is worth paying for?</summary>

Now covers cheap estimates, reservation-price ordering, stopping and final selection, and describes reservation prices as deciding whether to run more reasoning rather than being computed by running it. Still ten repetitive claims and unrequested Bidder detail.

- Pandora's Router decides that an expensive specialist estimate is worth paying for by computing reservation prices that quantify the expected value-of-information for querying a more accurate value estimate, minus total estimation cost. [2][4]
- The system stops querying expensive estimates when no remaining query is worth its cost, effectively choosing the maximizer of the observed value estimate. [1]
- The mechanism involves specialists generating cheap, noisy value estimates first, after which the system computes reservation prices to decide whether to run a specialist for additional reasoning tokens to check if it is on the right track. [1]
- The decision rule balances cheap screening and costly reasoning by deciding which expensive estimates are worth computing based on the cost-adjusted reward, which may combine graded output quality with production costs such as inference cost or API fees. [1]
- Under a Gaussian signal model, the reservation-price-based policy has a closed form that is straightforward to compute, allowing the system to efficiently trade off expensive and cheap estimates. [4]
- The process follows a sequence where a concrete prompt is received, multiple specialists generate initial estimates, reservation prices are computed for the next stage of estimation, and then the system decides whether to proceed with expensive estimates. [1]
- The centralized policy inspects specialists in reservation price order, stopping when no remaining query is worth its cost, while the decentralized policy selects the high bidder in an auction where each specialist refines its own value estimate only when the market price makes inspection worthwhile. [1]
- Both Pandora's Router and Pandora's Bidder are able to gracefully trade-off expensive and cheap estimates to achieve strong allocative performance relative to baselines across a range of estimation costs. [4]
- The unified principle supports allocation by centralized routing and decentralized auctions, applying the same logic of balancing cheap screening and costly reasoning for routing. [1]
- The system computes reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate, such as by running the specialist for a few reasoning tokens and checking if it is on the right track. [1]

Citation concern: The opening mechanism claim cites [2][4] rather than the explicit process in [1].

</details>

<details><summary>q21 — Partial: Which papers address auditable AI workflows derived from user activity or survey responses?</summary>

Correct papers and relevance, but still identifies them only by numeric paper ID.

- Paper ID 2608.20320 addresses auditable AI workflows derived from survey responses by defining agents as software components that produce structured and auditable outputs while maintaining researcher control over survey constructs and data processing. [2][4]
- Paper ID 2608.20319 addresses auditable AI workflows derived from user activity by introducing TASKMODELINDUCTION (TMI), which derives symbolic, auditable, and reusable models of how everyday work is done from naturalistic computer-use traces. [1]

Citation concern: Paper-ID warnings are metadata false positives.

</details>

<details><summary>q22 — Complete: Which papers evaluate AI agents or model specialists using benchmark tasks and costs?</summary>

Names both papers and explains specialist estimation costs and the benchmark agent/replay compute budgets.

- Pandora's AI Model Routing Box evaluates model specialists using benchmark tasks and costs by formalizing model routing with costly value estimation as an instance of Pandora's Box, where cheap estimators are fast but noisy while accurate estimators are expensive, and experiments across three domains show that the proposed policies trade off expensive and cheap estimates to achieve strong allocative performance relative to baselines. [2][5]
- AI4AI-Bench evaluates AI agents using benchmark tasks and costs by presenting 10 frozen research repositories spanning 10 training algorithm families, where an agent has 4 hours on one B300 to rewrite the training algorithm, its code is then rerun from scratch for up to 12 hours and scored by a fixed evaluator hidden from the agent against the repository's original algorithm under the same procedure. [3][4]

</details>

<details><summary>q23 — Complete: Which papers discuss evidence-grounded explanations and auditable task models?</summary>

Names both papers and correctly distinguishes auditable task models from evidence-grounded medical explanations.

- The paper Inducing Task Models from Computer-Use Traces discusses auditable task models derived from naturalistic computer-use traces. [2][1]
- The paper G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation discusses evidence-grounded explanations for medical reports. [3][4]

</details>

