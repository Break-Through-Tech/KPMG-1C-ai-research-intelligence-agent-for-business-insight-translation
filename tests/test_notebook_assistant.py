"""Exercise the merged notebook's assistant without model or network calls."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'notebooks'))
from retrieval import ResearchRetriever, RetrievedChunk, needs_multiple_papers

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def assistant():
    notebook = json.loads((ROOT / 'notebooks/eda_workbook.ipynb').read_text())
    source = next(''.join(c['source']) for c in notebook['cells']
                  if 'def generate_local_answer' in ''.join(c.get('source', [])))
    ns = {'needs_multiple_papers': needs_multiple_papers}
    exec(compile(source, 'assistant_cell', 'exec'), ns)
    chunks = [RetrievedChunk(rank=1, score=1.0,
              text='The survey collected 92 commuters and 454 respondent-scenario observations.',
              paper_id='p1', title='Survey', section='Results', source_url='https://example.org/p1',
              chunk_id='p1_1')]
    retriever = ResearchRetriever(None)
    calls = []
    retriever.retrieve = lambda query, **kwargs: calls.append((query, kwargs)) or chunks
    ns['rag_retriever'] = retriever
    structured_calls = []
    def structured(question, passages, **kwargs):
        structured_calls.append((question, passages, kwargs))
        return {'draft': 'The survey counted 92 commuters [1].',
                'generation_error': None, 'local_warnings': []}
    ns['structured_answers'] = SimpleNamespace(generate=structured)
    ns['structured_calls'] = structured_calls
    return ns, calls, chunks


def test_default_keeps_original_query_and_evidence(assistant, monkeypatch):
    ns, calls, _ = assistant
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    ns['generate_local_answer'] = lambda prompt, model: 'The survey counted 92 commuters [1].'
    result = ns['ask_llm']('How many commuters?')
    assert calls[0][0] == 'How many commuters?'
    assert 'Evidence:' in result and 'References:' in result
    assert 'chunk p1_1' in result


def test_rewriting_precedes_retrieval_but_preserves_question(assistant):
    ns, calls, _ = assistant
    prompts = []
    def generate(prompt, provider, model):
        prompts.append((prompt, provider))
        return 'rewritten search' if len(prompts) == 1 else 'The survey counted 92 commuters [1].'
    ns['generate_answer'] = generate
    question = 'Compare both papers: how many commuters?'
    ns['ask_llm'](question, provider='google', rewrite_query=True)
    assert calls[0][0] == 'rewritten search'
    assert calls[0][1]['min_papers'] == 2
    assert 'Question: ' + question in prompts[1][0]
    assert all(provider == 'google' for _, provider in prompts)


def test_citations_are_metadata_only_and_keep_original_numbers(assistant):
    ns, _, chunks = assistant
    second = RetrievedChunk(rank=2, score=.9, text='Other text', paper_id='p2',
                            title='Other', section='Results', source_url='https://example.org/p2')
    result = ns['citation_table']('Other finding [2][2][999].', chunks + [second])
    assert result.startswith('[2] Other')
    assert '[1]' not in result and '[999]' not in result
    assert ns['citation_table']('No citations', chunks) == ''


def test_invalid_citation_is_reported(assistant, capsys):
    ns, _, _ = assistant
    ns['generate_answer'] = lambda *args: 'Unsupported finding [999].'
    result = ns['ask_llm']('Question', provider='google')
    assert 'Unknown passage citations: [999]' in capsys.readouterr().out
    assert 'References:' not in result


def test_no_passages_abstains_without_generation(assistant):
    ns, _, _ = assistant
    ns['rag_retriever'].retrieve = lambda *args, **kwargs: []
    ns['generate_answer'] = lambda *args: pytest.fail('Generation should not run')
    ns['structured_answers'].generate = lambda *args, **kwargs: pytest.fail('Structured generation should not run')
    assert ns['ask_llm']('Question') == 'The provided papers do not address this question.'


def install_fake_google(monkeypatch, text='Google answer'):
    calls = []
    class Client:
        def __init__(self, **kwargs):
            calls.append(kwargs)
            self.models = self
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(text=text)
    monkeypatch.setitem(sys.modules, 'google', SimpleNamespace(genai=SimpleNamespace(Client=Client)))
    monkeypatch.setitem(sys.modules, 'dotenv', SimpleNamespace(load_dotenv=lambda *a, **kw: None))
    return calls


def test_google_adapter_uses_configured_model(assistant, monkeypatch):
    ns, _, _ = assistant
    calls = install_fake_google(monkeypatch)
    monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
    assert ns['generate_answer']('Prompt', 'google', 'configured-model') == 'Google answer'
    assert calls[1] == {'model': 'configured-model', 'contents': 'Prompt', 'config': {'temperature': 0}}


def test_google_requires_key_only_when_selected(assistant, monkeypatch):
    ns, _, _ = assistant
    install_fake_google(monkeypatch)
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    with pytest.raises(ValueError, match='GEMINI_API_KEY'):
        ns['generate_answer']('Prompt', 'google')


def test_empty_provider_response_is_rejected(assistant, monkeypatch):
    ns, _, _ = assistant
    install_fake_google(monkeypatch, text=None)
    monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
    with pytest.raises(ValueError, match='no text'):
        ns['generate_answer']('Prompt', 'google')


def test_invalid_inputs_rejected_before_retrieval(assistant):
    ns, calls, _ = assistant
    with pytest.raises(ValueError, match='empty'):
        ns['ask_llm'](' ')
    with pytest.raises(ValueError, match='Unknown provider'):
        ns['ask_llm']('Question', provider='unknown')
    assert not calls


def test_live_default_uses_tested_structured_policy_and_grouping(assistant):
    ns, _, chunks = assistant
    ns['ask_llm']('How many commuters?')
    question, passages, config = ns['structured_calls'][0]
    assert question == 'How many commuters?' and passages == chunks
    assert config['model'] == 'qwen3.5:9b'
    assert config['policy'] == 'coverage'
    assert config['evidence_mode'] == 'citation'
    assert config['repair'] is False
    assert 'Paper: Survey\nPaper ID: p1' in config['context']
    assert callable(ns['format_answer'])


def test_structured_failure_is_not_presented_as_abstention(assistant):
    ns, _, _ = assistant
    ns['structured_answers'].generate = lambda *a, **k: {
        'generation_error': 'Invalid JSON', 'draft': '', 'local_warnings': []}
    with pytest.raises(RuntimeError, match='could not be formatted reliably'):
        ns['ask_llm']('How many commuters?')


def test_local_rewrite_still_answers_original_question(assistant):
    ns, calls, _ = assistant
    ns['reformat_prompt'] = lambda *args: 'survey commuter count'
    ns['ask_llm']('How many commuters?', rewrite_query=True, model='qwen3.5:9b')
    assert calls[0][0] == 'survey commuter count'
    assert ns['structured_calls'][0][0] == 'How many commuters?'


def test_live_retriever_enables_tested_hybrid_settings():
    notebook = json.loads((ROOT / 'notebooks/eda_workbook.ipynb').read_text())
    source = next(''.join(c['source']) for c in notebook['cells']
                  if 'rag_retriever = ResearchRetriever(' in ''.join(c.get('source', [])))
    ns = {'vector_store': None}
    exec(compile(source, 'retriever_cell', 'exec'), ns)
    retriever = ns['rag_retriever']
    assert retriever.hybrid and retriever.order_by_vector
    assert retriever.max_chunks_per_paper == 4 and retriever.max_rerank_gap == 8
    assert retriever.rerank_model == 'cross-encoder/ms-marco-MiniLM-L6-v2'
