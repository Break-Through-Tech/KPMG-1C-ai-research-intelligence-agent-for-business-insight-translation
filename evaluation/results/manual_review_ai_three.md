# Answer review worksheet

3 answers · automatic checks complete · content awaits manual review.

Checklists are assistant-prepared and pending human approval. Automatic checks do not establish factual accuracy.

## q08 — Manual review needed

How do submissions that change the learning algorithm compare with those that do not?

**Answer:** Submissions that change the learning algorithm (122 submissions) do not differ significantly from those that do not (141 submissions) in terms of the number of submissions that reach the learning procedure, with 46.4% of the former and 53.6% of the latter reaching the procedure. [3]  The provided passages do not provide a direct comparison between the two groups.

**Automatic findings:** Check figures against their sources.

**Check these points:**

- [ ] Reports a mean normalized score of 0.226 for submissions that change the learning algorithm.
- [ ] Reports 0.126 for the rest and correctly identifies the former as higher, without claiming a causal effect.

**Sources found:** 1 of 1 expected papers. This measures paper retrieval, not whether the answer uses the right evidence.

**Source previews** — copied from saved passages, at most 240 characters each. Selected by word overlap for navigation; inspect full passages to verify claims.

**Source 1**

> Everything so far has been a score, and a score says only whether a submission worked. It does not say whether the agent designed an algorithm or tuned one that was already there, and those are the two outcomes this paper exists to…

**Source 2**

> optimum. The submissions say where the remaining distance went. Of the 263 that change anything, 141 leave the learning procedure exactly as they found it and move budgets, checkpointing, hyperparameters and capacity instead. The 122 that…

<details><summary>Full sources and automatic checks</summary>

**Source 1 — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement**

Everything so far has been a score, and a score says only whether a submission worked. It does not say whether the agent designed an algorithm or tuned one that was already there, and those are the two outcomes this paper exists to separate. Counting lines does not separate them either: a one-line diff can replace a learning rule, and a thousand-line refactor can leave the training procedure exactly as it was. The distinction has to be read off the submitted code, by asking which part of the training procedure it modifies. We group every change into eight families on two sides of that line (Table 4). The grouping is assigned by a separate language model reading each submitted diff against the definitions that follow. Four changehow this run goes: how long it trains and how often it saves; the training hyperparameters, such as the learning rate or the batch size; which of the checkpoints it produced to keep; and how much trainable capacity to attach and where, such as the rank and placement of an adapter. Four changehow the model learns: the loss it optimizes, by adding, removing or reweighting a term; the supervision it learns from, by introducing a signal the procedure did not have before; the update rule itself, replaced by a different one; and the data the procedure trains on. The families are not exclusive — a submission matches3.13of them on average, since changing a loss usually drags a hyperparameter along with it — so we report how many submissions reach a side rather than assigning each to a single family. Of the 280 submissions, 17 made no change that could be classified. Of the remaining 263, 141 stay entirely on the run

**Source 2 — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement**

optimum. The submissions say where the remaining distance went. Of the 263 that change anything, 141 leave the learning procedure exactly as they found it and move budgets, checkpointing, hyperparameters and capacity instead. The 122 that do reach it — the objective, the supervision signal, the learning rule, the data — average0.226 against0 .126for the rest: the algorithmic layer is where the distance gets closed, and most submissions never go there. More reasoning effort moves agents towards it, taking that share from8%to64%and the mean score from0 .094to0 .196, which is most of what effort buys. A machine learning scientist reads the training dynamics, names the mechanism that is failing, and changes that mechanism; few of these submissions do. In summary, we make the following contributions: • A benchmark that isolates the algorithmic level.Ten research repositories spanning ten families of training algorithms, evaluated under a unified protocol that separates a four-hour agent development window from the up to twelve-hour clean-start training run used for scoring. • A measurement of what agentsdo, not only whether they win.Every submission is classified by what it changes, which is what turns “the agent improved the training algorithm” into a checkable statement rather than a restatement of the score. • Revealing a gap between algorithmic exploration and actual improvement.The algorithmic design level is where the distance to a better algorithm is closed and the one these agents reach least often, and more reasoning effort mostly buys the willingness to reach it.

**Source 3 — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement**

how much trainable capacity, and where 73 27.8% learning the loss it optimizes 87 33.1% the supervision it learns from 66 25.1% the update rule itself 23 8.7% the data it trains on 21 8.0% any learning family 122 46.4% run side only141 53.6% reaching the learning sidenone low medium high xhigh max share of submissions 8% 39% 33% 49% 65% 64% ordering holds within four of the five models in this corpus. It is also not a randomized comparison: the systems that reach the learning procedure more often are the stronger ones to begin with, so the gap is the difference between the submissions that go there and the submissions that do not, rather than the effect of going there. Read together, the two numbers say that the algorithmic layer is where the distance actually gets closed, and that most submissions never go to it. What separates a submission that reaches that layer from one that does not is not effort spent but a step taken first: reading the training dynamics as a specific failure mechanism, and then addressing that mechanism.

**Source 4 — AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement**

Is there anything that pushes agents down to that layer? The setup has exactly one knob that can be turned on its own, the reasoning-effort level, and taking it from the lowest setting to the highest shows clearly what it buys and what it does not. It buys nerve. The share of submissions that touch the learning algorithm rises from8.0%to64 .0%. At low effort the submissions move budgets, logging and optimization knobs; at high effort they operate on objectives, replace learning rules, and add supervision to the procedure. It buys attempts. Within the Codex grid, the only one that exposes the lowest setting, the median configuration goes from 4 evaluations inside its four hours to 16, from 18 edited lines to 246, and from11k output tokens to 109k. Cost follows: the median exploration cost per task rises from $1.69 to $34.60. The exploration stage of the whole evaluation consumed $5,334 of API calls, with Kimi K3 converted from Chinese yuan and with neither the GPU hours of the twelve-hour runs nor the evaluator’s compute included. It buys completion. Of the 19 cells that score zero, 8 ended their four hours without a usable patch — four of them workspaces the host found empty after the agent exited early — and 11 submitted a complete patch that started its twelve-hour run but finished with nothing satisfying the contract, most often no loadable merged model written to disk. All 19 terminated normally: the failure is in what the agent submitted. They concentrate at low effort, with 12 of the 19 at the two lowest levels and one each at the two highest. And it does buy a result, though a small one

Source references exist; whether they support each claim still needs review.

Check figures against their sources.

Answer is 57 words; the review target is at most 120.


</details>

## q09 — Manual review needed

What two kinds of task structure does TMI recover from computer-use traces?

**Answer:** TMI recovers two kinds of task structure: objective models and procedure models. [3][2]  The objective model is a hierarchical decomposition of the objective of a task into subobjectives the user pursues. [3]  The procedure model is a trace-grounded composition of control-flow operators specifying how the execution of a task is organized through sequencing and iteration. [3]

**Automatic findings:** No mechanical issues flagged. This does not mean the answer is correct.

**Check these points:**

- [ ] Identifies a hierarchical objective model of recursive goal decomposition.
- [ ] Identifies a procedure model representing execution control flow.

**Sources found:** 1 of 1 expected papers. This measures paper retrieval, not whether the answer uses the right evidence.

**Source previews** — copied from saved passages, at most 240 characters each. Selected by word overlap for navigation; inspect full passages to verify claims.

**Source 1**

> TMI recovers task models from raw computer-use traces in three stages (Figure 2).Event grounding and activity segmentationrecovers what each event did from its visual context and groups the grounded events into semantic actions and…

**Source 3**

> …axes. • Theobjective model Ot is a hierarchical decomposition of the objective of t into the subobjectives the user pursues. • Theprocedure model Pt is a trace-grounded composition of control-flow operators specifying how the execution…

<details><summary>Full sources and automatic checks</summary>

**Source 1 — Inducing Task Models from Computer-Use Traces**

TMI recovers task models from raw computer-use traces in three stages (Figure 2).Event grounding and activity segmentationrecovers what each event did from its visual context and groups the grounded events into semantic actions and activities (3.1). Latent task inductiondiscovers the tasks pursued in the session and assigns each activity to the task it realizes (3.2).Task model constructionbuilds complementary objective and procedure models for each task and reconciles them into a single task model, in which every node pairs an objective with the control-flow operator over its children (3.3).

**Source 2 — Inducing Task Models from Computer-Use Traces**

We introduced TASKMODELINDUCTION, which abstracts raw computer-use events into activities, discovers the latent tasks they realize, and reconciles separately induced objective and procedure models into one task model per task. It turns everyday computer-use activity traces into durable, auditable records of how work are carried out. Experiments show that this representation recovers interleaved execution faithfully and yields better downstream agent skills than raw traces or workflow summaries. TMI has the potential to facilitate the study of how work is carried out across domains and to make these records reusable as knowledge for both people and agents.

**Source 3 — Inducing Task Models from Computer-Use Traces**

Describing the activity conducted in a computeruse session is necessary for analyzing, learning, and auditing it. We formalize this process as the recovery, from a naturalistic computer-use trace, of the latent tasks and their task models specifying the objectives and procedures. Let X=⟨x 1, x2, . . . , xN ⟩ be a user’s computeruse trace in an interactive computer environment, where each event xi = (si, ai, τi) contains the state represented as a screenshot si, a low-level operation (e.g.,click), and a timestampτ i. The trajectory reflects the user pursuing a set of latent tasks T={t 1, t2, . . .}, where a possibly non-contiguous subsequence of events collectively realizes a task tj. However, inducing these latent tasks remains an open challenge, as none of the tasks, their boundaries, or the event-to-task assignments are predefined in realistic human traces. We define the induction problem as jointly discovering the set of latent tasks T and, for each task t∈ T, inducing a task model Mt that unifies two complementary axes. • Theobjective model Ot is a hierarchical decomposition of the objective of t into the subobjectives the user pursues. • Theprocedure model Pt is a trace-grounded composition of control-flow operators specifying how the execution of t is organized through sequencing and iteration. The task model Mt is structured as a tree, whose every node pairs an objective with a control-flow operator over its children.

**Source 4 — Inducing Task Models from Computer-Use Traces**

Naturalistic computer-use traces, passively recorded screenshots and mouse or keyboard actions, are a valuable resource for deriving symbolic, auditable, and reusable models of how everyday work is done. Such models matter as computer-use agents enter real work, where agents need to learn how tasks are actually performed, and organizations need to audit and reuse that knowledge. However, inducing such task models is challenging, as activity is observed only as low-level events and realworld work is multi-threaded with interleaved goals. Existing methods assume a given task or a single workflow, and produce step-level summaries rather than structured task models. We introduce TASKMODELINDUCTION(TMI), which (i) discovers the latent tasks in an unconstrained trace, disentangling concurrent activity, and (ii) for each latent task, induces a task model pairing a hierarchical objective model of recursive goal decomposition with a procedure model of the control flow that organized the execution. Intrinsically, on controlled human and agent trajectories, TMI recovers interleaved tasks with 0.974 agreement against ground-truth groupings and reconstructs 74.9% of the observed execution steps, far more than the strongest workflow induction baseline. Extrinsically, skills derived from TMI’s task models improve held-out task accuracy by 30.0% over the strongest baseline. 1

Source references exist; whether they support each claim still needs review.

Answer is 53 words; the review target is at most 120.


</details>

## q18 — Manual review needed

How does G-CARL supervise factuality and response coverage?

**Answer:** G-CARL supervises factuality through a retrieval-grounded branch that verifies report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality reward Rfact (Sec. 3.2).   It also constructs a case-specific weighted checklist through MLLM generation followed by clinician-guided refinement, and evaluates the checklist coverage of the generated response to produce the checklist reward Rcheck (Sec. 3.3).

**Automatic findings:** Add source references to the answer itself. Check figures against their sources.

**Check these points:**

- [ ] Explains multi-source retrieval for verifying atomic claims.
- [ ] Explains context-aware, instance-specific weighted checklists for covering user needs/response content.

**Sources found:** 1 of 1 expected papers. This measures paper retrieval, not whether the answer uses the right evidence.

**Source previews** — copied from saved passages, at most 240 characters each. Selected by word overlap for navigation; inspect full passages to verify claims.

**Source 3**

> verification with context-aware, instance-specific weighted checklists for response coverage, providing structured supervision for factuality, user-demand satisfaction, and expression quality without constraining response diversity. We…

**Source 4**

> …historyh, and a user queryq,thepolicymodelfirstgeneratescandidateresponses. The retrieval-grounded branch then supervises medical factuality by verifying report-grounded medical claims against evidence retrieved from a multi-source…

<details><summary>Full sources and automatic checks</summary>

**Source 1 — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation**

reward provides localized supervision for sparse factual errors and discouragesunsupportedelaboration.Forcontext-dependent objectives such as demand satisfaction and expression quality,G-CARLconstructsinstance-specificweightedchecklists throughMLLMgenerationfollowedbyclinicianrefinement. Each checklist item is assigned an automatically generated weight, allowing the reward to emphasize the aspects most relevant to the current report and user question. This yields an explicit checklist score that provides transparent supervision for whether the response addresses the user’s concern appropriately. In summary, our contributions are as follows: •WeformulatePMRIasanevidence-groundedandpatientfacingmultimodalgenerationtask,andproposeG-CARL, a reinforcement learning framework that decomposes reward supervision according to the heterogeneous verifiability of different objectives. •We propose a retrieval-grounded claim reward that provides fine-grained supervision for medical factuality through atomic claim verification, and a case-specific checklist reward that explicitly supervises demand satisfactionandexpressionqualitywithoutrelyingonasingle reference response. •We constructMMedReport, a real-world PMRI benchmark with clinician-designed evaluation protocols. Extensive experiments across multiple LVLM backbones demonstrate that G-CARL consistently outperforms supervised and reinforcement learning baselines, with the gains further validated by clinician preference and user comprehension studies.

**Source 2 — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation**

In this paper, we present PMRI as a challenging yet underexplored task that requires both evidence-grounded medical factualityandcontext-dependentpatientcommunication.We propose G-CARL, a reinforcement learning framework that decomposes reward supervision through retrieval-grounded claim verification and case-specific checklist guidance. ExtensiveexperimentsonthenewlyconstructedMMedReport benchmark, together with clinician-authored evaluation and human preference studies, show that G-CARL consistently improves the quality of patient-oriented medical report interpretation.Wehopethisworklaysthefoundationformore reliable and patient-centered multimodal medical assistants.

**Source 3 — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation**

Personalized interpretation of medical reports has emerged as an increasingly important need among patients. Addressing this need requires both evidence-grounded medical factualityandcontext-dependentpatientcommunication,yetexisting medical vision-language tasks do not adequately capture these dual requirements. To bridge this gap, we introducePatient-orientedMedicalReportInterpretation(PMRI), a novel open-ended multimodal generation task that requires models to explain medical reports in accurate and accessible language based on a user’s query and dialogue history. Thesetwoobjectivesdifferfundamentallyintheirverifiability, yet remain tightly coupled, making them difficult to optimize jointly under conventional supervised fine-tuning and holistic reinforcement learning paradigms. To address this challenge, we propose G-CARL, a grounded, checklist-aligned reinforcementlearningframeworkthatcombinesmulti-source retrieval for atomic claim verification with context-aware, instance-specific weighted checklists for response coverage, providing structured supervision for factuality, user-demand satisfaction, and expression quality without constraining response diversity. We further constructMMedReport, a realworld PMRI benchmark, along with a clinician-designed three-dimensionalevaluationprotocol.Extensiveexperiments demonstrate that G-CARL consistently outperforms existing post-training baselines in overall quality, claim-level precision, and checklist recall. Pairwise preference evaluation by clinicians further confirms that G-CARL produces interpretations that are more accurate and better aligned with patient needs.

**Source 4 — G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation**

BuiltuponGRPO,G-CARLoptimizesthepolicymodelwith three reward signals, as illustrated in Fig. 2. Given uploaded medical report imagesI, the dialogue historyh, and a user queryq,thepolicymodelfirstgeneratescandidateresponses. The retrieval-grounded branch then supervises medical factuality by verifying report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality rewardRfact (Sec. 3.2). In parallel, the case-specific checklist branch optimizes demand satisfaction and expression quality by constructing a weighted checklist through MLLM generation followed by clinicianguided refinement, and evaluating the checklist coverage of thegeneratedresponsetoproducethechecklistrewardR check (Sec. 3.3). Together with the format rewardRformat, these components are integrated into a multi-objective optimization task (Sec. 3.4).

Add source references to the answer itself.

Check figures against their sources.

Answer is 58 words; the review target is at most 120.


</details>
