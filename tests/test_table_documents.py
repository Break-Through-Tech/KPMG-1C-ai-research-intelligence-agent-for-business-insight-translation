"""Source-layout regression checks, independent of answer-generation labels."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'notebooks'))
from table_documents import extract_tables,table_documents
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def tmi_tables():
    pytest.importorskip('pdfplumber')
    return extract_tables(next((ROOT/'data').glob('*2608.20319*')))

def test_adjacent_tables_keep_metric_columns_and_row_labels(tmi_tables):
    table=next(t for t in tmi_tables if t['page']==9 and t['caption'].startswith('Table 5:'))
    rows={r['label']:dict(zip(table['headers'],r['values'])) for r in table['rows']}
    assert rows['Ours']['Acc.']=='18.57'
    assert rows['Ours']['Align.']=='67.99'
    assert rows['Workflow summary']['Acc.']=='14.29'
    assert rows['Human curated']['Acc.']=='10.00'
    assert 'held-out task accuracy' in table['caption']

def test_repeated_rows_keep_judge_group(tmi_tables):
    table=next(t for t in tmi_tables if t['page']==9 and t['caption'].startswith('Table 4:'))
    labels={r['label'] for r in table['rows']}
    assert 'gpt-5.5 judge / Ours' in labels
    assert 'claude-sonnet-5 judge / Ours' in labels

def test_table_caption_does_not_use_inline_reference(tmi_tables):
    assert not any(t['caption']=='Table 4.' for t in tmi_tables)
