# Trials we did not keep in the notebook

These files are here so the comparison stays inspectable without crowding the
current results folder. They use the same five arXiv PDFs or the same 20-claim,
500-article SciFact subset as the baseline.

- `retrieval_reranked.json` and `retrieval_reranked_gap8.json`: a cross-encoder
  alone selected passages containing 23/28 literal fact snippets, but putting
  its top passage first sometimes led the answer model to confuse Pandora's
  Bidder with Pandora's Router. The corresponding SciFact runs lowered MRR@10
  from 0.950 to 0.929. The notebook now keeps those selected passages but
  orders them by the original vector search rank.
- `retrieval_fused.json`: equal-weight rank fusion dropped the arXiv literal
  fact matches to 10/28. `beir_scifact_20q_500d_fused.json` improved SciFact
  MRR@10 to 0.975, but the arXiv evidence loss made it a poor choice for this
  research-paper workflow. The rank-fusion option was removed from the code.
- `answers_reranked.json`: a two-question pilot with an answer-rewrite pass.
  The rewrite changed a partly useful q01 answer into a false abstention, so
  the rewrite pass was removed.
- `answers_qwen.json` and `answers_qwen_gap8.json`: short, incomplete pilots
  with `qwen2.5:7b`. One q01 answer was correct but cited an unrelated passage;
  another followed the Bidder passage and was wrong. The notebook keeps
  `llama3.2` as its existing default. These pilots do not establish a model
  comparison.
- `answer_pilot_ordered.json`: a one-question answer test after reordering.
  It gave the core value-of-information rule but added unrelated Bidder detail.
  The final passage-ordering setup has a full retrieval test, not a full answer
  quality test yet.
