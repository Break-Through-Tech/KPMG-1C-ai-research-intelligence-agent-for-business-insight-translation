# Evaluation results — October 14, 2026

**A quick summary before you get into it:**
There are two different mini-tests we did. The first you'll read is on arXiv (our actual data, GPT-6-Sol-generated ground-truth), the second is on BEIR (not our data, publically available scientific papers and their ground-truths). 

## 1. arXiv paper test

This dataset comes from the five arXiv research-paper PDFs committed in [`data/`](../../data/); it's got 25 manually written and labeled questions about those papers.

Twenty questions ask about one paper, three need two papers, and two can't be
answered from these papers at all. For this, the parser and prompt in
`eda_workbook.ipynb`, plus `all-mpnet-base-v2`, Chroma, and
`ResearchRetriever` were used. For each question, the retriever picked up to five short
pieces of paper text ("chunks") from 30 candidates, with no more than two
chunks per paper.

### Did it find the right papers and passages?

| Measure | Result |
| --- | ---: |
| Answerable questions with every labeled relevant paper retrieved | 23/23 (100%) |
| Macro paper recall@5 | 1.000 |
| Paper MRR@5 | 0.978 |
| Labeled fact snippets found literally in retrieved chunks | 7/28 (25.0%) |
| Unanswerable questions that still returned chunks | 2/2 |
| Returned chunks with paper ID and source URL | 100% |

The [question-by-question results](retrieval.json) show that it found the right
papers every time, but it didn't always find the part of the paper needed to
answer. For q13, it found the travel-behavior paper but didn't send the model
the passage with **92 commuters** and **454 observations**.

The **7/28** number is a strict wording check: we looked for 28 short fact
snippets in the chosen chunks, ignoring PDF punctuation and spacing. A passage
can still contain the answer in different words and count as a miss. For
example, q10's chunk included **0.974**, but it didn't contain the full labeled
phrase. So 7/28 tells us about exact snippet matches, **not** how often the
model answered correctly.

Codex and I also tried allowing five chunks per paper instead of two. That raised the
exact snippet matches to **9/28 (32.1%)**, but paper recall fell to **0.957**:
one paper could take more of the five available slots, leaving less room for a
second relevant paper. The [alternate run](retrieval_per_paper5.json) has the
details. Codex also saw chunks from reference lists in some results because the
PDF parser mistook author names for section headings.

### Were the answers right and complete?

Codex gave the same 25 questions and retrieved chunks to the notebook's
`llama3.2` model. One reviewer checked the [fresh answers](answers.json)
against the passages and the expected facts. **Full** means the answer got
every requested part right. **Partial** means it said something relevant and
correct but missed a part. **Fail** means it was wrong, contradicted itself,
or declined a question that the papers could answer. We used temperature 0
and seed 42.

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

The [manual review](answer_review.md) and [citation checks](answer_checks.json)
show what happened on each question. For q02, q11, and q13, the model didn't
get the passage it needed. On q15, it **did** get the right passage but mixed
up two numbers: random forest scored **69.6%**, while the best vision-based
setup scored **71.5%**. On q08, it gave the right comparison and then said the
papers didn't answer the question. So we have both retrieval and answer-writing
problems. A citation number can be valid even when the claim next to it is
wrong. The current notebook prompt also doesn't ask for the direct quote
required by issue #5.

### Possible improvements (just suggestions, they may or may not work)

1. Pick passages that contain the specific number or method the question asks
   for, while leaving room for both papers on two-paper questions.
2. Keep reference-list text out of the index, and test when the system should
   say it doesn't have an answer.
3. Require a direct quote and a page or chunk ID with each citation, then
   check the numbers in an answer against its cited passage.
4. Catch answers that give a result and then say no result exists.

This test covers only five related papers, and one person reviewed the
answers. It doesn't tell us how the system will do on the larger planned
research collection.

## 2. BEIR SciFact subset

This dataset comes from [BEIR's official SciFact archive](https://github.com/beir-cellar/beir), using 20 claims from its test split and a 500-article subset of its scientific-paper corpus.

We picked 20 claims from SciFact's 300 test claims using seed 42. We searched
500 articles: all **19 distinct articles marked relevant** to those claims,
plus randomly picked distractors from the full 5,183-article collection. Their
titles and abstracts became **710 chunks** in the same MPNet, Chroma, and
`ResearchRetriever` pipeline. The download passed BEIR's checksum check.
SciFact tells us which articles are relevant, so this run checks retrieval,
not the model's written answers.

| Measure | Result |
| --- | ---: |
| Relevant article ranked first (hit@1) | 18/20 (90%) |
| Relevant article in the first five distinct articles (hit@5) | 20/20 (100%) |
| Relevant article in the first ten distinct articles (hit@10) | 20/20 (100%) |
| Mean recall@5 | 1.000 |
| Mean recall@10 | 1.000 |
| MRR@10 | 0.950 |
| nDCG@10 | 0.963 |

In the [SciFact results for each claim](beir_scifact_20q_500d.json), the right
article came second for claims 577 and 212 and first for the other 18. This
was a small test. Searching 500 articles is easier than
searching all 5,183, so **don't compare these scores with published results
from the full BEIR corpus**. Many SciFact claims are also biomedical, unlike
the business research questions this project is meant to handle.
