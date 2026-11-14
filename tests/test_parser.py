import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BODY = "We study decision checkpoints in business process management and report results on a banking case."


def body(n: int) -> str:
    """Distinct paragraph text per page, as in a real paper."""
    return f"Paragraph {n} discusses finding number {n} about checkpoint design and its effect on process outcomes."


def parser_namespace(source: str) -> dict:
    """Load the notebook's parser cell the same way evaluation/run_retrieval.py does."""
    namespace = {"re": re}
    exec(compile(source, "eda_workbook.ipynb:process_paper", "exec"), namespace)
    return namespace


def parser_cell(notebook: dict) -> str:
    cells = ["".join(c.get("source", [])) for c in notebook["cells"] if c["cell_type"] == "code"]
    matches = [source for source in cells if "def process_paper(" in source]
    assert len(matches) == 1
    return matches[0]


@pytest.fixture(scope="module")
def parser():
    notebook = json.loads((ROOT / "notebooks/eda_workbook.ipynb").read_text(encoding="utf-8"))
    return parser_namespace(parser_cell(notebook))


def lncs_paper():
    """Pages laid out like a Springer LNCS paper: '<page> <author>' on even pages,
    '<short title> <page>' on odd pages, so the author header looks like 'Section 8'."""
    sections = ["1 Introduction", "2 Background", "3 Method", "4 Banking Case",
                "5 Checkpoints", "6 Evaluation", "7 Discussion", "8 Conclusion"]
    pages = ["AI-Decision Checkpoints for Business Process Management\nAmin Jalali\nAbstract\n" + BODY]
    for number, heading in enumerate(sections, start=2):
        header = f"{number} Amin Jalali" if number % 2 == 0 else f"AI-Decision Checkpoints {number}"
        pages.append(f"{header}\n{heading}\n{body(number)}\n{body(number + 100)}")
    pages.append("10 Amin Jalali\nReferences\n1. A. Author. A paper. 2024.")
    return pages


def test_running_author_header_is_not_a_section(parser):
    sections = parser["process_paper"](lncs_paper())
    assert not [heading for heading in sections if "Jalali" in heading]
    assert "8 Conclusion" in sections and "7 Discussion" in sections


def test_old_parser_had_the_bug():
    """Guards the test above: the parser before this fix produced 'Amin Jalali' sections."""
    try:
        source = subprocess.check_output(
            ["git", "show", "1594fda:notebooks/eda_workbook.ipynb"], cwd=ROOT, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("git history unavailable")
    old = parser_namespace(parser_cell(json.loads(source.decode("utf-8"))))
    assert [heading for heading in old["process_paper"](lncs_paper()) if "Jalali" in heading]


def test_running_title_header_and_footer_removed_from_text(parser):
    pages = [f"Paper Title\nAbstract\n{BODY}"] + [
        f"Paper Title: A Long Running Header\n{body(n)}\nPreprint. Under review. {n}" for n in range(2, 8)]
    text = parser["process_paper"](pages)["all"]
    assert "Running Header" not in text and "Under review" not in text
    assert all(body(n) in text for n in range(2, 8))
    assert "Paper Title" in text  # the first page keeps the real title


def test_lines_that_do_not_repeat_are_kept(parser):
    headings = ("1 Introduction", "2 Method", "3 Results", "4 Conclusion")
    pages = [f"Title page\n{BODY}"] + [f"{h}\n{body(n)}" for n, h in enumerate(headings)]
    sections = parser["process_paper"](pages)
    assert [h for h in sections if h not in ("all", "Front Matter")] == [
        "1 Introduction", "2 Method", "3 Results", "4 Conclusion"]


def test_short_documents_are_left_alone(parser):
    pages = ["Same line\nA", "Same line\nB", "Same line\nC"]
    assert parser["strip_running_lines"](pages) == pages


def test_edge_key_ignores_page_numbers(parser):
    assert parser["edge_key"]("8  Amin Jalali") == parser["edge_key"]("10 Amin Jalali")


def test_long_repeated_lines_are_not_treated_as_headers(parser):
    sentence = "This exact long sentence repeats at the top of every page but it is real text written by the authors"
    pages = [f"Title\n{BODY}"] + [f"{sentence}\n{body(n)}" for n in range(2, 8)]
    assert parser["strip_running_lines"](pages) == pages


def test_lines_differing_inside_are_not_merged(parser):
    assert parser["edge_key"]("Table 2 shows results") != parser["edge_key"]("Table 3 shows results")
    assert parser["edge_key"]("Preprint. Under review. 3") == parser["edge_key"]("Preprint. Under review. 14")


def test_table_and_figure_captions_are_not_headings(parser):
    for caption in ("TABLE II", "TABLE III WGA (%) ON CELEBA", "FIGURE 3", "FIG. 2", "ALGORITHM 1"):
        assert not parser["is_caps_heading"](caption)
    assert parser["is_caps_heading"]("RELATED WORK")
    assert parser["is_caps_heading"]("EXPERIMENTAL SETUP")


def test_caption_does_not_split_an_unnumbered_paper(parser):
    pages = ["Title\nAbstract\n" + BODY,
             "RELATED WORK\n" + body(1) + "\nTABLE II\n" + body(2),
             "EXPERIMENTS\n" + body(3)]
    sections = parser["process_paper"](pages)
    assert "TABLE II" not in sections
    assert "RELATED WORK" in sections and body(2) in sections["RELATED WORK"]


def test_long_capitalised_caption_text_is_not_a_heading(parser):
    # Real caption lines from an IEEE paper, with words merged by PDF extraction
    for caption in ("WGA (%)ONCELEBA-STD(RESNET-18)ANDCELEBA-MB (RESNET-18). 3SEEDS,MEAN±STD.",
                    "GROUPDROVS. BFR+GROUPDRO (3SEEDS,MEAN±STD). WGA (%).",
                    "FROZEN-BACKBONE STRESS TESTS ONCELEBA-STD(R18),THREE-SEED MEANS."):
        assert not parser["is_caps_heading"](caption)
    assert parser["is_caps_heading"]("EXPERIMENTAL SETUP AND CALIBRATION PERFORMANCE")


def test_caption_split_over_short_lines_is_not_a_heading(parser):
    # IEEE-style caption broken into short capitalised lines after "TABLE IV"
    pages = ["Title\nAbstract\n" + BODY,
             "RELATED WORK\n" + body(1) + "\nTABLE IV\nREPORTED SCORES BEFORE AND\nAFTER TRAINING (3 SEEDS)\n" + body(2),
             "EXPERIMENTS\n" + body(3)]
    headings = [h for h in parser["process_paper"](pages) if h not in ("all", "Front Matter", "Abstract")]
    assert headings == ["RELATED WORK", "EXPERIMENTS"]
