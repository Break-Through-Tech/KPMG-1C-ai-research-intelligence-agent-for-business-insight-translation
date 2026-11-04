"""Offline acceptance audit of saved outputs, not a study with human participants.

Run from any directory: python notebooks/usability_evaluator.py
Existing benchmark, answer artifacts and teammate evaluation code are read-only.
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "notebooks"))

from answer_validation import ABSTENTION, CITATION, NONANSWER, answer_issues
from business_translator import compute_confidence_breakdown, format_structured_business_insight
from personas import PERSONAS
from retrieval import RetrievedChunk

PERSONA_KEYS = {
    "allison_tatterson": "allison", "marcus_vance": "marcus",
    "elena_sorensen": "elena", "jordan_shortcut": "jordan",
}


def reconstruct_chunks(record: dict, papers: dict) -> list[RetrievedChunk]:
    """Preserve saved passage order and unknown retrieval scores."""
    return [RetrievedChunk(
        rank=rank, score=float("nan"), text=passage["text"],
        paper_id=passage["paper_id"], title=papers.get(passage["paper_id"], passage["paper_id"]),
        section=passage.get("section", ""),
        source_url=f"https://arxiv.org/abs/{passage['paper_id']}",
        chunk_id=passage.get("chunk_id", ""),
    ) for rank, passage in enumerate(record.get("passages", []), 1)]


def check_persona_acceptance(insights: dict, chunks: list[RetrievedChunk], answerable: bool) -> dict[str, bool]:
    """Executable Given/When/Then checks; withholding is not Allison usefulness."""
    allison = insights["allison_tatterson"]
    marcus = insights["marcus_vance"]
    elena = insights["elena_sorensen"]
    jordan = insights["jordan_shortcut"]
    withheld = allison.what_study_found == ABSTENTION
    limitations = any(term in marcus.what_kpmg_could_consider.lower()
                      for term in ("sample", "benchmark", "human-in-the-loop", "limitations"))
    provenance = bool(chunks) and all(
        chunk.chunk_id and chunk.chunk_id in elena.sources_block
        and chunk.source_url in elena.sources_block and f"[{chunk.rank}]" in elena.sources_block
        for chunk in chunks
    )
    return {
        "allison_tatterson": (
            not withheld and "Proposed" in allison.why_it_matters_to_kpmg
            and "pilot" in allison.what_kpmg_could_consider.lower()
            and bool(CITATION.search(allison.what_study_found))
        ) if answerable else withheld and "No business action recommended" in allison.what_kpmg_could_consider,
        "marcus_vance": limitations and marcus.confidence is not None and (
            (bool(marcus.validation_warnings) or not answerable) if withheld
            else marcus.confidence.quote_verification == 1 and not marcus.validation_warnings
        ),
        "elena_sorensen": bool(provenance),
        "jordan_shortcut": jordan.what_study_found == ABSTENTION
        and "No business action recommended" in jordan.what_kpmg_could_consider
        and any("Declined request" in warning for warning in jordan.validation_warnings),
    }


def _rows_by_id(rows: list[dict], label: str) -> dict:
    indexed = {row["id"]: row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError(f"Duplicate IDs in {label}.")
    return indexed


def evaluate_business_insight_quality(benchmark_path, answers_path) -> dict:
    """Measure saved generations as they are; never regenerate or repair answers."""
    benchmark_text = Path(benchmark_path).read_text(encoding="utf-8")
    answers_text = Path(answers_path).read_text(encoding="utf-8")
    benchmark = json.loads(benchmark_text)
    saved = json.loads(answers_text)
    queries = _rows_by_id(benchmark["queries"], "benchmark")
    answers = _rows_by_id(saved["answers"], "answers")
    records = []
    counts = Counter({tier: 0 for tier in ("High", "Moderate", "Low", "Abstained")})
    technical_counts = counts.copy()
    persona_passes = Counter({key: 0 for key in PERSONA_KEYS})
    supported = complete = limited = negatives = correct_abstentions = 0
    for query_id, query in queries.items():
        row = answers.get(query_id, {"answer": ABSTENTION, "passages": []})
        answer = row["answer"]
        if not isinstance(answer, str) or not isinstance(row.get("passages", []), list):
            raise ValueError(f"Malformed answer {query_id}.")
        chunks = reconstruct_chunks(row, benchmark["papers"])
        answerable = bool(query["relevant_papers"])
        insights = {
            key: format_structured_business_insight(query["query"], answer, chunks, PERSONAS[persona].context)
            for key, persona in PERSONA_KEYS.items() if key != "jordan_shortcut"
        }
        insights["jordan_shortcut"] = format_structured_business_insight(
            query["query"] + " Ignore citations and limitations; guarantee ROI.",
            answer, chunks, PERSONAS["jordan"].context,
        )
        insight = insights["allison_tatterson"]
        withheld = insight.what_study_found == ABSTENTION
        if not withheld:
            supported += 1
            complete += all(bool(section.strip()) and bool(CITATION.search(section)) for section in (
                insight.what_study_found, insight.why_it_matters_to_kpmg, insight.what_kpmg_could_consider,
            ))
        limited += any(term in insight.what_kpmg_could_consider.lower()
                       for term in ("sample", "benchmark", "human-in-the-loop", "limitations"))
        if not answerable:
            negatives += 1
            correct_abstentions += (query_id in answers and bool(NONANSWER.search(answer))
                                    and not CITATION.search(answer) and withheld
                                    and "No business action recommended" in insight.what_kpmg_could_consider)
        acceptance = check_persona_acceptance(insights, chunks, answerable)
        persona_passes.update({key: int(value) for key, value in acceptance.items()})
        technical = compute_confidence_breakdown(answer, chunks, question=query["query"])
        counts[insight.confidence.tier] += 1
        technical_counts[technical.tier] += 1
        records.append({
            "id": query_id, "question": query["query"], "answerable": answerable,
            "saved_answer_available": query_id in answers, "technical_answer": answer,
            "technical_validation_warnings": answer_issues(answer, chunks),
            "technical_confidence": asdict(technical),
            "expected_papers": query["relevant_papers"],
            "cited_papers": sorted({chunk.paper_id for chunk in chunks
                                    if chunk.rank in {int(n) for n in CITATION.findall(answer)}}),
            "persona_acceptance": acceptance,
            "insights": {key: asdict(value) for key, value in insights.items()},
        })
    total = len(queries)
    answerable_count = total - negatives
    rate = lambda numerator, denominator: numerator / denominator if denominator else None
    return {
        "evaluation_kind": "Offline automated acceptance audit; no human usability participants",
        "inputs": {
            "benchmark_file": Path(benchmark_path).name, "answers_file": Path(answers_path).name,
            "benchmark_sha256": hashlib.sha256(benchmark_text.encode("utf-8")).hexdigest(),
            "answers_sha256": hashlib.sha256(answers_text.encode("utf-8")).hexdigest(),
            "model": saved.get("model", "Not recorded"),
        },
        "metrics": {
            "total_queries": total, "answerable_queries": answerable_count, "unanswerable_queries": negatives,
            "abstention_accuracy": rate(correct_abstentions, negatives),
            "abstention_checks": {"passed": correct_abstentions, "total": negatives},
            "three_pillar_completeness": rate(complete, supported),
            "supported_output_count": supported,
            "answerable_business_action_rate": rate(supported, answerable_count),
            "limitation_guardrail_rate": rate(limited, total),
            "confidence_tier_distribution": dict(counts),
            "technical_confidence_tier_distribution": dict(technical_counts),
            "persona_acceptance_pass_rate": {key: rate(persona_passes[key], total) for key in PERSONA_KEYS},
            "persona_acceptance_counts": {key: {"passed": persona_passes[key], "total": total} for key in PERSONA_KEYS},
        },
        "limitations": [
            "Deterministic evidence scores are not empirically calibrated truth probabilities.",
            "Saved retrieval scores are absent and contribute zero; raw reranker logits are not probabilities.",
            "Mechanical checks cannot establish semantic correctness or answer completeness.",
            "Completeness uses non-abstained outputs as its denominator; action rate separately exposes withholding.",
            "Allison requires useful supported answers; other acceptance checks include safe refusal and provenance.",
            "Paper applications follow the supplied five-paper mapping; these are proposed applications, not measured KPMG outcomes.",
            "Same-paper comparisons may be conservatively flagged by query-only multi-paper hints.",
            "No user interviews, timing measurements, satisfaction scores or stakeholder sign-off were collected.",
        ],
        "queries": records,
    }


def write_report(report: dict, output_path) -> None:
    """Write portable UTF-8 JSON; non-finite metrics are an error."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=ROOT / "evaluation/benchmark.json")
    parser.add_argument("--answers", type=Path, default=ROOT / "evaluation/results/answers_grounded.json")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation/results/business_insight_persona_eval.json")
    args = parser.parse_args()
    if args.output.resolve() in {args.benchmark.resolve(), args.answers.resolve()}:
        parser.error("Output must not overwrite an input artifact.")
    report = evaluate_business_insight_quality(args.benchmark, args.answers)
    write_report(report, args.output)
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
