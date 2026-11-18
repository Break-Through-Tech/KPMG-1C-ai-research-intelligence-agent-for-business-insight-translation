"""Trace where known evidence chunks drop out of hybrid retrieval (no generation)."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'notebooks'));sys.path.insert(0,str(ROOT/'evaluation'))
from retrieval import ResearchRetriever,normalize_section,looks_like_bibliography
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
MISSES={'q01':['2608.20316_0_1','2608.20316_6_3'],'q02':['2608.20316_0_1'],'q10':['2608.20319_1_1'],'q28':['2608.20318_10_1'],'q32':['2608.20319_30_11']}
qs={q['id']:q['query'] for f in ('benchmark.json','benchmark_holdout.json') for q in json.loads((ROOT/'evaluation'/f).read_text())['queries']}
emb=HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2',encode_kwargs={'normalize_embeddings':True})
store=Chroma(collection_name='evaluation_mpnet_cosine',persist_directory=str(ROOT/'.evaluation_cache/ca5f3c8351d1'),embedding_function=emb)
r=ResearchRetriever(store,max_chunks_per_paper=4,rerank_model='cross-encoder/ms-marco-MiniLM-L6-v2',max_rerank_gap=8,order_by_vector=True,hybrid=True)
for qid,targets in MISSES.items():
    q=qs[qid];dense=store.similarity_search_with_relevance_scores(q,k=60)
    fused=r._hybrid_candidates(q,dense,60)
    elig=[(d,s) for d,s in fused if normalize_section(d.metadata.get('section',''))not in r.excluded_sections and not looks_like_bibliography(d.page_content)]
    r2=ResearchRetriever(store,rerank_model=r.rerank_model);r2._reranker=r._reranker or None
    ranked=r._rerank(q,elig);full=ResearchRetriever._rerank(type('X',(),{'rerank_model':r.rerank_model,'_reranker':r._reranker,'max_rerank_gap':None})(),q,elig)
    ids=lambda L:[d.metadata['chunk_id'] for d,_ in L]
    for t in targets:
        dr=ids(dense).index(t)+1 if t in ids(dense) else None
        fr=ids(fused).index(t)+1 if t in ids(fused) else None
        rr=ids(full).index(t)+1 if t in ids(full) else None
        top=full[0][1];ts=[s for d,s in full if d.metadata['chunk_id']==t]
        print(qid,t,'dense',dr,'fused',fr,'rerank',rr,f'score {ts[0]:.2f} vs top {top:.2f}' if ts else '','| top5 rerank',[(i[-6:],p) for i,p in zip(ids(full)[:6],[d.metadata['paper_id'][-5:] for d,_ in full[:6]])])
