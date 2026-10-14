# Evaluation on the committed research papers

`benchmark.json` contains 25 manually labeled questions about the five PDFs in
`data/`: 20 single-paper questions, three cross-paper questions, and two
questions the papers cannot answer. The fact snippets in the labels were
checked against the source PDFs. This is a small project-specific diagnostic
set, not a population-level estimate of RAG quality or a BEIR benchmark.

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

## Review generated answers

The answer prompt and Ollama `llama3.2` call live in
`notebooks/eda_workbook.ipynb`. `run_answers.py` uses that prompt and model
with the newer `ResearchRetriever` passage and paper-citation formatting.
Start a local Ollama server and pull the model, then run:

```bash
ollama serve  # separate terminal
ollama pull llama3.2
python evaluation/run_answers.py
python evaluation/check_answers.py
```

The answer runner resumes completed queries in `evaluation/results/answers.json`.
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
