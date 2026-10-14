# Initial retrieval findings

Run on October 14, 2026 against the five committed PDFs, using the notebook
parser, `all-mpnet-base-v2` embeddings, Chroma, and `ResearchRetriever` with
five chunks, 30 candidates, and a two-chunk-per-paper cap. Detailed query
results are in [retrieval.json](retrieval.json).

| Measure | Result |
| --- | ---: |
| Answerable queries with a relevant paper in the retrieved set | 23/23 |
| Macro paper recall@5 | 1.00 |
| Paper MRR@5 | 0.978 |
| Labeled fact snippets present in retrieved chunks | 7/28 (25.0%) |
| Unanswerable queries that still returned chunks | 2/2 |
| Returned chunks with paper ID and source URL | 100% |

Finding the right paper did not reliably surface the specific passage needed
to answer. For example, the system retrieved the TMI paper for the query about
its 0.974 task-grouping result, but the top chunks did not contain that result.
This is evidence availability, not a measured answer error.

Increasing the per-paper cap from two to five, while keeping five output
chunks, raised fact-snippet coverage to 9/28 (32.1%) but reduced macro
paper recall to 0.957 on cross-paper questions. This suggests a tradeoff
between multiple sources and depth within one paper. The corresponding run is
in [retrieval_per_paper5.json](retrieval_per_paper5.json).

The notebook parser also labels some text after the references as author-name
sections. Such chunks appeared in retrieval results despite the bibliography
filter. Both unanswerable questions returned passages because the retriever
has no calibrated rejection rule by default.

## Improvement opportunities

1. Add a second-stage passage reranker or keyword-sensitive search so the
   numerical result or method detail requested by a question reaches context.
2. For cross-paper questions, reserve source diversity while allowing more
   passages from one paper when the question asks for several facts from it.
3. Stop indexing text after references, or mark that region as bibliography
   regardless of the parser's later heading guesses.
4. Calibrate an abstention rule on more labeled negatives; the current score
   alone has not been shown to separate answerable from unanswerable queries.
5. Run the notebook generator on these same passages and manually score claim
   support, required-fact coverage, citations, and direct quotes. Retrieval
   metrics alone cannot establish answer accuracy or completeness.

These labels are from five related papers and were created for this project.
They do not establish performance on the larger intended corpus or on BEIR.
