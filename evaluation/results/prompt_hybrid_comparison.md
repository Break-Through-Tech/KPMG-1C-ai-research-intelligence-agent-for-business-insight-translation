# Hybrid prompt experiment — six-answer assessment

**Decision: reject this candidate as the default; restore the previous polished prompt.** The hybrid shortened responses but eliminated all passage citations and dropped useful content. The previous prompt also has known failures; restoring it does not mean it is validated.

This is an assistant assessment against the exact saved passages, not an LLM-judge score or independent human review. One generation per question with each prompt is a diagnostic test, not a robust performance estimate.

**Controlled comparison:** verified identical model weights, generation settings, benchmark, saved passage text/order, runner hash and selected question IDs between polished and hybrid runs. Only the prompt hash differs in their run configurations. The original baseline uses the same weights/settings/passages; the older q01–q03 runner hash differs.

| Measure | Original | Polished | Hybrid |
| --- | --- | --- |
| Answers with any passage citation | 4/6 | 3/6 | 0/6 |
| Recorded generation time | 39.2s | 37.4s | 27.7s |

Citation presence is not proof of support. Timings include local runtime conditions; shorter answers and one run per question do not establish a repeatable speed benefit. The hybrid prompt itself is 273 words versus 269 for the polished prompt; the change tested answer structures, not a substantially smaller input.

| Question | Assessment versus polished |
| --- | --- |
| q01 | Regressed |
| q02 | Shorter, still inadequate |
| q03 | Content unchanged |
| q08 | Unchanged failure |
| q09 | Citation regression |
| q18 | Essentially unchanged |

**Recommendation:** stop adding rules for now. Next, test a different installed generator against these same inputs, or test a structured response format with explicit claim/citation fields. Neither was run in this experiment. Do not add citation numbers automatically without checking claim support.

## q01 — Regressed

How does Pandora's Router decide when an expensive specialist estimate is worth paying for?

Keeps the value-of-information idea, but drops the stopping rule added by the polished prompt. Still omits inspection order and final selection. All citations are gone.

Answer length: 63 → 30 words.

<details><summary>Original, polished, and hybrid answers</summary>

**Original**

Pandora's Router decides when an expensive specialist estimate is worth paying for by computing reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate. [3][4]  The system computes reservation prices that are a trade-off between cheap screening and costly reasoning for routing. [1]  In the decentralized setting, the system uses value-of-information reasoning to decide whether to refine the self-assessment before accepting a posted price. [3]  The strategic specialist must apply the same value-of-information reasoning to decide whether the posted price is worth accepting. [3]  The system balances cheap screening and costly reasoning for routing by deciding which expensive estimates are worth computing. [1]  The platform collects nonstrategic value estimates from other specialists and posts the best estimate as the price at which the remaining specialist can claim the query. [3]  The strategic specialist must then decide whether to invest in a more accurate self-assessment before claiming the query. [4]  The decision is based on the expected value-of-information for querying a more costly and accurate value estimate. [3]  The system uses a reservation-price-based policy to make this decision. [4]  The policy has a closed form that is straightforward to compute under a Gaussian signal model. [4]  The system is able to trade-off expensive and cheap estimates to achieve strong allocative performance relative to baselines across a range of estimation costs. [4]

**Polished**

Pandora's Router decides when an expensive specialist estimate is worth paying for by computing reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate. This is done by running the specialist for a few reasoning tokens and checking if it is on the right track. The system then stops when no remaining query is worth its cost. [1]

**Hybrid**

Pandora's Router decides when an expensive specialist estimate is worth paying for by computing reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate.

</details>

**Source 1 to check** (literal excerpt, shortened):

> Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value estimate only when the market price makes inspection worthwhile. The same principle yields both a centralized and decentralized policy. Figure 1\| Overview of thePandoraframework.The system balances cheap screening and costly reasoning for routing.(1)A concrete prompt𝑥 is received.(2)Multiple speciali…

## q02 — Shorter, still inadequate

What is the difference between Pandora's Router and Pandora's Bidder?

Removes the polished answer’s spurious Router-versus-Margin attribution and broken numbered-list format, but again misses the defining centralized/decentralized and global-welfare/local-surplus contrasts. It emphasizes shared regret/cost behavior instead, with no citations.

Answer length: 239 → 48 words.

<details><summary>Original, polished, and hybrid answers</summary>

**Original**

Pandora's Router and Pandora's Bidder differ in their approach to querying expensive estimates. Pandora's Router queries the expensive estimate only when the value of information exceeds the cost, whereas Pandora's Bidder queries the expensive estimate when it holds a true advantage and the cost is low, and declines the price when the cost is high. [1][2][3]

**Polished**

1. Pandora's Router queries the expensive estimate 𝑔 only when the value of information exceeds the cost, whereas Pandora's Bidder queries the expensive estimate 𝑔 only when it holds a true advantage. 2. [1] 3. Pandora's Router offers a total regret + inspection cost that tracks the lower envelope of the baselines across the full 𝑐𝑔 range, whereas Pandora's Bidder closely tracks the lower envelope of the regret of the two baselines across the full 𝑐𝑔 range. 4. [2] 5. The difference in their performance is determined largely by the decision about how many 𝑔 values to query, with two queries both methods always select the 𝑔-maximizer, and with zero queries both methods almost always select the 𝑓-maximizer. 6. [3] 7. The 𝑓-only baseline leaves efficiency on the table at low costs by never investing in refinement, whereas Pandora's Bidder selectively defaults to the cheap estimate or declines the price, avoiding the cost collapse of the 𝑔-always baseline. 8. [3] 9. With decentralization, however, maximizing local surplus does not always lead to better overall allocative efficiency, as seen in the example where the price is inaccurate. 10. [3] 11. Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation offer insufficient expected profit to incentivize the bidder; declining them protects the bidder’s surplus but assigns the input to a less capable specialist. 12. [3] 13. The tension is absent in the centralized setting, where the router internalizes all costs and optimizes global welfare directly. 14. [3] 15. Extending Pandora's Bidder to multi-round ascending-pricemechanisms may recover some of this efficiency loss. 16. [3]

**Hybrid**

Pandora's Router and Pandora's Bidder closely track the lower envelope of the regret of the two baselines across the full cost range, with Pandora's Router querying the expensive estimate only when the value of information exceeds the cost, and Pandora's Bidder frequently refining its estimate at low costs.

</details>

**Source 3 to check** (literal excerpt, shortened):

> With decentralization, however, maximizing local surplus does not alwaysleadtobetteroverallallocativeefficiency. Forexample, whenthepriceisinaccurate(setusingthe cheap estimate𝑓 rather than𝑔 for the𝑀− 1competitors) the strategic bidder captures higher surplus at the cost of overall allocative efficiency (see additional results in Appendix D.2). Overpriced queries Pandora’s AI Model Routing Box: Efficient Allocation with Costly Value Estimation offer insufficient expected profit to incentivize the bidder; declining them protects the bidder’s surplus but assigns the input to a less capable speci…

## q03 — Content unchanged

In which three domains was the costly-value-estimation routing policy evaluated?

Correctly lists the three domains. Still has no citations and does not follow the requested list structure.

Answer length: 23 → 21 words.

<details><summary>Original, polished, and hybrid answers</summary>

**Original**

The costly-value-estimation routing policy was evaluated in three domains:  1. EmbedLLM (multi-LLM routing benchmark) 2. Retrieval-augmented specialists for factoid QA 3. LLMs with variable inference-time reasoning

**Polished**

The costly-value-estimation routing policy was evaluated in three domains:   1. EmbedLLM (multi-LLM routing benchmark) 2. Retrieval-augmented specialists for factoid QA 3. LLMs with variable inference-time reasoning

**Hybrid**

The costly-value-estimation routing policy was evaluated across three domains: EmbedLLM, retrieval-augmented specialists for factoid QA, and LLMs with variable inference-time reasoning.

</details>

**Source 3 to check** (literal excerpt, shortened):

> We evaluate both frameworks (see Figure 1) across three domains: a multi-LLM routing benchmark (EmbedLLM), retrieval-augmented specialists for factoid QA, and inference-time computation for mathematical reasoning. In each setting, both Pandora’s Router and Pandora’s Bidder are able to gracefully trade-off expensive and cheap estimates to achieve strong allocative performance relative to baselines across a range of estimation costs.…

## q08 — Unchanged failure

How do submissions that change the learning algorithm compare with those that do not?

The answer body is identical to the polished version. It omits 0.226 versus 0.126, substitutes submission shares for performance, and says 46.4% is more often than 53.6%. No citation is supplied.

Answer length: 29 → 29 words.

<details><summary>Original, polished, and hybrid answers</summary>

**Original**

Submissions that change the learning algorithm (122 submissions) do not differ significantly from those that do not (141 submissions) in terms of the number of submissions that reach the learning procedure, with 46.4% of the former and 53.6% of the latter reaching the procedure. [3]  The provided passages do not provide a direct comparison between the two groups.

**Polished**

Submissions that change the learning algorithm (122 submissions) reach the learning procedure more often (46.4%) than those that do not (141 submissions that stay entirely on the run, 53.6%).

**Hybrid**

Submissions that change the learning algorithm (122 submissions) reach the learning procedure more often (46.4%) than those that do not (141 submissions that stay entirely on the run, 53.6%).

</details>

**Source 2 to check** (literal excerpt, shortened):

> Of the 263 that change anything, 141 leave the learning procedure exactly as they found it and move budgets, checkpointing, hyperparameters and capacity instead. The 122 that do reach it — the objective, the supervision signal, the learning rule, the data — average0.226 against0 .126for the rest: the algorithmic layer is where the distance gets closed, and most submissions never go there. More reasoning effort moves agents towards it, taking that share from8%to64%and the mean score from0 .094to0 .196, which is most of what effort buys. A machine learning scientist reads the training dynamics, …

## q09 — Citation regression

What two kinds of task structure does TMI recover from computer-use traces?

Both objective and procedure models remain correctly explained, but the citations present in both earlier versions disappear.

Answer length: 51 → 43 words.

<details><summary>Original, polished, and hybrid answers</summary>

**Original**

TMI recovers two kinds of task structure: objective models and procedure models. [3][2]  The objective model is a hierarchical decomposition of the objective of a task into subobjectives the user pursues. [3]  The procedure model is a trace-grounded composition of control-flow operators specifying how the execution of a task is organized through sequencing and iteration. [3]

**Polished**

TMI recovers two kinds of task structure: objective models and procedure models. [3][1]  • Objective models are hierarchical decompositions of the objective of a task into subobjectives the user pursues. [3] • Procedure models are trace-grounded compositions of control-flow operators specifying how the execution of a task is organized through sequencing and iteration. [3]

**Hybrid**

TMI recovers two kinds of task structure: objective models and procedure models. Objective models are hierarchical decompositions of the objective of a task into subobjectives, and procedure models are trace-grounded compositions of control-flow operators specifying how the execution of a task is organized.

</details>

**Source 3 to check** (literal excerpt, shortened):

> Theobjective model Ot is a hierarchical decomposition of the objective of t into the subobjectives the user pursues. • Theprocedure model Pt is a trace-grounded composition of control-flow operators specifying how the execution of t is organized through sequencing and iteration. The task model Mt is structured as a tree, whose every node pairs an objective with a control-flow operator over its children.…

## q18 — Essentially unchanged

How does G-CARL supervise factuality and response coverage?

Both retrieval-grounded verification and weighted checklists remain correctly explained. Still missing passage citations; 3.2 and 3.3 are section references, not passage citations.

Answer length: 63 → 58 words.

<details><summary>Original, polished, and hybrid answers</summary>

**Original**

G-CARL supervises factuality through a retrieval-grounded branch that verifies report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality reward Rfact (Sec. 3.2).   It also constructs a case-specific weighted checklist through MLLM generation followed by clinician-guided refinement, and evaluates the checklist coverage of the generated response to produce the checklist reward Rcheck (Sec. 3.3).

**Polished**

G-CARL supervises factuality through the retrieval-grounded branch, which verifies report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality reward Rfact (Sec. 3.2).   The case-specific checklist branch optimizes response coverage by constructing a weighted checklist through MLLM generation followed by clinician-guided refinement, and evaluating the checklist coverage of the generated response to produce the checklist reward Rcheck (Sec. 3.3).

**Hybrid**

G-CARL supervises factuality through a retrieval-grounded branch that verifies report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality reward Rfact (Sec. 3.2). It also constructs a case-specific weighted checklist through MLLM generation followed by clinician-guided refinement, and evaluates the checklist coverage of the generated response to produce the checklist reward Rcheck (Sec. 3.3).

</details>

**Source 4 to check** (literal excerpt, shortened):

> The retrieval-grounded branch then supervises medical factuality by verifying report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality rewardRfact (Sec. 3.2). In parallel, the case-specific checklist branch optimizes demand satisfaction and expression quality by constructing a weighted checklist through MLLM generation followed by clinicianguided refinement, and evaluating the checklist coverage of thegeneratedresponsetoproducethechecklistrewardR check (Sec. 3.3). Together with the format rewardRformat, these components are integ…
