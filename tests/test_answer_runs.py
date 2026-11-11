"""Offline regression tests for frozen retrieval and compatible answer resumes."""
import copy
import io
import json
import sys
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evaluation'))
sys.path.insert(0, str(ROOT / 'notebooks'))
import run_answers
import run_retrieval
import check_answers
from retrieval import ResearchRetriever, RetrievedChunk


@pytest.fixture
def frozen():
    benchmark = {'papers': {'p1': 'Survey'}, 'queries': [
        {'id': 'q1', 'query': 'How many participants?', 'relevant_papers': ['p1'], 'evidence': ['192']},
        {'id': 'q2', 'query': 'What was the sample size?', 'relevant_papers': ['p1'], 'evidence': ['192']},
    ]}
    chunk = RetrievedChunk(1, .8, 'The survey enrolled 192 participants in the study.',
                           'p1', 'Survey', 'Results', 'https://example.org/survey', chunk_id='p1_1')
    formatter = ResearchRetriever(None)
    snapshot = {'snapshot_version': 1, 'benchmark_sha256': run_answers.json_digest(benchmark),
                'corpus_fingerprint': 'corpus-v1', 'model': 'embedding-model',
                'k_chunks': 5, 'fetch_k': 60, 'max_chunks_per_paper': 4,
                'rerank_model': 'reranker', 'max_rerank_gap': 8, 'order_by_vector': True,
                'queries': [dict(item, retrieved_chunks=[asdict(chunk)],
                                 context=formatter.format_context([chunk]),
                                 source_list=formatter.format_sources([chunk]))
                            for item in benchmark['queries']]}
    return benchmark, snapshot


def configuration(frozen):
    benchmark, snapshot = frozen
    return run_answers.run_configuration('model', 'model-digest', '{context}\n{question}', snapshot, benchmark)


@pytest.mark.parametrize('change', ['model', 'digest', 'prompt', 'options', 'corpus',
                                    'retrieval', 'passage', 'benchmark', 'pipeline'])
def test_incompatible_runs_cannot_resume(tmp_path, frozen, monkeypatch, change):
    benchmark, snapshot = frozen
    config = configuration(frozen)
    output = tmp_path / 'answers.json'
    run_answers.save_answers(output, config, tmp_path / 'retrieval.json', benchmark, {})
    original = output.read_bytes()
    altered = copy.deepcopy(config)
    if change == 'model':
        altered['model'] = 'another-model'
    elif change == 'digest':
        altered['model_digest'] = 'new-weights'
    elif change == 'prompt':
        altered = run_answers.run_configuration('model', 'model-digest', 'New prompt', snapshot, benchmark)
    elif change == 'options':
        monkeypatch.setitem(run_answers.GENERATION_OPTIONS, 'temperature', .5)
        altered = configuration(frozen)
    elif change == 'benchmark':
        modified = copy.deepcopy(benchmark)
        modified['queries'][0]['evidence'] = ['different expected fact']
        altered = run_answers.run_configuration('model', 'model-digest', '{context}\n{question}', snapshot, modified)
    elif change == 'pipeline':
        altered['answer_pipeline_sha256'] = 'new-validation-code'
    else:
        modified = copy.deepcopy(snapshot)
        if change == 'corpus':
            modified['corpus_fingerprint'] = 'corpus-v2'
        elif change == 'retrieval':
            modified['fetch_k'] = 100
        else:
            modified['queries'][0]['retrieved_chunks'][0]['text'] = 'Changed evidence'
        altered = run_answers.run_configuration('model', 'model-digest', '{context}\n{question}', modified, benchmark)
    with pytest.raises(ValueError, match='configuration changed'):
        run_answers.load_completed(output, altered, run_answers.load_snapshot(snapshot, benchmark))
    assert output.read_bytes() == original


def test_legacy_and_corrupt_checkpoints_are_rejected(tmp_path, frozen):
    benchmark, snapshot = frozen
    path = tmp_path / 'answers.json'
    snapshots = run_answers.load_snapshot(snapshot, benchmark)
    path.write_text(json.dumps({'answers': []}))
    with pytest.raises(ValueError, match='lack a verified'):
        run_answers.load_completed(path, configuration(frozen), snapshots)
    run_answers.save_answers(path, configuration(frozen), path, benchmark, {})
    data = json.loads(path.read_text())
    data['run_fingerprint'] = 'tampered'
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='fingerprint is invalid'):
        run_answers.load_completed(path, configuration(frozen), snapshots)


def test_missing_model_digest_is_rejected(frozen):
    with pytest.raises(ValueError, match='Cannot fingerprint'):
        run_answers.run_configuration('missing', None, 'prompt', frozen[1], frozen[0])


def test_checkpoint_write_failure_preserves_previous_file(tmp_path, frozen, monkeypatch):
    benchmark, _ = frozen
    output = tmp_path / 'answers.json'
    run_answers.save_answers(output, configuration(frozen), tmp_path / 'retrieval.json', benchmark, {})
    original = output.read_bytes()
    def fail_replace(*args):
        raise OSError('Simulated interrupted save')
    monkeypatch.setattr(Path, 'replace', fail_replace)
    with pytest.raises(OSError, match='interrupted save'):
        run_answers.save_answers(output, configuration(frozen), tmp_path / 'retrieval.json', benchmark, {})
    assert output.read_bytes() == original
    assert list(tmp_path.glob('*.tmp')) == []


@pytest.mark.parametrize('change', ['legacy', 'benchmark', 'query', 'missing', 'duplicate', 'rank', 'context'])
def test_bad_retrieval_snapshots_are_rejected(frozen, change):
    benchmark, snapshot = copy.deepcopy(frozen)
    if change == 'legacy':
        snapshot.pop('snapshot_version')
    elif change == 'benchmark':
        benchmark['queries'][0]['evidence'] = ['new label']
    elif change == 'query':
        snapshot['queries'][0]['query'] = 'Changed question'
    elif change == 'missing':
        snapshot['queries'].pop()
    elif change == 'duplicate':
        snapshot['queries'].append(snapshot['queries'][0])
    elif change == 'rank':
        snapshot['queries'][0]['retrieved_chunks'][0]['rank'] = 3
    else:
        snapshot['queries'][0]['context'] = 'Different context'
    with pytest.raises(ValueError):
        run_answers.load_snapshot(snapshot, benchmark)


def test_interrupted_run_resumes_exact_passages_without_retrieval(tmp_path, frozen, monkeypatch):
    benchmark, snapshot = frozen
    benchmark_path = tmp_path / 'benchmark.json'
    benchmark_path.write_text(json.dumps(benchmark))
    snapshot['benchmark'] = str(benchmark_path)
    retrieval_path = tmp_path / 'retrieval.json'
    retrieval_path.write_text(json.dumps(snapshot))
    args = SimpleNamespace(limit=0, retrieval=retrieval_path, output=tmp_path / 'answers.json',
                           model='model', host='http://test')
    monkeypatch.setattr(run_answers, 'notebook_prompt', lambda: '{context}\nQuestion: {question}')
    monkeypatch.setattr(run_answers.urllib.request, 'urlopen', lambda *a, **kw:
                        io.StringIO(json.dumps({'models': [{'name': 'model', 'digest': 'model-digest'}]})))
    monkeypatch.setattr(ResearchRetriever, 'retrieve', lambda *a, **kw: pytest.fail('Must not retrieve again'))
    prompts = []
    def generate(prompt, *args):
        prompts.append(prompt)
        if len(prompts) == 2:
            raise RuntimeError('Interrupted')
        return {'response': 'There were 192 participants [1].'}
    monkeypatch.setattr(run_answers, 'ask_ollama', generate)
    with pytest.raises(RuntimeError, match='Interrupted'):
        run_answers.main(args)
    initial = json.loads(args.output.read_text())
    assert len(initial['answers']) == 1
    assert initial['answers'][0]['passages'] == snapshot['queries'][0]['retrieved_chunks']
    assert initial['answers'][0]['claim_support_status'] == 'not_evaluated'
    assert prompts[0] == snapshot['queries'][0]['context'] + '\nQuestion: How many participants?'
    run_answers.main(args)
    complete = json.loads(args.output.read_text())
    assert len(prompts) == 3  # only unfinished q2 retried
    assert complete['answers'][0] == initial['answers'][0]
    assert len(complete['answers']) == 2
    run_answers.main(args)
    assert len(prompts) == 3  # completed run performs no generation
    before = args.output.read_bytes()
    monkeypatch.setattr(run_answers, 'notebook_prompt', lambda: 'Changed {context} {question}')
    with pytest.raises(ValueError, match='configuration changed'):
        run_answers.main(args)
    assert len(prompts) == 3
    assert args.output.read_bytes() == before


def test_retrieval_report_round_trips_as_frozen_inputs(tmp_path, frozen, monkeypatch):
    benchmark, snapshot = frozen
    (tmp_path / 'notebooks').mkdir()
    (tmp_path / 'notebooks/ingest.py').write_text('ingest version')
    benchmark_path = tmp_path / 'benchmark.json'
    benchmark_path.write_text(json.dumps(benchmark))
    chunks = [RetrievedChunk(**c) for c in snapshot['queries'][0]['retrieved_chunks']]
    retriever = ResearchRetriever(None)
    retriever.retrieve = lambda *args, **kwargs: chunks
    monkeypatch.setattr(run_retrieval, 'ROOT', tmp_path)
    monkeypatch.setattr(run_retrieval, 'notebook_parser', lambda: (None, 'parser version'))
    monkeypatch.setattr(run_retrieval, 'load_corpus', lambda *args: ({}, []))
    monkeypatch.setattr(run_retrieval, 'ResearchRetriever', lambda *args, **kwargs: retriever)
    monkeypatch.setitem(sys.modules, 'langchain_huggingface',
                        SimpleNamespace(HuggingFaceEmbeddings=lambda **kw: None))
    monkeypatch.setitem(sys.modules, 'ingest', SimpleNamespace(build_vector_store=lambda *a, **kw: None))
    output = tmp_path / 'retrieval.json'
    run_retrieval.run(benchmark_path, output, 5, 60, 4, 'reranker', 8, True)
    report = json.loads(output.read_text())
    loaded = run_answers.load_snapshot(report, benchmark)
    assert loaded['q1']['retrieved_chunks'] == [asdict(c) for c in chunks]
    assert report['summary']['evidence_coverage'] == 1


def test_quote_success_is_reported_separately_from_claim_support(tmp_path, frozen):
    benchmark, snapshot = frozen
    path = tmp_path / 'answers.json'
    row = snapshot['queries'][0]
    path.write_text(json.dumps({'benchmark': benchmark, 'answers': [{
        'id': 'q1', 'answer': 'The study had 92 participants [1].\nEvidence: '
        '"The survey enrolled 192 participants in the study." [1]',
        'source_list': row['source_list'], 'passages': row['retrieved_chunks'],
    }]}))
    output = tmp_path / 'checks.json'
    check_answers.main(SimpleNamespace(answers=path, output=output))
    result = json.loads(output.read_text())
    checked = result['answers'][0]
    assert checked['verified_direct_quote'] is True
    assert checked['claim_support_status'] == 'not_evaluated'
    assert any('92' in issue for issue in checked['issues'])
    assert 'Mechanical' in result['validation_scope']


def test_explicit_question_selection_preserves_order(frozen):
    benchmark,_=frozen
    assert [q['id'] for q in run_answers.select_queries(benchmark,['q2','q1'])]==['q2','q1']
    for ids,limit in [(['unknown'],0),(['q1','q1'],0),(['q1'],1)]:
        with pytest.raises(ValueError):run_answers.select_queries(benchmark,ids,limit)


def test_context_variants_preserve_evidence_and_citation_ids():
    chunks = [RetrievedChunk(i, score, f'Evidence {i}', paper, paper, 'Results', '')
              for i, score, paper in [(1, .1, 'A'), (2, .9, 'B'), (3, .8, 'B'), (4, .2, 'A')]]
    frozen = {'query': 'Compare both papers', 'retrieved_chunks': [asdict(c) for c in chunks]}
    original = copy.deepcopy(frozen)
    grouped = run_answers.experiment_context(frozen, group_by_paper=True)
    assert grouped.index('[1]') < grouped.index('[4]') < grouped.index('[2]')
    ordered = run_answers.experiment_context(frozen, selection_order=True)
    assert ordered.index('[2]') < ordered.index('[4]') < ordered.index('[3]') < ordered.index('[1]')
    both = run_answers.experiment_context(frozen, True, True)
    assert both.index('[2]') < both.index('[3]') < both.index('[4]') < both.index('[1]')
    for context in [grouped, ordered, both]:
        for c in chunks:
            assert context.count(f'[{c.rank}]') == 1
            assert context.count(c.text) == 1
    assert frozen == original
    assert run_answers.experiment_context(frozen) == ResearchRetriever(None).format_context(chunks)


def test_unknown_papers_are_not_merged():
    chunks = [RetrievedChunk(i, 1, f'Text {i}', '', '', '', '') for i in [1, 2]]
    assert ResearchRetriever(None).format_context(chunks, group_by_paper=True).count('Paper: Unknown title') == 2


def test_presentation_change_cannot_resume(tmp_path, frozen):
    config = configuration(frozen)
    config['context_presentation'] = {'group_by_paper': True, 'selection_order': False}
    path = tmp_path / 'answers.json'
    run_answers.save_answers(path, config, path, frozen[0], {})
    changed = copy.deepcopy(config)
    changed['context_presentation']['selection_order'] = True
    with pytest.raises(ValueError, match='context_presentation'):
        run_answers.load_completed(path, changed, run_answers.load_snapshot(frozen[1], frozen[0]))
