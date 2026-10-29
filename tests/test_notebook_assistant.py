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


def test_invalid_citation_is_withheld(assistant, capsys):
    ns, _, _ = assistant
    ns['generate_answer'] = lambda *args: 'Unsupported finding [999].'
    result = ns['ask_llm']('Question')
    assert 'Unknown passage citations: [999]' in capsys.readouterr().out
    assert 'I could not verify a cited answer' in result
    assert 'Unsupported finding' not in result
    assert 'References:' in result


def test_missing_citation_is_withheld_with_inspectable_source(assistant, capsys):
    ns, _, _ = assistant
    ns['generate_answer'] = lambda *args: 'The survey counted 92 commuters.'
    result = ns['ask_llm']('How many commuters?')
    assert 'No passage citation' in capsys.readouterr().out
    assert 'The survey counted 92 commuters.' not in result
    assert 'The survey collected 92 commuters' in result
    assert 'References:' in result


def test_which_papers_returns_source_matches_without_model(assistant):
    ns, _, chunks = assistant
    chunks.append(RetrievedChunk(rank=2, score=.8, text='A second study tested routing costs.',
                                 paper_id='p2', title='Routing', section='Results',
                                 source_url='https://example.org/p2', chunk_id='p2_1'))
    ns['generate_answer'] = lambda *args: pytest.fail('Paper search should not call model')
    result = ns['ask_llm']('Which papers study survey commuters and routing costs?')
    assert 'Survey [1]' in result and 'Routing [2]' in result
    assert 'Evidence:' in result and 'References:' in result


def test_comparison_uses_focused_context(assistant):
    ns, _, _ = assistant
    prompts = []
    ns['rag_retriever'].format_focused_context = lambda *args: 'FOCUSED OUTCOME'
    ns['generate_answer'] = lambda prompt, provider, model: (
        prompts.append(prompt) or 'The survey counted 92 commuters [1].')
    ns['ask_llm']('How do these results compare?')
    assert 'FOCUSED OUTCOME' in prompts[0]


def test_no_passages_abstains_without_generation(assistant):
    ns, _, _ = assistant
    ns['rag_retriever'].retrieve = lambda *args, **kwargs: []
    ns['generate_answer'] = lambda *args: pytest.fail('Generation should not run')
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
