import json
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'evaluation'))
import manual_review as review

@pytest.fixture
def sample():
    answer={'id':'q1','query':'How many people?','answer':'There were 92 participants [1].',
            'passages':[{'paper_id':'p1','title':'Survey','text':'There were 192 participants in the survey.'}]}
    gold={'id':'q1','query':answer['query'],'relevant_papers':['p1']}
    checklist={'id':'q1','query':answer['query'],'expected_numbers':['192'],
               'required_checks':[{'id':'q1.1','label':'Participants','requirement':'Reports 192 participants.'}]}
    decision={'checks':[{'id':'q1.1','verdict':'no',
                         'reason':'The answer says 92, but the source reports 192.','source_ids':['p1.1']}]}
    return answer,gold,checklist,decision


def test_catalog_matches_all_25_questions():
    root=Path(__file__).resolve().parents[1]
    gold={q['id']:q for q in json.loads((root/'evaluation/benchmark.json').read_text())['queries']}
    data, catalog=review.load_checklists(root/'evaluation/answer_checklists.json',gold)
    assert len(catalog)==25
    assert data['review_status']=='assistant_prepared_pending_human_approval'
    assert len(catalog['q02']['required_checks'])==3


def test_source_spans_are_exact_and_preview_bounded():
    text=('First detail.\nAnother detail about costs and benefits. '*40).strip()
    units=review.source_units([{'text':text}])
    assert len(units)>1
    for unit in units:
        assert unit['text']==text[unit['start']:unit['end']]
        assert len(review.preview(unit))<=240
        assert review.preview(unit).rstrip('…') in ' '.join(text.split())


def test_numeric_mismatch_and_source_list_not_counted(sample):
    answer,gold,checklist,_=sample
    result=review.automatic_checks(answer,gold,checklist)
    assert result['numbers_absent_from_cited_sources']==['92']
    assert result['expected_numbers_not_found']==['192']
    answer['answer']='There were 192 participants.\nSources:\n[1] Survey'
    result=review.automatic_checks(answer,gold,checklist)
    assert result['checks'][0]['status']=='attention'


def test_retrieval_deduplicates_papers_and_handles_unanswerable(sample):
    answer,gold,checklist,_=sample
    answer['passages']=[{'paper_id':p,'text':'A passage'} for p in ['other','other','p1']]
    metrics=review.automatic_checks(answer,gold,checklist)['retrieval']
    assert metrics['paper_recall']==1
    assert metrics['paper_mrr']==0.5
    assert metrics['paper_ndcg']==pytest.approx(1/review.math.log2(3))
    gold['relevant_papers']=[]
    assert review.automatic_checks(answer,gold,checklist)['retrieval']['paper_recall'] is None


def test_focused_source_preview_keeps_relevant_tail():
    text='Unrelated background information. '*12 + 'The comparison identifies centralized routing versus decentralized bidding.'
    shown=review.preview({'text':text},focus='centralized decentralized comparison routing bidding')
    assert len(shown)<=240
    assert 'centralized routing' in shown
    assert shown.strip('…') in text


def test_appended_source_list_cannot_supply_a_missing_comparison():
    assert review.answer_body('A vague answer.\nSource list:\nCentralized versus decentralized [1]')=='A vague answer.'



def test_manual_workflow_is_offline_and_never_grades_content(tmp_path,sample,monkeypatch):
    import socket
    def forbidden(*args,**kwargs):raise AssertionError('No network calls allowed')
    monkeypatch.setattr(socket,'socket',forbidden)
    answer,gold,checklist,_=sample
    source=tmp_path/'answers.json';source.write_text(json.dumps({'answers':[answer],'benchmark':{'queries':[gold]}}))
    catalog=tmp_path/'checklists.json';catalog.write_text(json.dumps({'provenance':'test','queries':[checklist]}))
    args=SimpleNamespace(answers=source,benchmark=None,checklists=catalog,output=tmp_path/'manual.json',max_words=120)
    result=review.main(args)
    assert result['answers'][0]['content_review_status']=='pending_manual_review'
    text=args.output.with_suffix('.md').read_text()
    assert 'Manual review needed' in text and 'Reports 192 participants' in text
    assert 'There were 192 participants in the survey.' in text
    assert 'LLM' not in text
    args.output=source
    with pytest.raises(ValueError):review.main(args)


def test_archived_files_are_preserved_byte_for_byte():
    import hashlib
    root=Path(__file__).resolve().parents[1]/'evaluation/archive/llm_judge'
    for entry in json.loads((root/'manifest.json').read_text()):
        assert hashlib.sha256((root/entry['archive_path']).read_bytes()).hexdigest()==entry['sha256']
