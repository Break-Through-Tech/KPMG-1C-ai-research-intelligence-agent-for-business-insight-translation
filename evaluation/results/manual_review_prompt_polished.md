# Answer review worksheet

6 answers · automatic checks complete · content awaits manual review.

Checklists are assistant-prepared and pending human approval. Automatic checks do not establish factual accuracy.

## q01 — Manual review needed

How does Pandora's Router decide when an expensive specialist estimate is worth paying for?

**Answer:** Pandora's Router decides when an expensive specialist estimate is worth paying for by computing reservation prices that quantify the expected value-of-information for querying a more costly and accurate value estimate. This is done by running the specialist for a few reasoning tokens and checking if it is on the right track. The system then stops when no remaining query is worth its cost. [1]

**Automatic findings:** No mechanical issues flagged. This does not mean the answer is correct.

**Check these points:**

- [ ] Explains that reservation prices/value of information determine whether a more accurate estimate is worth its cost.
- [ ] Explains inspection in reservation-price order, stopping when no remaining inspection is worthwhile, then selecting the best observed estimate.
- [ ] Answers about the centralized Router without attributing decentralized posted-price acceptance or specialist bidding to it.

**Sources found:** 1 of 1 expected papers. This measures paper retrieval, not whether the answer uses the right evidence.

**Source previews** — copied from saved passages, at most 240 characters each. Selected by word overlap for navigation; inspect full passages to verify claims.

**Source 1**

> …order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value estimate only when…

**Source 3**

> The strategic specialist must then apply the same value-of-information (VoI) reasoning from Pandora’s Router to decide whether this price is worth accepting, and whether or not to pay to observe a refined estimate before making this…

<details><summary>Full sources and automatic checks</summary>

**Source 1 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value estimate only when the market price makes inspection worthwhile. The same principle yields both a centralized and decentralized policy. Figure 1\| Overview of thePandoraframework.The system balances cheap screening and costly reasoning for routing.(1)A concrete prompt𝑥 is received.(2)Multiple specialists 𝑚∈{ 1,...,𝑀} generate cheap, noisy value estimates𝑓𝑚(𝑥).(3)The system computesreservation pricesthat quantify the expected value-of-information for querying a more costly and accurate value estimate 𝑔𝑚(𝑥), e.g., by running the specialist for a few reasoning tokens and checking if it is on the right track. (4)This unified principle supports allocation by centralized routing and decentralized auctions. minus total estimation cost by deciding which expensive estimates𝑔𝑚(𝑥) are worth computing. Formally, let𝑋∈X be a random input prompt, and let𝑥 denote a realization. Conditional on the input 𝑋=𝑥 , specialist𝑚 samples an output𝑌𝑚∼𝑃 𝑚(·\|𝑥) ,𝑌𝑚∈Y , and receives a cost-adjusted reward 𝑅𝑚(𝑥,𝑌 𝑚). For notational convenience, we will write the cost-adjusted reward𝑅𝑚(𝑥,𝑌 𝑚) simply as𝑅𝑚. The reward may combine, for example, the graded quality of the output with the cost of producing it (which could be the inference cost, or API fees for tools called), and is

**Source 2 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

benchmark, retrieval-augmented specialists, and LLMs with variable inference-time reasoning—show that Pandora’s Router matches the routing quality of exhaustive estimation, while querying the expensive estimator far less often. In the decentralized setting, value-of-information reasoning improves allocative efficiency when competing estimates are accurate; when competing estimates are noisy, however, it can increase the strategic specialist’s utility at the expense of others.

**Source 3 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

We now extend Pandora’s Router to a decentralized setting in which the specialists control their own value estimates, and use them to participate in a marketplace. Pandora’s Router assumes that a single decision-maker controls which boxes to open and which specialist to select. In many settings, however, the specialists themselves are better positioned to estimate their own value: a retrieval-augmented specialisthasaccesstoitsowncorpus,amathspecialistcanexecutepartialcomputations,andadomainexpert may have proprietary benchmarks. None of these resources need be visible to a centralized router. Decentralization also has practical advantages: new specialists can join without retraining the routing model, and the cost of value estimation is borne by the specialists rather than the platform. As an alternative to a centralized router, consider a market-based mechanism where each specialist can purchase the right to answer a query. We formalize this via a posted-price mechanism corresponding to a single stage of the ascending-price framework with costly preference elicitation studied by Parkes (2005). For simplicity, we consider a leave-one-out setting with a single strategic specialist. A platform collects nonstrategic value estimates from𝑀− 1specialists and posts the best estimate as the price at which the remaining specialist can claim the query. The strategic specialist must then apply the same value-of-information (VoI) reasoning from Pandora’s Router to decide whether this price is worth accepting, and whether or not to pay to observe a refined estimate before making this decision. Concretely, for a given query𝑥, the platform solicits𝐺𝑗 from each of the𝑀− 1nonstrategic specialists and sets the

**Source 4 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

Bidder: each specialist faces a posted price—the current best competing offer—and must decide whether to invest in a more accurate self-assessment before claiming the query. This corresponds to a single stage of the ascending-price mechanism with costly preference elicitation studied by Parkes (2005); analyzing this simple setting isolates core components of decentralized prompt allocation under private value estimation with profit incentives. Core contributions of this work As AI systems with diverse capabilities proliferate, reasoning about the economics of model selection becomes increasingly relevant. To our knowledge, this is the first paper to explicitly connect model routing with the classical Pandora’s Box problem from economics and operations research. Specifically, this paper makes three main contributions: • We formalize model routing with costly value estimation as an instance of Pandora’s Box with non-obligatory inspection (Doval, 2018), yielding a reservation-price-based policy. Under a Gaussian signal model, this policy has a closed form that is straightforward to compute (4). • We extend to a decentralized setting where specialists use value-of-information reasoning to decide whether to refine their self-assessments before accepting a posted price (5). • We evaluate both frameworks (see Figure 1) across three domains: a multi-LLM routing benchmark (EmbedLLM), retrieval-augmented specialists for factoid QA, and inference-time computation for mathematical reasoning. In each setting, both Pandora’s Router and Pandora’s Bidder are able to gracefully trade-off expensive and cheap estimates to achieve strong allocative performance relative to baselines across a range of estimation costs.

Source references exist; whether they support each claim still needs review.

Answer is 63 words; the review target is at most 120.


</details>

## q02 — Manual review needed

What is the difference between Pandora's Router and Pandora's Bidder?

**Answer:** 1. Pandora's Router queries the expensive estimate 𝑔 only when the value of information exceeds the cost, whereas Pandora's Bidder queries the expensive estimate 𝑔 only when it holds a true advantage. 2. [1] 3. Pandora's Router offers a total regret + inspection cost that tracks the lower envelope of the baselines across the full 𝑐𝑔 range, whereas Pandora's Bidder closely tracks the lower envelope of the regret of the two baselines across the full 𝑐𝑔 range. 4. [2] 5. The difference in their performance is determined largely by the decision about how many 𝑔 values to query, with two queries both methods always select the 𝑔-maximizer, and with zero queries both methods almost always select the 𝑓-maximizer. 6. [3] 7. The 𝑓-only baseline leaves efficiency on the table at low costs by never investing in refinement, whereas Pandora's Bidder selectively defaults to the cheap estimate or declines the price, avoiding the cost collapse of the 𝑔-always baseline. 8. [3] 9. With decentralization, however, maximizing local surplus does not always lead to better overall allocative efficiency, as seen in the example where the price is inaccurate. 10. [3] 11. Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation offer insufficient expected profit to incentivize the bidder; declining them protects the bidder’s surplus but assigns the input to a less capable specialist. 12. [3] 13. The tension is absent in the centralized setting, where the router internalizes all costs and optimizes global welfare directly. 14. [3] 15. Extending Pandora's Bidder to multi-round ascending-pricemechanisms may recover some of this efficiency loss. 16. [3]

**Automatic findings:** Answer is 239 words; the review target is at most 120.

**Check these points:**

- [ ] Explicitly contrasts the centralized Router with decentralized specialists using Bidder.
- [ ] Explains that Router accounts for overall costs/global welfare, whereas a bidder optimizes its own surplus, which can conflict with overall efficiency.
- [ ] If discussing high inspection costs, preserves the option to use a cheap estimate OR decline a posted price; does not state that high costs always cause refusal.

**Sources found:** 1 of 1 expected papers. This measures paper retrieval, not whether the answer uses the right evidence.

**Source previews** — copied from saved passages, at most 240 characters each. Selected by word overlap for navigation; inspect full passages to verify claims.

**Source 1**

> …Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value estimate only when the market price makes inspection worthwhile. The same principle yields both a centralized and…

**Source 3**

> …surplus does not alwaysleadtobetteroverallallocativeefficiency. Forexample, whenthepriceisinaccurate(setusingthe cheap estimate𝑓 rather than𝑔 for the𝑀− 1competitors) the strategic bidder captures higher surplus at the cost of overall…

<details><summary>Full sources and automatic checks</summary>

**Source 1 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

Pandora’s Router Centralized policy Inspect specialists𝑔𝑚(𝑥) in reservationprice order, stopping when no remaining query is worth its cost. Choose the maximizer of the observed𝑔𝑚. Pandora’s Bidder Decentralized policy The high bidder is selected in an auction. Each specialist refines its own value estimate only when the market price makes inspection worthwhile. The same principle yields both a centralized and decentralized policy. Figure 1\| Overview of thePandoraframework.The system balances cheap screening and costly reasoning for routing.(1)A concrete prompt𝑥 is received.(2)Multiple specialists 𝑚∈{ 1,...,𝑀} generate cheap, noisy value estimates𝑓𝑚(𝑥).(3)The system computesreservation pricesthat quantify the expected value-of-information for querying a more costly and accurate value estimate 𝑔𝑚(𝑥), e.g., by running the specialist for a few reasoning tokens and checking if it is on the right track. (4)This unified principle supports allocation by centralized routing and decentralized auctions. minus total estimation cost by deciding which expensive estimates𝑔𝑚(𝑥) are worth computing. Formally, let𝑋∈X be a random input prompt, and let𝑥 denote a realization. Conditional on the input 𝑋=𝑥 , specialist𝑚 samples an output𝑌𝑚∼𝑃 𝑚(·\|𝑥) ,𝑌𝑚∈Y , and receives a cost-adjusted reward 𝑅𝑚(𝑥,𝑌 𝑚). For notational convenience, we will write the cost-adjusted reward𝑅𝑚(𝑥,𝑌 𝑚) simply as𝑅𝑚. The reward may combine, for example, the graded quality of the output with the cost of producing it (which could be the inference cost, or API fees for tools called), and is

**Source 2 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

and all methods except𝑓-only (which never queries𝑔) perform similarly. As𝑐𝑔 increases, the𝑔-always baseline continues to make a fixed number of queries regardless of cost, while𝑓-only still never queries at all. Pandora’s Router interpolates between these extremes, querying𝑔 only when the value of information exceeds the cost. The result is a total regret + inspection cost that tracks the lower envelope of the baselines across the full𝑐𝑔 range. As a secondary analysis, Figure 6 shows the cost-performance tradeoff offered by Pandora’s Router, Pandora’s AI Model Routing Box: Efficient Allocation with Costly Value Estimation in terms of monetary costs and routing regret. The costs are computed from the Gemini API prices described in Section 2.2. When𝑐𝑔 = 0.001, we are in a setting in which users are eager to pay for queries that improve routing; here Pandora’s Router obtains regret that almost matches𝑔-only, while incurring much lower inspection costs. When𝑐𝑔 = 0.1, we are in a setting in which users are unwilling to pay for queries to𝑔. As a result, the Pandora’s Router never queries𝑔, and routing performance and cost match the𝑓-only baseline. In the MATH domain the aggregate results for Pandora and Margin are nearly identical. Because there are only two routing targets, the regret is determined largely by the decision about how many𝑔 values to query: with two queries, both methods always select the𝑔-maximizer; with zero queries both methods almost always select the𝑓-maximizer (except in very rare cases where the reserve price ordering is different from the ordering of𝑓). Because Margin inherits the query budget from Pandora, it is unsurprising that its overall

**Source 3 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

we measure the regret versus an oracle that knows𝐺𝑚 for free. Results.Figure3plotsallocativeefficiencyandbiddersurplusfordifferent 𝑐𝑔. Pandora’sBidderclosely tracks the lower envelope of the regret of the two baselines across the full𝑐𝑔 range. When𝑐𝑔 is low, the bidder frequently refines its estimate, winning queries where it holds a true advantage. As𝑐𝑔 increases, the bidder selectively defaults to the cheap estimate or declines the price, avoiding the cost collapse of the𝑔-always baseline. The𝑓-only baseline, conversely, leaves efficiency on the table at low costs by never investing in refinement. With decentralization, however, maximizing local surplus does not alwaysleadtobetteroverallallocativeefficiency. Forexample, whenthepriceisinaccurate(setusingthe cheap estimate𝑓 rather than𝑔 for the𝑀− 1competitors) the strategic bidder captures higher surplus at the cost of overall allocative efficiency (see additional results in Appendix D.2). Overpriced queries Pandora’s AI Model Routing Box: Efficient Allocation with Costly Value Estimation offer insufficient expected profit to incentivize the bidder; declining them protects the bidder’s surplus but assigns the input to a less capable specialist. This tension is absent in the centralized setting, where the router internalizes all costs and optimizes global welfare directly. Extending Pandora’s Bidder to multi-roundascending-pricemechanisms(Parkes,2005)mayrecoversomeofthisefficiencyloss.

**Source 4 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

Bidder: each specialist faces a posted price—the current best competing offer—and must decide whether to invest in a more accurate self-assessment before claiming the query. This corresponds to a single stage of the ascending-price mechanism with costly preference elicitation studied by Parkes (2005); analyzing this simple setting isolates core components of decentralized prompt allocation under private value estimation with profit incentives. Core contributions of this work As AI systems with diverse capabilities proliferate, reasoning about the economics of model selection becomes increasingly relevant. To our knowledge, this is the first paper to explicitly connect model routing with the classical Pandora’s Box problem from economics and operations research. Specifically, this paper makes three main contributions: • We formalize model routing with costly value estimation as an instance of Pandora’s Box with non-obligatory inspection (Doval, 2018), yielding a reservation-price-based policy. Under a Gaussian signal model, this policy has a closed form that is straightforward to compute (4). • We extend to a decentralized setting where specialists use value-of-information reasoning to decide whether to refine their self-assessments before accepting a posted price (5). • We evaluate both frameworks (see Figure 1) across three domains: a multi-LLM routing benchmark (EmbedLLM), retrieval-augmented specialists for factoid QA, and inference-time computation for mathematical reasoning. In each setting, both Pandora’s Router and Pandora’s Bidder are able to gracefully trade-off expensive and cheap estimates to achieve strong allocative performance relative to baselines across a range of estimation costs.

Source references exist; whether they support each claim still needs review.

Answer is 239 words; the review target is at most 120.


</details>

## q03 — Manual review needed

In which three domains was the costly-value-estimation routing policy evaluated?

**Answer:** The costly-value-estimation routing policy was evaluated in three domains:   1. EmbedLLM (multi-LLM routing benchmark) 2. Retrieval-augmented specialists for factoid QA 3. LLMs with variable inference-time reasoning

**Automatic findings:** Add source references to the answer itself.

**Check these points:**

- [ ] Names the standard multi-LLM routing benchmark, such as EmbedLLM.
- [ ] Names retrieval-augmented specialists for factoid question answering.
- [ ] Names variable inference-time computation/reasoning, including mathematical reasoning.

**Sources found:** 1 of 1 expected papers. This measures paper retrieval, not whether the answer uses the right evidence.

**Source previews** — copied from saved passages, at most 240 characters each. Selected by word overlap for navigation; inspect full passages to verify claims.

**Source 3**

> …reasoning to decide whether to refine their self-assessments before accepting a posted price (5). • We evaluate both frameworks (see Figure 1) across three domains: a multi-LLM routing benchmark (EmbedLLM), retrieval-augmented…

**Source 4**

> …Pandora’s Bidder, where specialists independently decide whether to invest in self-assessment before accepting an offered price to claim a query. Experiments across three domains—a standard multi-LLM benchmark, retrieval-augmented…

<details><summary>Full sources and automatic checks</summary>

**Source 1 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

expensive boxes), the inequality reverses. 2The value of the best committing policy that holds out multiple boxes cannot exceed that of the best single-box policy (Beyhaghi and Kleinberg, 2019), so it suffices to evaluate all𝑀 single-holdout policies, in addition to the obligatory inspection policy (no holdouts). These M + 1 policies are compared by simulating their performance via MC sampling. Pandora’s AI Model Routing Box: Efficient Allocation with Costly Value Estimation The algorithm proceeds as follows. For each candidate holdout𝑚∈{ 0, 1,...,𝑀} , define the expected payoff of the committing policy that reserves box𝑚: 𝜈𝑚 =𝔼 " 𝑉 ˆ𝑚− ∑︁ 𝑗∈𝑂𝑚 𝑐𝑗 # ,(3) where𝑉 ˆ𝑚isthevalueofthe(random)boxthatthecommittingpolicyselects,and 𝑂𝑚 isthe(random)set ofboxesopenedbyPandora-OIon {1,...,𝑀}\{𝑚} withinitialoutsideoption 𝑣 =𝑢 backup𝑚 . Thecase𝑚= 0corresponds to running Pandora-OI on all𝑀 boxes with no holdout (𝑢backup0 =−∞ ). Because the heldoutboxisunobserved, weestimate 𝜈𝑚 viaMonteCarlo(MC)samples ˜𝑉𝑚∼𝑃 𝑚(·\|𝑥) ; wedenotetheMC estimate ˆ𝜈𝑚. We select𝑚 that maximizesˆ𝜈𝑚, using𝑆= 100samples. 3 At test time, we run Pandora-OI on{1,...,𝑀}\{𝑚 } with initial value𝑣 =𝑢 backup𝑚 , opening the actual boxes. We default to𝑚 if we open no boxes or if no realized value clears𝑢backup𝑚 ; otherwise, we select the best opened box.4

**Source 2 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

=(𝐹 1,...,𝐹 𝑀). Inspecting specialist𝑚 then reveals the costly information𝑍𝑚, from which the refined estimate𝐺𝑚 =𝑔 𝑚(𝑋,𝑍 𝑚) is computed. We denote the cost of this process as𝑐𝑔. For the additional cost of𝐺𝑚 to be justified, it should be more accurate, in the sense that on calibration data we have𝔼[(𝑅 𝑚−𝐺 𝑚)2]&lt;𝔼[(𝑅 𝑚−𝐹 𝑚)2]. The router must dynamically decide which specialists to inspect in order to maximize the expected reward of the final assignment minus the total cost of the realized𝐺𝑚 estimates. To make things more concrete before presenting our routing algorithms, we now describe three real-world domains where the two-tier estimation between𝑓𝑚 versus𝑔𝑚 arises organically, each with a qualitatively different source of costly information that is useful for deciding the best allocation. 2.1. Experimental domains and value estimators We explore several empirical settings, each featuring different types of specialists and value estimators. Inallcases, thecheapestimator 𝑓 embedsthepromptwithapretrainedencoder, retrievesthe 𝑘nearest prompts from a calibration set (measured by cosine similarity in embedding space), and returns the average reward of the retrieved neighbors as the value estimate. The costly estimator is then constructed by fine-tuning a small language model encoder to predict the reward from a tailored, domain-specific input context. We describe these below. Note that in each domain, we partition the data into three splits: training (for fitting value estimators), calibration (for estimating the value-of-information model parameters in Sections 4

**Source 3 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

Bidder: each specialist faces a posted price—the current best competing offer—and must decide whether to invest in a more accurate self-assessment before claiming the query. This corresponds to a single stage of the ascending-price mechanism with costly preference elicitation studied by Parkes (2005); analyzing this simple setting isolates core components of decentralized prompt allocation under private value estimation with profit incentives. Core contributions of this work As AI systems with diverse capabilities proliferate, reasoning about the economics of model selection becomes increasingly relevant. To our knowledge, this is the first paper to explicitly connect model routing with the classical Pandora’s Box problem from economics and operations research. Specifically, this paper makes three main contributions: • We formalize model routing with costly value estimation as an instance of Pandora’s Box with non-obligatory inspection (Doval, 2018), yielding a reservation-price-based policy. Under a Gaussian signal model, this policy has a closed form that is straightforward to compute (4). • We extend to a decentralized setting where specialists use value-of-information reasoning to decide whether to refine their self-assessments before accepting a posted price (5). • We evaluate both frameworks (see Figure 1) across three domains: a multi-LLM routing benchmark (EmbedLLM), retrieval-augmented specialists for factoid QA, and inference-time computation for mathematical reasoning. In each setting, both Pandora’s Router and Pandora’s Bidder are able to gracefully trade-off expensive and cheap estimates to achieve strong allocative performance relative to baselines across a range of estimation costs.

**Source 4 — Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation**

2026-08-21 Pandora’s AI Model Routing Box: Efficient Allocation with Costly Value Estimation Adam Fisch, Shubhendu Trivedi, Fantine Huot, William W. Cohen, Michael Kaisers, Mirella Lapata, Kate Larson, Jacob Eisenstein Google DeepMind Heterogeneous AI systems composed of multiple models, architectures, harnesses, or inference-time settings can improve quality and efficiency by routing queries to thespecialistwho can answer most effectively at the lowest cost. Routing requires estimating each specialist’s expected return, but this value estimation has a cost. Cheap estimators (e.g., embedding-based predictors) are fast but noisy, while accurate estimators (e.g., fine-tuned models with access to retrieval results or partial reasoning traces) are expensive. We formalize this tradeoff as an instance of Pandora’s Box, the classical problem of optimal search with costly inspection. Under a Gaussian signal model, the resulting policies have closed-form value-of-information expressions that determine, for each specialist and input, whether refining the value estimate is worth its cost. We call the centralized policy Pandora’s Router. We extend this to a decentralized setting, Pandora’s Bidder, where specialists independently decide whether to invest in self-assessment before accepting an offered price to claim a query. Experiments across three domains—a standard multi-LLM benchmark, retrieval-augmented specialists, and LLMs with variable inference-time reasoning—show that Pandora’s Router matches the routing quality of exhaustive estimation, while querying the expensive estimator far less often. In

Add source references to the answer itself.

Answer is 23 words; the review target is at most 120.


</details>

## q08 — Manual review needed

How do submissions that change the learning algorithm compare with those that do not?

**Answer:** Submissions that change the learning algorithm (122 submissions) reach the learning procedure more often (46.4%) than those that do not (141 submissions that stay entirely on the run, 53.6%).

**Automatic findings:** Add source references to the answer itself. Check figures against their sources.

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

Add source references to the answer itself.

Check figures against their sources.

Answer is 29 words; the review target is at most 120.


</details>

## q09 — Manual review needed

What two kinds of task structure does TMI recover from computer-use traces?

**Answer:** TMI recovers two kinds of task structure: objective models and procedure models. [3][1]  • Objective models are hierarchical decompositions of the objective of a task into subobjectives the user pursues. [3] • Procedure models are trace-grounded compositions of control-flow operators specifying how the execution of a task is organized through sequencing and iteration. [3]

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

Answer is 51 words; the review target is at most 120.


</details>

## q18 — Manual review needed

How does G-CARL supervise factuality and response coverage?

**Answer:** G-CARL supervises factuality through the retrieval-grounded branch, which verifies report-grounded medical claims against evidence retrieved from a multi-source medical datastore, producing the factuality reward Rfact (Sec. 3.2).   The case-specific checklist branch optimizes response coverage by constructing a weighted checklist through MLLM generation followed by clinician-guided refinement, and evaluating the checklist coverage of the generated response to produce the checklist reward Rcheck (Sec. 3.3).

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

Answer is 63 words; the review target is at most 120.


</details>
