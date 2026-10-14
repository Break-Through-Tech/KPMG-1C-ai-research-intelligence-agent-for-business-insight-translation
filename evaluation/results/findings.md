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
5. Add source page or chunk IDs to generated citations and require a verbatim
   evidence quote for each cited paper. The current notebook prompt requests
   numbered citations but not the direct quote required by issue #5.
6. Validate generated numbers and claims against the cited passage before
   showing an answer. Add a consistency check so an answer cannot both supply
   a result and claim that no result exists.

## Fresh answer findings

The [per-query manual review](answer_review.md) of 25 fresh `llama3.2`
answers found 10 full, 4 partial, and 9 failed responses among 23 answerable
questions. Both unanswerable questions were declined. Only 14/23 answerable
responses contained a citation, and none contained a verified direct quote.
The numeric error on q15 occurred even though the correct values were in a
retrieved passage; q08 contradicted itself. These are generation failures in
addition to the passage-selection misses above.

The project-specific labels are from five related papers, and the answer
review was performed by one person. Those results do not establish performance
on the larger intended corpus or on BEIR.

## Small BEIR SciFact diagnostic

The separate [SciFact result](beir_scifact_20q_500d.json) uses 20 claims
selected with seed 42 from BEIR's official test split. The search corpus has
500 article titles and abstracts: all 19 distinct judged relevant articles for
those claims plus fixed random distractors. The index holds 710 chunks. The
archive passed BEIR's published MD5 check. SciFact provides article relevance
labels, so this run evaluates retrieval only.

| Measure | Result |
| --- | ---: |
| Relevant article ranked first (hit@1) | 18/20 (90%) |
| Relevant article in the first five distinct articles (hit@5) | 20/20 (100%) |
| Mean recall@5 | 1.00 |
| MRR@10 | 0.95 |
| nDCG@10 | 0.963 |

Queries 577 and 212 placed their relevant article second; the other 18 placed
it first. This is a deliberately small, easier subset of a 5,183-article
corpus. These numbers must not be compared with published full-corpus BEIR
scores or taken as evidence of generated-answer accuracy. The test does show
that the retriever can find labeled scientific articles beyond the five PDFs
used in our project-specific questions.
