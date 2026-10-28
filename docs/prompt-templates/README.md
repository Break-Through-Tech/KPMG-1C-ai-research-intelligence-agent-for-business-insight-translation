# Prompt design and testing package

This folder contains the prompt design and evaluation package on the prompt-templates branch. Worked examples are demonstrations; actual model evaluation remains pending.

## Five deliverables

1. Strategy: 01_strategy_and_recommendation.md.
2. Reusable instructions: template_a.txt and template_b.txt.
3. Examples: 02_worked_examples.md contains six paired demonstrations; test_cases.json defines ten fixed inputs.
4. Evaluation: 03_evaluation.md explains the rubric; evaluation_results.csv contains 20 unscored rows for actual runs.
5. Recommendation: 01_strategy_and_recommendation.md recommends B for testing and states what evidence is still needed before final selection.

The demonstrations are drafted examples, not captured Gemini or Llama results. Numerical scores and independent review are intentionally pending. Do not submit this package as a completed model benchmark until those steps are done.

## Running the comparison

Python standard library only. No provider package, credential, or model is installed by these files. The generation adapter is the team's existing approved model call wrapped as a function that takes a prompt string and returns an answer string. Keep credentials outside this package. The adapter must enforce the model and settings documented on the command line; the runner records these declarations but cannot independently verify provider configuration.

First check input rendering without contacting a model:

```text
python run_comparison.py --dry-run --model not_called --split all --output rendered_inputs.json
```

Then, after providing an approved adapter such as team_adapter.generate:

```text
python run_comparison.py --adapter team_adapter:generate --model EXACT_MODEL_ID --split development --output development_run.json
```

Use --settings with a JSON object to document actual generation settings. After reviewing and revising the development cases, run --split held_out with a new output path. Existing output files are never overwritten. Errors are retained as errors, and the runner does not automatically retry calls. The held-out cases are available for transparency; avoid using them to revise the initial template.

## What the user and team still need to do

- Connect the approved model call and run the cases. No configured Gemini or local Ollama access was found through environment-variable names and command availability in this session; no credentials were read.
- Obtain an independent teammate's scores and product owner feedback.
- Complete the actual results and final selection. Only then describe the work as tested in the team's model environment.
- Agree the appropriate team branch before integration. The new local branch is based on the original current checkout, not automatically on the newest generation branch.

## Current verification

Local dry-run checks rendered twenty prompts across ten unique cases and confirmed that evaluation scores remain blank. A dry run confirms input preparation only; it does not establish model behavior or research accuracy.
