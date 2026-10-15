from types import SimpleNamespace

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "notebooks"))
from answer_validation import answer_issues  # noqa: E402


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
