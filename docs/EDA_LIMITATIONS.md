# EDA limitations and preprocessing needs

The current analysis supports identifying corpus-quality and coverage risks. It does not establish that the corpus is representative, that every paper is business-relevant, or that the resulting assistant is fair or accurate.

## Observed limitations

| Limitation | Evidence in the current repository | Implication and next step |
| --- | --- | --- |
| Quotas and keyword selection | Seven areas target ten papers each; general targets thirty. Searches match abstract phrases and prioritize newest submissions. | Counts reflect a designed sample, not the AI research population. Review coverage against stakeholder questions and test broader terms or date strata. |
| Overlapping area assignments | One paper can belong to several collection areas. | Use assignment shares for area proportions, unique-paper denominators for paper-level results; explicitly state which is used. |
| Category-name collisions | Both `cs.LG` and `stat.ML` map to “Machine Learning” before category counts are displayed. | A paper can contribute twice to that display label. Audit raw codes and deduplicate per paper before interpreting field shares. |
| No completed business-relevance assessment | The original notebook initializes empty relevance/review-note fields. The new screening notebook has not been run on the full corpus. | Report model-assessed labels only after running the classifier; show uncertainty and unassessed counts. Domain difference alone does not establish irrelevance. |

## Potential biases requiring further measurement

- **Source and publication bias:** arXiv-only coverage excludes other research and practice evidence. Preprints vary in validation status; source inclusion does not establish peer review or applicability.
- **Recency bias:** newest-first selection favors recent work. The actual date distribution must be measured from restored metadata; dates must not be inferred from partial displayed examples alone.
- **Search-term bias:** broad phrases such as risk assessment or forecasting may capture unrelated tasks, while exact phrases miss synonyms. Measure relevance per query and area before changing the search design.
- **Acquisition and extraction bias:** download interruptions, storage constraints, and difficult PDF layouts may change which papers remain usable. These effects are plausible, but the saved counts do not measure them reliably.
- **Length-related retrieval exposure:** the saved 95-paper summary spans 2,533–46,527 approximate words, with median 7,693. Longer papers may create more chunks. Measure actual chunk counts and retrieval frequency before claiming or correcting unequal exposure.
- **Reviewer bias:** business relevance depends on a defined use case. Record reasons, review disagreements, and stakeholder feedback instead of relying only on titles or automatic keyword scores.

These are corpus and evidence-coverage risks. The repository does not contain verified protected-group attributes or outcomes for demographic fairness analysis. Do not infer gender, ethnicity, nationality, or geographic coverage from author names.

## Constraints of the new visualizations

The [bias visualization notebook](../notebooks/eda_bias_visualizations.ipynb) reads recorded outputs from the original workbook. It shows source-cell references and the source-file fingerprint. Individual saved cells may describe different datasets, so comparisons are diagnostic rather than a validated snapshot analysis.

- Topic percentages use overlapping assignment counts and have rounding error.
- Category counts include only the displayed top ten and may conflate code labels.
- The word-count box uses recorded minimum/quartiles/maximum; whiskers show the full range. It does not reconstruct individual papers or outliers.
- The corpus-size chart is a comparison of inconsistent recorded observations, not an acquisition funnel.
- No synthetic relevance labels, publication dates, or missingness rates are supplied.

## Limits of automated screening

The team prefers automated relevance and extraction screening rather than manual paper-by-paper review. [eda_automated_screening.ipynb](../notebooks/eda_automated_screening.ipynb) implements that workflow without automatically excluding papers.

| Automated check | What it supports | What it cannot establish |
| --- | --- | --- |
| LLM title/abstract relevance classification | Consistent rubric, business mapping, rationale, and exact evidence quote | Actual business usefulness, full-text evidence quality, calibrated confidence, or classification accuracy |
| Quote validation and structured-response checks | Rejects absent quotes and malformed labels | A real quote can still be misinterpreted; valid formatting does not establish correctness |
| Low-text, encoding, whitespace, repeated-line checks | Flags likely extraction issues using explicit thresholds | Thresholds are provisional; figure-heavy pages and legitimate formatting can trigger false positives |
| Abstract-token coverage | Detects possible missing abstract content | Ignores order and structure; cannot verify tables, equations, or complete extraction |
| Optional second-parser token agreement | Flags differences on suspect PDFs | Two parsers can agree while sharing errors; higher overlap is not a gold-standard fidelity score |

The relevance model is optional and uses a locally available Ollama model; no model is installed by the notebook. The model name, prompt fingerprint, source PDF fingerprints, thresholds, and results are displayed. The cache is only in memory, so save notebook outputs before closing the kernel. Temperature zero does not guarantee reproducibility across model/runtime versions.

The default ten-call pilot follows catalog order and is not representative of the whole corpus. Increase the limit or continue runs for broader assessment. Missing abstracts, invalid model responses, missing PDFs, unavailable libraries, and extraction failures remain visible as uncertain, unresolved, or unassessed statuses. Model calls are off by default. No corpus-level results are claimed until the real metadata and PDFs are restored and assessed.

Charts count papers once within each original collection area; multi-area papers appear in multiple bars. Do not sum these counts as unique papers. Automated screening cannot establish the rate of missed or incorrectly flagged issues without independent validation; that limitation remains even if the team elects not to perform manual review. No automatic deletion, OCR processing, or measurement of actual retrieval exposure is included.
