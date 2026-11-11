# Passage grouping and ordering — assessment

**Conclusion:** mixed results, not a reliable overall upgrade. Grouping and selection order improve paper coverage, but the combined version introduces a wrong metric comparison and an incorrect extra detail. Keep these changes experimental. The next bounded test should evaluate grouping alone more broadly before adopting it.

**Scope:** 31 new generations: grouping-only and ordering-only on q08/q21/q23 (six calls), then both together on all 25 questions. Compared with the previous 25 Llama 3.1 8B answers. Model weights, prompt, generation options and passage text were verified unchanged. No new retrieval or LLM judge. Original citation IDs are preserved; the ordering experiment reconstructs reserved-paper selection from saved reranker scores. Live retrieval assigns IDs after ordering, so this is a controlled presentation test, not a fresh end-to-end retrieval run.

**Review basis:** assistant assessment against saved passages, not an independent human rating. Complete means the core factual answer is supported; citation/formatting flaws are reported separately. Partial includes missing required content or a correct core answer with a material incorrect extra detail. Major issue includes a misleading central comparison or unanswered central question. Small single-run tests do not establish a stable accuracy rate.

| Result | Previous | Grouping + ordering |
| --- | ---: | ---: |
| Complete | 17 | 18 |
| Partial | 4 | 3 |
| Major issue | 2 | 2 |
| Correct abstention | 2 | 2 |

## What changed

- **Improved:** q21 no longer falsely refuses; q18 now explains multi-source retrieval and checklist coverage. q03 gives a citation for each domain.
- **Still wrong:** q08 omits **0.226 versus 0.126**, even with the direct score passage first. Moving evidence earlier was insufficient.
- **New regression:** q10 compares **0.974 grouping agreement** with **30.3% execution reconstruction**. The latter should be compared with 74.9%, not 0.974.
- **Mixed:** q23 now covers both papers but adds an incorrect claim about selection operators, despite the source explicitly excluding selection. It is also more verbose.
- **Preserved:** both genuinely unsupported questions are declined. Citation presence still does not establish factual correctness.

## Three-question isolation test

| Variant | q08: performance comparison | q21: auditable workflows | q23: explanations and task models |
| --- | --- | --- | --- |
| Previous | Missing scores | False refusal | Omits G-CARL |
| Grouping only | Missing scores | Both papers covered | Both papers covered; no operator error |
| Ordering only | Missing scores | Both papers covered | Both papers covered; no operator error |
| Both | Missing scores | Both papers covered | Both papers covered, but adds operator error |

Grouping-only and ordering-only were tested on three selected failures, not all 25; neither can yet be declared the best general configuration. Grouping can itself change order by making a paper’s passages adjacent. No extra multi-paper prompt rule was added, keeping this test focused on presentation.

## Implementation and validation

- Moved the notebook’s standalone `format_context` into `ResearchRetriever`; the notebook call now resolves correctly. Previously the class method rejected `group_by_paper`, and the standalone function referenced an unimported `RetrievedChunk` annotation.
- Restored the accidentally replaced `format_answer` helper.
- Added optional grouping while preserving original citation IDs and the legacy default format used to validate frozen snapshots.
- Added `--group-by-paper` and `--selection-order` to the answer runner, saved exact generation context, and fingerprinted both switches to prevent incompatible resumes.
- 132 offline tests passed, including notebook wiring, grouping/citation identity, unknown-paper separation, selection ordering and resume protection. The notebook keeps the user’s grouping and `order_by_vector=False` experiment; the default generator is still llama3.2, so request llama3.1:8b explicitly.

- `answers_context_grouped.json`: 3 calls, 48.6s recorded generation time.
- `answers_context_ordered.json`: 3 calls, 45.5s recorded generation time.
- `answers_context_both_full.json`: 25 calls, 257.6s recorded generation time.

Timing is descriptive, not a controlled speed benchmark; warmth and answer length differ.

## Per-question comparison

| ID | Before | After | Explanation |
| --- | --- | --- | --- |
| q01 | Partial | Partial | Still omits inspection in reservation-price order. Value of information, stopping and selection are supported. |
| q02 | Partial | Partial | Explains centralized inspection versus decentralized auction, but still omits the global-welfare objective and now also omits the local-surplus trade-off. Citations appear only at the end. |
| q03 | Complete | Complete | All three domains are correct; each list item now has its own citation. |
| q04 | Complete | Complete | Correctly explains increased strategic utility at other specialists’ expense when competing estimates are noisy. |
| q05 | Complete | Complete | Correctly reports ten repositories and ten algorithm families. |
| q06 | Complete | Complete | Correct four-hour agent budget on one B300 and twelve-hour replay budget. |
| q07 | Complete | Complete | Correctly associates 0, 0.1 and 1.0 with the uninformative model, shipped algorithm and optimum. |
| q08 | Major issue | Major issue | Still omits the performance scores 0.226 versus 0.126, even though source [2] is presented first. Submission shares and types of changes do not cover the main performance comparison. The prior non-causal caveat is also absent. |
| q09 | Complete | Complete | Correctly explains hierarchical objective models and procedure/control-flow models. Citation is at paragraph end. |
| q10 | Complete | Major issue | New metric-mixing error: 0.974 is task-grouping agreement, but the answer compares it with 30.3%, which source [2] assigns to execution-step reconstruction. The correct reconstruction comparison is 74.9% versus 30.3%. Also retains the paper’s first-person “Our method”. |
| q11 | Complete | Complete | Correct 74.9% reconstruction result; a metric label would make the bare number more self-contained. |
| q12 | Complete | Complete | Correctly states a 30% relative gain from 14.29 to 18.57, rather than a percentage-point increase. |
| q13 | Complete | Complete | Correct 92 student commuters and 454 respondent-scenario observations. |
| q14 | Complete | Complete | Correct adverse-weather sensitivity for cycling and increased transit use under snow. |
| q15 | Complete | Complete | Correctly associates 69.6% with random forest and 69.9% with text-only zero-shot LLM; source [4] contains both. |
| q16 | Complete | Complete | Correct 71.5% result, though the bare number would benefit from a metric label. |
| q17 | Complete | Complete | Correct patient-oriented explanation task, grounded in report images, user query and dialogue history. |
| q18 | Partial | Complete | Now covers multi-source medical retrieval and claim verification plus the weighted case-specific checklist, all supported by source [4]. This fills the earlier retrieval omission. |
| q19 | Complete | Complete | Correct MMedReport benchmark and all three evaluation dimensions. Extra CMB and precision/recall details are supported. Citations remain bunched at the end instead of following each factual sentence. |
| q20 | Complete | Complete | Correct clinician preference finding and supported margins 136:85 and 106:64. |
| q21 | Major issue | Complete | False refusal is resolved: identifies both the survey workflow and TMI, explains their different inputs, and cites both papers. Citation placement is still mostly at bullet ends. |
| q22 | Complete | Complete | Correctly identifies Pandora routing and AI4AI-Bench, their evaluation domains and budgets/costs. More detailed than the earlier answer; citations remain at paragraph ends. |
| q23 | Partial | Partial | Now covers both G-CARL and TMI, but adds a false detail: says the three observable operators are sequence, selection and iteration. Source [5] explicitly excludes selection from the output and specifies SEQ, FOR and WHILE. The answer is also long and exposes paper IDs instead of readable titles. |
| q24 | Correct abstention | Correct abstention | Correctly declines the unsupported KPMG revenue forecast. |
| q25 | Correct abstention | Correct abstention | Correctly declines the unsupported NVIDIA stock price. |

## Answers and source excerpts

Excerpts below are literal saved-source text, shortened to at most 300 characters. They are spot checks; the offline worksheet contains full passages.

<details><summary>q01 — How does Pandora's Router decide when an expensive specialist estimate is worth paying for?</summary>

**New answer:**

Pandora's Router computes reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate 𝑔𝑚(𝑥), e.g., by running the specialist for a few reasoning tokens and checking if it is on the right track [3]. The system stops when no remaining query is worth its cost [1]. The maximizer of the observed 𝑔𝑚 is chosen [1].

**Assessment:** Still omits inspection in reservation-price order. Value of information, stopping and selection are supported.

**Source [3] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> We now extend Pandora’s Router to a decentralized setting in which the specialists control their own value estimates, and use them to participate in a marketplace. Pandora’s Router assumes that a single decision-maker controls which boxes to open and which specialist to select. In many settings, how…

**Source [1] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value e…

</details>

<details><summary>q02 — What is the difference between Pandora's Router and Pandora's Bidder?</summary>

**New answer:**

Pandora's Router is a centralized policy that inspects specialists in reservation price order, stopping when no remaining query is worth its cost, and chooses the maximizer of the observed value estimate. In contrast, Pandora's Bidder is a decentralized policy that selects the high bidder in an auction, where each specialist refines its own value estimate only when the market price makes inspection worthwhile. [1][2][3]

**Assessment:** Explains centralized inspection versus decentralized auction, but still omits the global-welfare objective and now also omits the local-surplus trade-off. Citations appear only at the end.

**Source [1] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value e…

**Source [2] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> and all methods except𝑓-only (which never queries𝑔) perform similarly. As𝑐𝑔 increases, the𝑔-always baseline continues to make a fixed number of queries regardless of cost, while𝑓-only still never queries at all. Pandora’s Router interpolates between these extremes, querying𝑔 only when the value of i…

</details>

<details><summary>q03 — In which three domains was the costly-value-estimation routing policy evaluated?</summary>

**New answer:**

The three domains where the costly-value-estimation routing policy was evaluated are: 
1. a multi-LLM routing benchmark (EmbedLLM) [3]
2. retrieval-augmented specialists for factoid QA [3]
3. inference-time computation for mathematical reasoning [3]

**Assessment:** All three domains are correct; each list item now has its own citation.

**Source [3] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Bidder: each specialist faces a posted price—the current best competing offer—and must decide whether to invest in a more accurate self-assessment before claiming the query. This corresponds to a single stage of the ascending-price mechanism with costly preference elicitation studied by Parkes (2005…

</details>

<details><summary>q04 — What limitation appears when competing specialists' estimates are noisy?</summary>

**New answer:**

When competing estimates are noisy, value-of-information reasoning can increase the strategic specialist's utility at the expense of others. [1]

**Assessment:** Correctly explains increased strategic utility at other specialists’ expense when competing estimates are noisy.

**Source [1] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> benchmark, retrieval-augmented specialists, and LLMs with variable inference-time reasoning—show that Pandora’s Router matches the routing quality of exhaustive estimation, while querying the expensive estimator far less often. In the decentralized setting, value-of-information reasoning improves al…

</details>

<details><summary>q05 — How many frozen repositories and training algorithm families are in AI4AI-Bench?</summary>

**New answer:**

10 frozen research repositories, each covering a distinct family of training algorithm, spanning 10 training algorithm families. [2]

**Assessment:** Correctly reports ten repositories and ten algorithm families.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> The suite is ten frozen research repositories, listed in Table 1 and chosen so that between them they cover ten families of training algorithm rather than ten instances of one: supervised fine-tuning, multi-turn agentic RL, on-policy distillation, Bradley–Terry reward modeling, preference optimizati…

</details>

<details><summary>q06 — What is the AI4AI-Bench time budget for an agent and for the replay?</summary>

**New answer:**

The AI4AI-Bench time budget for an agent is 4 hours on one B300 GPU [2]. The time budget for replay is 12 hours [2].

**Assessment:** Correct four-hour agent budget on one B300 and twelve-hour replay budget.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> Each task presents an agent with a research repository, a base model to start from, and an inexpensive proxy metric that can be evaluated freely during development 2.2. The agent is given 4 hours on one B300 GPU and a single objective: improve the training algorithm implemented in the repository. It…

</details>

<details><summary>q07 — How are the incommensurable AI4AI-Bench task metrics normalized?</summary>

**New answer:**

The AI4AI-Bench task metrics are normalized to a common scale where 0 is an uninformative model, 0.1 is the algorithm the repository ships, and 1.0 is the task optimum. [2]

**Assessment:** Correctly associates 0, 0.1 and 1.0 with the uninformative model, shipped algorithm and optimum.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> incommensurable, every task is mapped onto one scale on which0is an uninformative model,0 .1is the algorithm the repository ships, and1.0 is the task optimum. Across 29 configurations of 6 systems on all 10 tasks the mean score is0.166, and the best system reaches0.250: even the strongest closes und…

</details>

<details><summary>q08 — How do submissions that change the learning algorithm compare with those that do not?</summary>

**New answer:**

Submissions that change the learning algorithm (46.4% of 263 submissions) are less common than those that do not (53.6% of 263 submissions) [3]. The former group includes changes to the loss it optimizes, supervision it learns from, update rule itself, and data it trains on [1]. In contrast, submissions that do not change the learning algorithm instead modify how the run goes, such as training time, hyperparameters, and checkpointing [1].

**Assessment:** Still omits the performance scores 0.226 versus 0.126, even though source [2] is presented first. Submission shares and types of changes do not cover the main performance comparison. The prior non-causal caveat is also absent.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> …reach it — the objective, the supervision signal, the learning rule, the data — average0.226 against0 .126for the rest: the algorithmic layer is where the distance gets closed, and most submissions never go there. More reasoning effort moves agents towards it, taking that share from8%to64%and the me…

</details>

<details><summary>q09 — What two kinds of task structure does TMI recover from computer-use traces?</summary>

**New answer:**

TMI recovers two kinds of task structure: objective models and procedure models. Objective models are hierarchical decompositions of the objective of a task into subobjectives, while procedure models are trace-grounded compositions of control-flow operators specifying how the execution of a task is organized. [3]

**Assessment:** Correctly explains hierarchical objective models and procedure/control-flow models. Citation is at paragraph end.

**Source [3] — Inducing Task Models from Computer-Use Traces:**

> Describing the activity conducted in a computeruse session is necessary for analyzing, learning, and auditing it. We formalize this process as the recovery, from a naturalistic computer-use trace, of the latent tasks and their task models specifying the objectives and procedures. Let X=⟨x 1, x2, . .…

</details>

<details><summary>q10 — How well does task model induction group interleaved tasks?</summary>

**New answer:**

Our method recovers interleaved tasks with 0.974 agreement against ground-truth task groupings [2]. This is compared to 30.3% for the strongest workflow induction baseline [2].

**Assessment:** New metric-mixing error: 0.974 is task-grouping agreement, but the answer compares it with 30.3%, which source [2] assigns to execution-step reconstruction. The correct reconstruction comparison is 74.9% versus 30.3%. Also retains the paper’s first-person “Our method”.

**Source [2] — Inducing Task Models from Computer-Use Traces:**

> …n work sessions (Wang et al., 2025), our method recovers interleaved tasks with 0.974 agreement against ground-truth task groupings and matches 74.9% of observed execution steps against 30.3% for the strongest workflow induction baseline. Using the induced task model to generate reusable agent skill…

</details>

<details><summary>q11 — How much of observed execution does TMI reconstruct?</summary>

**New answer:**

74.9% [2]

**Assessment:** Correct 74.9% reconstruction result; a metric label would make the bare number more self-contained.

**Source [2] — Inducing Task Models from Computer-Use Traces:**

> Naturalistic computer-use traces, passively recorded screenshots and mouse or keyboard actions, are a valuable resource for deriving symbolic, auditable, and reusable models of how everyday work is done. Such models matter as computer-use agents enter real work, where agents need to learn how tasks …

</details>

<details><summary>q12 — What was the held-out task accuracy gain from skills derived from TMI?</summary>

**New answer:**

The held-out task accuracy gain from skills derived from TMI was 30% relative accuracy gain, from 14.29 to 18.57, over the strongest baseline. [1]

**Assessment:** Correctly states a 30% relative gain from 14.29 to 18.57, rather than a percentage-point increase.

**Source [1] — Inducing Task Models from Computer-Use Traces:**

> Exec. Safe. Align. Acc. No skill N/A N/A N/A 59.20 8.57 Human curated 93.59 63.80 90.50 56.59 10.00 Raw demonstration 52.46 53.4992.5263.15 11.43 Workflow summary 54.07 59.35 91.74 66.18 14.29 Ours54.95 67.6590.5767.99 18.57 The task model is an effective representation for skill transfer.Skills gen…

</details>

<details><summary>q13 — How many commuters and respondent-scenario observations did the weather travel survey collect?</summary>

**New answer:**

The study collected 92 student commuters and 454 respondent-scenario observations. [2]

**Assessment:** Correct 92 student commuters and 454 respondent-scenario observations.

**Source [2] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> The Data Collection Agent was implemented as a purpose-built conversational chatbot,Travel- BehaviorSurveyBot, developed in Voiceflow and deployed as a web application accessible through a public link and QR code (Figure 2). Respondents completed the survey on their own devices through a guided dial…

</details>

<details><summary>q14 — Which travel modes responded most clearly to adverse weather and snow?</summary>

**New answer:**

Cycling was particularly sensitive to adverse weather, while public transit use increased substantially under the Snowy scenario. [4]

**Assessment:** Correct adverse-weather sensitivity for cycling and increased transit use under snow.

**Source [4] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> Travel-behavior research increasingly combines digital data collection with predictive modeling, yet these stages are often developed and evaluated separately. This study proposes and applies a three-agent workflow integrating conversational data collection, structured data processing, and behaviora…

</details>

<details><summary>q15 — How did random forest and the best text-only zero-shot LLM compare on five-class travel prediction?</summary>

**New answer:**

Random forest achieved a five-class accuracy of 69.6% [4], while the best text-only zero-shot LLM reached 69.9% [4].

**Assessment:** Correctly associates 69.6% with random forest and 69.9% with text-only zero-shot LLM; source [4] contains both.

**Source [4] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> Travel-behavior research increasingly combines digital data collection with predictive modeling, yet these stages are often developed and evaluated separately. This study proposes and applies a three-agent workflow integrating conversational data collection, structured data processing, and behaviora…

</details>

<details><summary>q16 — What was the best vision-based travel mode prediction accuracy?</summary>

**New answer:**

71.5% [3].

**Assessment:** Correct 71.5% result, though the bare number would benefit from a metric label.

**Source [3] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> labeled travel-behavior data are limited, although the small sample and multiple evaluated configurations require cautious interpretation. The five-class task provides a clearer assessment of whether models distinguish among individual modes. Vision-based prediction.The vision experiments directly c…

</details>

<details><summary>q17 — What is the patient-oriented medical report interpretation task introduced with G-CARL?</summary>

**New answer:**

Patient-Oriented Medical Report Interpretation (PMRI), a novel open-ended multimodal generation task that requires models to explain medical reports in accurate and accessible language based on a user’s query and dialogue history [3].

**Assessment:** Correct patient-oriented explanation task, grounded in report images, user query and dialogue history.

**Source [3] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> Personalized interpretation of medical reports has emerged as an increasingly important need among patients. Addressing this need requires both evidence-grounded medical factualityandcontext-dependentpatientcommunication,yetexisting medical vision-language tasks do not adequately capture these dual …

</details>

<details><summary>q18 — How does G-CARL supervise factuality and response coverage?</summary>

**New answer:**

G-CARL supervises factuality through a retrieval-grounded branch that verifies report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality reward Rfact [4]. It also supervises response coverage through a case-specific checklist branch that constructs a weighted checklist through MLLM generation followed by clinician-guided refinement, and evaluates the checklist coverage of the generated response to produce the checklist reward Rcheck [4].

**Assessment:** Now covers multi-source medical retrieval and claim verification plus the weighted case-specific checklist, all supported by source [4]. This fills the earlier retrieval omission.

**Source [4] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> BuiltuponGRPO,G-CARLoptimizesthepolicymodelwith three reward signals, as illustrated in Fig. 2. Given uploaded medical report imagesI, the dialogue historyh, and a user queryq,thepolicymodelfirstgeneratescandidateresponses. The retrieval-grounded branch then supervises medical factuality by verifyin…

</details>

<details><summary>q19 — What benchmark and evaluation dimensions accompany G-CARL?</summary>

**New answer:**

The benchmark accompanying G-CARL is MMedReport, a real-world multimodal PMRI benchmark, and CMB, an external benchmark that evaluates both medical QA accuracy and the professionalism of open-ended clinical interpretation. 

The evaluation dimensions for PMRI responses include Medical Accuracy (Accuracy), Demand Satisfaction (Satisfaction), and Expression Quality (Expression), scored according to a clinician-authored rubric ranging from -2 to 3. 

Additionally, objective evaluation metrics include claim-level Precision and checklist-level Recall, measuring factual correctness and coverage of case-specific requirements, respectively. [1][2][3]

**Assessment:** Correct MMedReport benchmark and all three evaluation dimensions. Extra CMB and precision/recall details are supported. Citations remain bunched at the end instead of following each factual sentence.

**Source [1] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> Datasets.We evaluate G-CARL primarily on(1)MMedReport, a real-world multimodal PMRI benchmark collectedfromonlinehealthcareconsultations.Itcontains2,450 instances, each including dialogue history, a user query, uploaded medical report images, and clinician-verified reference annotations. All instanc…

**Source [2] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> (OpenAI 2025) as the judge by strictly following these evaluation criteria. The complete judging protocol is provided in theAppendix Bto facilitate reproducibility. (2) Objective Evaluation. In addition to holistic assessment, we report claim-levelPrecisionand checklist-levelRecall. Precisionisdefin…

</details>

<details><summary>q20 — What did clinician pairwise preferences find about G-CARL?</summary>

**New answer:**

G-CARL was consistently preferred over both SFT and MLLM-as-a-Judge, particularly in medical accuracy and demand satisfaction, with preference margins of 136:85 and 106:64, respectively. [1]

**Assessment:** Correct clinician preference finding and supported margins 136:85 and 106:64.

**Source [1] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> andproducesclinicallyaccurateinterpretations.Similarly,in therightexample,SFTfailstoincorporatetheuser’ssmoking andalcoholcessationhistory,whileMLLM-as-a-Judgefails toaddresstheuser’sprimaryconcernofwhethertocontinue themedication.Incontrast,ourmethodeffectivelyintegrates historical context, directl…

</details>

<details><summary>q21 — Which papers address auditable AI workflows derived from user activity or survey responses?</summary>

**New answer:**

The provided papers address auditable AI workflows derived from user activity or survey responses.

* An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction addresses auditable AI workflows derived from survey responses. The paper proposes a multi-agent framework that integrates data collection, data processing, and behavioral modeling for commuter mode-choice research, with a focus on stateful conversational survey administration and structured response capture. [4][3]
* Inducing Task Models from Computer-Use Traces addresses auditable AI workflows derived from user activity. The paper introduces TASKMODELINDUCTION(TMI), which discovers latent tasks in unconstrained traces and induces task models pairing hierarchical objective models with procedure models of control flow. [1]

**Assessment:** False refusal is resolved: identifies both the survey workflow and TMI, explains their different inputs, and cites both papers. Citation placement is still mostly at bullet ends.

**Source [4] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> a commonmulti-agent workflowremains largely unexplored for travel behavior and individual mode-choice modeling. This study addresses these gaps through a multi-agent workflow that connects AI-assisted behavioral data collection with travel-choice modeling and LLM-based prediction. The paper makes fo…

**Source [3] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> Throughout this paper,active data collectionrefers to stateful conversational survey administration with predefined interaction logic and structured response Table 1: Roles, interfaces, and supported functions of the three agents. Agent Main inputs Authorized functions Main outputs Data Collection A…

</details>

<details><summary>q22 — Which papers evaluate AI agents or model specialists using benchmark tasks and costs?</summary>

**New answer:**

Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation evaluates both Pandora's Router and Pandora's Bidder using three domains: a multi-LLM routing benchmark, retrieval-augmented specialists for factoid QA, and inference-time computation for mathematical reasoning. The evaluation assesses their allocative performance relative to baselines across a range of estimation costs [5].

AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement presents a benchmark that evaluates AI agents' ability to design training algorithms. In each task, an agent has 4 hours to rewrite the training algorithm, and its code is then rerun from scratch for up to 12 hours and scored by a fixed evaluator [3].

**Assessment:** Correctly identifies Pandora routing and AI4AI-Bench, their evaluation domains and budgets/costs. More detailed than the earlier answer; citations remain at paragraph ends.

**Source [5] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Bidder: each specialist faces a posted price—the current best competing offer—and must decide whether to invest in a more accurate self-assessment before claiming the query. This corresponds to a single stage of the ascending-price mechanism with costly preference elicitation studied by Parkes (2005…

**Source [3] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement Yizhe Chi , Wenyi Li, Deyao Hong, Xiaoqiu Wang, Mingju Gao, Kaisen Yang, Bingxiang He, Y oujie Zheng, Calvin Xiao, Qinhuai Na Navers Lab, Einsia.AI T singhua University Project Lead Corresponding Author Abstrac…

</details>

<details><summary>q23 — Which papers discuss evidence-grounded explanations and auditable task models?</summary>

**New answer:**

The provided papers discuss the following concepts related to evidence-grounded explanations and auditable task models:

* Evidence-grounded explanations:
	+ Paper 2608.20331 discusses patient-oriented medical report interpretation (PMRI) as an evidence-bounded generation task that requires explanations grounded in reports and reliable clinical knowledge. [4]
	+ Paper 2608.20331 proposes a reinforcement learning framework, G-CARL, that decomposes reward supervision through retrieval-grounded claim verification and case-specific checklist guidance. [3]
* Auditable task models:
	+ Paper 2608.20319 introduces TASKMODELINDUCTION (TMI), which induces task models pairing a hierarchical objective model of recursive goal decomposition with a procedure model of the control flow that organized the execution. [2]
	+ Paper 2608.20319 describes the objective model as a hierarchy that explains why the observed activities were performed, and the procedure model as capturing how the execution of the task was organized in time. [1]
	+ Paper 2608.20319 also describes the procedure model as inducing a tree using three observable operators: sequence, selection, and iteration. [5]

**Assessment:** Now covers both G-CARL and TMI, but adds a false detail: says the three observable operators are sequence, selection and iteration. Source [5] explicitly excludes selection from the output and specifies SEQ, FOR and WHILE. The answer is also long and exposes paper IDs instead of readable titles.

**Source [5] — Inducing Task Models from Computer-Use Traces:**

> …(while). The trace records only the path enacted, not unchosen alternatives, so selection is not represented in the output. Decompose the observed activity trace into a tree using the three observable operators below. The three operators are the complete and closed vocabulary: -`SEQ`: steps in fixed…

**Source [3] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> In this paper, we present PMRI as a challenging yet underexplored task that requires both evidence-grounded medical factualityandcontext-dependentpatientcommunication.We propose G-CARL, a reinforcement learning framework that decomposes reward supervision through retrieval-grounded claim verificatio…

</details>

<details><summary>q24 — What is KPMG's 2026 revenue forecast?</summary>

**New answer:**

The provided papers do not address this question.

**Assessment:** Correctly declines the unsupported KPMG revenue forecast.

</details>

<details><summary>q25 — Which of these papers reports the stock price of NVIDIA on October 14, 2026?</summary>

**New answer:**

The provided papers do not address this question.

**Assessment:** Correctly declines the unsupported NVIDIA stock price.

</details>
