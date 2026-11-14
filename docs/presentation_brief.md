# Challenge advisor demo brief

## One-minute overview

This prototype helps a reviewer explore public AI research. It searches paper passages, generates a short answer with numbered citations, attaches exact source quotes, and offers a separately labeled business application. The browser UI keeps the source trail visible and lets reviewers export a brief. It is a local research prototype over five committed papers, not a deployment on KPMG data.

## Architecture to explain

1. The notebook parses PDF pages into sections. The integrated parser removes repeated page headers and table captions mistaken for section headings.
2. Shared ingestion splits content into stable chunks, embeds them with `all-mpnet-base-v2`, and stores them in cosine Chroma.
3. Retrieval searches candidate chunks, applies a cross-encoder, and reserves room for more than one paper when the question asks across papers.
4. Local `qwen2.5:7b` answers from numbered passages. The answer layer checks citation IDs, verbatim quotes, and exact numbers against cited passages. Unsupported questions can abstain; unverified drafts become source lists for review.
5. Raghul's UI adds paper browsing, review perspectives, source dialogs, saved briefs, exported Markdown, and an evidence score. The business view labels applications as proposals and can withhold them when checks warn.

## Results to show

| Test | Result | Meaning |
| --- | --- | --- |
| Five-paper retrieval | Relevant paper found for 23/23 answerable questions | Paper-level hit on a small AI-drafted set. |
| Five-paper literal fact coverage | 23/28 snippets present in selected chunks | Exact wording diagnostic, not answer accuracy. |
| Post-parser Qwen run | 20/20 direct answers pass mechanical source checks; 3/3 paper lists; 2/2 abstentions | Citations and quotes are traceable. One answer (q01) still omits a requested stopping rule. |
| Tiny BEIR SciFact | 18/20 rank-one hits; 20/20 top-five hits | Retrieval only, using 20 claims and a reduced 500-article corpus. |

The five-paper questions were drafted by Codex and checked against the PDFs, with no independent labeling pass. The evidence score is a heuristic reviewer aid, not a probability that an answer is correct. No KPMG reviewer has rated business usefulness or trust yet.

## Live demo, about three minutes

1. Start Ollama with `ollama pull qwen2.5:7b` and `ollama serve`. In another terminal, run `python frontend_server.py --port 8765 --live-root .` from the repository root. Open `http://127.0.0.1:8765`.
2. Choose **Ask a question** and enter: “How many commuters and valid observations did the travel study include?” The tested live path returned 92 commuters and 454 observations with passage [4].
3. Click the citation to open the exact passage. Show the **Technical answer** and **Sources** tabs, then the evidence-score explanation and business-application caveat.
4. Open **Evidence & evaluation** to show the fixed benchmark. Save and export a brief if time permits.

If Ollama is unavailable, run `python frontend_server.py --port 8765` and demonstrate the saved benchmark; the current complete Qwen run is selected by default.

## Discussion points and next work

- q01 shows why a valid citation and quote are not enough: a response can omit a required condition. Add independently reviewed completeness labels and claim-level support checks.
- Expand beyond five papers and the reduced SciFact subset, then recheck ranking and business-relevance screening.
- Ask KPMG reviewers to score usefulness, clarity, and trust on realistic questions. Calibrate the evidence score only after independent labels exist.
- The teammate's prompt-template package is a structured experiment for business questions. Its small local pilot does not replace KPMG review.
