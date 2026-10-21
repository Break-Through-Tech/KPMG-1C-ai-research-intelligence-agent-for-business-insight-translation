# AI Research Intelligence Agent for Business Insight Translation

**Break Through Tech AI Studio × KPMG · Fall 2026 · Prototype in progress**

AI papers arrive faster than teams can read them. This project explores a research assistant that finds relevant papers, answers questions using passages from those papers, and shows where each answer came from. The longer-term goal is to turn supported findings into useful business implications for KPMG reviewers. Human review is still needed before using an output for a business decision or client conversation.

## Team

| Name | GitHub handle | Contribution |
| --- | --- | --- |
| Kathleen Higgins | @kathigg | RAG evaluation, benchmark queries, and retrieval improvements |
| QiQi Li | @qiqi0211 | EDA, RAG evaluation, and prompt engineering |
| Thien Nguyen | @Trungu | EDA and LangChain pipeline development |

## Project overview

This is a [Break Through Tech AI Studio](https://www.breakthroughtech.org/) challenge hosted by KPMG. The prototype uses public AI research rather than internal or client data. A user asks a question; the system searches paper passages, reranks them, and asks an LLM to answer with passage citations and a direct source excerpt. The current notebook supports local Ollama (`llama3.2`) and an optional Google Gemini provider. The evaluation results below used Ollama, not Gemini.

The project measures **retrieval relevance**, **answer accuracy and completeness**, and whether citations and quotes can be traced to a source. Translating findings into business recommendations and assessing their usefulness with KPMG reviewers remain future work. See the [challenge overview](Challenge-Project-Overview.md) for the full scope.

## Data collection and exploration

- The [EDA workbook](notebooks/eda_workbook.ipynb) searches [arXiv](https://arxiv.org/) by seven team-selected business research themes and a broader computer-science search. Its pilot target is about 100 papers, with 70% from theme searches and 30% from general discovery. The themes were informed by [KPMG's published capabilities](https://kpmg.com/us/en/capabilities-services.html), but the mapping and split are project choices, not an official KPMG classification or an established sampling standard. The general search covers arXiv categories such as `cs.AI`, `cs.LG`, `cs.CL`, `cs.IR`, and `cs.CV`.
- The notebook caches metadata, deduplicates paper IDs while preserving collection-area labels, downloads PDFs within a storage budget, checks basic PDF integrity, and records page counts, approximate word counts, and extraction errors. Its recorded EDA run analyzed **85 downloaded papers**, ranging from about **2,900 to 46,500 words** and **5 to 151 pages**. Some keyword matches had weak business relevance, so search and screening need refinement.
- The larger downloaded collection lives in local `arxiv_data/` and is not included in this repository. The five PDFs in [`data/`](data/) are the committed, reproducible corpus for the project-specific evaluation. A separate small retrieval test uses [BEIR SciFact](https://github.com/beir-cellar/beir).

The parser cleans extracted PDF text and groups it into sections. Shared ingestion skips reference sections, splits text into chunks of about 350 tokens with 50-token overlap, and keeps stable paper and chunk IDs for tracing results. Page-level citation mapping and validation across more PDF layouts still need work.

## RAG pipeline

```text
arXiv metadata and PDFs → extracted sections → text chunks → MPNet embeddings
→ Chroma cosine search → passage reranking → cited LLM answer and source excerpt
```

The [shared ingestion code](notebooks/ingest.py) creates the Chroma index with `all-mpnet-base-v2` embeddings. The [retriever](notebooks/retrieval.py) filters non-content sections, limits how many chunks one paper can take, and uses a cross-encoder to select passages. It reserves room for multiple papers when a question calls for a comparison. The [answer checks](notebooks/answer_validation.py) flag invalid citation numbers, quotes that do not occur in the cited chunk, and certain answer contradictions. These checks cannot establish that every claim is true or that a quote supports the sentence next to it.

The current assistant workflow is in [the EDA workbook](notebooks/eda_workbook.ipynb). Query rewriting and Gemini are optional notebook paths; neither is part of the reported baseline evaluation.

## Setup and use

Use Python 3.10 or newer. From the repository root:

```bash
git clone https://github.com/Break-Through-Tech/KPMG-1C-ai-research-intelligence-agent-for-business-insight-translation.git
cd KPMG-1C-ai-research-intelligence-agent-for-business-insight-translation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r evaluation/requirements.txt
```

To run the notebook, also install its exploration and Jupyter dependencies:

```bash
python -m pip install arxiv pandas numpy matplotlib jupyterlab
cd notebooks
jupyter lab eda_workbook.ipynb
```

Run the notebook's metadata, PDF extraction, parser, embedding, shared-index, and assistant cells in order. It creates local `arxiv_data/` files and may download papers and embedding models on first use. Follow the notebook's cell-level instructions; **do not use “Run All,”** and run its optional PDF cleanup cell only if the integrity check identifies a problem. The five committed PDFs support the evaluation scripts documented in [evaluation/README.md](evaluation/README.md), but the full notebook collection needs its own local metadata catalog and PDFs.

For local answers, [install Ollama](https://ollama.com/), then run `ollama pull llama3.2` and `ollama serve` in a separate terminal before calling `ask_llm(question)` in the notebook. To use the optional Gemini provider, run `python -m pip install -r notebooks/requirements-gemini.txt` from the repository root, set `GEMINI_API_KEY` in your environment or a local root `.env`, and call `ask_llm(question, provider="google")`. Keep API keys out of Git.

## Evaluation and findings

Kathleen's [evaluation notes](evaluation/results/findings.md) separate two datasets:

| Dataset | What was tested | Result |
| --- | --- | --- |
| Five committed arXiv PDFs | 25 labeled questions: 23 answerable and two unanswerable | The latest retriever found every labeled relevant paper for **23/23 answerable questions**. Literal labeled fact snippets in selected chunks rose from **7/28** in the baseline to **23/28**. |
| BEIR SciFact subset | 20 test claims searched against 500 selected article titles and abstracts | The relevant article ranked first for **18/20** claims and appeared in the top five for **20/20**. MRR@10 was **0.950**. |

The 23/28 figure is an exact wording check on retrieved passages, **not answer accuracy**. The SciFact corpus was reduced from the full benchmark, so these scores should not be compared with published full-corpus BEIR scores. SciFact tests retrieval, not the assistant's written answers or business usefulness.

The first manually reviewed Ollama answer run on the 23 answerable arXiv questions had **10 full**, **4 partial**, and **9 failed** answers. In a later full run using an earlier reranked passage order, **18/23** answerable responses had mechanically verified citations and direct quotes, up from **0/23** verified quotes in the baseline. Some answers were still factually wrong. The notebook's final passage order has been tested for retrieval, but **has not had a full 25-answer quality rerun or claim-by-claim human review**. Citation and quote checks alone do not prove accuracy or completeness.

For the exact commands, result files, review rubric, and limitations, see [evaluation/README.md](evaluation/README.md) and [evaluation/results/findings.md](evaluation/results/findings.md). From the repository root, run the existing tests with:

```bash
python -m pytest -q
```

## Next steps

1. Run and manually review all 25 answers with the notebook's final retrieval settings, checking each claim and every requested part of each question against its cited passage.
2. Test retrieval on a larger, more representative paper collection and improve business-relevance screening, PDF section detection, and page-level traceability.
3. Compare optional query rewriting and Gemini with the same questions and passages before changing the evaluated default.
4. Add a clearly sourced business-implications layer and ask KPMG reviewers to assess usefulness and trust.

## License and acknowledgements

No license file has been selected for this repository. Please check with the project team before reusing the code or data. Thanks to KPMG's challenge advisors and the Break Through Tech AI Studio coach for project guidance.
