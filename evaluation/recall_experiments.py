"""Retrieval-recall variants over dev + holdout (no generation).

Each variant writes a frozen snapshot that optimize_answers.py can consume, so
answers can be regenerated on exactly the passages scored here. Evidence hits
are literal-phrase checks, a proxy for recall, not answer quality.
"""
import argparse, json, sys
from dataclasses import asdict, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'notebooks')); sys.path.insert(0, str(ROOT / 'evaluation'))
from retrieval import ResearchRetriever, needs_multiple_papers
from run_retrieval import compact
from run_answers import json_digest

BASE = dict(k=5, fetch_k=60, per_paper=4, gap=8)
VARIANTS = {
    'base': {},
    # Let single-paper questions use every slot on that paper (cap stays 4 for cross-paper).
    'cap_single': dict(single_paper_cap=5),
    'k6': dict(k=6, per_paper=5),
    'wide': dict(k=8, per_paper=6, gap=12),
    # Combine first-stage (BM25+dense) rank with cross-encoder rank instead of trusting the reranker alone.
    'rrf_rerank': dict(rerank='rrf'),
    # Give the cross-encoder the paper title and section heading as well as the chunk text.
    'header_rerank': dict(rerank='header'),
    # Merge the previous and next chunk of the same section into each selected passage.
    'neighbours': dict(neighbours=True),
    'rrf_cap_single': dict(rerank='rrf', single_paper_cap=5),
    'rrf_header': dict(rerank='rrf_header'),
    'rrf_header_cap_single': dict(rerank='rrf_header', single_paper_cap=5),
}


class VariantRetriever(ResearchRetriever):
    def __init__(self, *a, rerank_mode='plain', **kw):
        super().__init__(*a, **kw); self.rerank_mode = rerank_mode

    def _rerank(self, query, candidates):
        if not candidates:
            return candidates
        if self._reranker is None:
            from sentence_transformers import CrossEncoder
            self._reranker = CrossEncoder(self.rerank_model)
        header = 'header' in self.rerank_mode
        text = lambda d: (f"{d.metadata.get('title', '')}. {d.metadata.get('section', '')}.\n" if header else '') + d.page_content
        scores = [float(s) for s in self._reranker.predict([(query, text(d)) for d, _ in candidates], batch_size=16, show_progress_bar=False)]
        if self.rerank_mode.startswith('rrf'):
            # candidates arrive in first-stage (fused) order
            order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
            rerank_rank = {i: r for r, i in enumerate(order, 1)}
            fused = [(i, 1 / (60 + i + 1) + 1 / (60 + rerank_rank[i])) for i in range(len(scores))]
            return [(candidates[i][0], s) for i, s in sorted(fused, key=lambda p: p[1], reverse=True)]
        ranked = sorted(enumerate(scores), key=lambda p: p[1], reverse=True)
        if self.max_rerank_gap is not None:
            ranked = [(i, s) for i, s in ranked if s >= ranked[0][1] - self.max_rerank_gap]
        return [(candidates[i][0], s) for i, s in ranked]


def neighbour_text(chunk, by_id):
    paper, section, n = chunk.chunk_id.rsplit('_', 2)
    parts = [by_id.get(f'{paper}_{section}_{int(n) + d}') for d in (-1, 0, 1)]
    parts[1] = chunk.text
    return '\n'.join(p for p in parts if p)


def run_variant(name, cfg, store, reranker, by_id, benchmarks, out_dir):
    c = {**BASE, **cfg}
    out = {}
    for label, path in benchmarks.items():
        bench = json.loads(path.read_text())
        rows = []
        for q in bench['queries']:
            multi = needs_multiple_papers(q['query'])
            cap = c['per_paper'] if multi or 'single_paper_cap' not in c else c['single_paper_cap']
            r = VariantRetriever(store, max_chunks_per_paper=cap, rerank_model='cross-encoder/ms-marco-MiniLM-L6-v2',
                                 max_rerank_gap=c['gap'], order_by_vector=True, hybrid=True, rerank_mode=c.get('rerank', 'plain'))
            r._reranker = reranker; r._lexical_documents = store._lex
            chunks = r.retrieve(q['query'], k=c['k'], fetch_k=c['fetch_k'], min_papers=2 if multi else 1)
            if c.get('neighbours'):
                chunks = [replace(ch, text=neighbour_text(ch, by_id)) for ch in chunks]
            gold = q['relevant_papers']
            hits = [any(compact(e) in compact(ch.text) for ch in chunks if ch.paper_id in gold) for e in q['evidence']]
            rows.append(dict(id=q['id'], query=q['query'], retrieved_chunks=[asdict(ch) for ch in chunks],
                             context=r.format_context(chunks), source_list=r.format_sources(chunks),
                             relevant_papers=gold, retrieved_papers=list(dict.fromkeys(ch.paper_id for ch in chunks)), evidence_hits=hits))
        facts = [h for row in rows for h in row['evidence_hits']]
        snap = dict(snapshot_version=1, benchmark=str(path.relative_to(ROOT)), benchmark_sha256=json_digest(bench),
                    corpus_fingerprint='ca5f3c8351d1', variant=name, config=c, queries=rows,
                    summary=dict(evidence_hits=sum(facts), evidence_total=len(facts),
                                 context_words=round(sum(len(row['context'].split()) for row in rows) / len(rows))))
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f'{name}_{label}.json').write_text(json.dumps(snap, ensure_ascii=False, indent=2) + '\n')
        out[label] = snap
    return out


def main(args):
    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    from langchain_huggingface import HuggingFaceEmbeddings
    from sentence_transformers import CrossEncoder
    emb = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2', encode_kwargs={'normalize_embeddings': True})
    store = Chroma(collection_name='evaluation_mpnet_cosine', persist_directory=str(ROOT / '.evaluation_cache/ca5f3c8351d1'), embedding_function=emb)
    stored = store.get(include=['documents', 'metadatas'])
    store._lex = [Document(page_content=t, metadata=m or {}, id=i) for i, t, m in zip(stored['ids'], stored['documents'], stored['metadatas'])]
    by_id = dict(zip(stored['ids'], stored['documents']))
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L6-v2')
    benchmarks = {'dev': ROOT / 'evaluation/benchmark.json', 'holdout': ROOT / 'evaluation/benchmark_holdout.json'}
    results = {n: run_variant(n, VARIANTS[n], store, reranker, by_id, benchmarks, args.output_dir) for n in args.variants}
    base = results.get('base')
    summary = {}
    for n, res in results.items():
        s = {lab: res[lab]['summary'] for lab in res}
        if base:
            s['changed_contexts'] = sum(a['context'] != b['context'] for lab in res for a, b in zip(res[lab]['queries'], base[lab]['queries']))
            s['gained'] = [r['id'] for lab in res for r, b in zip(res[lab]['queries'], base[lab]['queries']) if sum(r['evidence_hits']) > sum(b['evidence_hits'])]
            s['lost'] = [r['id'] for lab in res for r, b in zip(res[lab]['queries'], base[lab]['queries']) if sum(r['evidence_hits']) < sum(b['evidence_hits'])]
        summary[n] = s
        print(n, json.dumps(s), flush=True)
    (args.output_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--variants', nargs='+', default=list(VARIANTS), choices=list(VARIANTS))
    p.add_argument('--output-dir', type=Path, default=ROOT / 'evaluation/results/opt_recall')
    main(p.parse_args())
