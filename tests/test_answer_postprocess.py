import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'notebooks'))
from answer_postprocess import postprocess, render, replace_paper_ids

PASSAGES = [{'paper_id': '2608.20319', 'title': 'Inducing Task Models from Computer-Use Traces'}]


def claims(*texts):
    return {'claims': [{'claim': t, 'evidence': [{'passage_id': i + 1}]} for i, t in enumerate(texts)], 'unanswered': ''}


def test_paper_id_replaced_with_title():
    out, log = postprocess(claims('Paper ID 2608.20319 derives auditable task models.'), PASSAGES)
    assert out[0]['claim'] == '“Inducing Task Models from Computer-Use Traces” derives auditable task models.'
    assert log and log[0].startswith('title')


def test_unknown_paper_id_left_unchanged():
    assert replace_paper_ids('Paper ID 9999.00001 says x', {}) == 'Paper ID 9999.00001 says x'


def test_repeated_claim_dropped_and_citation_merged():
    a = 'Clinician pairwise preferences found that G-CARL is consistently preferred over both SFT and MLLM-as-a-Judge baselines, particularly in medical accuracy.'
    b = 'In the clinician pairwise preference study, G-CARL was consistently preferred over both SFT and MLLM-as-a-Judge baselines, particularly in medical accuracy.'
    out, _ = postprocess(claims(a, b), [])
    assert len(out) == 1 and out[0]['evidence'] == [1, 2]


def test_short_distinct_facts_are_kept():
    # Differ by a single word; both are required facts (q37 case).
    out, _ = postprocess(claims('The reward weight for checklist items is set to 0.3.',
                                'The reward weight for format is set to 0.3.'), [])
    assert len(out) == 2


def test_claim_with_new_number_is_kept():
    a = 'The clinician preference study found G-CARL consistently preferred over SFT and MLLM-as-a-Judge baselines in accuracy.'
    b = 'The clinician preference study found G-CARL consistently preferred over SFT and MLLM-as-a-Judge baselines in accuracy, 136:85.'
    assert len(postprocess(claims(a, b), [])[0]) == 2


def test_claim_adding_negation_is_kept():
    a = 'The travel survey agents combine large language models with deterministic rules and statistical software tools.'
    b = 'The travel survey agents do not combine large language models with deterministic rules and statistical software tools.'
    assert len(postprocess(claims(a, b), [])[0]) == 2


def test_render_matches_structured_format():
    assert render([{'claim': 'A fact.', 'evidence': [1, 2]}]) == '- A fact. [1][2]'
    assert render([]) == 'The provided papers do not address this question.'
