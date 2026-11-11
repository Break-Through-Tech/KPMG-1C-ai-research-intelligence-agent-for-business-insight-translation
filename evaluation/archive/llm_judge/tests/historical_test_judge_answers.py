"""Offline tests: judge evidence, retries, rendering and safe resume behavior."""
import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'evaluation'))
import judge_answers as judge


@pytest.fixture
def sample():
    gold = {'id': 'q1', 'query': 'How many people?', 'relevant_papers': ['p1'], 'evidence': ['192']}
    answer = {'id': 'q1', 'query': gold['query'], 'answer': 'There were 92 participants [1].',
              'passages': [{'paper_id': 'p1', 'chunk_id': 'c1', 'text': 'There were 192 participants in the survey.'}]}
    review = {
        'content_verdict': 'fail', 'context_sufficiency': 'sufficient',
        **{d: {'rating': 'pass', 'reason': 'The decision is supported.'} for d in judge.DIMENSIONS},
        'passages': [{'passage_id': 1, 'relevance': 'relevant', 'reason': 'Contains the sample size.'}],
        'findings': [{'issue': 'Wrong sample size', 'answer_excerpt': '92 participants',
                      'explanation': 'The passage says 192, not 92.',
                      'evidence': [{'passage_id': 1, 'quote': '192 participants in the survey.'}]}],
        'improved_answer': 'There were 192 participants [1].',
    }
    review['faithfulness'] = {'rating': 'fail', 'reason': 'The numeric value is wrong.'}
    return answer, gold, review


def test_review_accepts_real_evidence(sample):
    judge.validate_review(sample[2], sample[0], sample[1])


@pytest.mark.parametrize('change', ['invented_quote', 'wrong_passage', 'missing_passage',
                                   'duplicate_passage', 'invented_answer_excerpt', 'bad_revision_citation',
                                   'false_full', 'false_abstention', 'wrong_type', 'missing_field', 'na'])
def test_invalid_reviews_are_rejected(sample, change):
    answer, gold, review = copy.deepcopy(sample)
    if change == 'invented_quote':
        review['findings'][0]['evidence'][0]['quote'] = '92 participants in the survey.'
    elif change == 'wrong_passage':
        review['findings'][0]['evidence'][0]['passage_id'] = 9
    elif change == 'missing_passage':
        review['passages'] = []
    elif change == 'duplicate_passage':
        review['passages'] *= 2
    elif change == 'invented_answer_excerpt':
        review['findings'][0]['answer_excerpt'] = 'The answer never said this.'
    elif change == 'bad_revision_citation':
        review['improved_answer'] += ' [99]'
    elif change == 'false_full':
        review['content_verdict'] = 'full'
    elif change == 'false_abstention':
        review['content_verdict'] = 'appropriate_abstention'
    elif change == 'wrong_type':
        review['passages'][0]['passage_id'] = True
    elif change == 'missing_field':
        del review['faithfulness']
    else:
        review['completeness']['rating'] = 'not_applicable'
    with pytest.raises(ValueError):
        judge.validate_review(review, answer, gold)


def test_correct_content_can_fail_citations(sample):
    answer, gold, review = copy.deepcopy(sample)
    review['content_verdict'] = 'full'
    review['faithfulness']['rating'] = 'pass'
    review['citation_support']['rating'] = 'fail'
    judge.validate_review(review, answer, gold)
    row = {'status': 'reviewed', 'review': review, 'mechanical_issues': []}
    assert judge.outcome(row) == 'NEEDS REVIEW'


def test_answerable_factual_answer_can_mark_abstention_not_applicable(sample):
    answer, gold, review = copy.deepcopy(sample)
    review['abstention']['rating'] = 'not_applicable'
    judge.validate_review(review, answer, gold)


@pytest.mark.parametrize('refusal', [True, False])
def test_abstention_cannot_be_skipped_for_refusal_or_unanswerable_question(sample, refusal):
    answer, gold, review = copy.deepcopy(sample)
    review['abstention']['rating'] = 'not_applicable'
    if refusal:
        answer['answer'] = 'The provided papers do not address this question.'
    else:
        gold['relevant_papers'] = []
    with pytest.raises(ValueError, match='Abstention must be assessed'):
        judge.validate_review(review, answer, gold)


def test_unsupported_question_can_correctly_abstain(sample):
    answer, gold, review = copy.deepcopy(sample)
    gold['relevant_papers'] = []
    answer['answer'] = 'The provided papers do not address this question.'
    answer['passages'] = []
    review['content_verdict'] = 'appropriate_abstention'
    review['context_sufficiency'] = 'insufficient'
    review['faithfulness']['rating'] = 'not_applicable'
    review['citation_support']['rating'] = 'not_applicable'
    review['passages'] = []
    review['findings'] = []
    review['improved_answer'] = answer['answer']
    judge.validate_review(review, answer, gold)
    assert judge.outcome({'status': 'reviewed', 'review': review, 'mechanical_issues': []}) == 'PASS'


def test_invalid_quote_retries_with_feedback(sample, monkeypatch):
    answer, gold, review = sample
    bad = copy.deepcopy(review)
    bad['findings'][0]['evidence'][0]['quote'] = 'Invented evidence'
    payloads = []
    def request(host, endpoint, payload, timeout):
        payloads.append(copy.deepcopy(payload))
        return {'message': {'content': json.dumps(bad if len(payloads) == 1 else review)}, 'done_reason': 'stop'}
    monkeypatch.setattr(judge, 'request_json', request)
    result = judge.judge_one(answer, gold, 'judge', 'host', {}, 5)
    assert result['status'] == 'reviewed'
    assert len(result['attempts']) == 2
    assert 'validation_error' in result['attempts'][0]
    assert payloads[0]['format'] == judge.SCHEMA
    assert payloads[0]['messages'][0]['role'] == 'system'
    assert 'Validation error' in payloads[1]['messages'][-1]['content']
    assert json.loads(payloads[0]['messages'][1]['content'])['answer'] == answer['answer']


def test_zero_retries_makes_only_one_request(sample, monkeypatch):
    calls = []
    def request(*args):
        calls.append(args)
        return {'message': {'content': 'invalid'}}
    monkeypatch.setattr(judge, 'request_json', request)
    result = judge.judge_one(sample[0], sample[1], 'judge', 'host', {}, 5, retries=0)
    assert result['status'] == 'judge_error'
    assert len(calls) == len(result['attempts']) == 1
    assert result['attempts'][0]['seconds'] >= 0


@pytest.mark.parametrize('response', [
    {'message': {'content': 'not json'}},
    {'message': {'content': '{}'}, 'done_reason': 'length'},
])
def test_invalid_or_truncated_judge_is_not_counted_as_review(sample, monkeypatch, response):
    monkeypatch.setattr(judge, 'request_json', lambda *args: response)
    result = judge.judge_one(sample[0], sample[1], 'judge', 'host', {}, 5)
    assert result['status'] == 'judge_error'
    assert judge.outcome(result) == 'JUDGE ERROR'
    assert len(result['attempts']) == 2


def test_render_explains_verdict_and_source(sample):
    answer, _, review = sample
    row = dict(status='reviewed', review=review, mechanical_issues=['Missing direct quote'],
               id='q1', query=answer['query'])
    report = {'run_config': {'model': 'judge'}, 'reviews': [row]}
    text = judge.render_report(report)
    for required in ['Needs attention', 'What went well', 'What needs fixing', '192, not 92',
                     'Next step']:
        assert required in text


def test_rejected_review_explanations_are_visible_but_not_accepted(sample):
    answer, _, review = sample
    row = dict(status='judge_error', error='Invalid quote', id='q1', query=answer['query'],
               mechanical_issues=['Missing citation'], attempts=[
                   {'raw_response': json.dumps(review), 'validation_error': 'Invalid quote'},
                   {'raw_response': 'truncated ``` response'}])
    text = judge.render_row(row)
    for required in ['Review unavailable (judge error)', 'Reviewer’s unverified view', '192, not 92',
                     'quotation that does not match', 'not proof that the answer is wrong']:
        assert required in text
    assert judge.outcome(row) == 'JUDGE ERROR'


def test_main_saves_resumes_and_rejects_changed_inputs(tmp_path, sample, monkeypatch, capsys):
    answer, gold, review = sample
    source = tmp_path / 'answers.json'
    data = {'model': 'generator', 'model_digest': 'generator-weights', 'answers': [answer],
            'benchmark': {'queries': [gold]}}
    source.write_text(json.dumps(data))
    args = SimpleNamespace(answers=source, benchmark=None, output=tmp_path / 'judge.json',
                           host='host', model='judge', limit=0, num_ctx=16384, num_predict=3072, timeout=5, retries=1)
    calls = []
    def request(host, endpoint, payload=None, timeout=5):
        calls.append(endpoint)
        if endpoint == '/api/tags':
            return {'models': [{'name': 'judge:latest', 'digest': 'judge-weights'}]}
        return {'message': {'content': json.dumps(review)}, 'done_reason': 'stop'}
    monkeypatch.setattr(judge, 'request_json', request)
    assert judge.main(args) == 0
    saved = json.loads(args.output.read_text())
    assert saved['reviews'][0]['review'] == review
    assert args.output.with_suffix('.md').exists()
    assert '192, not 92' in capsys.readouterr().out
    assert judge.main(args) == 0
    assert calls.count('/api/chat') == 1
    original = args.output.read_bytes()
    data['answers'][0]['answer'] = 'Different response [1].'
    source.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='inputs changed'):
        judge.main(args)
    assert args.output.read_bytes() == original
    assert calls.count('/api/chat') == 1


def test_input_question_must_match_benchmark(tmp_path, sample):
    answer, gold, _ = sample
    source = tmp_path / 'answers.json'
    wrong = dict(answer, query='Different question')
    source.write_text(json.dumps({'benchmark': {'queries': [gold]}, 'answers': [wrong]}))
    with pytest.raises(ValueError, match='mismatched'):
        judge.read_inputs(source)


@pytest.mark.parametrize('error, expected', [
    ('answer_excerpt must be copied', 'changed or shortened'),
    ('Evidence quote does not occur in passage [4]', 'does not match source 4'),
    ('Judge output reached its token limit', 'cut off'),
    ('Connection refused', 'unavailable or took too long'),
    ('Invalid schema', 'incomplete or inconsistent'),
])
def test_plain_language_failure_reason(error, expected):
    assert expected in judge.explain_judge_error(error)
