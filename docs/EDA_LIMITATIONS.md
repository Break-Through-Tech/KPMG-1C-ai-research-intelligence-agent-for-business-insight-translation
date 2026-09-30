# EDA limitations and preprocessing needs

The current analysis supports identifying corpus-quality and coverage risks. It does not establish that the corpus is representative, that every paper is business-relevant, or that the resulting assistant is fair or accurate.

## Observed limitations

| Limitation | Evidence in the current repository | Implication and next step |
| --- | --- | --- |
| Mixed saved execution states | Catalog output reports 97 papers; extraction summary reports 95; the written findings and relevance table refer to 85; download inventory shows 16. | Do not treat these as one sequential funnel or calculate dropout rates. Reconcile paper IDs and versions from one fixed run. |
| Raw corpus is not available in this checkout | No `arxiv_data` catalog or paper-level EDA CSV accompanies the checkout; notebook tables are truncated. | New charts use saved aggregates. Restore the corpus before measuring full-dataset missingness, dates, exclusions, or detailed distributions. The five example PDFs under `data/` are not the full EDA corpus. |
| Quotas and keyword selection | Seven areas target ten papers each; general targets thirty. Searches match abstract phrases and prioritize newest submissions. | Counts reflect a designed sample, not the AI research population. Review coverage against stakeholder questions and test broader terms or date strata. |
| Overlapping area assignments | One paper can belong to several collection areas. | Use assignment shares for area proportions, unique-paper denominators for paper-level results; explicitly state which is used. |
| Category-name collisions | Both `cs.LG` and `stat.ML` map to “Machine Learning” before category counts are displayed. | A paper can contribute twice to that display label. Audit raw codes and deduplicate per paper before interpreting field shares. |
| No completed business-relevance labels | The notebook initializes empty relevance/review-note fields. | Do not report relevance rates. Review abstracts/full text with a shared rubric and double-review a subset. Domain difference alone does not establish irrelevance. |
| Extraction exceptions do not capture all quality issues | Saved output includes skipped-content and malformed-string warnings despite a zero-exception count. | Record warnings and compare extracted text to source pages, including tables, equations, figures, and reading order. |
| Heuristic low-text screening | A page is flagged if stripped extracted text is shorter than 100 characters. | This can flag valid figure/title pages and miss corrupted but long text. Use it for manual triage, not automatic deletion. |
| Section parsing is heuristic | Some sample papers place thousands of words under Front Matter; an example retrieval returns REFERENCES. | Validate headings and boilerplate; consider tagging/filtering reference sections and preserving raw text/page spans for traceability. |
| Small retrieval demonstration | Five selected sample papers and two example queries. | Cannot support cross-domain retrieval-performance or fairness claims. Use a separate, balanced benchmark and paper-level relevance judgments. |

## Potential biases requiring further measurement

- **Source and publication bias:** arXiv-only coverage excludes other research and practice evidence. Preprints vary in validation status; source inclusion does not establish peer review or applicability.
- **Recency bias:** newest-first selection favors recent work. The actual date distribution must be measured from restored metadata; dates must not be inferred from partial displayed examples alone.
- **Search-term bias:** broad phrases such as risk assessment or forecasting may capture unrelated tasks, while exact phrases miss synonyms. Measure relevance per query and area before changing the search design.
- **Acquisition and extraction bias:** download interruptions, storage constraints, and difficult PDF layouts may change which papers remain usable. These effects are plausible, but the saved counts do not measure them reliably.
- **Length-related retrieval exposure:** the saved 95-paper summary spans 2,533–46,527 approximate words, with median 7,693. Longer papers may create more chunks. Measure actual chunk counts and retrieval frequency before claiming or correcting unequal exposure.
- **Reviewer bias:** business relevance depends on a defined use case. Record reasons, review disagreements, and stakeholder feedback instead of relying only on titles or automatic keyword scores.

These are corpus and evidence-coverage risks. The repository does not contain verified protected-group attributes or outcomes for demographic fairness analysis. Do not infer gender, ethnicity, nationality, or geographic coverage from author names.

## Constraints of the new visualizations

The [bias visualization notebook](../workbook/eda_bias_visualizations.ipynb) reads recorded outputs from the original workbook. It shows source-cell references and the source-file fingerprint. Individual saved cells may describe different datasets, so comparisons are diagnostic rather than a validated snapshot analysis.

- Topic percentages use overlapping assignment counts and have rounding error.
- Category counts include only the displayed top ten and may conflate code labels.
- The word-count box uses recorded minimum/quartiles/maximum; whiskers show the full range. It does not reconstruct individual papers or outliers.
- The corpus-size chart is a comparison of inconsistent recorded observations, not an acquisition funnel.
- No synthetic relevance labels, publication dates, or missingness rates are supplied.

## Preprocessing actions justified by the EDA

1. Freeze a manifest of paper IDs, versions, query settings, and collection timestamps; reconcile PDFs against it.
2. Keep an exclusion log with a reason for every missing or unusable document.
3. Complete relevance labels using agreed business questions; retain uncertain cases for review.
4. Inspect extraction warnings and representative pages; try OCR only where appropriate, while preserving originals.
5. Preserve source URLs, versions, and page spans; validate section boundaries and distinguish references from body evidence.
6. Measure chunk counts by paper and area; evaluate diversity and filtering changes on benchmark queries before imposing caps.

User story: As a KPMG research analyst, I want to see the corpus's coverage and quality gaps so that I can judge which questions are supported and where additional evidence or preprocessing is needed. Acceptance requires traceable counts, documented exclusions, reviewed relevance, and explicit unresolved limitations.
