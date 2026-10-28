# Evaluation on the committed research papers

`benchmark.json` contains 25 questions and labels drafted by Codex
(GPT-6-Sol) from the five PDFs in `data/`: 20 single-paper questions, three
cross-paper questions, and two questions the papers cannot answer. The labeled
fact snippets were checked against the source PDFs during preparation; the repo
does not document an independent human annotation pass. This is a small
project-specific diagnostic set, not a population-level estimate of RAG quality
or a BEIR benchmark.

## Use the changes in the team notebook

Open [`notebooks/eda_workbook.ipynb`](../notebooks/eda_workbook.ipynb) and run
its metadata, PDF extraction, parser, and embeddings cells, followed by the
shared-index and research-assistant cells. The notebook now calls
`notebooks/ingest.py`, `notebooks/retrieval.py`, and
`notebooks/answer_validation.py` directly. It builds a resumable Chroma index,
skips reference sections, reranks candidate passages, shows stable chunk IDs
with citations, and checks that any attached quote appears in its cited chunk.
The notebook has its own step-by-step setup note immediately above the answer
cell. Install `evaluation/requirements.txt`; the answer cell uses a local
Ollama server with `llama3.2` by default. It writes a new
`research_mpnet_cosine_v3_citable` collection so an older index cannot hide
the parser and citation-metadata changes.

## Run the retrieval evaluation

From the repository root:

```bash
python -m pip install -r evaluation/requirements.txt
python evaluation/run_retrieval.py
python -m pytest -q
```

The script reads the checked-in PDFs, executes the `process_paper` parser from
`notebooks/eda_workbook.ipynb`, calls `notebooks/ingest.py` to build a cosine
Chroma index with the notebook's MPNet model, and calls
`notebooks/retrieval.py`. The index is cached under `.evaluation_cache/` and is
invalidated when a PDF or the parser changes. Results go to
`evaluation/results/retrieval.json`.

Paper-level `macro_recall_at_k` averages the fraction of labeled relevant
papers found per answerable question. `mrr_at_k` uses the rank of the first
relevant **paper**. `evidence_coverage` is the share of labeled fact snippets
found literally (ignoring PDF punctuation and whitespace) in the retrieved
chunks. It measures whether the generator received specific evidence, **not**
whether its answer was factual. The two unanswerable questions are counted
separately. `citation_metadata_complete` checks paper IDs and source URLs on
returned chunks; it does not validate generated citations.

To reproduce the notebook's current retrieval settings on the five PDFs:

```bash
python evaluation/run_retrieval.py --output evaluation/results/retrieval_ordered.json --per-paper 4 --fetch-k 60 --rerank-model cross-encoder/ms-marco-MiniLM-L6-v2 --max-rerank-gap 8 --order-by-vector
```

The latest run found all labeled relevant papers and 23/28 labeled snippets
literally in selected chunks. The original baseline found 7/28 snippets. This
strict wording check does not measure answer correctness.

## BEIR SciFact relevance test

```bash
python evaluation/run_beir_scifact.py
```

For the notebook's current retrieval settings on the **same** tiny subset:

```bash
python evaluation/run_beir_scifact.py --output evaluation/results/beir_scifact_20q_500d_ordered.json --rerank-model cross-encoder/ms-marco-MiniLM-L6-v2 --max-rerank-gap 8 --order-by-vector
```

This downloads the [official BEIR SciFact dataset](https://github.com/beir-cellar/beir)
and verifies its published MD5 checksum. It samples **20 claims** from the
official 300-query test split (seed 42), includes every judged relevant article
for those claims, and adds fixed random distractors for a **500-article**
corpus. Each article's title and abstract form its indexed text. Duplicate
titles receive an ID suffix in metadata so the repo's title-keyed ingestion
can keep both articles.

The report in `evaluation/results/beir_scifact_20q_500d.json` gives document-level
hit@1/5/10, recall@5/10, MRR@10, and nDCG@10 against BEIR's test qrels.
Results at five papers are obtained from the first five **distinct** article
IDs returned by the retriever. SciFact consists of scientific claims and
article abstracts, with many biomedical topics. This is a small diagnostic
subset; because the search corpus is reduced, its scores are **not comparable
to published full-corpus BEIR scores**. It tests retrieval relevance, not
answer accuracy or business usefulness.

## Review generated answers

The answer prompt and Ollama `llama3.2` call live in
`notebooks/eda_workbook.ipynb`. `run_answers.py` uses that prompt and model
with passage-specific citations.
Start a local Ollama server and pull the model, then run:

```bash
ollama serve  # separate terminal
ollama pull llama3.2
python evaluation/run_answers.py
python evaluation/check_answers.py
```

The answer runner resumes completed queries in its chosen output file. To test
the notebook's current retrieval settings, pass `--retrieval
evaluation/results/retrieval_ordered.json` and a new `--output` path. The full
25-answer result in `results/answers_grounded.json` used an earlier passage
order; the final ordering has a full retrieval test and a one-answer pilot,
not a full answer-quality run.
`check_answers.py` verifies citation numbers, literal quotes against the
retrieved passages, and the notebook prompt's abstention phrase. It cannot
verify claim support. For each answer, inspect the source passages and record:

| Dimension | Pass condition |
| --- | --- |
| Citation validity | Every cited number maps to a supplied paper and the cited passage supports the claim. |
| Factual accuracy | Every material claim is supported by its cited passage; numbers, direction, and caveats are correct. |
| Completeness | All fact snippets required by the benchmark question are answered, or missing evidence is stated explicitly. |
| Direct quote | A verbatim quote from the cited paper is present when required by issue #5. |
| Abstention | Questions 24–25 are declined without invented KPMG or market facts. |

Report claim accuracy as `supported material claims / all material claims`,
completeness as `answered required facts / all required facts`, and the number
of answers with a valid citation and direct quote. Do not treat a citation or
quote by itself as proof of accuracy. The retrieval report does not supply
these answer metrics. The first completed [manual review](results/answer_review.md)
uses a full/partial/fail rubric for each answer and records the observed
generation failures. `notebooks/evaluation.ipynb` provides a notebook view of
both runs and the source passages.
