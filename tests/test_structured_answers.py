import copy
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'notebooks'))
import structured_answers as s
from retrieval import RetrievedChunk


def chunks():
    return [RetrievedChunk(1, 1, 'Learning changes average 0.226 against 0 .126 for the rest.', 'p', 'Paper', '', '')]


def payload():
    return {'claims': [{'evidence': [{'passage_id': 1, 'quote': 'Learning changes average 0.226 against 0 .126 for the rest.'}], 'claim': 'The scores are 0.226 and 0.126.'}], 'unanswered': ''}


def test_render_citations_and_pdf_decimals():
    assert s.validate(payload(), chunks()) == ([], [])
    assert s.render(payload()).endswith('[1]')
    assert s.numeric_values('0.226 0 .126') == {'0.226', '0.126'}


def test_mismatched_quote_and_unknown_citations_rejected():
    p=payload();p['claims'][0]['evidence'][0]['quote']=p['claims'][0]['evidence'][0]['quote'].replace('0.226','0.126')
    assert s.validate(p,chunks())[0]
    p=payload();p['claims'][0]['evidence'][0]['passage_id']=2
    assert s.validate(p,chunks())[0]
    p=payload();p['claims'][0]['evidence']=[]
    assert s.validate(p,chunks())[0]


def test_abstention_and_failure_are_distinct(monkeypatch):
    monkeypatch.setattr(s,'request',lambda *a,**kw:{'response':'not json'})
    r=s.generate('Question',chunks())
    assert r['generation_error'] and not r['draft']
    assert s.render({'claims':[],'unanswered':'Not supplied'}) == s.ABSTENTION


def test_bounded_mechanical_repair(monkeypatch):
    calls=[]
    bad=payload();bad['claims'][0]['evidence'][0]['passage_id']=99
    def request(*args,**kw):
        calls.append(args[0]);return {'response':json.dumps(bad if len(calls)==1 else payload())}
    monkeypatch.setattr(s,'request',request)
    result=s.generate('Question',chunks(),repair=True)
    assert len(calls)==2 and result['generation_error'] is None
    assert 'Local checks found' in calls[1]


def test_schema_only_allows_supplied_ids():
    assert s.schema(chunks())['properties']['claims']['items']['properties']['evidence']['items']['properties']['passage_id']['enum']==[1]


def test_citation_only_mode_rejects_missing_or_invented_ids():
    p=payload();p['claims'][0]['evidence']=[{'passage_id':1}]
    assert s.validate(p,chunks(),evidence_mode='citation') == ([],[])
    p['claims'][0]['evidence']=[{'passage_id':True}]
    assert s.validate(p,chunks(),evidence_mode='citation')[0]
