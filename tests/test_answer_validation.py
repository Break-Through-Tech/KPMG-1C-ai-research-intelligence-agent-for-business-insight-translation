from types import SimpleNamespace

from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "notebooks"))
from answer_validation import (  # noqa: E402
    ABSTENTION, answer_issues, attach_evidence, paper_search_answer, quote_matches,
)


CHUNKS = [SimpleNamespace(
    paper_id="paper1",
    text="The survey collected 92 commuters and 454 respondent-scenario observations.",
)]


def test_verified_quote_and_numbers():
    answer = ('The survey had 92 commuters and 454 observations [1].\n'
              'Evidence: "The survey collected 92 commuters and 454 respondent-scenario observations." [1]')
    assert answer_issues(answer, CHUNKS) == []


def test_wrong_quote_source_and_number_are_flagged():
    answer = ('The survey had 900 commuters [1].\n'
              'Evidence: "The survey collected 900 commuters and 454 respondent-scenario observations." [1]')
    issues = answer_issues(answer, CHUNKS)
    assert any("not verbatim" in issue for issue in issues)
    assert any("900" in issue for issue in issues)


def test_abstention_cannot_also_cite_answer():
    assert answer_issues("The provided papers do not address this question. [1]", CHUNKS)
    assert answer_issues("The survey had 92 commuters [1]. The provided papers do not address the question.", CHUNKS)


def test_attached_quote_is_literal_and_passage_specific():
    answer = attach_evidence("The survey counted 92 commuters [1].", CHUNKS, "How many commuters?")
    assert "Evidence:" in answer
    assert answer_issues(answer, CHUNKS) == []


def test_evidence_quote_cannot_replace_a_missing_answer_citation():
    answer = ('The survey counted 92 commuters.\n'
              'Evidence: "The survey collected 92 commuters and 454 respondent-scenario observations." [1]')
    assert any('No passage citation' in issue for issue in answer_issues(answer, CHUNKS))


def test_quote_from_an_uncited_passage_does_not_verify_the_citation():
    chunks = [CHUNKS[0], SimpleNamespace(
        paper_id='paper1', text='A separate passage contains an unrelated but valid literal quotation.'
    )]
    answer = ('The survey had 92 commuters [1].\n'
              'Evidence: "A separate passage contains an unrelated but valid literal quotation." [2]')
    assert any('per cited passage' in issue for issue in answer_issues(answer, chunks))


def test_number_check_does_not_join_unrelated_digits():
    chunks = [SimpleNamespace(
        paper_id='paper1', text='The separate results were 74 and 9, and another score was 94.74%.',
    )]
    answer = ('The reconstruction rate was 74.9% [1].\n'
              'Evidence: "The separate results were 74 and 9, and another score was 94.74%." [1]')
    assert any('74.9%' in issue for issue in answer_issues(answer, chunks))


def test_number_check_handles_pdf_spacing_in_decimals():
    chunks = [SimpleNamespace(
        paper_id='paper1', text='The groups average0.226 against0 .126for the rest.',
    )]
    answer = ('The scores are 0.226 and 0.126 [1].\n'
              'Evidence: "The groups average0.226 against0 .126for the rest." [1]')
    assert answer_issues(answer, chunks) == []


def test_paper_search_uses_literal_quotes_from_each_paper():
    chunks = [SimpleNamespace(**vars(CHUNKS[0]), rank=1, title='Survey')]
    chunks.append(SimpleNamespace(
        rank=2, paper_id='paper2', title='Routing',
        text='This routing paper evaluated specialists using several benchmark tasks and costs.',
    ))
    answer = paper_search_answer(chunks, 'Which papers study survey commuters and routing costs?')
    assert 'Survey [1]' in answer and 'Routing [2]' in answer
    assert answer_issues(answer, chunks) == []


def test_paper_search_does_not_claim_unrelated_papers_match():
    chunks = [SimpleNamespace(**vars(CHUNKS[0]), rank=1, title='Survey')]
    assert paper_search_answer(
        chunks, 'Which of these papers reports the NVIDIA stock price?') == ABSTENTION


@pytest.mark.parametrize("claimed,actual", [
    ("92", "192"), ("9.2", "92"), ("92", "9.2"),
    ("30%", "30"), ("30", "30%"), ("-5", "5"),
    ("0.5", "0.05"), (".5", "5"), ("1e3", "1e4"),
])
def test_numeric_values_are_not_substrings(claimed, actual):
    chunks = [SimpleNamespace(paper_id="p1", text=f"The study reported a value of {actual} overall.")]
    answer = attach_evidence(f"The reported value was {claimed} [1].", chunks)
    assert any("numbers absent" in issue for issue in answer_issues(answer, chunks))


@pytest.mark.parametrize("claimed,actual", [
    ("1,000", "1000"), ("1000", "1,000"), ("30%", "30.0 %"),
    ("69.6 percent", "69.6%"), ("0.5", ".5"), ("1000", "1e3"),
    ("-5", "−5"),
])
def test_equivalent_numeric_formats(claimed, actual):
    chunks = [SimpleNamespace(paper_id="p1", text=f"The study reported a value of {actual} overall.")]
    answer = attach_evidence(f"The reported value was {claimed} [1].", chunks)
    assert answer_issues(answer, chunks) == []


def test_citations_and_numbered_bullets_are_not_measurements():
    answer = attach_evidence("1. The survey counted 92 commuters [1].", CHUNKS)
    assert answer_issues(answer, CHUNKS) == []


def test_attached_evidence_cannot_expand_numeric_support_for_body():
    chunks = [SimpleNamespace(paper_id="p1", text="The study counted 192 participants in total."),
              SimpleNamespace(paper_id="p1", text="A different study counted 92 participants in total.")]
    answer = ('The study counted 92 participants [1].\n\nEvidence:\n'
              '"A different study counted 92 participants in total." [2]')
    assert any("92" in issue for issue in answer_issues(answer, chunks))


def test_quotes_preserve_numeric_punctuation_but_tolerate_whitespace():
    assert quote_matches("The score was 9.2 for the method.", "The score was\n9.2 for the method.")
    assert not quote_matches("92 participants were enrolled in total", "192 participants were enrolled in total")
    assert not quote_matches("5 participants were enrolled in total", "9.5 participants were enrolled in total")
    assert not quote_matches("The reported value was 30", "The reported value was 30%")
    chunks = [SimpleNamespace(paper_id="p1", text="The score was 92 for the method.")]
    answer = 'The method was evaluated [1]. Evidence: "The score was 9.2 for the method." [1]'
    assert any("not verbatim" in issue for issue in answer_issues(answer, chunks))


def test_matching_numbers_do_not_establish_method_association():
    chunks = [SimpleNamespace(paper_id="p1", text=
              "Random forest scored 69.6%; the vision method scored 71.5% in the study.")]
    answer = attach_evidence("Random forest scored 71.5% [1].", chunks)
    # Mechanical success remains distinct from semantic claim support.
    assert answer_issues(answer, chunks) == []
