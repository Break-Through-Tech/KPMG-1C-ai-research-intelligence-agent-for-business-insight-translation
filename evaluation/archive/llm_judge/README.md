# Archived LLM-as-a-judge experiment

Archived at the user's request. The judges sometimes credited generated answers
with facts present only in the sources, so their ratings were not reliable enough
to guide optimization. No archived judge runs in the active review workflow.

Preserved here:

- `judge_answers.py`: broad reviewer.
- `review_answers.py`: focused checklist reviewer.
- `notebooks/judge_answers.ipynb`: executed three-question AI experiment.
- `results/`: original judge reports, pilot checks, calibration notes and spot-checks.
- `tests/historical_*.py`: historical test source, excluded by normal pytest naming.
- `historical_usage.md`: original documentation.
- `manifest.json`: original paths and SHA-256 hashes of moved files.

These are byte-identical historical snapshots, not relocated runnable tools.
Relative imports, notebook links and saved absolute paths refer to their original
locations. To reproduce the experiment, restore the manifest's original layout
in a separate checkout; do not run the archived notebook against the active tree.
Earlier Qwen2.5 pilot artifacts remain in `../didnt_work/`.

Use `../../../notebooks/answer_review.ipynb` (from the repository root:
`notebooks/answer_review.ipynb`) for the active offline workflow: automatic checks,
manual checklists, and source excerpts. Checklists remain assistant-prepared,
pending human approval; automatic checks do not prove semantic correctness.
