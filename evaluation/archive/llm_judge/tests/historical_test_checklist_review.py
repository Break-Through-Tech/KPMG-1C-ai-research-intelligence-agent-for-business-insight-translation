import copy
import json
import sys
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'evaluation'))
import review_answers as review


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


@pytest.mark.parametrize('mutation', ['missing','duplicate','source','unsupported'])
def test_decision_integrity(sample,mutation):
    answer,gold,checklist,decision=sample
    if mutation=='missing': decision['checks']=[]
    elif mutation=='duplicate': decision['checks']*=2
    elif mutation=='source': decision['checks'][0]['source_ids']=['p99.1']
    else: decision['checks'][0]['source_ids']=[]
    with pytest.raises(ValueError):
        review.validate_decisions(decision,checklist,review.source_units(answer['passages']),False)


def make_row(sample,status='reviewed'):
    answer,gold,checklist,decision=sample
    return dict(id='q1',query=answer['query'],answer=answer['answer'],status=status,
                checklist=checklist,source_units=review.source_units(answer['passages']),
                automatic=review.automatic_checks(answer,gold,checklist),review=decision if status=='reviewed' else {})


def test_business_report_has_specific_issue_and_original_source(sample):
    row=make_row(sample)
    text=review.render_row(row)
    assert 'What went well' in text and 'What needs attention' in text
    assert '92, but the source reports 192' in text
    assert '> There were 192 participants in the survey.' in text
    assert 'source_support' not in text
    assert review.disposition(row)=='Needs attention'


def test_pending_is_never_a_pass(sample):
    row=make_row(sample,'not_run')
    assert review.disposition(row)=='Content review pending'
    assert 'Not reviewed' in review.render_row(row)


def test_failed_review_does_not_display_rejected_ratings(sample):
    row=make_row(sample,'judge_error');row['error']='Review points to an unknown or duplicate source ID'
    text=review.render_row(row)
    assert 'Why review is unavailable' in text
    assert 'not mean the answer is wrong' in text
    assert 'Not reviewed' in text


def test_focused_prompt_uses_body_and_ids_not_quotes(sample,monkeypatch):
    answer,gold,checklist,decision=sample
    answer['answer']+='\nEvidence:\n"192 participants in the survey" [1]'
    payloads=[]
    def request(host,endpoint,payload,timeout):
        payloads.append(payload)
        return {'message':{'content':json.dumps(decision)},'done_reason':'stop'}
    monkeypatch.setattr(review.legacy,'request_json',request)
    args=review.parser().parse_args(['--answers','unused'])
    result=review.judge_checklist(answer,gold,checklist,review.source_units(answer['passages']),args)
    assert result['status']=='reviewed'
    sent=json.loads(payloads[0]['messages'][1]['content'])
    assert 'Evidence:' not in sent['answer_body']
    assert sent['source_units'][0]['id']=='p1.1'


def test_truncated_output_preserves_diagnostics(sample,monkeypatch):
    monkeypatch.setattr(review.legacy,'request_json',lambda *a: {'message':{'content':'{'},'done_reason':'length'})
    args=review.parser().parse_args(['--answers','unused'])
    answer,gold,checklist,_=sample
    result=review.judge_checklist(answer,gold,checklist,review.source_units(answer['passages']),args)
    assert result['status']=='judge_error'
    assert result['attempts'][0]['raw_response']=='{'


def test_offline_checkpoint_resume_and_mismatch(tmp_path,sample,monkeypatch):
    answer,gold,checklist,_=sample
    source=tmp_path/'answers.json';source.write_text(json.dumps({'answers':[answer],'benchmark':{'queries':[gold]}}))
    catalog=tmp_path/'checklists.json';catalog.write_text(json.dumps({'provenance':'test','queries':[checklist]}))
    output=tmp_path/'review.json'
    args=review.parser().parse_args(['--answers',str(source),'--checklists',str(catalog),'--output',str(output),'--checks-only'])
    def forbidden(*a,**kw): raise AssertionError('offline must not call Ollama')
    monkeypatch.setattr(review.legacy,'request_json',forbidden)
    assert review.main(args)==0
    first=output.read_bytes()
    assert review.main(args)==0
    assert output.read_bytes()==first
    assert 'Content review pending' in output.with_suffix('.md').read_text()
    args.max_words=10
    with pytest.raises(ValueError,match='settings changed'):review.main(args)
    assert output.read_bytes()==first


def test_focused_source_preview_keeps_relevant_tail():
    text='Unrelated background information. '*12 + 'The comparison identifies centralized routing versus decentralized bidding.'
    shown=review.preview({'text':text},focus='centralized decentralized comparison routing bidding')
    assert len(shown)<=240
    assert 'centralized routing' in shown
    assert shown.strip('…') in text


def test_appended_source_list_cannot_supply_a_missing_comparison():
    assert review.answer_body('A vague answer.\nSource list:\nCentralized versus decentralized [1]')=='A vague answer.'


def test_live_path_resume_does_not_repeat_model_request(tmp_path,sample,monkeypatch):
    answer,gold,checklist,decision=sample
    source=tmp_path/'answers.json';source.write_text(json.dumps({'answers':[answer],'benchmark':{'queries':[gold]}}))
    catalog=tmp_path/'checklists.json';catalog.write_text(json.dumps({'provenance':'test','queries':[checklist]}))
    args=review.parser().parse_args(['--answers',str(source),'--checklists',str(catalog),'--output',str(tmp_path/'out.json')])
    calls=[]
    def fake(host,endpoint,payload=None,timeout=None):
        calls.append(endpoint)
        if endpoint=='/api/tags':return {'models':[{'name':'qwen3.5:9b','digest':'test'}]}
        return {'message':{'content':json.dumps(decision)}}
    monkeypatch.setattr(review.legacy,'request_json',fake)
    assert review.main(args)==0
    assert review.main(args)==0
    assert calls.count('/api/chat')==1
