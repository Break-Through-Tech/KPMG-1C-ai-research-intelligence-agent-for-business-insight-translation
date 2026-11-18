# Optimization loop — checkpoint and best observed results

**Decision:** keep the existing tested default. The user requested wrapping up within a few minutes, so the model experiments were stopped before a complete candidate could be tested on all 25 questions. The best full-benchmark result remains **19 complete, 4 partial, 0 major issues and 2 correct abstentions**. Do not treat the examples below as a single improved pipeline or a new benchmark score.

## Results from this loop

| Candidate | Completed questions | Local validation failures | Outcome |
| --- | ---: | ---: | --- |
| llama3.1:8b, basic, quote, repair=False | 8 | 3 | Rejected: quote-copy failures and missing content. |
| llama3.1:8b, coverage, quote, repair=True | 4 | 3 | Stopped as unpromising: three failures remained after repair; high latency. |
| llama3.1:8b, coverage, citation, repair=False | 8 | 0 | Valid citation structure, but Llama still omitted key facts and numerical outcomes. |
| qwen3.5:9b, coverage, citation, repair=False | 5 | 0 | Promising individual answers; insufficient results for adoption. |

These are intentionally different pilot sizes. Local validation counts measure format/ID/quote validity, not factual correctness. No comparative accuracy percentage is inferred from these pilots.

## Best observed examples

These are selected examples from the Qwen pilot, reviewed against saved passages. They are not a full-benchmark result or outputs of a deployed automatic selector.

### q02: What is the difference between Pandora's Router and Pandora's Bidder?

Model/policy: `qwen3.5:9b` / `coverage`. Recorded time: 38.2s.

- Pandora's Router operates as a centralized policy that computes reservation prices to decide when querying a more accurate value estimate is worthwhile, interpolating between baselines by querying only when the value of information exceeds the cost. [2][3]
- Pandora's Bidder operates as a decentralized policy where the high bidder is selected in an auction, and each specialist refines its own value estimate only when the market price makes inspection worthwhile. [1][3]
- In the decentralized setting of Pandora's Bidder, maximizing local surplus does not always lead to better overall allocative efficiency, particularly when prices are inaccurate or queries are overpriced. [3]
- The tension between protecting a bidder's surplus by declining overpriced queries and assigning inputs to less capable specialists is absent in the centralized setting of Pandora's Router, where the router internalizes all costs and optimizes global welfare directly. [3]
- Pandora's Bidder corresponds to a single stage of an ascending-price mechanism with costly preference elicitation, isolating core components of decentralized prompt allocation under private value estimation with profit incentives. [4]
- Both Pandora's Router and Pandora's Bidder are derived from the same principle of balancing cheap screening and costly reasoning for routing, supporting allocation by either centralized routing or decentralized auctions. [1]

**Assessment:** The Qwen answer supplies the previously missing global-welfare/local-surplus distinction. Core content is complete, though the answer is long and citation alignment could be tighter.

- [2] Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation — chunk `2608.20316_4_22`
- [3] Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation — chunk `2608.20316_5_5`
- [1] Pandora's AI Model Routing Box: Efficient Allocation with Costly Value Estimation — chunk `2608.20316_4_1`

### q18: How does G-CARL supervise factuality and response coverage?

Model/policy: `qwen3.5:9b` / `coverage`. Recorded time: 33.4s.

- G-CARL supervises factuality through retrieval-grounded claim verification that decomposes reward supervision by verifying atomic claims against evidence retrieved from a multi-source medical datastore. [2][3]
- G-CARL supervises response coverage by constructing instance-specific weighted checklists through MLLM generation followed by clinician refinement to explicitly supervise demand satisfaction and expression quality. [1][3]
- The retrieval-grounded branch supervises medical factuality by verifying report-grounded medical claims against evidence retrieved from a multi-source medical datastore to produce the factuality reward Rfact. [4]
- The case-specific checklist branch optimizes demand satisfaction and expression quality by constructing a weighted checklist through MLLM generation followed by clinician-guided refinement, and evaluating the checklist coverage of the generated response to produce the checklist reward Rcheck. [4]
- Each checklist item is assigned an automatically generated weight, allowing the reward to emphasize the aspects most relevant to the current report and user question. [1]

**Assessment:** Qwen covers multi-source retrieval, atomic claim verification and weighted checklist construction. Core content is complete, though repetitive.

- [2] G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation — chunk `2608.20331_11_1`
- [3] G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation — chunk `2608.20331_1_1`
- [1] G-CARL: Grounded Checklist-Aligned Reward Learning for Patient-Oriented Medical Report Interpretation — chunk `2608.20331_2_5`

### q08: How do submissions that change the learning algorithm compare with those that do not?

Model/policy: `qwen3.5:9b` / `coverage`. Recorded time: 35.2s.

- Submissions that change the learning algorithm achieve a mean score of 0.226, whereas submissions that do not change the learning procedure achieve a mean score of 0.126. [2][3]
- The gap between submissions that reach the learning algorithm layer and those that do not represents the difference between the two groups rather than an effect caused by reaching that layer, as the systems that reach it more often are stronger to begin with. [3]
- Submissions that change the learning algorithm represent 46.4% of the submissions that change anything, while those that do not change the learning procedure but modify other aspects like budgets or hyperparameters represent 53.6%. [2]
- Submissions that change the learning algorithm focus on the objective, supervision signal, learning rule, and data, whereas submissions that do not change the learning procedure move budgets, checkpointing, hyperparameters, and capacity. [2]
- Submissions that reach the learning algorithm layer are where the distance to a better algorithm is closed, while most submissions never go there. [3]

**Assessment:** Core performance comparison is now correct: 0.226 versus 0.126, with the caveat attributed to stronger systems rather than stronger submissions. The extra 46.4%/53.6% claim cites [2] but those percentages appear in [3]; this is a citation-alignment warning, not an incorrect value. This is a complete core answer with an unresolved secondary citation issue.

- [2] AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement — chunk `2608.20318_1_7`
- [3] AI4AI-Bench: Benchmarking LLM Agents in Algorithmic Design for Recursive Self-Improvement — chunk `2608.20318_9_10`

## Implemented and verified

- Experimental structured answer module with schema-constrained passage IDs, local validation, explicit generation failures and an optional single repair. Invalid output is not presented as evidence that a question is unsupported.
- Reproducible runner saving model digest, prompts/policy, generation settings, exact contexts, raw outputs, checks and timings. Citation-only mode is available alongside stricter quote-copy mode.
- Optional hybrid BM25/dense rank fusion and a retrieval-sweep runner covering candidate count, context size, per-paper limits, score gap and reranker ordering. **These new retrieval variants were not benchmarked or enabled.**
- Fifteen additional questions and criteria frozen from the PDFs before answer generation; same corpus, not an external test. The baseline retrieval run found the relevant papers for all 12 answerable additions and 24/28 evidence phrases. This is retrieval coverage, not answer accuracy.
- 140 offline tests passed. Existing notebook defaults remain unchanged.

## Work not completed

The three-stage plan is incomplete under the new time limit: no new generator had a full 25-question run, the 15 added questions have no generated-answer comparison, and retrieval/ranking candidates have not been evaluated for significant answer-quality gains. No significant retrieval improvement is claimed.

**Next continuation:** finish the Qwen structured pilot, then run the strongest candidate on the full development set before any default switch. Only after that, run the prepared retrieval sweep and hold-out answer comparison.

Implementation uses Ollama’s documented JSON-schema `format` parameter; structural validity does not prove semantic support. [Ollama API documentation](https://github.com/ollama/ollama/blob/main/docs/api.md).
