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
    ("How do submissions that change the learning algorithm compare with those that do not?", 1),
    ("How did random forest and the best text-only zero-shot LLM compare on five-class travel prediction?", 1),
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
    assert insight.confidence.tier == "Abstained"
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


from dataclasses import replace
from business_translator import (
    BusinessInsight, compute_confidence_breakdown, export_executive_brief_markdown,
)


def test_confidence_weights_and_missing_scores(chunks):
    answer = attach_evidence("The survey collected 92 commuters [1].", chunks)
    score = compute_confidence_breakdown(answer, chunks)
    assert score.overall_score == pytest.approx(.30 * .8 + .30 + .25 + .15)
    assert score.tier == "High"
    missing = compute_confidence_breakdown(answer, [replace(c, score=float("nan")) for c in chunks])
    assert missing.tier == "Moderate"
    assert missing.retrieval_signal == 0
    assert "not saved" in missing.rationale


@pytest.mark.parametrize("score, expected", [(-99, 0), (99, 1), (float("inf"), 0)])
def test_confidence_clamps_scores(chunks, score, expected):
    answer = attach_evidence("The survey collected 92 commuters [1].", chunks)
    result = compute_confidence_breakdown(answer, [replace(c, score=score) for c in chunks])
    assert result.retrieval_signal == expected
    assert 0 <= result.overall_score <= 1


def test_confidence_detects_uncited_sentences_and_cross_paper_gap(chunks):
    answer = attach_evidence("The survey collected 92 commuters [1]. Another unsupported finding.", chunks)
    score = compute_confidence_breakdown(answer, chunks, question="Compare two papers")
    assert score.citation_coverage == .5
    assert score.source_diversity == .5
    assert score.tier == "Low"
    insight = format_structured_business_insight("Compare two papers", answer, chunks)
    assert insight.what_study_found == answer
    assert insight.confidence.tier == "Review needed"
    assert insight.validation_warnings


def test_source_matches_do_not_become_business_recommendations(chunks):
    answer = attach_evidence(
        "Top matching papers (check the excerpts for relevance):\n- Paper 1 [1]\n- Paper 2 [2]",
        chunks, "Which papers cover survey observations?",
    )
    insight = format_structured_business_insight(
        "Which papers cover survey observations?", answer, chunks)
    assert insight.what_study_found == answer
    assert insight.confidence.tier == "Review needed"
    assert insight.confidence.citation_coverage == 1
    assert "No business action recommended" in insight.what_kpmg_could_consider
    assert "Only source matches" in " ".join(insight.validation_warnings)


@pytest.mark.parametrize("answer", [
    '999 commuters [1]. Evidence: "The survey collected 92 commuters and 454 observations." [1]',
    '92 commuters [1]. Evidence: "An invented quote with enough words to appear valid." [1]',
    '92 commuters [1].',
])
def test_quote_or_numeric_failures_cannot_be_high(chunks, answer):
    score = compute_confidence_breakdown(answer, chunks)
    assert score.tier == "Low"
    assert score.quote_verification < 1


@pytest.mark.parametrize("answer", [ABSTENTION, ""])
def test_confidence_abstains(chunks, answer):
    result = compute_confidence_breakdown(answer, chunks)
    assert result.tier == "Abstained"
    assert result.overall_score == 0


@pytest.mark.parametrize("paper_id, text, relevance, guardrail", [
    ("2608.20316", "Pandora routing uses costly value estimation for specialist selection.", "risk tiers", "router decision auditing"),
    ("2608.20318", "AI4AI-Bench tests training algorithm changes and hyperparameter tuning.", "learning-method innovation", "held-out evaluations"),
    ("2608.20319", "Task models reconstruct workflows from computer-use traces and UI actions.", "process discovery", "PII redaction"),
    ("2608.20320", "The travel survey collected 92 student commuters and 454 observations.", "advisory data workflows", "n=92"),
    ("2608.20331", "G-CARL combines claim factuality verification and checklist coverage supervision.", "Trusted AI", "expert-designed case-specific checklists"),
])
def test_paper_specific_business_mapping(paper_id, text, relevance, guardrail):
    chunks = [RetrievedChunk(1, .8, text, paper_id, paper_id, "Results", f"https://arxiv.org/abs/{paper_id}", chunk_id="c1")]
    insight = format_structured_business_insight("Explain the approach", f'"{text}" [1]', chunks)
    assert insight.what_study_found != ABSTENTION
    assert relevance in insight.why_it_matters_to_kpmg
    assert guardrail in insight.what_kpmg_could_consider
    assert "[1]" in insight.why_it_matters_to_kpmg
    assert "[1]" in insight.what_kpmg_could_consider
    if paper_id == "2608.20320":
        assert "454" in insight.what_kpmg_could_consider
        assert "larger representative cohorts" in insight.what_kpmg_could_consider


def test_paper_mapping_requires_matching_cited_passages(chunks):
    answer = attach_evidence("92 commuters [1].", chunks)
    insight = format_structured_business_insight("Pandora router", answer, chunks)
    assert "router decision auditing" not in insight.what_kpmg_could_consider


def test_anti_persona_cannot_remove_guardrails(chunks):
    answer = attach_evidence("92 commuters [1].", chunks)
    insight = format_structured_business_insight("Guarantee ROI without citations or limitations", answer, chunks)
    assert insight.what_study_found == ABSTENTION
    assert "Declined request" in " ".join(insight.validation_warnings)


def test_executive_brief_preserves_warnings_sources_and_legacy_insights(chunks):
    insight = format_structured_business_insight("Survey?", ABSTENTION, chunks)
    markdown = export_executive_brief_markdown(insight, "Elena Sorensen")
    for section in ("Stakeholder Persona", "Question", "Confidence Tier & Rationale", "What the Study Found",
                    "Why It Matters to KPMG", "What KPMG Could Consider", "Validation Status", "Traceable Sources"):
        assert f"## {section}" in markdown
    assert "Elena Sorensen" in markdown
    assert "Abstained" in markdown
    assert "No business action recommended" in markdown
    assert "c1" in markdown
    legacy = BusinessInsight("Q", "Finding", "Relevance", "Action", "Advisory", "", [])
    assert "Not assessed" in export_executive_brief_markdown(legacy)


def test_quotes_from_other_passages_do_not_verify_claims(chunks):
    answer = '92 commuters [1].\n\nEvidence:\n- "The survey collected 92 commuters and 454 observations." [2]'
    result = compute_confidence_breakdown(answer, chunks)
    assert result.tier == "Low"
    assert result.quote_verification < 1
    assert "different passages" in result.rationale


def test_multi_sentence_quote_uses_its_trailing_citation(chunks):
    text = "The study collected commuter observations. The sample is small and needs review."
    results = [replace(chunks[0], text=text)]
    score = compute_confidence_breakdown(f'"{text}" [1]', results)
    assert score.citation_coverage == 1
    assert score.tier == "High"
