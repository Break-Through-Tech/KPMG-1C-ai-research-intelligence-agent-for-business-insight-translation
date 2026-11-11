"""Reproducible structured-answer experiment runner; no rubric/labels in prompts."""
import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from dataclasses import asdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'notebooks'))
import structured_answers as engine
from retrieval import RetrievedChunk
from run_answers import load_snapshot, json_digest, select_queries, experiment_context


def main(args):
    retrieval = json.loads(args.retrieval.read_text())
    benchmark_path = ROOT / retrieval['benchmark']
    if args.output.resolve() in {args.retrieval.resolve(), benchmark_path.resolve()}:
        raise ValueError('Output must not overwrite inputs.')
    benchmark = json.loads(benchmark_path.read_text())
    snapshots = load_snapshot(retrieval, benchmark)
    with urllib.request.urlopen(args.host.rstrip('/')+'/api/tags', timeout=30) as response:
        models = json.load(response)['models']
    digest = next(m['digest'] for m in models if m['name'] in {args.model, args.model+':latest'})
    config = {'model': args.model, 'model_digest': digest, 'policy': args.policy,
              'repair': args.repair, 'evidence_mode': args.evidence_mode, 'selection_order': args.selection_order,
              'options': engine.OPTIONS, 'think': False if args.model.startswith(('qwen3','gpt-oss')) else None, 'policy_text': engine.POLICIES[args.policy],
              'retrieval_sha256': json_digest(retrieval), 'benchmark_sha256': json_digest(benchmark),
              'ids': args.ids, 'pipeline_sha256': hashlib.sha256(
                  Path(engine.__file__).read_bytes()+Path(__file__).read_bytes()+(ROOT/'notebooks/retrieval.py').read_bytes()).hexdigest()}
    result = {'schema_version': 1, 'run_config': config, 'run_fingerprint': json_digest(config),
              'benchmark': benchmark, 'answers': []}
    if args.output.exists():
        result = json.loads(args.output.read_text())
        if result['run_config'] != config or result['run_fingerprint'] != json_digest(config):
            raise ValueError('Run configuration changed; use a new output.')
        for row in result['answers']:
            assert row['passages'] == snapshots[row['id']]['retrieved_chunks']
    completed = {r['id'] for r in result['answers']}
    for item in select_queries(benchmark, args.ids):
        if item['id'] in completed:
            continue
        frozen = snapshots[item['id']]
        chunks = [RetrievedChunk(**c) for c in frozen['retrieved_chunks']]
        context = experiment_context(frozen, True, args.selection_order)
        generated = engine.generate(item['query'], chunks, args.model, args.host,
                                    args.policy, args.repair, context, args.evidence_mode)
        row = dict(id=item['id'], query=item['query'], passages=[asdict(c) for c in chunks],
                   source_list=frozen['source_list'], **generated)
        row['answer'] = row['draft'] or 'Evaluation unavailable: structured generation failed validation.'
        row['claim_support_status'] = 'not_evaluated'
        result['answers'].append(row)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temp = args.output.with_suffix('.tmp')
        temp.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        temp.replace(args.output)
        print(f"{item['id']}: {row['seconds']}s; {len(row['calls'])} call(s); error={row['generation_error']}; warnings={len(row['local_warnings'])}", flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--retrieval', type=Path, default=ROOT/'evaluation/results/retrieval_ordered_frozen.json')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--model', default='llama3.1:8b')
    p.add_argument('--host', default='http://127.0.0.1:11434')
    p.add_argument('--policy', choices=list(engine.POLICIES), default='coverage')
    p.add_argument('--repair', action='store_true')
    p.add_argument('--evidence-mode', choices=['quote','citation'], default='quote')
    p.add_argument('--selection-order', action='store_true')
    p.add_argument('--ids', nargs='+')
    main(p.parse_args())
