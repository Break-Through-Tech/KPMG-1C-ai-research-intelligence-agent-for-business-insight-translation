from types import SimpleNamespace

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "notebooks"))
from answer_validation import answer_issues, attach_evidence, paper_search_answer  # noqa: E402


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


def test_paper_search_uses_literal_quotes_from_each_paper():
    chunks = [SimpleNamespace(**vars(CHUNKS[0]), rank=1, title='Survey')]
    chunks.append(SimpleNamespace(
        rank=2, paper_id='paper2', title='Routing',
        text='This routing paper evaluated specialists using several benchmark tasks and costs.',
    ))
    answer = paper_search_answer(chunks, 'Which papers study surveys and routing?')
    assert 'Survey [1]' in answer and 'Routing [2]' in answer
    assert answer_issues(answer, chunks) == []
