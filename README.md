<p align="center">
  <a href="https://www.breakthroughtech.org/"><img src="assets/break-through-tech-logo.png" alt="Break Through Tech logo" width="150"></a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://kpmg.com/us/en.html"><img src="assets/kpmg-logo.png" alt="KPMG logo" width="180"></a>
</p>

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

This is a [Break Through Tech AI Studio](https://www.breakthroughtech.org/) challenge hosted by KPMG. The prototype uses public AI research rather than internal or client data. A user asks a question; the system searches paper passages, reranks them, and asks an LLM to answer with passage citations and direct source excerpts. The notebook uses local Ollama (`qwen2.5:7b`) by default and also supports optional Google Gemini. The evaluation results below used Ollama, not Gemini.

The project measures **retrieval relevance**, **answer accuracy and completeness**, and whether citations and quotes can be traced to a source. Translating findings into business recommendations and assessing their usefulness with KPMG reviewers remain future work. See the [challenge overview](Challenge-Project-Overview.md) for the full scope.

## Data collection and exploration

- The [EDA workbook](notebooks/eda_workbook.ipynb) searches [arXiv](https://arxiv.org/) by seven team-selected business research themes and a broader computer-science search. Its pilot target is about 100 papers, with 70% from theme searches and 30% from general discovery. The themes were informed by [KPMG's published capabilities](https://kpmg.com/us/en/capabilities-services.html), but the mapping and split are project choices, not an official KPMG classification or an established sampling standard. The general search covers arXiv categories such as `cs.AI`, `cs.LG`, `cs.CL`, `cs.IR`, and `cs.CV`.
- The notebook caches metadata, deduplicates paper IDs while preserving collection-area labels, downloads PDFs within a storage budget, checks basic PDF integrity, and records page counts, approximate word counts, and extraction errors. Its recorded EDA run analyzed **85 downloaded papers**, ranging from about **2,900 to 46,500 words** and **5 to 151 pages**. Some keyword matches had weak business relevance, so search and screening need refinement.
- The larger downloaded collection lives in local `arxiv_data/` and is not included in this repository. The five PDFs in [`data/`](data/) are the committed, reproducible corpus for the project-specific evaluation. A separate small retrieval test uses [BEIR SciFact](https://github.com/beir-cellar/beir).

For a quick hands-on test, use the [starter dataset](sample_data/README.md): it lists all five included PDFs and seven representative questions with expected source papers and short check hints. The CSV files are UTF-8 and can be opened without running the model.

The parser cleans extracted PDF text and groups it into sections. Shared ingestion skips reference sections, splits text into chunks of about 350 tokens with 50-token overlap, and keeps stable paper and chunk IDs for tracing results. Page-level citation mapping and validation across more PDF layouts still need work.

## RAG pipeline

```text
arXiv metadata and PDFs → extracted sections → text chunks → MPNet embeddings
→ Chroma cosine search → passage reranking → cited LLM answer and source excerpt
```

The [shared ingestion code](notebooks/ingest.py) creates the Chroma index with `all-mpnet-base-v2` embeddings. The [retriever](notebooks/retrieval.py) filters non-content sections, limits how many chunks one paper can take, and uses a cross-encoder to select passages. It reserves room for multiple papers when a question calls for a comparison. The [answer checks](notebooks/answer_validation.py) flag invalid citation numbers, quotes that do not occur in the cited chunk, and certain answer contradictions. These checks cannot establish that every claim is true or that a quote supports the sentence next to it.

The current assistant workflow is in [the EDA workbook](notebooks/eda_workbook.ipynb). Raghul's [browser UI](frontend/README.md) puts live questions first and also includes example answers, source dialogs, saved briefs, and an evidence score. The evidence score helps reviewers inspect outputs; it is [not a calibrated correctness probability](docs/evidence_score.md). Query rewriting and Gemini remain optional paths outside the reported default evaluation.

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

For a quick demo using the **five committed PDFs**, scroll to **“Run the research assistant on the five committed papers”** near the bottom. Run the next two setup cells, then edit and run the example question cell. The first setup cell builds the saved index if it is missing. You do not need to run the earlier EDA cells for this demo. The full EDA workflow uses local `arxiv_data/` files and requires its metadata, PDF extraction, parser, and embedding cells in order. Follow the notebook's cell-level instructions; **do not use “Run All,”** and run its optional PDF cleanup cell only if the integrity check identifies a problem.

For local answers, [install Ollama](https://ollama.com/), then run `ollama pull qwen2.5:7b` and `ollama serve` in a separate terminal before calling `ask_llm(question)` in the notebook. The smaller `llama3.2` model can still be selected with `ask_llm(question, model="llama3.2")`, but it had more citation and content errors in this test. To use the optional Gemini provider, run `python -m pip install -r notebooks/requirements-gemini.txt` from the repository root, set `GEMINI_API_KEY` in your environment or a local root `.env`, and call `ask_llm(question, provider="google")`. Keep API keys out of Git.

To ask a new question across arXiv, keep Ollama running and start the browser chat with `python frontend_server.py --port 8765 --arxiv`, then open `http://127.0.0.1:8765`. Each question searches arXiv's catalog, reads passages from up to three top matching PDFs, and asks local Qwen for a cited answer. It searches on demand rather than indexing every arXiv paper. The separate five-paper evaluation path is still available with `--live-root .`; running without either flag shows example answers only. See the [frontend guide](frontend/README.md).

### Share the chat with GitHub Pages

The [Pages site](docs/demo/) includes 25 recorded example answers. **Ask arXiv** can also work there when a separate HTTPS API is deployed and its URL is configured in the static build. GitHub Pages serves the browser files; the API searches arXiv and generates answers. The [hosting guide](docs/hosting.md) has the exact setup, including the server-only model key. Until that setup is complete, the Pages site keeps Ask arXiv disabled and the examples remain available. The live hosted path has not been measured by the five-paper or BEIR evaluations below.

To refresh the static files after changing the frontend or saved evaluation run, run `python scripts/build_pages_demo.py` from the repository root and commit the updated `docs/demo/` files. To publish, a repository maintainer can set **Settings → Pages → Build and deployment → Deploy from a branch**, select this branch (or `main` after merging), and choose `/docs`. The site is at `https://break-through-tech.github.io/KPMG-1C-ai-research-intelligence-agent-for-business-insight-translation/`. Treat the demo as public; do not add private papers, prompts, or client data to its generated files.

## Evaluation and findings

### Five-paper arXiv test

This project-specific dataset uses the five PDFs committed in [`data/`](data/) and 25 project-drafted questions in [`evaluation/benchmark.json`](evaluation/benchmark.json). The latest run uses local `qwen2.5:7b` after the teammate's PDF parser fix; the index contains 288 chunks.

| Check | Result | What it means |
| --- | --- | --- |
| Find the labeled relevant paper | **23/23** answerable questions (100%) | Paper-level retrieval on this small corpus. |
| Find the exact labeled fact snippets | **23/28** snippets (82%) | Literal presence in selected chunks; some missed snippets may appear in different words. |
| Cover requested facts in direct answers | **19/20** complete (95%); **1/20** partial | One review against the fixed labels found that q01 omitted the Router's stopping rule. |
| Pass citation, exact-quote, and number checks | **20/20** direct answers (100%) | Mechanical traceability, not proof that every claim is supported or complete. |
| Paper-search and abstention cases | **3/3** source lists included both labeled papers; **2/2** unsupported questions were declined | The paper lists and one abstention use rules rather than a Qwen-generated answer. |

The original questions and labels were drafted by Codex and checked against the PDFs, without an independent annotation pass. The content review used one reviewer. These results are useful for diagnosing this prototype; they do not estimate accuracy across a broad research collection or business usefulness for KPMG. See the [question-by-question review](evaluation/results/branch_evaluation.md) and [saved answer checks](evaluation/results/answer_checks_after_parser_integrated.json).

### Tiny BEIR SciFact retrieval test

This subset comes from BEIR's official SciFact test split: 20 claims searched against 500 selected article titles and abstracts, including their labeled relevant articles.

The relevant article ranked first for **18/20** claims (90%) and appeared in the top five for **20/20** (100%). MRR@10 was **0.950** and nDCG@10 was **0.963**. This tests retrieval only. The reduced corpus makes it easier than the full BEIR benchmark, so these scores cannot be compared with published full-corpus results. See the [saved SciFact run](evaluation/results/beir_scifact_after_integration.json).

For the exact commands, result files, question-by-question review, and limitations, see [evaluation/README.md](evaluation/README.md) and [evaluation/results/branch_evaluation.md](evaluation/results/branch_evaluation.md). From the repository root, run the existing tests with:

```bash
python -m pytest -q
```

The [advisor demo brief](docs/presentation_brief.md) has a short walkthrough. The [issue status](docs/issue_status.md) distinguishes implemented work from the parts that still need reviewer evidence. The [business prompt pilot](docs/prompt-templates/pilot_review.md) uses fixed passages from one paper; it is separate from the live answer evaluation.

## Next steps

1. Have teammates or KPMG reviewers independently label new questions and assess answer support, completeness, business usefulness, and trust.
2. Test retrieval on a larger paper collection and improve business-relevance screening, PDF section detection, and page-level traceability.
3. Compare optional query rewriting and Gemini with the same questions and passages before changing the evaluated default.
4. Have KPMG reviewers try the interactive business-application view and compare it with the experimental prompt template on a larger, fixed evidence set.

## License and acknowledgements

No license file has been selected for this repository. Please check with the project team before reusing the code or data. Thanks to KPMG's challenge advisors and the Break Through Tech AI Studio coach for project guidance.
