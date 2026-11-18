"""Assemble this paired experiment, verifying identical inputs before reuse."""
import json,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'evaluation'))
from run_answers import json_digest,load_snapshot,experiment_context
r=ROOT/'evaluation/results'
b=json.loads((r/'opt_qwen_coverage_full.json').read_text())
h=json.loads((r/'opt_qwen_hybrid_changed.json').read_text())
s=json.loads((r/'opt_retrieval_sweep/hybrid.json').read_text())
benchmark=json.loads((ROOT/s['benchmark']).read_text()); snapshots=load_snapshot(s,benchmark)
for k,v in b['run_config'].items():
 if k not in {'ids','retrieval_sha256'}:assert h['run_config'][k]==v,k
assert len(b['answers'])==25
base={a['id']:a for a in b['answers']};changed={a['id']:a for a in h['answers']}
result=copy.deepcopy(h);result['answers']=[];result['run_config']['ids']=None
result['run_fingerprint']=json_digest(result['run_config']);result['assembly_note']='Paired comparison: newly generated changed contexts plus reused outputs for identical generation inputs; per-answer provenance recorded. Not an independent second full generation run.'
for q in benchmark['queries']:
 key=q['id'];f=snapshots[key];context=experiment_context(f,True,False)
 source='opt_qwen_hybrid_changed.json' if key in changed else 'opt_qwen_coverage_full.json'
 a=copy.deepcopy(changed[key] if key in changed else base[key])
 assert a['query']==q['query'] and a['generation_context']==context
 assert a['source_list']==f['source_list']
 # Scores need not be byte-identical; all evidence text/IDs/metadata must match.
 strip=lambda ps:[{k:v for k,v in p.items() if k!='score'} for p in ps]
 assert strip(a['passages'])==strip(f['retrieved_chunks'])
 a['passages']=f['retrieved_chunks'];a['provenance']={'source_file':source,'source_sha256':json_digest(h if key in changed else b),'reused_identical_generation_inputs':key not in changed}
 result['answers'].append(a)
(r/'opt_qwen_hybrid_full.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Assembled',len(result['answers']),'answers;',len(changed),'new generations')
