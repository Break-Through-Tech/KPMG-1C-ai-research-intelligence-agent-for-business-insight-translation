# Prompt design and testing package

## What is included

| File | Purpose |
|---|---|
| 01_strategy_and_recommendation.md | Audience, design strategy, scope, preliminary recommendation, and next actions. |
| template_a.txt and template_b.txt | Version 2 reusable instructions, aligned with professional-services decisions and requested formats. |
| 04_persona_and_user_stories.md | One optional draft persona, four user stories, and observable success checks. |
| 05_allison_test_mapping.md | Exact selected questions, links to stories, expected behavior, and evidence preparation. |
| test_cases.json | Sixteen primary cases: eight questions with original and paraphrased wording. |
| evidence_inputs.example.json | Empty evidence schema; copy and populate with real retrieved passages and metadata. |
| 03_evaluation.md and evaluation_results.csv | Review method and 32 blank primary evaluation rows. |
| stress_cases.json and 02_worked_examples.md | Supplementary transport/synthetic fixtures and historical version 1 demonstrations. |
| run_comparison.py | Provider-neutral runner; blocked cases are not passed to the model. |
| build_cases.py | Creates a fresh blank evaluation sheet in a separate destination, without overwriting results. |
| 06_source_notes.md | Provenance and interpretation of the two advisor documents. |
| 07_revision_summary.md | Original additions, current revisions, verification, and outstanding work. |
| test_runner.py | Seven local checks for evidence gating, history, fixed comparisons, and preserving outputs. |

All explanatory documents are Markdown. No Word files are added or deleted. Allison's questions are test inputs, not source evidence or generated answers. Personas are optional. Model testing, independent scores, and stakeholder validation remain pending.

## Start here

Read the strategy and persona, then use the mapping document to obtain evidence from the retrieval team. Populate a copy of evidence_inputs.example.json and supply the research topic. Save a checked A31 prior answer for follow-up cases A41 and A42. Without that evidence the runner blocks actual business-case model calls; it does not fabricate a corpus.

Run commands from this folder. Standard library only; no credentials or provider dependencies are installed. The team's adapter accepts one prompt string and returns an answer string; it must enforce the model and settings declared on the command line. These declarations are recorded, not verified against the provider. Do not commit API keys or confidential data.

Check all inputs without a model:

```text
python run_comparison.py --dry-run --model not_called --split all --output rendered_inputs.json
```

Run only exact originals first using the team's approved adapter:

```text
python run_comparison.py --adapter team_adapter:generate --model EXACT_MODEL_ID --evidence evidence_inputs.json --split development --variant original --output originals_run.json
```

Then repeat with --variant paraphrase and a new output path, holding evidence and model settings fixed. Add the saved prior answer to the A31 evidence entry before running follow-ups; use --case-ids to target those cases if needed. Use --split held_out only after freezing the candidate. Existing output files are never overwritten, and errors are not automatically retried. Use --settings with a JSON object documenting the adapter's actual generation settings.

Run supplementary checks with --suite stress. They do not require a primary evidence file and include deliberately empty evidence. Their outputs need separate review and must not be mixed with the primary business score rows.

## Revision status

The original package was committed as a565ebd. Version 2 is based on Allison's two supplied documents, keeps the previous demonstrations as historical examples, and replaces the primary transport tests with business questions. See source notes for the exact inputs. Nothing in this package claims completed model experiments.
