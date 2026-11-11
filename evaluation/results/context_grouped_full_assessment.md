# Paper grouping alone — full benchmark assessment

**Conclusion:** grouping alone is the most promising of the tested configurations for core content, but it is not a clean upgrade: two answers lose all citations. It fixes the earlier cross-paper failures without the combined version’s new factual errors. Use it as the next optimization candidate, with citation compliance and concise output as the next targets. No production defaults were changed in this test.

**Scope:** 25 fresh Llama 3.1 8B generations with grouping enabled and selection-order reconstruction disabled. Same model weights, prompt, generation settings and exact frozen passages as the prior baseline. Grouping preserves first-seen paper order and within-paper order, but makes a paper’s passages adjacent; it is not an order-neutral change for interleaved papers. The earlier three-question pilot was rerun as part of this full run. No LLM judge or new retrieval was used.

**Review basis:** assistant assessment against saved sources, not independent human ratings. Complete refers to core factual content, not perfect citation/format compliance. Partial indicates material omissions or a correct core with a material erroneous extra detail. This small single-run comparison does not establish a stable accuracy rate.

| Content result | Baseline | Grouping + ordering | Grouping alone |
| --- | ---: | ---: | ---: |
| Complete | 17 | 18 | 19 |
| Partial | 4 | 3 | 3 |
| Major issue | 2 | 2 | 1 |
| Correct abstention | 2 | 2 | 2 |

**Citation trade-off:** q19 and q22 contain correct core content but no passage citations. Grouping alone has citations in 21/23 answerable responses, versus 22/23 for baseline (one false refusal) and 23/23 for both changes. These counts check citation presence, not whether every claim is supported.

## What improved and what remains

- **q21:** correctly names both auditable-workflow papers instead of falsely declining.
- **q23:** covers both TMI and G-CARL and avoids the combined version’s incorrect selection-operator claim.
- **q10:** retains the correct 0.974 grouping-agreement result without comparing it with unrelated 30.3% reconstruction.
- **q08:** still misses 0.226 versus 0.126; paper grouping does not solve this comparison failure.
- **q01, q02, q18:** existing omissions remain. In particular, q18 still lacks explicit multi-source retrieval, which the combined variant supplied.
- **q19 and q22:** new citation omissions; q22 is also verbose. Do not count the factual completeness increase as universal improvement.
- **q24 and q25:** both unsupported questions are correctly declined.

**Runtime:** 240.6 seconds of recorded generation time for 25 calls. Timing is descriptive, not a controlled latency benchmark.

**Recommendation:** prefer grouping alone as the next candidate, then test a small citation/conciseness prompt adjustment against this saved run. Treat q08 as a separate evidence-use/comparison problem. Keep the current configuration unchanged until those trade-offs are acceptable; this task only generated and assessed outputs.

## Per-question results

| ID | Baseline | Combined | Grouping alone | Explanation |
| --- | --- | --- | --- | --- |
| q01 | Partial | Partial | Partial | Value of information, stopping and selection are correct, but inspection in reservation-price order is still missing. |
| q02 | Partial | Partial | Partial | Correct centralized/decentralized distinction and local-surplus caveat. Still does not explicitly explain Router’s global-welfare objective and exceeds the requested three sentences. |
| q03 | Complete | Complete | Complete | All three domains are correct; one citation follows the whole list instead of each item. |
| q04 | Complete | Complete | Complete | Correctly describes increased strategic utility at others’ expense when competing estimates are noisy. |
| q05 | Complete | Complete | Complete | Correct ten repositories and ten algorithm families. |
| q06 | Complete | Complete | Complete | Correct four-hour agent budget on one B300 GPU and twelve-hour replay budget. |
| q07 | Complete | Complete | Complete | Correctly explains the 0, 0.1 and 1.0 normalization anchors. |
| q08 | Major issue | Major issue | Major issue | Still omits the performance comparison 0.226 versus 0.126 despite source [2] containing both. Submission shares and the supported non-causal caveat do not answer the main performance comparison. |
| q09 | Complete | Complete | Complete | Correct objective hierarchies and procedure/control-flow models; citation follows the paragraph. |
| q10 | Complete | Major issue | Complete | Correct 0.974 grouping agreement. Avoids the combined version’s false comparison with 30.3%. Still copies the paper’s first-person wording “Our method”. |
| q11 | Complete | Complete | Complete | Correct 74.9% execution reconstruction; a metric label would make the bare number clearer. |
| q12 | Complete | Complete | Complete | Correct 30% relative gain from 14.29 to 18.57, rather than a percentage-point change. |
| q13 | Complete | Complete | Complete | Correct 92 McGill student commuters and 454 respondent-scenario observations; citations are grouped after the second sentence. |
| q14 | Complete | Complete | Complete | Correct cycling sensitivity to adverse weather and increased transit use under snow. |
| q15 | Complete | Complete | Complete | Correct 69.6% random forest versus 69.9% best text-only zero-shot LLM; both values are supported by source [4]. |
| q16 | Complete | Complete | Complete | Correct 71.5% accuracy result; the bare number lacks a self-contained metric label. |
| q17 | Complete | Complete | Complete | Correct patient-oriented, report-grounded explanation task, using query and dialogue history. Explains patient communication and distinction from VQA/report generation. |
| q18 | Partial | Complete | Partial | Correct atomic claim verification and weighted case-specific checklists. Still omits explicit multi-source retrieval/datastore support, unlike the combined version. |
| q19 | Complete | Complete | Complete | Core benchmark and evaluation dimensions are correct, including the extra CMB and precision/recall details. However, the answer contains no passage citations: a citation regression, recorded separately from core factual completeness. |
| q20 | Complete | Complete | Complete | Correct clinician preference finding and supported margins of 136:85 and 106:64. |
| q21 | Major issue | Complete | Complete | Resolves the false refusal and identifies both relevant papers, with supported descriptions and TMI results. The answer is verbose and exposes paper IDs; claim-level citation placement can still improve. |
| q22 | Complete | Complete | Complete | Correctly identifies both papers and gives supported benchmark details. However, no passage citations are supplied, and the answer is unnecessarily long: another citation/formatting regression. |
| q23 | Partial | Partial | Complete | Covers both TMI and G-CARL with supported descriptions and citations. Avoids the combined version’s false selection-operator detail. Paper IDs are unnecessary for a business-facing answer. |
| q24 | Correct abstention | Correct abstention | Correct abstention | Correctly declines the unsupported KPMG revenue forecast. |
| q25 | Correct abstention | Correct abstention | Correct abstention | Correctly declines the unsupported NVIDIA stock-price question. |

## New answers and source checks

The excerpts are literal saved-source text, shortened to 300 characters. Full passages are in `manual_review_context_grouped_full.json` and its Markdown worksheet.

<details><summary>q01 — How does Pandora's Router decide when an expensive specialist estimate is worth paying for?</summary>

**Answer:**

Pandora's Router computes reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate 𝑔𝑚(𝑥), e.g., by running the specialist for a few reasoning tokens and checking if it is on the right track [1]. The system stops when no remaining query is worth its cost, and chooses the maximizer of the observed 𝑔𝑚 [1].

**Assessment:** Value of information, stopping and selection are correct, but inspection in reservation-price order is still missing.

**Source [1] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value e…

</details>

<details><summary>q02 — What is the difference between Pandora's Router and Pandora's Bidder?</summary>

**Answer:**

Pandora's Router and Pandora's Bidder differ in their approach to value estimation and decision-making. Pandora's Router is a centralized policy that inspects specialists in reservation price order, stopping when no remaining query is worth its cost, and chooses the maximizer of the observed value estimate [1]. In contrast, Pandora's Bidder is a decentralized policy that selects the high bidder in an auction, with each specialist refining its own value estimate only when the market price makes inspection worthwhile [1]. Additionally, Pandora's Bidder measures regret versus an oracle that knows the true value for free, and its performance is affected by the price being inaccurate, leading to a trade-off between local surplus and overall allocative efficiency [3].

**Assessment:** Correct centralized/decentralized distinction and local-surplus caveat. Still does not explicitly explain Router’s global-welfare objective and exceeds the requested three sentences.

**Source [1] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value e…

**Source [3] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> we measure the regret versus an oracle that knows𝐺𝑚 for free. Results.Figure3plotsallocativeefficiencyandbiddersurplusfordifferent 𝑐𝑔. Pandora’sBidderclosely tracks the lower envelope of the regret of the two baselines across the full𝑐𝑔 range. When𝑐𝑔 is low, the bidder frequently refines its estimat…

</details>

<details><summary>q03 — In which three domains was the costly-value-estimation routing policy evaluated?</summary>

**Answer:**

The three domains where the costly-value-estimation routing policy was evaluated are:

1. A multi-LLM routing benchmark (EmbedLLM)
2. Retrieval-augmented specialists for factoid QA
3. Inference-time computation for mathematical reasoning

[3]

**Assessment:** All three domains are correct; one citation follows the whole list instead of each item.

**Source [3] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Bidder: each specialist faces a posted price—the current best competing offer—and must decide whether to invest in a more accurate self-assessment before claiming the query. This corresponds to a single stage of the ascending-price mechanism with costly preference elicitation studied by Parkes (2005…

</details>

<details><summary>q04 — What limitation appears when competing specialists' estimates are noisy?</summary>

**Answer:**

When competing estimates are noisy, value-of-information reasoning can increase the strategic specialist's utility at the expense of others. [1]

**Assessment:** Correctly describes increased strategic utility at others’ expense when competing estimates are noisy.

**Source [1] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> benchmark, retrieval-augmented specialists, and LLMs with variable inference-time reasoning—show that Pandora’s Router matches the routing quality of exhaustive estimation, while querying the expensive estimator far less often. In the decentralized setting, value-of-information reasoning improves al…

</details>

<details><summary>q05 — How many frozen repositories and training algorithm families are in AI4AI-Bench?</summary>

**Answer:**

The AI4AI-Bench suite consists of 10 frozen research repositories, covering 10 distinct families of training algorithm. [2]

**Assessment:** Correct ten repositories and ten algorithm families.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> The suite is ten frozen research repositories, listed in Table 1 and chosen so that between them they cover ten families of training algorithm rather than ten instances of one: supervised fine-tuning, multi-turn agentic RL, on-policy distillation, Bradley–Terry reward modeling, preference optimizati…

</details>

<details><summary>q06 — What is the AI4AI-Bench time budget for an agent and for the replay?</summary>

**Answer:**

The AI4AI-Bench time budget for an agent is 4 hours on one B300 GPU [2]. The time budget for replay is 12 hours [3].

**Assessment:** Correct four-hour agent budget on one B300 GPU and twelve-hour replay budget.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> Each task presents an agent with a research repository, a base model to start from, and an inexpensive proxy metric that can be evaluated freely during development 2.2. The agent is given 4 hours on one B300 GPU and a single objective: improve the training algorithm implemented in the repository. It…

**Source [3] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> Recursive self-improvement compounds through the algorithmic link, and AI4AI-Bench is built to measure that link on its own: ten frozen research repositories, each asking an agent to improve the training algorithm it already applies to its own model, with four hours to write code, twelve to run what…

</details>

<details><summary>q07 — How are the incommensurable AI4AI-Bench task metrics normalized?</summary>

**Answer:**

Each task is mapped onto one scale where 0 is an uninformative model, 0.1 is the algorithm the repository ships, and 1.0 is the task optimum [2].

**Assessment:** Correctly explains the 0, 0.1 and 1.0 normalization anchors.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> incommensurable, every task is mapped onto one scale on which0is an uninformative model,0 .1is the algorithm the repository ships, and1.0 is the task optimum. Across 29 configurations of 6 systems on all 10 tasks the mean score is0.166, and the best system reaches0.250: even the strongest closes und…

</details>

<details><summary>q08 — How do submissions that change the learning algorithm compare with those that do not?</summary>

**Answer:**

Submissions that change the learning algorithm (46.4% of 263 submissions) are compared to those that do not (53.6% of 263 submissions). The comparison is limited by the fact that the systems that reach the learning procedure more often are the stronger ones to begin with, so the gap is the difference between the submissions that go there and the submissions that do not, rather than the effect of going there [3].

**Assessment:** Still omits the performance comparison 0.226 versus 0.126 despite source [2] containing both. Submission shares and the supported non-causal caveat do not answer the main performance comparison.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> … the objective, the supervision signal, the learning rule, the data — average0.226 against0 .126for the rest: the algorithmic layer is where the distance gets closed, and most submissions never go there. More reasoning effort moves agents towards it, taking that share from8%to64%and the mean score f…

</details>

<details><summary>q09 — What two kinds of task structure does TMI recover from computer-use traces?</summary>

**Answer:**

TMI recovers two kinds of task structure: objective models and procedure models. Objective models are hierarchical decompositions of the objective of a task into subobjectives, while procedure models are trace-grounded compositions of control-flow operators specifying how the execution of a task is organized. [3]

**Assessment:** Correct objective hierarchies and procedure/control-flow models; citation follows the paragraph.

**Source [3] — Inducing Task Models from Computer-Use Traces:**

> Describing the activity conducted in a computeruse session is necessary for analyzing, learning, and auditing it. We formalize this process as the recovery, from a naturalistic computer-use trace, of the latent tasks and their task models specifying the objectives and procedures. Let X=⟨x 1, x2, . .…

</details>

<details><summary>q10 — How well does task model induction group interleaved tasks?</summary>

**Answer:**

Our method recovers interleaved tasks with 0.974 agreement against ground-truth task groupings [2].

**Assessment:** Correct 0.974 grouping agreement. Avoids the combined version’s false comparison with 30.3%. Still copies the paper’s first-person wording “Our method”.

**Source [2] — Inducing Task Models from Computer-Use Traces:**

> …sions (Wang et al., 2025), our method recovers interleaved tasks with 0.974 agreement against ground-truth task groupings and matches 74.9% of observed execution steps against 30.3% for the strongest workflow induction baseline. Using the induced task model to generate reusable agent skills, evaluat…

</details>

<details><summary>q11 — How much of observed execution does TMI reconstruct?</summary>

**Answer:**

74.9% [4]

**Assessment:** Correct 74.9% execution reconstruction; a metric label would make the bare number clearer.

**Source [4] — Inducing Task Models from Computer-Use Traces:**

> into semantic actions and activities, bridging low-level signal and local intent (3.1).Latent task inductionuntangles the multi-threaded activity stream, discovering tasks and assigning possibly non-contiguous activities to each without a pre-specified task set (3.2).Task model constructionbuilds ea…

</details>

<details><summary>q12 — What was the held-out task accuracy gain from skills derived from TMI?</summary>

**Answer:**

The held-out task accuracy gain from skills derived from TMI was 30% relative accuracy gain, from 14.29 to 18.57, over the strongest baseline. [1]

**Assessment:** Correct 30% relative gain from 14.29 to 18.57, rather than a percentage-point change.

**Source [1] — Inducing Task Models from Computer-Use Traces:**

> Exec. Safe. Align. Acc. No skill N/A N/A N/A 59.20 8.57 Human curated 93.59 63.80 90.50 56.59 10.00 Raw demonstration 52.46 53.4992.5263.15 11.43 Workflow summary 54.07 59.35 91.74 66.18 14.29 Ours54.95 67.6590.5767.99 18.57 The task model is an effective representation for skill transfer.Skills gen…

</details>

<details><summary>q13 — How many commuters and respondent-scenario observations did the weather travel survey collect?</summary>

**Answer:**

The Data Collection Agent collected mode choices from 92 McGill student commuters. The final processed dataset contained 454 valid respondent–scenario observations. [2][3]

**Assessment:** Correct 92 McGill student commuters and 454 respondent-scenario observations; citations are grouped after the second sentence.

**Source [2] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> The Data Collection Agent was implemented as a purpose-built conversational chatbot,Travel- BehaviorSurveyBot, developed in Voiceflow and deployed as a web application accessible through a public link and QR code (Figure 2). Respondents completed the survey on their own devices through a guided dial…

**Source [3] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> The Data Processing Agent converted the chatbot’s raw, JSON-encoded response export into an analysis-ready dataset. Processing steps included parsing nested list- and slider-valued fields, validating and recoding categorical responses, constructing derived features, and flagging incomplete or incons…

</details>

<details><summary>q14 — Which travel modes responded most clearly to adverse weather and snow?</summary>

**Answer:**

Cycling was particularly sensitive to adverse weather, while public transit use increased substantially under the Snowy scenario. [4]

**Assessment:** Correct cycling sensitivity to adverse weather and increased transit use under snow.

**Source [4] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> Travel-behavior research increasingly combines digital data collection with predictive modeling, yet these stages are often developed and evaluated separately. This study proposes and applies a three-agent workflow integrating conversational data collection, structured data processing, and behaviora…

</details>

<details><summary>q15 — How did random forest and the best text-only zero-shot LLM compare on five-class travel prediction?</summary>

**Answer:**

Random forest achieved a five-class accuracy of 69.6% [4], while the best text-only zero-shot LLM reached 69.9% [4].

**Assessment:** Correct 69.6% random forest versus 69.9% best text-only zero-shot LLM; both values are supported by source [4].

**Source [4] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> Travel-behavior research increasingly combines digital data collection with predictive modeling, yet these stages are often developed and evaluated separately. This study proposes and applies a three-agent workflow integrating conversational data collection, structured data processing, and behaviora…

</details>

<details><summary>q16 — What was the best vision-based travel mode prediction accuracy?</summary>

**Answer:**

71.5% [2]

**Assessment:** Correct 71.5% accuracy result; the bare number lacks a self-contained metric label.

**Source [2] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> and the best vision-based configuration reached the highest observed five-class accuracy of 71.5%, indicating that visual context can provide additional predictive information for selected models. Taken together, the findings show that habitual travel information, prompting strategy, demonstrations,…

</details>

<details><summary>q17 — What is the patient-oriented medical report interpretation task introduced with G-CARL?</summary>

**Answer:**

Patient-oriented Medical Report Interpretation (PMRI) is a novel open-ended multimodal generation task that requires models to explain medical reports in accurate and accessible language based on a user's query and dialogue history. [3]

PMRI must align professional medical knowledge with patient-centered communication by transforming report evidence into accessible explanations, addressing user-specific concerns, and offering clinically cautious guidance. [4]

PMRI differs fundamentally from medical VQA (Task A) and conventional report generation (Task B) in that it produces long-form, patient-facing explanations grounded in multimodal reports and extended patient-doctor dialogue. [4]

**Assessment:** Correct patient-oriented, report-grounded explanation task, using query and dialogue history. Explains patient communication and distinction from VQA/report generation.

**Source [3] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> Personalized interpretation of medical reports has emerged as an increasingly important need among patients. Addressing this need requires both evidence-grounded medical factualityandcontext-dependentpatientcommunication,yetexisting medical vision-language tasks do not adequately capture these dual …

**Source [4] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> Written within a professional medical context, medical reports commonly present abnormal values and descriptive findingswithoutexplainingtheirimplicationsfornon-expert readers. This gap becomes particularly salient in online healthcare scenarios, where patients upload one or more report images and a…

</details>

<details><summary>q18 — How does G-CARL supervise factuality and response coverage?</summary>

**Answer:**

G-CARL supervises factuality through a retrieval-grounded claim reward that provides fine-grained supervision for medical factuality through atomic claim verification [1]. It also supervises response coverage through a case-specific checklist reward that explicitly supervises demand satisfaction and expression quality without relying on a single reference response [1]. This is achieved by constructing instance-specific weighted checklists through MLLM generation followed by clinician refinement [1].

**Assessment:** Correct atomic claim verification and weighted case-specific checklists. Still omits explicit multi-source retrieval/datastore support, unlike the combined version.

**Source [1] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> reward provides localized supervision for sparse factual errors and discouragesunsupportedelaboration.Forcontext-dependent objectives such as demand satisfaction and expression quality,G-CARLconstructsinstance-specificweightedchecklists throughMLLMgenerationfollowedbyclinicianrefinement. Each checkl…

</details>

<details><summary>q19 — What benchmark and evaluation dimensions accompany G-CARL?</summary>

**Answer:**

The benchmark accompanying G-CARL is MMedReport, a real-world multimodal PMRI benchmark, and CMB, an external benchmark that evaluates both medical QA accuracy and the professionalism of open-ended clinical interpretation. 

The evaluation dimensions for PMRI responses include subjective evaluation along three clinician-defined dimensions: Medical Accuracy (Accuracy), Demand Satisfaction (Satisfaction), and Expression Quality (Expression), and objective evaluation using claim-level Precision and checklist-level Recall.

**Assessment:** Core benchmark and evaluation dimensions are correct, including the extra CMB and precision/recall details. However, the answer contains no passage citations: a citation regression, recorded separately from core factual completeness.

**Source [1] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> Datasets.We evaluate G-CARL primarily on(1)MMedReport, a real-world multimodal PMRI benchmark collectedfromonlinehealthcareconsultations.Itcontains2,450 instances, each including dialogue history, a user query, uploaded medical report images, and clinician-verified reference annotations. All instanc…

**Source [2] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> (OpenAI 2025) as the judge by strictly following these evaluation criteria. The complete judging protocol is provided in theAppendix Bto facilitate reproducibility. (2) Objective Evaluation. In addition to holistic assessment, we report claim-levelPrecisionand checklist-levelRecall. Precisionisdefin…

</details>

<details><summary>q20 — What did clinician pairwise preferences find about G-CARL?</summary>

**Answer:**

G-CARL was consistently preferred over both SFT and MLLM-as-a-Judge, particularly in medical accuracy and demand satisfaction, with preference margins of 136:85 and 106:64, respectively. [1]

**Assessment:** Correct clinician preference finding and supported margins of 136:85 and 106:64.

**Source [1] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> andproducesclinicallyaccurateinterpretations.Similarly,in therightexample,SFTfailstoincorporatetheuser’ssmoking andalcoholcessationhistory,whileMLLM-as-a-Judgefails toaddresstheuser’sprimaryconcernofwhethertocontinue themedication.Incontrast,ourmethodeffectivelyintegrates historical context, directl…

</details>

<details><summary>q21 — Which papers address auditable AI workflows derived from user activity or survey responses?</summary>

**Answer:**

The provided papers address auditable AI workflows derived from user activity or survey responses.

* Inducing Task Models from Computer-Use Traces (Paper ID: 2608.20319) introduces TASKMODELINDUCTION (TMI), which induces task models from computer-use traces, allowing for the recovery of interleaved tasks with 0.974 agreement against ground-truth groupings and the reconstruction of 74.9% of observed execution steps. [1]
* An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction (Paper ID: 2608.20320) proposes a multi-agent framework that integrates data collection, data processing, and behavioral modeling, producing structured and auditable outputs. [2] The framework consists of three specialized agents: a Data Collection Agent, a Data Processing Agent, and a Data Modeling Agent, which exchange information through standardized data objects and explicit input–output interfaces. [3]

**Assessment:** Resolves the false refusal and identifies both relevant papers, with supported descriptions and TMI results. The answer is verbose and exposes paper IDs; claim-level citation placement can still improve.

**Source [1] — Inducing Task Models from Computer-Use Traces:**

> Naturalistic computer-use traces, passively recorded screenshots and mouse or keyboard actions, are a valuable resource for deriving symbolic, auditable, and reusable models of how everyday work is done. Such models matter as computer-use agents enter real work, where agents need to learn how tasks …

**Source [2] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> We propose a multi-agent framework that integrates data collection, data processing, and behavioral modeling for commuter mode-choice research. The framework consists of three specialized agents: a Data Collection Agent, a Data Processing Agent, and a Data Modeling Agent. The agents perform distinct…

</details>

<details><summary>q22 — Which papers evaluate AI agents or model specialists using benchmark tasks and costs?</summary>

**Answer:**

Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation (Paper ID: 2608.20316) evaluates AI agents or model specialists using benchmark tasks and costs. Specifically, it evaluates Pandora's Router and Pandora's Bidder across three domains: a multi-LLM routing benchmark, retrieval-augmented specialists for factoid QA, and inference-time computation for mathematical reasoning. The evaluation shows that both frameworks are able to trade-off expensive and cheap estimates to achieve strong allocative performance relative to baselines across a range of estimation costs.

AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement (Paper ID: 2608.20318) also evaluates AI agents or model specialists using benchmark tasks and costs. It presents AI4AI-Bench, a benchmark that isolates the ability of an agent to design training algorithms, and evaluates 6 systems across 29 configurations on 10 frozen research repositories spanning 10 training algorithm families. The evaluation scores the agent's ability to improve the training algorithm and maps the 10 metrics onto a single scale.

**Assessment:** Correctly identifies both papers and gives supported benchmark details. However, no passage citations are supplied, and the answer is unnecessarily long: another citation/formatting regression.

**Source [3] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement Yizhe Chi , Wenyi Li, Deyao Hong, Xiaoqiu Wang, Mingju Gao, Kaisen Yang, Bingxiang He, Y oujie Zheng, Calvin Xiao, Qinhuai Na Navers Lab, Einsia.AI T singhua University Project Lead Corresponding Author Abstrac…

**Source [5] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Bidder: each specialist faces a posted price—the current best competing offer—and must decide whether to invest in a more accurate self-assessment before claiming the query. This corresponds to a single stage of the ascending-price mechanism with costly preference elicitation studied by Parkes (2005…

</details>

<details><summary>q23 — Which papers discuss evidence-grounded explanations and auditable task models?</summary>

**Answer:**

The provided papers discuss evidence-grounded explanations and auditable task models.

* Inducing Task Models from Computer-Use Traces (Paper ID: 2608.20319) discusses auditable task models, specifically objective models that explain why observed activities were performed, and procedure models that capture how the execution of the task was organized in time. [1]
* G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation (Paper ID: 2608.20331) discusses evidence-grounded explanations, specifically transforming report evidence into accessible explanations that address user-specific concerns and offer clinically cautious guidance. [4]

**Assessment:** Covers both TMI and G-CARL with supported descriptions and citations. Avoids the combined version’s false selection-operator detail. Paper IDs are unnecessary for a business-facing answer.

**Source [1] — Inducing Task Models from Computer-Use Traces:**

> Modeling a task t requires understanding the two types of evidence it carries, procedure and objective. Constructing a task model thus means inducing an objective model Ot and a procedure model Pt from the activities Et of each discovered task t, then reconciling them into the task model Mt (Figure …

**Source [4] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> explanations grounded inmultimodalreportsandextendedpatient–doctordialogue. cation by transforming report evidence into accessible explanations, addressing user-specific concerns, and offering clinically cautious guidance. As illustrated in Fig. 1, PMRI differs from conventional medical visual quest…

</details>

<details><summary>q24 — What is KPMG's 2026 revenue forecast?</summary>

**Answer:**

The provided papers do not address this question.

**Assessment:** Correctly declines the unsupported KPMG revenue forecast.

</details>

<details><summary>q25 — Which of these papers reports the stock price of NVIDIA on October 14, 2026?</summary>

**Answer:**

The provided papers do not address this question.

**Assessment:** Correctly declines the unsupported NVIDIA stock-price question.

</details>
