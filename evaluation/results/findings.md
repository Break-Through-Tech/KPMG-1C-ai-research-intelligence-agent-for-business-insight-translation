# Evaluation results — October 14, 2026

## 1. arXiv paper test

This dataset comes from the five arXiv research-paper PDFs committed in [`data/`](../../data/), with 25 manually written and labeled questions about those papers.

Twenty questions target one paper, three require two papers, and two cannot be
answered from the collection. The run used the parser and prompt in
`eda_workbook.ipynb`, `all-mpnet-base-v2` embeddings, cosine Chroma, and
`ResearchRetriever`. The default retrieval setting returned up to five chunks
from 30 candidates, capped at two chunks per paper.

### Retrieval relevance and evidence

| Measure | Result |
| --- | ---: |
| Answerable questions with every labeled relevant paper retrieved | 23/23 (100%) |
| Macro paper recall@5 | 1.000 |
| Paper MRR@5 | 0.978 |
| Labeled fact snippets found literally in retrieved chunks | 7/28 (25.0%) |
| Unanswerable questions that still returned chunks | 2/2 |
| Returned chunks with paper ID and source URL | 100% |

The [per-query retrieval results](retrieval.json) show strong paper matching,
but the selected passages sometimes lacked the requested detail. For q13, the
system found the travel-behavior paper yet did not pass the **92 commuters**
and **454 observations** to the answer model. The 7/28 fact-snippet measure is
a strict text match after removing PDF punctuation and whitespace. It can
undercount usable evidence when a passage states a fact differently: q10's
retrieved passage contained the **0.974** result even though the longer labeled
phrase did not match literally. This metric is a passage-selection diagnostic,
not an answer-accuracy score.

As a sensitivity check, raising the per-paper cap from two to five increased
literal fact coverage to **9/28 (32.1%)**, while macro paper recall fell to
**0.957** because one paper could occupy more of the five output slots. See
the [alternate retrieval run](retrieval_per_paper5.json). The PDF parser also
mislabels some text after references as author-name sections, allowing
bibliography-like chunks into results.

### Generated-answer accuracy and completeness

The same 25 questions were answered with the notebook's `llama3.2` prompt and
model, using the newer retriever's passages and paper citation numbers. One
reviewer checked the [fresh answers](answers.json) against the retrieved
passages and labeled facts. “Full” means the answer correctly covers every
requested part; “partial” means it contains correct relevant material but
omits a part; “fail” means it is wrong, contradictory, or declines an
answerable question. Generation used temperature 0 and seed 42.

| Measure | Result |
| --- | ---: |
| Full answers among 23 answerable questions | 10/23 |
| Partial answers | 4/23 |
| Failed answers | 9/23 |
| Appropriate abstentions on unanswerable questions | 2/2 |
| Answerable responses containing a citation | 14/23 |
| Responses with an out-of-range citation number | 0/25 |
| Answerable responses with a verified direct quote | 0/23 |

Full: q01, q03–q07, q09, q10, q19, q20. Partial: q14, q17, q18, q23.
Fail: q02, q08, q11–q13, q15, q16, q21, q22. q24 and q25 appropriately
abstained.

The [per-question manual review](answer_review.md) and [mechanical citation
checks](answer_checks.json) provide the detailed judgments. q02, q11, and q13
missed facts that were absent from their retrieved context. q15 gave random
forest's accuracy as **71.5%** although its cited passage reports **69.6%**
for random forest and **71.5%** for the best vision-based setup. q08 gave the
correct numeric comparison and then claimed the papers did not address the
same question. Thus passage selection and answer generation both contributed
to failures. A citation number being in range does not mean its claim is
supported. The notebook prompt does not request the direct non-paraphrased
quote specified in issue #5.

### Improvement opportunities and limits

1. Retrieve and rerank passages for the specific number or method detail in
   the question; preserve source diversity for cross-paper questions.
2. Exclude text after each PDF's references more reliably, and calibrate a
   rejection rule with more negative questions.
3. Require a verbatim supporting quote and a source page or chunk ID with
   each citation; verify generated numbers against the cited passage.
4. Add a consistency check for answers that both state a result and claim no
   result exists.

These project-specific labels cover only five related papers. The answer
review involved one reviewer. Neither result estimates performance on the
larger intended research corpus.

## 2. BEIR SciFact subset

This dataset comes from [BEIR's official SciFact archive](https://github.com/beir-cellar/beir), using 20 claims from its test split and a 500-article subset of its scientific-paper corpus.

The 20 test claims were sampled with seed 42 from 300 labeled test claims. The
500 indexed articles include all **19 distinct judged relevant articles** for
those claims plus fixed random distractors from the full 5,183-article corpus.
Their titles and abstracts produced **710 chunks** with the repo's MPNet,
Chroma, and `ResearchRetriever` pipeline. The downloaded archive matched
BEIR's published MD5 checksum. SciFact labels article relevance, so this run
tests retrieval only; it does not score generated answers.

| Measure | Result |
| --- | ---: |
| Relevant article ranked first (hit@1) | 18/20 (90%) |
| Relevant article in the first five distinct articles (hit@5) | 20/20 (100%) |
| Relevant article in the first ten distinct articles (hit@10) | 20/20 (100%) |
| Mean recall@5 | 1.000 |
| Mean recall@10 | 1.000 |
| MRR@10 | 0.950 |
| nDCG@10 | 0.963 |

In the [per-query SciFact results](beir_scifact_20q_500d.json), queries 577
and 212 ranked their relevant article second; the other 18 ranked it first.
This is a deliberately small search set. Including the relevant articles and
removing most distractors makes it easier than full-corpus BEIR, so these
scores are **not comparable with published full-corpus BEIR scores**. SciFact
also contains many biomedical claims rather than the project's business
research questions.
