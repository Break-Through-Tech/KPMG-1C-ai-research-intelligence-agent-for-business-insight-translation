import sys
from pathlib import Path
from langchain_core.documents import Document
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'evaluation'))
from experimental_retrieval import ExpandedRetriever,should_rewrite,fuse_candidates

def test_candidate_fusion_deduplicates_and_keeps_both_routes():
    a=Document(page_content='original',metadata={'chunk_id':'a'});b=Document(page_content='rewrite',metadata={'chunk_id':'b'})
    fused=fuse_candidates([[(a,1)],[(a,.5),(b,.4)]],60)
    assert [d.page_content for d,_ in fused]==['original','rewrite']

def test_rewrite_selector_uses_broad_question_shape():
    assert should_rewrite('Which papers discuss auditable workflows?')
    assert should_rewrite('How does the method work?')
    assert not should_rewrite('How many frozen repositories are in AI4AI-Bench?')

def test_final_reranker_receives_original_question(monkeypatch):
    from retrieval import ResearchRetriever
    a=Document(page_content='original',metadata={'chunk_id':'a','paper_id':'p'})
    b=Document(page_content='expanded',metadata={'chunk_id':'b','paper_id':'p'})
    class Store:
        def similarity_search_with_relevance_scores(self,q,**kw):return [(a if q=='question' else b,1)]
    monkeypatch.setattr(ResearchRetriever,'_hybrid_candidates',lambda self,q,dense,*args:dense)
    retriever=ExpandedRetriever(Store(),rewrites={'question':'rewrite'},hybrid=True,max_chunks_per_paper=4)
    seen=[]
    retriever._rerank=lambda q,c:seen.append(q) or c
    chunks=retriever.retrieve('question',k=2)
    assert seen==['question']
    assert {c.text for c in chunks}=={'original','expanded'}
