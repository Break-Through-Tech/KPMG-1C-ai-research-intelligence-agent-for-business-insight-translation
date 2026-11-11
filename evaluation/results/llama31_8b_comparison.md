# Generator comparison: Llama 3.1 8B versus Llama 3.2

**Assessment: Llama 3.1 8B is a promising next candidate, but not a complete fix.** It improves citation presence and the Router/Bidder explanation. The AI4AI performance question still fails; some checklist details and per-sentence citations remain missing. Keep this an experiment until a broader benchmark confirms the benefit. The default generator has not been changed.

Assistant assessment against the exact saved passages, not an LLM-judge score or independent human evaluation. Six previously problematic questions and one run per model cannot establish general accuracy or repeatable latency.

**Controls verified:** identical polished prompt, frozen passages and order, benchmark, temperature 0, seed 42, 8,192-token context, 550-token output limit, runner hash, and selected questions. Model name and weights are the changed configuration fields. Different model tokenizers mean equal token limits need not represent equal text capacity.

| Measure | Llama 3.2 | Llama 3.1 8B |
| --- | --- | --- |
| Answers containing a passage citation | 3/6 | 6/6 |
| Recorded total generation time | 37.4s | 71.3s |
| Generated output tokens | 719 | 512 |

Citation presence is not the same as complete citation coverage or factual accuracy. Timing includes local runtime conditions and possible model loading; this was not a warmed, repeated speed benchmark.

| Question | Assessment |
| --- | --- |
| q01 | Improved, still incomplete |
| q02 | Substantially improved |
| q03 | Citation improvement |
| q08 | Still inadequate |
| q09 | Content maintained |
| q18 | Citation improvement, detail trade-off |

**Recommended next step:** evaluate Llama 3.1 8B on the remaining benchmark questions before changing the default. Specifically check numerical comparisons, missing evidence, abstention and cross-paper questions. For q08, investigate why the generator ignores the score-bearing passage despite its presence.

## q01 — Improved, still incomplete

How does Pandora's Router decide when an expensive specialist estimate is worth paying for?

Adds selection of the best observed estimate and cites each sentence. Preserves the stopping rule and marks the short reasoning run as an example rather than a universal mechanism. Still omits inspection in reservation-price order.

Answer length: 63 → 61 words. Generation time: 8.1s → 18.0s.

<details><summary>Compare both generated answers</summary>

**Llama 3.2**

Pandora's Router decides when an expensive specialist estimate is worth paying for by computing reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate. This is done by running the specialist for a few reasoning tokens and checking if it is on the right track. The system then stops when no remaining query is worth its cost. [1]

**Llama 3.1 8B**

Pandora's Router computes reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate 𝑔𝑚(𝑥), e.g., by running the specialist for a few reasoning tokens and checking if it is on the right track [1]. The system stops when no remaining query is worth its cost [1]. The maximizer of the observed 𝑔𝑚 is chosen [1].

</details>

**Source 1 to check** (literal excerpt, shortened):

> Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value estimate only when the market price makes inspection worthwhile. The same principle yields both a centralized and decentralized policy. Figure 1\| Overview of thePandoraframework.The system balances cheap screening and costly reasoning for routing.(1)A concrete prompt𝑥 is received.(2)Multiple specialists 𝑚∈{ 1,...,𝑀} generate cheap, noisy value estim…

## q02 — Substantially improved

What is the difference between Pandora's Router and Pandora's Bidder?

Clearly distinguishes centralized Router and decentralized Bidder, removes the incorrect Router-versus-Margin attribution, and gives a supported local-surplus/overall-efficiency caveat. Still does not explicitly state that Router internalizes all costs and optimizes global welfare. Adds extra performance detail and uses four sentences rather than the requested maximum of three.

Answer length: 239 → 109 words. Generation time: 12.8s → 13.2s.

<details><summary>Compare both generated answers</summary>

**Llama 3.2**

1. Pandora's Router queries the expensive estimate 𝑔 only when the value of information exceeds the cost, whereas Pandora's Bidder queries the expensive estimate 𝑔 only when it holds a true advantage. 2. [1] 3. Pandora's Router offers a total regret + inspection cost that tracks the lower envelope of the baselines across the full 𝑐𝑔 range, whereas Pandora's Bidder closely tracks the lower envelope of the regret of the two baselines across the full 𝑐𝑔 range. 4. [2] 5. The difference in their performance is determined largely by the decision about how many 𝑔 values to query, with two queries both methods always select the 𝑔-maximizer, and with zero queries both methods almost always select the 𝑓-maximizer. 6. [3] 7. The 𝑓-only baseline leaves efficiency on the table at low costs by never investing in refinement, whereas Pandora's Bidder selectively defaults to the cheap estimate or declines the price, avoiding the cost collapse of the 𝑔-always baseline. 8. [3] 9. With decentralization, however, maximizing local surplus does not always lead to better overall allocative efficiency, as seen in the example where the price is inaccurate. 10. [3] 11. Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation offer insufficient expected profit to incentivize the bidder; declining them protects the bidder’s surplus but assigns the input to a less capable specialist. 12. [3] 13. The tension is absent in the centralized setting, where the router internalizes all costs and optimizes global welfare directly. 14. [3] 15. Extending Pandora's Bidder to multi-round ascending-pricemechanisms may recover some of this efficiency loss. 16. [3]

**Llama 3.1 8B**

Pandora's Router and Pandora's Bidder differ in their approach to allocating queries. Pandora's Router is a centralized policy that inspects specialists' value estimates in reservation price order, stopping when no remaining query is worth its cost [1]. In contrast, Pandora's Bidder is a decentralized policy that uses an auction mechanism to select the high bidder, with each specialist refining its own value estimate only when the market price makes inspection worthwhile [1]. Additionally, Pandora's Bidder measures regret versus an oracle that knows the true value for free, and its performance is affected by the price being inaccurate, leading to a trade-off between local surplus and overall allocative efficiency [3].

</details>

**Source 3 to check** (literal excerpt, shortened):

> With decentralization, however, maximizing local surplus does not alwaysleadtobetteroverallallocativeefficiency. Forexample, whenthepriceisinaccurate(setusingthe cheap estimate𝑓 rather than𝑔 for the𝑀− 1competitors) the strategic bidder captures higher surplus at the cost of overall allocative efficiency (see additional results in Appendix D.2). Overpriced queries Pandora’s AI Model Routing Box: Efficient Allocation with Costly Value Estimation offer insufficient expected profit to incentivize the bidder; declining them protects the bidder’s surplus but assigns the input to a less capable specialist. This tension is absent in the centralized s…

## q03 — Citation improvement

In which three domains was the costly-value-estimation routing policy evaluated?

All three domains remain correct. Now includes source references [3][4], but only after the final list item; the prompt asks for a citation on each factual bullet.

Answer length: 23 → 26 words. Generation time: 4.5s → 10.8s.

<details><summary>Compare both generated answers</summary>

**Llama 3.2**

The costly-value-estimation routing policy was evaluated in three domains:   1. EmbedLLM (multi-LLM routing benchmark) 2. Retrieval-augmented specialists for factoid QA 3. LLMs with variable inference-time reasoning

**Llama 3.1 8B**

The three domains where the costly-value-estimation routing policy was evaluated are:  1. a multi-LLM routing benchmark (EmbedLLM) 2. retrieval-augmented specialists for factoid QA 3. inference-time computation for mathematical reasoning [3][4]

</details>

**Source 3 to check** (literal excerpt, shortened):

> We evaluate both frameworks (see Figure 1) across three domains: a multi-LLM routing benchmark (EmbedLLM), retrieval-augmented specialists for factoid QA, and inference-time computation for mathematical reasoning. In each setting, both Pandora’s Router and Pandora’s Bidder are able to gracefully trade-off expensive and cheap estimates to achieve strong allocative performance relative to baselines across a range of estimation costs.…

## q08 — Still inadequate

How do submissions that change the learning algorithm compare with those that do not?

Drops the false claim that 46.4% is more often than 53.6% and adds a supported non-causal caveat. However, it still substitutes submission shares for performance and omits BOTH mean scores, 0.226 and 0.126, despite source 2 providing them. It cites [3], but the denominator 263 appears explicitly in sources [1]/[2], so the number warning needs citation review rather than being treated as proof of a fabricated value.

Answer length: 29 → 61 words. Generation time: 4.0s → 11.6s.

<details><summary>Compare both generated answers</summary>

**Llama 3.2**

Submissions that change the learning algorithm (122 submissions) reach the learning procedure more often (46.4%) than those that do not (141 submissions that stay entirely on the run, 53.6%).

**Llama 3.1 8B**

Submissions that change the learning algorithm (46.4% of 263 submissions) are compared to those that do not (53.6% of 263 submissions). The comparison is limited by the fact that the stronger systems are more likely to reach the learning procedure, so the gap is between submissions that go there and those that do not, rather than the effect of going there. [3]

</details>

**Source 2 to check** (literal excerpt, shortened):

> Of the 263 that change anything, 141 leave the learning procedure exactly as they found it and move budgets, checkpointing, hyperparameters and capacity instead. The 122 that do reach it — the objective, the supervision signal, the learning rule, the data — average0.226 against0 .126for the rest: the algorithmic layer is where the distance gets closed, and most submissions never go there. More reasoning effort moves agents towards it, taking that share from8%to64%and the mean score from0 .094to0 .196, which is most of what effort buys. A machine learning scientist reads the training dynamics, names the mechanism that is failing, and changes t…

## q09 — Content maintained

What two kinds of task structure does TMI recover from computer-use traces?

Both hierarchical objectives and procedure/control-flow models remain correctly described. The single [3] at paragraph end supports the content, but the first factual sentence has no adjacent citation, unlike the previous answer.

Answer length: 51 → 43 words. Generation time: 3.6s → 7.9s.

<details><summary>Compare both generated answers</summary>

**Llama 3.2**

TMI recovers two kinds of task structure: objective models and procedure models. [3][1]  • Objective models are hierarchical decompositions of the objective of a task into subobjectives the user pursues. [3] • Procedure models are trace-grounded compositions of control-flow operators specifying how the execution of a task is organized through sequencing and iteration. [3]

**Llama 3.1 8B**

TMI recovers two kinds of task structure: objective models and procedure models. Objective models are hierarchical decompositions of the objective of a task into subobjectives, while procedure models are trace-grounded compositions of control-flow operators specifying how the execution of a task is organized. [3]

</details>

**Source 3 to check** (literal excerpt, shortened):

> Theobjective model Ot is a hierarchical decomposition of the objective of t into the subobjectives the user pursues. • Theprocedure model Pt is a trace-grounded composition of control-flow operators specifying how the execution of t is organized through sequencing and iteration. The task model Mt is structured as a tree, whose every node pairs an objective with a control-flow operator over its children.…

## q18 — Citation improvement, detail trade-off

How does G-CARL supervise factuality and response coverage?

Now cites each factual sentence and correctly explains atomic claim verification and weighted, case-specific checklists. It no longer explicitly mentions the multi-source retrieval/datastore detail included in the previous answer and required by the checklist; the explanation is therefore less specific on that point.

Answer length: 63 → 62 words. Generation time: 4.4s → 9.8s.

<details><summary>Compare both generated answers</summary>

**Llama 3.2**

G-CARL supervises factuality through the retrieval-grounded branch, which verifies report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality reward Rfact (Sec. 3.2).   The case-specific checklist branch optimizes response coverage by constructing a weighted checklist through MLLM generation followed by clinician-guided refinement, and evaluating the checklist coverage of the generated response to produce the checklist reward Rcheck (Sec. 3.3).

**Llama 3.1 8B**

G-CARL supervises factuality through a retrieval-grounded claim reward that provides fine-grained supervision for medical factuality through atomic claim verification [1]. It also supervises response coverage through a case-specific checklist reward that explicitly supervises demand satisfaction and expression quality without relying on a single reference response [1]. This is achieved by constructing instance-specific weighted checklists through MLLM generation followed by clinician refinement [1].

</details>

**Source 3 to check** (literal excerpt, shortened):

> combinesmulti-source retrieval for atomic claim verification with context-aware, instance-specific weighted checklists for response coverage, providing structured supervision for factuality, user-demand satisfaction, and expression quality without constraining response diversity. We further constructMMedReport, a realworld PMRI benchmark, along with a clinician-designed three-dimensionalevaluationprotocol.Extensiveexperiments demonstrate that G-CARL consistently outperforms existing post-training baselines in overall quality, claim-level precision, and checklist recall. Pairwise preference evaluation by clinicians further confirms that G-CARL…
