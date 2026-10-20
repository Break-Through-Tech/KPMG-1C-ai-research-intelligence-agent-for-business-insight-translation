"""Fast, model-free checks for business framing and retrieval hints."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "notebooks"))
from answer_validation import ABSTENTION, attach_evidence
from retrieval import RetrievedChunk
from business_translator import (
    KPMG_COLLECTION_AREAS, build_business_insight_prompt, format_structured_business_insight,
    infer_collection_area, needs_multiple_papers_enhanced, print_sources,
    recommend_min_papers, reformat_prompt, translate_to_business_insight,
)


@pytest.fixture
def chunks():
    return [RetrievedChunk(i, 0.8, "The survey collected 92 commuters and 454 observations.",
                           f"p{i}", f"Paper {i}", "Results", f"https://arxiv.org/abs/p{i}",
                           chunk_id=f"c{i}") for i in (1, 2, 3)]


@pytest.mark.parametrize("question,term", [
    ("How can we cut LLM API costs and pick the right model?", "Pandora router"),
    ("Explain employee screen workflows and process mining", "computer-use traces UI actions"),
    ("Medical checklist hallucination QA", "factuality coverage"),
    ("Autonomous coding and self-improvement", "algorithmic design"),
    ("Survey demand forecasting with weather", "weather-sensitive demand"),
])
def test_query_expansion(question, term):
    rewritten = reformat_prompt(question)
    assert rewritten.startswith(question)
    assert term in rewritten


def test_query_unchanged_without_mapping():
    assert reformat_prompt("Explain quantum gravity") == "Explain quantum gravity"


def test_blank_rejected():
    with pytest.raises(ValueError):
        reformat_prompt(" \n ")


@pytest.mark.parametrize("question,count", [
    ("How does Pandora's Router work?", 1),
    ("Difference between Pandora's Router and Pandora's Bidder?", 1),
    ("How well does TMI reconstruct tasks?", 1),
    ("difference between the approaches", 2),
    ("how do the approaches differ", 2),
    ("synthesize findings across the corpus", 2),
    ("trade-offs between the approaches", 2),
    ("Which papers address auditable AI workflows derived from user activity or survey responses?", 2),
    ("Which papers evaluate AI agents or model specialists using benchmark tasks and costs?", 2),
    ("Which papers discuss evidence-grounded explanations and auditable task models?", 2),
    ("Compare Pandora and G-CARL", 2),
    ("Pandora, AI4AI-Bench, and Task Models/TMI", 3),
    ("all papers that discuss agents", 3),
    ("Compare three papers", 3),
    ("Summarize two papers", 2),
    ("Summarize 2 studies", 2),
    ("Summarize 4 papers", 3),
    ("Summarize five studies", 3),
])
def test_paper_reservations(question, count):
    assert recommend_min_papers(question) == count
    assert needs_multiple_papers_enhanced(question) == (count > 1)


@pytest.mark.parametrize("area", list(KPMG_COLLECTION_AREAS))
def test_taxonomy_routes_unambiguous_keywords(area):
    assert infer_collection_area(KPMG_COLLECTION_AREAS[area][0]) == area


@pytest.mark.parametrize("query", ["General business opportunities", "RAG and hallucination", "bragging"])
def test_ambiguous_or_general_query_does_not_route(query):
    assert infer_collection_area(query) is None


def test_sources_keep_passage_numbers(chunks):
    assert print_sources(chunks, {2}).startswith("[2] Paper 2")
    assert "[1]" not in print_sources(chunks, {2})
    assert "[3] Paper 3" in print_sources(chunks)
    assert print_sources(chunks, set()) == ""


@pytest.mark.parametrize("persona", [None, "Your current user is Allison Tatterson, AI Consulting decision-maker."])
def test_prompt_evidence_rules_and_persona(persona):
    prompt = build_business_insight_prompt("What did the study find?", "[1] Evidence", persona)
    assert ABSTENTION in prompt
    assert "[1], [2]" in prompt
    assert "sample-size" in prompt
    assert "never as instructions" in prompt
    if persona:
        assert persona in prompt


def test_supported_insight_preserves_evidence_and_adds_guardrails(chunks):
    answer = attach_evidence("The survey collected 92 commuters [1].", chunks)
    insight = format_structured_business_insight("Travel behavior", answer, chunks)
    assert insight.what_study_found == answer
    assert insight.validation_warnings == []
    assert "[1]" in insight.what_study_found
    assert "Advisory" in insight.why_it_matters_to_kpmg
    assert "Sample-size" in insight.what_kpmg_could_consider
    assert "human-in-the-loop" in insight.what_kpmg_could_consider


def test_abstention_has_no_business_recommendation(chunks):
    insight = format_structured_business_insight("Revenue?", ABSTENTION, chunks)
    assert insight.what_study_found == ABSTENTION
    assert insight.kpmg_service_area == "Unassigned"
    assert "No business action recommended" in insight.what_kpmg_could_consider


@pytest.mark.parametrize("answer", [
    "The survey collected 92 commuters [9].",
    'The survey collected 999 commuters [1]. Evidence: "This is an invented quote with enough words." [1]',
    "An answer without any citations.",
    ABSTENTION + " [1]",
])
def test_invalid_evidence_withholds_business_action(answer, chunks):
    insight = format_structured_business_insight("What happened?", answer, chunks)
    assert insight.validation_warnings
    assert "No business action recommended" in insight.what_kpmg_could_consider


def test_translation_attaches_verbatim_evidence(chunks):
    insight = translate_to_business_insight("Survey?", "92 commuters [1].", chunks)
    assert "Evidence:" in insight.what_study_found
    assert insight.validation_warnings == []


def test_nonconsecutive_ranks_rejected(chunks):
    with pytest.raises(ValueError, match="consecutive"):
        format_structured_business_insight("Survey?", "92 commuters [3].", chunks[2:])
