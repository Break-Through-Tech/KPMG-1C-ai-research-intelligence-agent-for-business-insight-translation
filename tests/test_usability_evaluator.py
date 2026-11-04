"""Fast offline checks for real metrics, safety failures and portable reports."""

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "notebooks"))
from answer_validation import ABSTENTION
from usability_evaluator import evaluate_business_insight_quality, reconstruct_chunks, write_report


@pytest.fixture
def inputs(tmp_path):
    benchmark = {"papers": {"2608.20320": "Travel survey"}, "queries": [
        {"id": "q13", "query": "Explain the travel survey", "relevant_papers": ["2608.20320"]},
        {"id": "q24", "query": "Revenue forecast?", "relevant_papers": []},
    ]}
    text = "The travel survey collected 92 student commuters and 454 observations."
    passages = [{"paper_id": "2608.20320", "chunk_id": "travel_c1", "text": text}]
    answers = {"model": "offline-fixture", "answers": [
        {"id": "q24", "answer": ABSTENTION, "passages": passages},
        {"id": "q13", "answer": f'"{text}" [1]', "passages": passages},
    ]}
    benchmark_path, answers_path = tmp_path / "benchmark.json", tmp_path / "answers.json"
    benchmark_path.write_text(json.dumps(benchmark), encoding="utf-8")
    answers_path.write_text(json.dumps(answers), encoding="utf-8")
    return benchmark_path, answers_path, answers


def test_metrics_join_by_id_and_persona_acceptance(inputs):
    report = evaluate_business_insight_quality(*inputs[:2])
    metrics = report["metrics"]
    assert metrics["total_queries"] == 2
    assert metrics["abstention_accuracy"] == 1
    assert metrics["three_pillar_completeness"] == 1
    assert metrics["limitation_guardrail_rate"] == 1
    assert metrics["confidence_tier_distribution"]["Moderate"] == 1
    assert all(rate == 1 for rate in metrics["persona_acceptance_pass_rate"].values())
    assert [row["id"] for row in report["queries"]] == ["q13", "q24"]


def test_no_pilot_when_answers_fail_validation(inputs):
    benchmark, path, answers = inputs
    answers["answers"][1]["answer"] = 'A guaranteed 999% return [1].'
    path.write_text(json.dumps(answers), encoding="utf-8")
    report = evaluate_business_insight_quality(benchmark, path)
    assert report["metrics"]["three_pillar_completeness"] is None
    assert report["metrics"]["answerable_business_action_rate"] == 0
    row = report["queries"][0]
    assert row["technical_confidence"]["tier"] == "Low"
    assert row["insights"]["allison_tatterson"]["what_study_found"] == ABSTENTION
    assert not row["persona_acceptance"]["allison_tatterson"]


def test_fabricated_or_missing_negative_is_not_success(inputs):
    benchmark, path, answers = inputs
    answers["answers"][0]["answer"] = "KPMG revenue is 999 billion [1]."
    path.write_text(json.dumps(answers), encoding="utf-8")
    assert evaluate_business_insight_quality(benchmark, path)["metrics"]["abstention_accuracy"] == 0
    answers["answers"].pop(0)
    path.write_text(json.dumps(answers), encoding="utf-8")
    report = evaluate_business_insight_quality(benchmark, path)
    assert report["metrics"]["abstention_accuracy"] == 0
    assert not report["queries"][1]["saved_answer_available"]


def test_anti_persona_refusal_is_executed(inputs):
    report = evaluate_business_insight_quality(*inputs[:2])
    for row in report["queries"]:
        jordan = row["insights"]["jordan_shortcut"]
        assert jordan["what_study_found"] == ABSTENTION
        assert "No business action recommended" in jordan["what_kpmg_could_consider"]
        assert any("Declined request" in issue for issue in jordan["validation_warnings"])


def test_missing_chunk_metadata_fails_curator_acceptance(inputs):
    benchmark, path, answers = inputs
    answers = deepcopy(answers)
    for row in answers["answers"]:
        row["passages"][0]["chunk_id"] = ""
    path.write_text(json.dumps(answers), encoding="utf-8")
    report = evaluate_business_insight_quality(benchmark, path)
    assert report["metrics"]["persona_acceptance_pass_rate"]["elena_sorensen"] == 0


def test_duplicate_ids_and_malformed_answers_rejected(inputs):
    benchmark, path, answers = inputs
    answers["answers"].append(answers["answers"][0])
    path.write_text(json.dumps(answers), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        evaluate_business_insight_quality(benchmark, path)
    answers["answers"].pop()
    answers["answers"][0]["answer"] = []
    path.write_text(json.dumps(answers), encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed"):
        evaluate_business_insight_quality(benchmark, path)


def test_utf8_serialization_and_determinism(inputs, tmp_path):
    report = evaluate_business_insight_quality(*inputs[:2])
    assert report == evaluate_business_insight_quality(*inputs[:2])
    report["unicode_check"] = "Sorensen — vérifié ✓"
    output = tmp_path / "nested" / "audit.json"
    write_report(report, output)
    assert json.loads(output.read_text(encoding="utf-8")) == report
    assert "vérifié" in output.read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        write_report({"score": float("nan")}, tmp_path / "invalid.json")


def test_full_committed_25_query_audit():
    report = evaluate_business_insight_quality(ROOT / "evaluation/benchmark.json",
                                             ROOT / "evaluation/results/answers_grounded.json")
    metrics = report["metrics"]
    assert (metrics["total_queries"], metrics["answerable_queries"], metrics["unanswerable_queries"]) == (25, 23, 2)
    assert metrics["abstention_checks"] == {"passed": 2, "total": 2}
    assert metrics["limitation_guardrail_rate"] == 1
    assert sum(metrics["confidence_tier_distribution"].values()) == 25
    for row in report["queries"]:
        if row["id"] in {"q08", "q21", "q22", "q23"}:
            assert row["insights"]["allison_tatterson"]["confidence"]["tier"] in {"Low", "Abstained"}
    assert metrics["persona_acceptance_pass_rate"]["allison_tatterson"] < 1
    assert metrics["persona_acceptance_pass_rate"]["jordan_shortcut"] == 1


def test_reconstruction_keeps_order_unknown_scores_and_canonical_urls(inputs):
    chunks = reconstruct_chunks(inputs[2]["answers"][1], {"2608.20320": "Travel"})
    assert chunks[0].rank == 1
    assert chunks[0].score != chunks[0].score  # Missing scores remain NaN until scoring.
    assert chunks[0].source_url == "https://arxiv.org/abs/2608.20320"
