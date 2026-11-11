"""Compare retrieval settings with shared embedding/reranker caches (no generation)."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from dataclasses import asdict
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'notebooks'))
from retrieval import ResearchRetriever,needs_multiple_papers
from run_retrieval import notebook_parser,load_corpus,compact
from run_answers import json_digest

VARIANTS={
 'baseline':dict(k=5,fetch_k=60,per_paper=4,gap=8,order=True,hybrid=False),
 'small':dict(k=3,fetch_k=60,per_paper=3,gap=8,order=True,hybrid=False),
 'wide':dict(k=8,fetch_k=60,per_paper=6,gap=12,order=True,hybrid=False),
 'rerank_order':dict(k=5,fetch_k=60,per_paper=4,gap=8,order=False,hybrid=False),
 'tight':dict(k=5,fetch_k=60,per_paper=4,gap=4,order=True,hybrid=False),
 'fetch20':dict(k=5,fetch_k=20,per_paper=4,gap=8,order=True,hybrid=False),
 'hybrid':dict(k=5,fetch_k=60,per_paper=4,gap=8,order=True,hybrid=True),
 'hybrid_wide':dict(k=8,fetch_k=60,per_paper=6,gap=12,order=True,hybrid=True),
}
class CachedStore:
 def __init__(self,store):self.store=store;self.cache={}
 def similarity_search_with_relevance_scores(self,query,**kwargs):
  key=(query,json.dumps(kwargs,sort_keys=True))
  if key not in self.cache:self.cache[key]=self.store.similarity_search_with_relevance_scores(query,**kwargs)
  return self.cache[key]
 def get(self,**kwargs):return self.store.get(**kwargs)

class CachedRetriever(ResearchRetriever):
 scores={}
 def _rerank(self,query,candidates):
  missing=[doc for doc,_ in candidates if (query,doc.page_content) not in self.scores]
  if missing:
   scores=self._reranker.predict([(query,d.page_content) for d in missing],batch_size=16,show_progress_bar=False)
   self.scores.update({(query,d.page_content):float(s) for d,s in zip(missing,scores)})
  ranked=sorted([(d,self.scores[query,d.page_content]) for d,_ in candidates],key=lambda p:p[1],reverse=True)
  if ranked and self.max_rerank_gap is not None:ranked=[p for p in ranked if p[1]>=ranked[0][1]-self.max_rerank_gap]
  return ranked

def main(args):
 from langchain_huggingface import HuggingFaceEmbeddings
 from sentence_transformers import CrossEncoder
 from ingest import build_vector_store
 benchmark=json.loads(args.benchmark.read_text());parser,source=notebook_parser();parsed,metadata=load_corpus(benchmark,parser)
 digest=hashlib.sha256(source.encode());digest.update((ROOT/'notebooks/ingest.py').read_bytes())
 for path in sorted((ROOT/'data').glob('*.pdf')):digest.update(path.read_bytes())
 fingerprint=digest.hexdigest()[:12]
 embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2',encode_kwargs={'normalize_embeddings':True})
 store=CachedStore(build_vector_store(parsed,metadata,embeddings,persist_directory=ROOT/'.evaluation_cache'/fingerprint,collection_name='evaluation_mpnet_cosine'))
 model='cross-encoder/ms-marco-MiniLM-L6-v2';reranker=CrossEncoder(model)
 summary={}
 for name in args.variants or VARIANTS:
  cfg=VARIANTS[name];retriever=CachedRetriever(store,max_chunks_per_paper=cfg['per_paper'],rerank_model=model,max_rerank_gap=cfg['gap'],order_by_vector=cfg['order'],hybrid=cfg['hybrid']);retriever._reranker=reranker
  rows=[]
  for item in benchmark['queries']:
   chunks=retriever.retrieve(item['query'],k=cfg['k'],fetch_k=cfg['fetch_k'],min_papers=2 if needs_multiple_papers(item['query']) else 1)
   papers=list(dict.fromkeys(c.paper_id for c in chunks));gold=item['relevant_papers'];hits=[any(compact(e) in compact(c.text) for c in chunks if c.paper_id in gold) for e in item['evidence']]
   rows.append(dict(id=item['id'],query=item['query'],relevant_papers=gold,retrieved_papers=papers,retrieved_chunks=[asdict(c) for c in chunks],context=retriever.format_context(chunks),source_list=retriever.format_sources(chunks),recall=len(set(gold)&set(papers))/len(gold) if gold else None,evidence_hits=hits))
  positive=[r for r in rows if r['relevant_papers']];facts=[v for r in rows for v in r['evidence_hits']]
  stats={'macro_recall':sum(r['recall'] for r in positive)/len(positive),'evidence_coverage':sum(facts)/len(facts) if facts else None,'evidence_hits':sum(facts),'evidence_total':len(facts),'average_chunks':sum(len(r['retrieved_chunks']) for r in rows)/len(rows)}
  result=dict(snapshot_version=1,benchmark_sha256=json_digest(benchmark),benchmark=str(args.benchmark.resolve().relative_to(ROOT)),corpus_fingerprint=fingerprint,model='sentence-transformers/all-mpnet-base-v2',k_chunks=cfg['k'],fetch_k=cfg['fetch_k'],max_chunks_per_paper=cfg['per_paper'],rerank_model=model,max_rerank_gap=cfg['gap'],order_by_vector=cfg['order'],hybrid=cfg['hybrid'],summary=stats,queries=rows)
  args.output_dir.mkdir(parents=True,exist_ok=True);(args.output_dir/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n');summary[name]=stats
  print(name,json.dumps(stats),flush=True)
 (args.output_dir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--benchmark',type=Path,default=ROOT/'evaluation/benchmark.json');p.add_argument('--output-dir',type=Path,default=ROOT/'evaluation/results/opt_retrieval_sweep');p.add_argument('--variants',nargs='+',choices=list(VARIANTS));main(p.parse_args())
