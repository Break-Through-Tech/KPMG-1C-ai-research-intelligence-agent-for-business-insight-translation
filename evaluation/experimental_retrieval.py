"""Isolated table-addition / selective-query-expansion retrieval experiments."""
import argparse,hashlib,json,sys,time
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'notebooks'))
from retrieval import ResearchRetriever,needs_multiple_papers
from run_answers import json_digest
from run_retrieval import compact


def should_rewrite(query):
    # Fixed query-only selector: broad comparisons, mechanisms and cross-paper questions.
    return any(term in query.lower() for term in ('which papers','how does','how do ','how well','what is the difference'))


def fuse_candidates(rankings,limit):
    scores={};docs={}
    for ranking in rankings:
        for rank,(doc,_) in enumerate(ranking,1):
            key=doc.metadata.get('chunk_id') or doc.id or (doc.metadata.get('paper_id'),doc.page_content)
            docs.setdefault(key,doc);scores[key]=scores.get(key,0)+1/(60+rank)
    return [(docs[key],score) for key,score in sorted(scores.items(),key=lambda pair:pair[1],reverse=True)[:limit]]


class ExpandedRetriever(ResearchRetriever):
    def __init__(self,*args,rewrites=None,**kwargs):
        super().__init__(*args,**kwargs);self.rewrites=rewrites or {}
    def _hybrid_candidates(self,query,dense,fetch_k,paper_ids=None):
        original=super()._hybrid_candidates(query,dense,fetch_k,paper_ids)
        rewrite=self.rewrites.get(query)
        if not rewrite or rewrite==query:return original
        where={'paper_id':{'$in':list(paper_ids)}} if paper_ids else None
        expanded_dense=self.vector_store.similarity_search_with_relevance_scores(rewrite,k=fetch_k,filter=where)
        expanded=super()._hybrid_candidates(rewrite,expanded_dense,fetch_k,paper_ids)
        return fuse_candidates([original,expanded],fetch_k)


def main(args):
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    benchmark=json.loads(args.benchmark.read_text());baseline=json.loads(args.baseline.read_text())
    embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2',encode_kwargs={'normalize_embeddings':True})
    base=Chroma(collection_name='evaluation_mpnet_cosine',persist_directory=str(ROOT/'.evaluation_cache'/baseline['corpus_fingerprint']),embedding_function=embeddings)
    config={'mode':args.mode,'base_snapshot_sha256':json_digest(baseline),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    store=base;added=[];rewrites={}
    if args.mode=='tables':
        from table_documents import table_documents
        config['extractor_sha256']=hashlib.sha256((ROOT/'notebooks/table_documents.py').read_bytes()).hexdigest()
        for path in sorted((ROOT/'data').glob('*.pdf')):
            pid=path.name.split('v',1)[0]
            added.extend(table_documents(path,dict(id=pid,title=benchmark['papers'][pid],source_url=f'https://arxiv.org/abs/{pid}')))
        config['table_documents_sha256']=json_digest([{'text':d.page_content,'metadata':d.metadata} for d in added])
        store=Chroma(collection_name='evaluation_tables',persist_directory=str(ROOT/'.evaluation_cache'/('tables_'+json_digest(config)[:12])),embedding_function=embeddings,collection_metadata={'hnsw:space':'cosine'})
        original=base.get(include=['documents','metadatas','embeddings'])
        if store._collection.count()==0:
            store._collection.add(ids=original['ids'],documents=original['documents'],metadatas=original['metadatas'],embeddings=original['embeddings'])
        existing=set(store.get(include=[])['ids']);pending=[d for d in added if d.metadata['chunk_id'] not in existing]
        if pending:store.add_documents(pending,ids=[d.metadata['chunk_id'] for d in pending])
        print('Added',len(added),'table chunks',flush=True)
    elif args.mode=='rewrite':
        saved=json.loads(args.rewrites.read_text());config['rewrites_sha256']=json_digest(saved)
        rewrites={r['query']:r['rewrite'] for r in saved['rewrites']}
    retriever=ExpandedRetriever(store,max_chunks_per_paper=4,rerank_model='cross-encoder/ms-marco-MiniLM-L6-v2',max_rerank_gap=8,order_by_vector=True,hybrid=True,rewrites=rewrites)
    rows=[]
    for q in benchmark['queries']:
        chunks=retriever.retrieve(q['query'],k=5,fetch_k=60,min_papers=2 if needs_multiple_papers(q['query']) else 1)
        papers=list(dict.fromkeys(c.paper_id for c in chunks));gold=q['relevant_papers']
        rows.append(dict(id=q['id'],query=q['query'],retrieved_chunks=[asdict(c) for c in chunks],context=retriever.format_context(chunks),source_list=retriever.format_sources(chunks),relevant_papers=gold,retrieved_papers=papers,evidence_hits=[any(compact(e) in compact(c.text) for c in chunks if c.paper_id in gold) for e in q['evidence']]))
    hits=[v for r in rows for v in r['evidence_hits']]
    result=dict(snapshot_version=1,benchmark=str(args.benchmark.resolve().relative_to(ROOT)),benchmark_sha256=json_digest(benchmark),corpus_fingerprint=baseline['corpus_fingerprint'],experiment=config,queries=rows,summary={'evidence_hits':sum(hits),'evidence_total':len(hits),'queries_retrieving_tables':sum(any('_table_' in c['chunk_id'] for c in r['retrieved_chunks']) for r in rows)})
    args.output.parent.mkdir(exist_ok=True,parents=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if added:args.output.with_suffix('.tables.json').write_text(json.dumps([{'text':d.page_content,'metadata':d.metadata} for d in added],ensure_ascii=False,indent=2)+'\n')
    print(result['summary'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['control','tables','rewrite'],required=True);p.add_argument('--benchmark',type=Path,default=ROOT/'evaluation/benchmark.json');p.add_argument('--baseline',type=Path,default=ROOT/'evaluation/results/opt_retrieval_sweep/hybrid.json');p.add_argument('--rewrites',type=Path);p.add_argument('--output',type=Path,required=True);main(p.parse_args())
