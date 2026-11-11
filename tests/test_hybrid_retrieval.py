import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'notebooks'))
from retrieval import ResearchRetriever
from langchain_core.documents import Document

class Store:
 def get(self,**kwargs):
  return {'ids':['dense','rare','other'],'documents':['general background','zygomatic evidence','zygomatic other paper'],
          'metadatas':[{'paper_id':'a','chunk_id':'dense'},{'paper_id':'a','chunk_id':'rare'},{'paper_id':'b','chunk_id':'other'}]}


def test_hybrid_adds_literal_match_and_respects_paper_filter():
 r=ResearchRetriever(Store(),hybrid=True)
 dense=[(Document(page_content='general background',metadata={'paper_id':'a','chunk_id':'dense'},id='dense'),.9)]
 hits=r._hybrid_candidates('zygomatic',dense,3,paper_ids=['a'])
 assert {d.metadata['chunk_id'] for d,_ in hits}=={'dense','rare'}
 assert all(d.metadata['paper_id']=='a' for d,_ in hits)


def test_hybrid_does_not_reuse_dense_score_threshold():
 with pytest.raises(ValueError,match='not calibrated'):
  ResearchRetriever(Store(),hybrid=True,min_score=.5)
