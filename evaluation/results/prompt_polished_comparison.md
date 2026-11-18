# Polished prompt versus baseline — six-answer comparison

**Decision: do not treat this prompt as an improvement yet.** It improves q01, regresses q02, leaves q08 incorrect with worse citation coverage, and leaves q03/q09/q18 largely unchanged. No prompt was reverted or edited during this experiment.

This is an assistant assessment against the exact saved passages, not an LLM-judge score or independent human review. These six selected examples are diagnostic, not a system-wide accuracy estimate.

**Controls verified:** same llama3.2 model weights, temperature 0, seed 42, context/output limits, benchmark, and exact passage text/order for every question. Both baselines used the same original prompt. The q08/q09/q18 runner hash matches this run; the earlier q01/q02/q03 runner hash differs because question-selection support was added later, so this is not a byte-identical replay of that older runner.

**Results:** answers containing any passage citation fell from **4/6 to 3/6** (presence is not proof of support). Recorded generation time was **39.2s before versus 37.4s after**; single runs on different occasions are insufficient for a speed claim.

| Question | Assessment | Main finding |
| --- | --- | --- |
| q01 | Improved, still incomplete | Stopping rule added; still missing inspection order/selection. |
| q02 | Regressed | Introduces a Router/Margin attribution error and excessive detail. |
| q03 | Unchanged | Correct domains; still no citations. |
| q08 | Still incorrect; citation regression | Still misses 0.226 vs 0.126; now no citation. |
| q09 | Essentially unchanged | Both structures remain correct and cited. |
| q18 | Essentially unchanged | Both mechanisms remain correct; still no citations. |

**Next experiment:** a shorter, explicit comparison format that names each method/group, its metric or decision rule, the actual value where relevant, and its supporting passage. Keep the same evidence and test these failures before moving to retrieval changes.

## q01 — Improved, still incomplete

How does Pandora's Router decide when an expensive specialist estimate is worth paying for?

Much shorter and now states when to stop. Removes distracting Bidder material. Still omits inspection in reservation-price order and selecting the best observed estimate; one end-of-paragraph citation does not meet the per-sentence citation rule.

Answer length: 215 → 63 words. Generation: 15.6s → 8.1s.

<details><summary>Before and after answers</summary>

**Before**

Pandora's Router decides when an expensive specialist estimate is worth paying for by computing reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate. [3][4]  The system computes reservation prices that are a trade-off between cheap screening and costly reasoning for routing. [1]  In the decentralized setting, the system uses value-of-information reasoning to decide whether to refine the self-assessment before accepting a posted price. [3]  The strategic specialist must apply the same value-of-information reasoning to decide whether the posted price is worth accepting. [3]  The system balances cheap screening and costly reasoning for routing by deciding which expensive estimates are worth computing. [1]  The platform collects nonstrategic value estimates from other specialists and posts the best estimate as the price at which the remaining specialist can claim the query. [3]  The strategic specialist must then decide whether to invest in a more accurate self-assessment before claiming the query. [4]  The decision is based on the expected value-of-information for querying a more costly and accurate value estimate. [3]  The system uses a reservation-price-based policy to make this decision. [4]  The policy has a closed form that is straightforward to compute under a Gaussian signal model. [4]  The system is able to trade-off expensive and cheap estimates to achieve strong allocative performance relative to baselines across a range of estimation costs. [4]

**After**

Pandora's Router decides when an expensive specialist estimate is worth paying for by computing reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate. This is done by running the specialist for a few reasoning tokens and checking if it is on the right track. The system then stops when no remaining query is worth its cost. [1]

</details>

**Source 1 to check** (literal excerpt; shortened):

> Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value estimate only when the market price makes inspection worthwhile. The same principle yields both a centralized and decentralized policy. Figure 1\| Overview of thePandoraframework.The system balances cheap screening and costly reasoning for routing.(1)A concrete prompt𝑥 is received.(2)Multiple specialists 𝑚∈{ 1,...,𝑀} generate cheap, noisy value estim…

## q02 — Regressed

What is the difference between Pandora's Router and Pandora's Bidder?

Adds the global-welfare versus local-surplus distinction and the cheap-estimate alternative, but becomes much longer and introduces a false comparison. The zero/two-query claim concerns Router versus Margin in source 2, not Router versus Bidder, and the answer cites source 3 for it. It also treats a true advantage as a decision condition, includes a PDF header as prose, and places citations in separate numbered bullets.

Answer length: 55 → 239 words. Generation: 4.1s → 12.8s.

<details><summary>Before and after answers</summary>

**Before**

Pandora's Router and Pandora's Bidder differ in their approach to querying expensive estimates. Pandora's Router queries the expensive estimate only when the value of information exceeds the cost, whereas Pandora's Bidder queries the expensive estimate when it holds a true advantage and the cost is low, and declines the price when the cost is high. [1][2][3]

**After**

1. Pandora's Router queries the expensive estimate 𝑔 only when the value of information exceeds the cost, whereas Pandora's Bidder queries the expensive estimate 𝑔 only when it holds a true advantage. 2. [1] 3. Pandora's Router offers a total regret + inspection cost that tracks the lower envelope of the baselines across the full 𝑐𝑔 range, whereas Pandora's Bidder closely tracks the lower envelope of the regret of the two baselines across the full 𝑐𝑔 range. 4. [2] 5. The difference in their performance is determined largely by the decision about how many 𝑔 values to query, with two queries both methods always select the 𝑔-maximizer, and with zero queries both methods almost always select the 𝑓-maximizer. 6. [3] 7. The 𝑓-only baseline leaves efficiency on the table at low costs by never investing in refinement, whereas Pandora's Bidder selectively defaults to the cheap estimate or declines the price, avoiding the cost collapse of the 𝑔-always baseline. 8. [3] 9. With decentralization, however, maximizing local surplus does not always lead to better overall allocative efficiency, as seen in the example where the price is inaccurate. 10. [3] 11. Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation offer insufficient expected profit to incentivize the bidder; declining them protects the bidder’s surplus but assigns the input to a less capable specialist. 12. [3] 13. The tension is absent in the centralized setting, where the router internalizes all costs and optimizes global welfare directly. 14. [3] 15. Extending Pandora's Bidder to multi-round ascending-pricemechanisms may recover some of this efficiency loss. 16. [3]

</details>

**Source 2 to check** (literal excerpt; shortened):

> In the MATH domain the aggregate results for Pandora and Margin are nearly identical. Because there are only two routing targets, the regret is determined largely by the decision about how many𝑔 values to query: with two queries, both methods always select the𝑔-maximizer; with zero queries both methods almost always select the𝑓-maximizer (except in very rare cases where the reserve price ordering is different from the ordering of𝑓). Because Margin inherits the query budget from Pandora, it is unsurprising that its overall…

## q03 — Unchanged

In which three domains was the costly-value-estimation routing policy evaluated?

All three domains remain correct, but citations are still missing.

Answer length: 23 → 23 words. Generation: 4.5s → 4.5s.

<details><summary>Before and after answers</summary>

**Before**

The costly-value-estimation routing policy was evaluated in three domains:  1. EmbedLLM (multi-LLM routing benchmark) 2. Retrieval-augmented specialists for factoid QA 3. LLMs with variable inference-time reasoning

**After**

The costly-value-estimation routing policy was evaluated in three domains:   1. EmbedLLM (multi-LLM routing benchmark) 2. Retrieval-augmented specialists for factoid QA 3. LLMs with variable inference-time reasoning

</details>

**Source 3 to check** (literal excerpt; shortened):

> We evaluate both frameworks (see Figure 1) across three domains: a multi-LLM routing benchmark (EmbedLLM), retrieval-augmented specialists for factoid QA, and inference-time computation for mathematical reasoning. In each setting, both Pandora’s Router and Pandora’s Bidder are able to gracefully trade-off expensive and cheap estimates to achieve strong allocative performance relative to baselines across a range of estimation costs.…

## q08 — Still incorrect; citation regression

How do submissions that change the learning algorithm compare with those that do not?

Still omits the actual mean scores (0.226 versus 0.126). Instead, it compares submission shares (46.4% versus 53.6%) as though they measure performance or within-group success, even saying the smaller share is more often. Unlike the baseline, the new answer has no citation. The baseline’s unsupported significance statement disappeared, but the central error remains.

Answer length: 57 → 29 words. Generation: 7.2s → 4.0s.

<details><summary>Before and after answers</summary>

**Before**

Submissions that change the learning algorithm (122 submissions) do not differ significantly from those that do not (141 submissions) in terms of the number of submissions that reach the learning procedure, with 46.4% of the former and 53.6% of the latter reaching the procedure. [3]  The provided passages do not provide a direct comparison between the two groups.

**After**

Submissions that change the learning algorithm (122 submissions) reach the learning procedure more often (46.4%) than those that do not (141 submissions that stay entirely on the run, 53.6%).

</details>

**Source 2 to check** (literal excerpt; shortened):

> Of the 263 that change anything, 141 leave the learning procedure exactly as they found it and move budgets, checkpointing, hyperparameters and capacity instead. The 122 that do reach it — the objective, the supervision signal, the learning rule, the data — average0.226 against0 .126for the rest: the algorithmic layer is where the distance gets closed, and most submissions never go there. More reasoning effort moves agents towards it, taking that share from8%to64%and the mean score from0 .094to0 .196, which is most of what effort buys. A machine learning scientist reads the training dynamics, names the mechanism that is failing, and changes t…

## q09 — Essentially unchanged

What two kinds of task structure does TMI recover from computer-use traces?

Correctly explains hierarchical objectives and execution control flow, with supporting citations. Bullets make the two structures easier to scan.

Answer length: 53 → 51 words. Generation: 3.6s → 3.6s.

<details><summary>Before and after answers</summary>

**Before**

TMI recovers two kinds of task structure: objective models and procedure models. [3][2]  The objective model is a hierarchical decomposition of the objective of a task into subobjectives the user pursues. [3]  The procedure model is a trace-grounded composition of control-flow operators specifying how the execution of a task is organized through sequencing and iteration. [3]

**After**

TMI recovers two kinds of task structure: objective models and procedure models. [3][1]  • Objective models are hierarchical decompositions of the objective of a task into subobjectives the user pursues. [3] • Procedure models are trace-grounded compositions of control-flow operators specifying how the execution of a task is organized through sequencing and iteration. [3]

</details>

**Source 3 to check** (literal excerpt; shortened):

> Theobjective model Ot is a hierarchical decomposition of the objective of t into the subobjectives the user pursues. • Theprocedure model Pt is a trace-grounded composition of control-flow operators specifying how the execution of t is organized through sequencing and iteration. The task model Mt is structured as a tree, whose every node pairs an objective with a control-flow operator over its children.…

## q18 — Essentially unchanged

How does G-CARL supervise factuality and response coverage?

Both verification and weighted-checklist mechanisms remain correctly described. Passage citations are still absent; section references 3.2 and 3.3 are not passage citations. Automatic number flags here are section-reference warnings, not proof of incorrect research figures.

Answer length: 58 → 63 words. Generation: 4.2s → 4.4s.

<details><summary>Before and after answers</summary>

**Before**

G-CARL supervises factuality through a retrieval-grounded branch that verifies report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality reward Rfact (Sec. 3.2).   It also constructs a case-specific weighted checklist through MLLM generation followed by clinician-guided refinement, and evaluates the checklist coverage of the generated response to produce the checklist reward Rcheck (Sec. 3.3).

**After**

G-CARL supervises factuality through the retrieval-grounded branch, which verifies report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality reward Rfact (Sec. 3.2).   The case-specific checklist branch optimizes response coverage by constructing a weighted checklist through MLLM generation followed by clinician-guided refinement, and evaluating the checklist coverage of the generated response to produce the checklist reward Rcheck (Sec. 3.3).

</details>

**Source 4 to check** (literal excerpt; shortened):

> The retrieval-grounded branch then supervises medical factuality by verifying report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality rewardRfact (Sec. 3.2). In parallel, the case-specific checklist branch optimizes demand satisfaction and expression quality by constructing a weighted checklist through MLLM generation followed by clinicianguided refinement, and evaluating the checklist coverage of thegeneratedresponsetoproducethechecklistrewardR check (Sec. 3.3). Together with the format rewardRformat, these components are integrated into a multi-objective optimization task (Se…
