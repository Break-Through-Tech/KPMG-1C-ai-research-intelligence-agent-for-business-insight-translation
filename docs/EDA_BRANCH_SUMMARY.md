# EDA work completed across branches

This summary records the branch versions available in the repository on September 30, 2026. Attribution is based on commit authors and inspected notebook code. These branches share a development history; their findings are not separate independent experiments.

## Project goal

Explore publicly available AI research, assess data quality, and identify gaps and preprocessing needs for a retrieval-augmented assistant that translates research into cited business insights. Business relevance and source quality matter alongside successful PDF extraction.

## Contributions

| Branch and inspected tip | Contributor / commits | Work completed |
| --- | --- | --- |
| `main` — `a1ce3d2` | Project setup and challenge documentation | Defines the project, EDA milestone, public arXiv source, storage constraint, and evaluation expectations. No EDA implementation at this tip. |
| `test-alex` — `a1ce3d2` | Same tip as main | No additional EDA work relative to main. |
| `alex-eda-visualizations` — `940d488` | Alex Nguyen: `b97d84b`, `f8f075e`; Adarsh Alex: `940d488` | Initial EDA, revised collection pipeline, descriptive visualizations, and dataset findings. |
| `Braa-EDA` — `44e8cfb` | braa-oudeh: `0849a6d`, `44e8cfb` | Inherits the prior EDA; adds text cleaning, heading detection, structured section dictionaries, and formatting. |
| `EDA-Feature-Engineering` — `1992fab` | Alex Nguyen: `1992fab` | Inherits the EDA and section parser; adds the initial LangChain/chunking/embedding/Chroma retrieval workflow. |
| `eda-coverage-visualizations` — based on `1992fab` | Current contribution | Adds a separate bias-diagnostic notebook under `workbook/`, this summary, and a limitations document. |

### Collection and descriptive EDA

The shared notebook configures seven business areas with ten requested papers each and a general category with thirty. It searches abstracts using keywords and sorts by newest submission. It saves metadata and search caches, deduplicates using version-independent arXiv IDs, inventories/downloads PDFs, and enforces a 900 MB working budget.

Quality checks include PDF header/end markers, page count, approximate extracted words, low-text-page counts, and extraction exceptions. Descriptive analysis includes category counts, area proportions, word/page histograms, file-size versus word-count scatterplots, and title/abstract tables for manual relevance review. Relevance fields are provided but are not completed labels.

### Section parsing

Braa's work cleans PDF lines and splits text into named or numbered sections. The later feature-engineering work separates parsing from initial extraction and reuses saved page text. This supports section-aware processing. A heading referring to parsing text and images is not evidence of a completed image-processing implementation.

### Initial retrieval pipeline

The feature-engineering branch prepares LangChain documents with paper/section metadata, uses a five-paper sample, splits into nominal 350-token chunks with 50-token overlap, embeds with `sentence-transformers/all-mpnet-base-v2`, and stores/retrieves through Chroma. Saved outputs report 38 section documents, 175 chunks, and two example query results. These are prototype checks, not a benchmark establishing accuracy, fairness, or performance across business areas.

## New visualization notebook

Open [workbook/eda_bias_visualizations.ipynb](../workbook/eda_bias_visualizations.ipynb).

It reads saved outputs from the existing [EDA workbook](../notebooks/eda_workbook.ipynb), without executing its download or cleanup cells. Four charts address:

1. Planned topic quotas versus recorded area-assignment shares.
2. Concentration among the ten reported category labels.
3. Paper-length variation as a possible source of unequal chunk representation.
4. Conflicting recorded corpus sizes as a reproducibility problem.

The clean checkout has no raw metadata catalog or paper-level EDA CSV. The new notebook therefore labels its figures as recorded-output diagnostics. It does not reconstruct full records from truncated tables or claim those figures describe one newly audited corpus. Python and Matplotlib are required; instructions are inside the notebook. Charts display inline, with no extra output directory.

## Remaining EDA work

Reconcile one fixed catalog with the PDFs, complete business-relevance labels, inspect extraction fidelity, and measure coverage using consistent denominators. Follow up with actual chunk/exposure measurements before concluding that document length biases retrieval. See [EDA_LIMITATIONS.md](EDA_LIMITATIONS.md) for the evidence, limits, and preprocessing needs.

## Source history

- [Initial EDA](https://github.com/Break-Through-Tech/KPMG-1C-ai-research-intelligence-agent-for-business-insight-translation/commit/b97d84b)
- [Revised collection](https://github.com/Break-Through-Tech/KPMG-1C-ai-research-intelligence-agent-for-business-insight-translation/commit/f8f075e)
- [Visualizations and findings](https://github.com/Break-Through-Tech/KPMG-1C-ai-research-intelligence-agent-for-business-insight-translation/commit/940d488)
- [Section parsing](https://github.com/Break-Through-Tech/KPMG-1C-ai-research-intelligence-agent-for-business-insight-translation/commit/0849a6d)
- [Initial LangChain pipeline](https://github.com/Break-Through-Tech/KPMG-1C-ai-research-intelligence-agent-for-business-insight-translation/commit/1992fab)
