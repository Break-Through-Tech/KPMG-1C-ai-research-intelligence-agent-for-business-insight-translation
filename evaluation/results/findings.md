# Evaluation results — October 14, 2026

**A quick summary before you get into it:**
There are two different mini-tests here. The first uses our arXiv papers and questions and labels drafted by Codex (GPT-6-Sol). The second uses BEIR's public SciFact data and its relevance labels.

## 1. arXiv paper test

This dataset comes from the five arXiv research-paper PDFs committed in [`data/`](../../data/); Codex (GPT-6-Sol) drafted 25 questions and their labels from those papers. The labeled fact snippets were checked against the PDFs during preparation, but the repo does not document an independent human annotation pass.

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
wrong. The notebook prompt at the time also didn't ask for the direct quote
required by issue #5.

### Suggestions from the first run

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

### What changed in the notebook

The shared ingestion code now keeps reference sections out of the index and
adds a stable ID to each chunk. Retrieval considers more passages, reranks
them, reserves space for a second paper when the question asks across papers,
and shows the chosen passages in vector-search order. The answer cell uses
those passage numbers, adds a literal excerpt from a cited paper, and points
out citation and quote problems for review.

On the **same 25 questions and five PDFs**, the [latest retrieval
run](retrieval_ordered.json) got these results:

| Measure | Earlier run | Latest run |
| --- | ---: | ---: |
| Questions with every labeled paper found | 23/23 | 23/23 |
| Paper MRR@5 | 0.978 | 1.000 |
| Literal labeled fact snippets in chosen chunks | 7/28 | 23/28 |

The literal snippet check still has the wording limitation explained above.
The larger gain suggests the model gets more of the facts it needs, but it
doesn't prove the written answers are right.

We also did a [full 25-question `llama3.2` answer
run](answers_grounded.json) with an earlier version of the reranked passage
order. Mechanical [source checks](answer_checks_grounded.json) found citations
and verified literal quotes in **18/23** answerable responses, versus 14/23
citations and 0/23 quotes in the original run. Both unanswerable questions
were declined. The model now answered q11's **74.9%** and q13's **92 / 454**
questions because those facts reached its context. It still confused Router
with Bidder on q01, contradicted itself on q04, gave the wrong comparison on
q08, and declined q12. A quote matching a source does not by itself prove
that the answer is faithful to that source.

The notebook's final passage order has been rerun for retrieval, but **not for
all 25 generated answers**. A [one-question pilot](../archive/didnt_work/answer_pilot_ordered.json)
still added unrelated Bidder details to a Router answer. The next answer
quality comparison needs a full run and human review of every claim.

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

With the [notebook's current passage selection and
ordering](beir_scifact_20q_500d_ordered.json), hit@1 stayed at **18/20**,
hit@5 stayed at **20/20**, MRR@10 stayed at **0.950**, and nDCG@10 stayed at
**0.963** on the same tiny subset. This test still says nothing about answer
accuracy or business usefulness. Earlier reranker-only and rank-fusion trials
are kept in the [archive](../archive/didnt_work/README.md) with the reasons we
didn't use them.
