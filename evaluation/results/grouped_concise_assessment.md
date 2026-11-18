# Grouping alone: citations and concise comparisons

**Decision:** keep grouping alone and the shorter prompt as an incremental improvement. The key performance comparison now includes both scores, answers are shorter on average, and one previously uncited answer now has citations. Citation compliance remains incomplete; this is not a fully verified answer pipeline.

**Active setup:** notebook cell 77 uses `order_by_vector=True`; `ask_llm` groups passages by paper; the notebook default generator is `llama3.1:8b`. The shorter prompt is saved in `prompt_grouped_concise.txt` and is the active `PROMPT` in cell 85. No extra judge or repair model call was added.

**Controlled test:** two complete 25-question prompt runs against the same frozen passages and presentation, model weights and generation settings. Only the prompt changed between these two runs and the previous grouping-only baseline. Three completed answers from an initial literal-template attempt were preserved separately; that attempt was stopped after it copied the comparison template into an unrelated question. One request was interrupted. The longer revision was rejected for verbosity and factual regressions.

**Review basis:** assistant inspection against supplied passages, not independent human ratings. Complete means core factual content is supported, not perfect citation/format compliance. Partial includes missing material content or a correct core with an incorrect extra detail. Small single-run results do not establish general accuracy.

| Content result | Previous grouping | Longer revision (rejected) | Shorter revision (kept) |
| --- | ---: | ---: | ---: |
| Complete | 19 | 17 | 19 |
| Partial | 3 | 6 | 4 |
| Major issue | 1 | 0 | 0 |
| Correct abstention | 2 | 2 | 2 |

| Measure (23 answerable questions) | Previous grouping | Longer revision | Shorter revision |
| --- | ---: | ---: | ---: |
| Average answer words | 47.5 | 66.7 | 39.0 |
| Answers over 70 words | 6 | 8 | 3 |
| Answers containing a citation | 21 | 23 | 22 |

Word counts exclude bracketed citation numbers and appended software-generated evidence/references. Citation presence is not sentence-level compliance or proof of support.

## What improved

- **q08:** now reports **0.226 versus 0.126**, without the rejected candidate’s unsupported “significant difference” wording. Still rated partial: its caveat refers to stronger submissions, whereas the source refers to stronger systems producing them.
- **q15:** gives **69.6% versus 69.9% five-class accuracy** in one cited sentence.
- **q12:** states the **30% relative gain, from 14.29 to 18.57**, without repeated arithmetic or duplicated figures.
- **q22:** citations return to the cross-paper benchmark answer, though their positioning and source alignment remain imperfect.
- **q21/q23:** coverage of both relevant papers is retained; the longer candidate’s false attribution of auditable task models to G-CARL is avoided.
- **Unsupported questions:** both use the exact required refusal sentence.

## What remains unresolved

- **q19 still has no citations.** Several other answers put a citation only after multiple sentences or leave individual bullets uncited.
- **q01/q02/q18 remain incomplete.** Shortening also removes some previously present details: q01 loses the explicit stopping rule, q02 loses the local-surplus caveat, and q18 does not clearly specify weighted checklist construction. Their category stays partial; this should not be mistaken for no regression.
- **q17 repeats its definition in uncited bullets.** Some multi-paper answers still exceed the word target.
- Prompt-only instructions do not guarantee citation alignment or numerical reasoning. The next focused improvement would be a structured answer format with explicit claim/citation fields, validated locally; that has not been added here.

**Validation:** 132 offline tests passed after the final prompt change. Saved contexts and passages were verified identical to the grouping-only baseline. The review notebook was executed separately without model calls.

**Timing:** longer revision 305.7s; selected shorter revision 355.1s. These are recorded generation totals, not a controlled speed comparison; runtime was variable. The initial stopped template attempt is excluded from these totals.

## Per-question assessment

| ID | Before | After | Explanation |
| --- | --- | --- | --- |
| q01 | Partial | Partial | Correct value-of-information principle and final selection, but still omits reservation-price inspection order and the explicit stopping rule. First factual sentence has no adjacent citation. |
| q02 | Partial | Partial | Correct centralized versus decentralized distinction, but omits the Router’s global-welfare objective and local-surplus trade-off. Concise but less complete. |
| q03 | Complete | Complete | Correct three domains; citations appear on a separate line after the list instead of each bullet. |
| q04 | Complete | Complete | Correct possible harm from noisy competing estimates, without the longer candidate’s categorical claim. Second sentence repeats the point and citation follows only the second sentence. |
| q05 | Complete | Complete | Directly gives ten repositories and ten algorithm families as two cited bullets. |
| q06 | Complete | Complete | Correct four-hour agent budget and twelve-hour replay budget, with sentence-level citations. |
| q07 | Complete | Complete | Correct 0, 0.1 and 1.0 normalization anchors, with a supporting citation. |
| q08 | Major issue | Partial | Now gives the key 0.226 versus 0.126 scores without calling them statistically significant. However, the caveat says submissions were stronger to begin with; source [3] says the systems producing them were stronger. Adds unrequested reasoning-effort statistics. This is a substantial improvement over missing the scores, but not a fully precise comparison. |
| q09 | Complete | Complete | Correct objective hierarchy and procedure/control-flow explanation. Citation remains at paragraph end rather than after each factual sentence. |
| q10 | Complete | Complete | Correct 0.974 grouping agreement without unrelated metric comparisons. Still copies first-person wording from the paper. |
| q11 | Complete | Complete | Correct 74.9% result, now includes its metric label and citation. |
| q12 | Complete | Complete | Concise correct 30% relative accuracy gain from 14.29 to 18.57, with citation. |
| q13 | Complete | Complete | Correct 92 commuters and 454 observations, but citations still follow both sentences together. |
| q14 | Complete | Complete | Correct cycling and transit findings in one cited sentence. |
| q15 | Complete | Complete | Concise comparison with correctly assigned 69.6% and 69.9% five-class accuracies, plus the supported no-task-specific-fitting qualification. |
| q16 | Complete | Complete | Correct 71.5% accuracy with supporting citations. Extra image-context sentence is supported but not required. |
| q17 | Complete | Complete | Core PMRI definition is supported, but repeats it as three uncited bullets after two cited sentences. Fails the intended brevity and per-bullet citation format. |
| q18 | Partial | Partial | Correct atomic claim verification and case-specific checklist supervision. Still omits explicit multi-source datastore support and does not spell out the weighted checklist construction; citations are present per sentence. |
| q19 | Complete | Complete | Correct benchmark names and evaluation dimensions, and shorter than before. Still contains no passage citations; the citation-compliance goal is not met here. |
| q20 | Complete | Complete | Concise supported clinician preference finding with correct 136:85 and 106:64 margins and citation. |
| q21 | Complete | Complete | Both relevant papers are correctly identified with cited descriptions. Still adds a third bullet repeating the survey framework and exceeds the 70-word target. |
| q22 | Complete | Complete | Both benchmark papers and their roles are correct, and citations return. Citations are embedded near titles instead of ending the claims; the explicit evaluation of both Router and Bidder is in source [5], while the first bullet cites [4]. Still exceeds the length target. |
| q23 | Complete | Complete | Correctly identifies TMI and G-CARL without the longer candidate’s false claim that G-CARL induces auditable task models. Repeats TMI in two bullets; [2] would support its auditability more directly than [1]. |
| q24 | Correct abstention | Correct abstention | Correctly declines the unsupported KPMG forecast using the required exact sentence. |
| q25 | Correct abstention | Correct abstention | Correctly declines the unsupported NVIDIA stock price using the required exact sentence. |

## Answers and source checks

Source excerpts are literal saved passages shortened to 300 characters; full passages are available in the `manual_review_grouped_concise_full` worksheet.

<details><summary>q01 — How does Pandora's Router decide when an expensive specialist estimate is worth paying for?</summary>

**Answer:**

Pandora's Router decides when an expensive specialist estimate is worth paying for by computing reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate. This is done by running the specialist for a few reasoning tokens and checking if it is on the right track [1]. The system then chooses the maximizer of the observed value estimate [1].

**Assessment:** Correct value-of-information principle and final selection, but still omits reservation-price inspection order and the explicit stopping rule. First factual sentence has no adjacent citation.

**Source [1] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value e…

</details>

<details><summary>q02 — What is the difference between Pandora's Router and Pandora's Bidder?</summary>

**Answer:**

Pandora's Router is a centralized policy that queries the more accurate value estimate 𝑔𝑚(𝑥) when the value of information exceeds the cost, while Pandora's Bidder is a decentralized policy where specialists use value-of-information reasoning to decide whether to refine their self-assessments before accepting a posted price. [1][3]

**Assessment:** Correct centralized versus decentralized distinction, but omits the Router’s global-welfare objective and local-surplus trade-off. Concise but less complete.

**Source [1] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value e…

**Source [3] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> we measure the regret versus an oracle that knows𝐺𝑚 for free. Results.Figure3plotsallocativeefficiencyandbiddersurplusfordifferent 𝑐𝑔. Pandora’sBidderclosely tracks the lower envelope of the regret of the two baselines across the full𝑐𝑔 range. When𝑐𝑔 is low, the bidder frequently refines its estimat…

</details>

<details><summary>q03 — In which three domains was the costly-value-estimation routing policy evaluated?</summary>

**Answer:**

The costly-value-estimation routing policy was evaluated in the following three domains:

• Multi-LLM routing benchmark (EmbedLLM)
• Retrieval-augmented specialists for factoid QA
• Inference-time computation for mathematical reasoning

[3][4]

**Assessment:** Correct three domains; citations appear on a separate line after the list instead of each bullet.

**Source [3] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> Bidder: each specialist faces a posted price—the current best competing offer—and must decide whether to invest in a more accurate self-assessment before claiming the query. This corresponds to a single stage of the ascending-price mechanism with costly preference elicitation studied by Parkes (2005…

**Source [4] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> 2026-08-21 Pandora’s AI Model Routing Box: Efficient Allocation with Costly Value Estimation Adam Fisch, Shubhendu Trivedi, Fantine Huot, William W. Cohen, Michael Kaisers, Mirella Lapata, Kate Larson, Jacob Eisenstein Google DeepMind Heterogeneous AI systems composed of multiple models, architectur…

</details>

<details><summary>q04 — What limitation appears when competing specialists' estimates are noisy?</summary>

**Answer:**

When competing estimates are noisy, value-of-information reasoning can increase the strategic specialist's utility at the expense of others. This is because the noisy estimates can lead to incorrect decisions, benefiting the strategic specialist but harming others. [1]

**Assessment:** Correct possible harm from noisy competing estimates, without the longer candidate’s categorical claim. Second sentence repeats the point and citation follows only the second sentence.

**Source [1] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> benchmark, retrieval-augmented specialists, and LLMs with variable inference-time reasoning—show that Pandora’s Router matches the routing quality of exhaustive estimation, while querying the expensive estimator far less often. In the decentralized setting, value-of-information reasoning improves al…

</details>

<details><summary>q05 — How many frozen repositories and training algorithm families are in AI4AI-Bench?</summary>

**Answer:**

• 10 frozen repositories [2]
• 10 distinct families of training algorithm [1]

**Assessment:** Directly gives ten repositories and ten algorithm families as two cited bullets.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> The suite is ten frozen research repositories, listed in Table 1 and chosen so that between them they cover ten families of training algorithm rather than ten instances of one: supervised fine-tuning, multi-turn agentic RL, on-policy distillation, Bradley–Terry reward modeling, preference optimizati…

**Source [1] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> are kept. An evaluator fixed before the first run, with no access to the agent’s workspace, scores them, and the cell takes the best of the three under the task’s direction; for the two tasks that do not train, the twelve hours are only a ceiling on the verification stage (2.3).Bottom:the ten frozen…

</details>

<details><summary>q06 — What is the AI4AI-Bench time budget for an agent and for the replay?</summary>

**Answer:**

The AI4AI-Bench time budget for an agent is 4 hours on one B300 GPU [2]. The time budget for the replay is 12 hours [3].

**Assessment:** Correct four-hour agent budget and twelve-hour replay budget, with sentence-level citations.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> Each task presents an agent with a research repository, a base model to start from, and an inexpensive proxy metric that can be evaluated freely during development 2.2. The agent is given 4 hours on one B300 GPU and a single objective: improve the training algorithm implemented in the repository. It…

**Source [3] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> Recursive self-improvement compounds through the algorithmic link, and AI4AI-Bench is built to measure that link on its own: ten frozen research repositories, each asking an agent to improve the training algorithm it already applies to its own model, with four hours to write code, twelve to run what…

</details>

<details><summary>q07 — How are the incommensurable AI4AI-Bench task metrics normalized?</summary>

**Answer:**

The incommensurable AI4AI-Bench task metrics are normalized to a scale where 0 is an uninformative model, 0.1 is the algorithm the repository ships, and 1.0 is the task optimum. [2]

**Assessment:** Correct 0, 0.1 and 1.0 normalization anchors, with a supporting citation.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> incommensurable, every task is mapped onto one scale on which0is an uninformative model,0 .1is the algorithm the repository ships, and1.0 is the task optimum. Across 29 configurations of 6 systems on all 10 tasks the mean score is0.166, and the best system reaches0.250: even the strongest closes und…

</details>

<details><summary>q08 — How do submissions that change the learning algorithm compare with those that do not?</summary>

**Answer:**

• Submissions that change the learning algorithm average 0.226 against 0.126 for those that do not. [2]
• The share of submissions that touch the learning algorithm rises from 8.0% to 64.0% when reasoning effort is increased. [4]
• Submissions that change the learning algorithm are stronger to begin with, but the gap is the difference between those that go there and those that do not. [3]

**Assessment:** Now gives the key 0.226 versus 0.126 scores without calling them statistically significant. However, the caveat says submissions were stronger to begin with; source [3] says the systems producing them were stronger. Adds unrequested reasoning-effort statistics. This is a substantial improvement over missing the scores, but not a fully precise comparison.

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> …tive, the supervision signal, the learning rule, the data — average0.226 against0 .126for the rest: the algorithmic layer is where the distance gets closed, and most submissions never go there. More reasoning effort moves agents towards it, taking that share from8%to64%and the mean score from0 .094t…

**Source [3] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> …in this corpus. It is also not a randomized comparison: the systems that reach the learning procedure more often are the stronger ones to begin with, so the gap is the difference between the submissions that go there and the submissions that do not, rather than the effect of going there. Read togeth…

</details>

<details><summary>q09 — What two kinds of task structure does TMI recover from computer-use traces?</summary>

**Answer:**

TMI recovers two kinds of task structure: objective models and procedure models. Objective models are hierarchical decompositions of the objective of a task into subobjectives, while procedure models are trace-grounded compositions of control-flow operators specifying how the execution of a task is organized. [3]

**Assessment:** Correct objective hierarchy and procedure/control-flow explanation. Citation remains at paragraph end rather than after each factual sentence.

**Source [3] — Inducing Task Models from Computer-Use Traces:**

> Describing the activity conducted in a computeruse session is necessary for analyzing, learning, and auditing it. We formalize this process as the recovery, from a naturalistic computer-use trace, of the latent tasks and their task models specifying the objectives and procedures. Let X=⟨x 1, x2, . .…

</details>

<details><summary>q10 — How well does task model induction group interleaved tasks?</summary>

**Answer:**

Our method recovers interleaved tasks with 0.974 agreement against ground-truth task groupings [2].

**Assessment:** Correct 0.974 grouping agreement without unrelated metric comparisons. Still copies first-person wording from the paper.

**Source [2] — Inducing Task Models from Computer-Use Traces:**

> into semantic actions and activities, bridging low-level signal and local intent (3.1).Latent task inductionuntangles the multi-threaded activity stream, discovering tasks and assigning possibly non-contiguous activities to each without a pre-specified task set (3.2).Task model constructionbuilds ea…

</details>

<details><summary>q11 — How much of observed execution does TMI reconstruct?</summary>

**Answer:**

TMI reconstructs 74.9% of observed execution steps. [4]

**Assessment:** Correct 74.9% result, now includes its metric label and citation.

**Source [4] — Inducing Task Models from Computer-Use Traces:**

> into semantic actions and activities, bridging low-level signal and local intent (3.1).Latent task inductionuntangles the multi-threaded activity stream, discovering tasks and assigning possibly non-contiguous activities to each without a pre-specified task set (3.2).Task model constructionbuilds ea…

</details>

<details><summary>q12 — What was the held-out task accuracy gain from skills derived from TMI?</summary>

**Answer:**

The held-out task accuracy gain from skills derived from TMI was 30% relative accuracy gain, from 14.29 to 18.57. [1]

**Assessment:** Concise correct 30% relative accuracy gain from 14.29 to 18.57, with citation.

**Source [1] — Inducing Task Models from Computer-Use Traces:**

> Exec. Safe. Align. Acc. No skill N/A N/A N/A 59.20 8.57 Human curated 93.59 63.80 90.50 56.59 10.00 Raw demonstration 52.46 53.4992.5263.15 11.43 Workflow summary 54.07 59.35 91.74 66.18 14.29 Ours54.95 67.6590.5767.99 18.57 The task model is an effective representation for skill transfer.Skills gen…

</details>

<details><summary>q13 — How many commuters and respondent-scenario observations did the weather travel survey collect?</summary>

**Answer:**

The survey collected 92 McGill student commuters. The final processed dataset contained 454 valid respondent–scenario observations. [2][3]

**Assessment:** Correct 92 commuters and 454 observations, but citations still follow both sentences together.

**Source [2] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> The Data Collection Agent was implemented as a purpose-built conversational chatbot,Travel- BehaviorSurveyBot, developed in Voiceflow and deployed as a web application accessible through a public link and QR code (Figure 2). Respondents completed the survey on their own devices through a guided dial…

**Source [3] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> The Data Processing Agent converted the chatbot’s raw, JSON-encoded response export into an analysis-ready dataset. Processing steps included parsing nested list- and slider-valued fields, validating and recoding categorical responses, constructing derived features, and flagging incomplete or incons…

</details>

<details><summary>q14 — Which travel modes responded most clearly to adverse weather and snow?</summary>

**Answer:**

Cycling was particularly sensitive to adverse weather, while public transit use increased substantially under the Snowy scenario [4].

**Assessment:** Correct cycling and transit findings in one cited sentence.

**Source [4] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> Travel-behavior research increasingly combines digital data collection with predictive modeling, yet these stages are often developed and evaluated separately. This study proposes and applies a three-agent workflow integrating conversational data collection, structured data processing, and behaviora…

</details>

<details><summary>q15 — How did random forest and the best text-only zero-shot LLM compare on five-class travel prediction?</summary>

**Answer:**

Random forest achieved a 69.6% five-class accuracy, while the best text-only zero-shot LLM reached 69.9% without task-specific fitting. [4]

**Assessment:** Concise comparison with correctly assigned 69.6% and 69.9% five-class accuracies, plus the supported no-task-specific-fitting qualification.

**Source [4] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> Travel-behavior research increasingly combines digital data collection with predictive modeling, yet these stages are often developed and evaluated separately. This study proposes and applies a three-agent workflow integrating conversational data collection, structured data processing, and behaviora…

</details>

<details><summary>q16 — What was the best vision-based travel mode prediction accuracy?</summary>

**Answer:**

The best vision-based travel mode prediction accuracy was 71.5% [2]. This was achieved by the best vision-based configuration, which used the same generated weather images shown to respondents [3].

**Assessment:** Correct 71.5% accuracy with supporting citations. Extra image-context sentence is supported but not required.

**Source [2] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> and the best vision-based configuration reached the highest observed five-class accuracy of 71.5%, indicating that visual context can provide additional predictive information for selected models. Taken together, the findings show that habitual travel information, prompting strategy, demonstrations,…

**Source [3] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> labeled travel-behavior data are limited, although the small sample and multiple evaluated configurations require cautious interpretation. The five-class task provides a clearer assessment of whether models distinguish among individual modes. Vision-based prediction.The vision experiments directly c…

</details>

<details><summary>q17 — What is the patient-oriented medical report interpretation task introduced with G-CARL?</summary>

**Answer:**

The patient-oriented medical report interpretation task, PMRI, is a novel open-ended multimodal generation task that requires models to explain medical reports in accurate and accessible language based on a user's query and dialogue history. [3] This task differs from existing medical vision-language tasks in that it requires both evidence-grounded medical factuality and context-dependent patient communication. [2]

Key properties of PMRI:
- Requires models to explain medical reports in accurate and accessible language
- Based on a user's query and dialogue history
- Combines evidence-grounded medical factuality and context-dependent patient communication

**Assessment:** Core PMRI definition is supported, but repeats it as three uncited bullets after two cited sentences. Fails the intended brevity and per-bullet citation format.

**Source [3] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> Personalized interpretation of medical reports has emerged as an increasingly important need among patients. Addressing this need requires both evidence-grounded medical factualityandcontext-dependentpatientcommunication,yetexisting medical vision-language tasks do not adequately capture these dual …

**Source [2] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> In this paper, we present PMRI as a challenging yet underexplored task that requires both evidence-grounded medical factualityandcontext-dependentpatientcommunication.We propose G-CARL, a reinforcement learning framework that decomposes reward supervision through retrieval-grounded claim verificatio…

</details>

<details><summary>q18 — How does G-CARL supervise factuality and response coverage?</summary>

**Answer:**

G-CARL supervises factuality through a retrieval-grounded claim reward that provides fine-grained supervision for medical factuality through atomic claim verification [1]. It supervises response coverage through a case-specific checklist reward that explicitly supervises demand satisfaction and expression quality without relying on a single reference response [1]. This reward is constructed through MLLM generation followed by clinician-guided refinement [4].

**Assessment:** Correct atomic claim verification and case-specific checklist supervision. Still omits explicit multi-source datastore support and does not spell out the weighted checklist construction; citations are present per sentence.

**Source [1] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> reward provides localized supervision for sparse factual errors and discouragesunsupportedelaboration.Forcontext-dependent objectives such as demand satisfaction and expression quality,G-CARLconstructsinstance-specificweightedchecklists throughMLLMgenerationfollowedbyclinicianrefinement. Each checkl…

**Source [4] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> BuiltuponGRPO,G-CARLoptimizesthepolicymodelwith three reward signals, as illustrated in Fig. 2. Given uploaded medical report imagesI, the dialogue historyh, and a user queryq,thepolicymodelfirstgeneratescandidateresponses. The retrieval-grounded branch then supervises medical factuality by verifyin…

</details>

<details><summary>q19 — What benchmark and evaluation dimensions accompany G-CARL?</summary>

**Answer:**

The benchmark accompanying G-CARL is MMedReport, a real-world multimodal PMRI benchmark, and CMB, an external benchmark that evaluates both medical QA accuracy and the professionalism of open-ended clinical interpretation. The evaluation dimensions for PMRI responses include Medical Accuracy, Demand Satisfaction, and Expression Quality.

**Assessment:** Correct benchmark names and evaluation dimensions, and shorter than before. Still contains no passage citations; the citation-compliance goal is not met here.

**Source [1] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> Datasets.We evaluate G-CARL primarily on(1)MMedReport, a real-world multimodal PMRI benchmark collectedfromonlinehealthcareconsultations.Itcontains2,450 instances, each including dialogue history, a user query, uploaded medical report images, and clinician-verified reference annotations. All instanc…

</details>

<details><summary>q20 — What did clinician pairwise preferences find about G-CARL?</summary>

**Answer:**

G-CARL was consistently preferred over both SFT and MLLM-as-a-Judge, particularly in medical accuracy and demand satisfaction, with preference margins of 136:85 and 106:64, respectively. [1]

**Assessment:** Concise supported clinician preference finding with correct 136:85 and 106:64 margins and citation.

**Source [1] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> andproducesclinicallyaccurateinterpretations.Similarly,in therightexample,SFTfailstoincorporatetheuser’ssmoking andalcoholcessationhistory,whileMLLM-as-a-Judgefails toaddresstheuser’sprimaryconcernofwhethertocontinue themedication.Incontrast,ourmethodeffectivelyintegrates historical context, directl…

</details>

<details><summary>q21 — Which papers address auditable AI workflows derived from user activity or survey responses?</summary>

**Answer:**

• Inducing Task Models from Computer-Use Traces introduces TASKMODELINDUCTION(TMI), which induces task models from computer-use traces, producing auditable and reusable models of how everyday work is done. [1]
• An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction proposes a multi-agent framework that integrates data collection, data processing, and behavioral modeling, producing structured and auditable outputs. [2]
• The framework in An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction connects AI-assisted behavioral data collection with travel-choice modeling and LLM-based prediction, providing a reproducible basis for exploring AI-assisted travel-behavior research. [4]

**Assessment:** Both relevant papers are correctly identified with cited descriptions. Still adds a third bullet repeating the survey framework and exceeds the 70-word target.

**Source [1] — Inducing Task Models from Computer-Use Traces:**

> Naturalistic computer-use traces, passively recorded screenshots and mouse or keyboard actions, are a valuable resource for deriving symbolic, auditable, and reusable models of how everyday work is done. Such models matter as computer-use agents enter real work, where agents need to learn how tasks …

**Source [2] — An Agentic Approach for Active Data Collection, Travel Behavior Modeling, and Weather-Sensitive Demand Prediction:**

> We propose a multi-agent framework that integrates data collection, data processing, and behavioral modeling for commuter mode-choice research. The framework consists of three specialized agents: a Data Collection Agent, a Data Processing Agent, and a Data Modeling Agent. The agents perform distinct…

</details>

<details><summary>q22 — Which papers evaluate AI agents or model specialists using benchmark tasks and costs?</summary>

**Answer:**

• Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation [4] evaluates both Pandora’s Router and Pandora’s Bidder across three domains, including a multi-LLM routing benchmark and retrieval-augmented specialists for factoid QA.
• AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement [2] presents a benchmark that isolates the ability of an agent to design training algorithms, and [3] describes the benchmark's evaluation process, where agents rewrite training algorithms and their code is rerun from scratch for up to 12 hours.

**Assessment:** Both benchmark papers and their roles are correct, and citations return. Citations are embedded near titles instead of ending the claims; the explicit evaluation of both Router and Bidder is in source [5], while the first bullet cites [4]. Still exceeds the length target.

**Source [4] — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation:**

> 2026-08-21 Pandora’s AI Model Routing Box: Efficient Allocation with Costly Value Estimation Adam Fisch, Shubhendu Trivedi, Fantine Huot, William W. Cohen, Michael Kaisers, Mirella Lapata, Kate Larson, Jacob Eisenstein Google DeepMind Heterogeneous AI systems composed of multiple models, architectur…

**Source [2] — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement:**

> equations , AutoML-Zero evolves learning algorithms from primitive operations , and symbolic program search discovered Lion . These works establish that algorithmic design can be automated, but each demonstrates a method inside a compact search space and short proxy tasks; none is a benchmark of whe…

</details>

<details><summary>q23 — Which papers discuss evidence-grounded explanations and auditable task models?</summary>

**Answer:**

• Inducing Task Models from Computer-Use Traces discusses auditable task models [1].
• Inducing Task Models from Computer-Use Traces also discusses evidence-grounded explanations [1].
• G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation discusses evidence-grounded explanations [4].

**Assessment:** Correctly identifies TMI and G-CARL without the longer candidate’s false claim that G-CARL induces auditable task models. Repeats TMI in two bullets; [2] would support its auditability more directly than [1].

**Source [1] — Inducing Task Models from Computer-Use Traces:**

> Modeling a task t requires understanding the two types of evidence it carries, procedure and objective. Constructing a task model thus means inducing an objective model Ot and a procedure model Pt from the activities Et of each discovered task t, then reconciling them into the task model Mt (Figure …

**Source [4] — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation:**

> explanations grounded inmultimodalreportsandextendedpatient–doctordialogue. cation by transforming report evidence into accessible explanations, addressing user-specific concerns, and offering clinically cautious guidance. As illustrated in Fig. 1, PMRI differs from conventional medical visual quest…

</details>

<details><summary>q24 — What is KPMG's 2026 revenue forecast?</summary>

**Answer:**

The provided papers do not address this question.

**Assessment:** Correctly declines the unsupported KPMG forecast using the required exact sentence.

</details>

<details><summary>q25 — Which of these papers reports the stock price of NVIDIA on October 14, 2026?</summary>

**Answer:**

The provided papers do not address this question.

**Assessment:** Correctly declines the unsupported NVIDIA stock price using the required exact sentence.

</details>
