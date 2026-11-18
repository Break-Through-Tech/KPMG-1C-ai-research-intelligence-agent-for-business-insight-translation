"""Reuse answers only for identical generation inputs in paired experiments."""
import argparse,copy,json,hashlib,ast
from pathlib import Path
from run_answers import load_snapshot,experiment_context,json_digest
ROOT=Path(__file__).resolve().parents[1]

def verified_policy_additions(base_config,new_config):
    if base_config['policy'] != 'coverage' or new_config['policy'] != 'coverage':return False
    source=(ROOT/'notebooks/structured_answers.py').read_text()
    start=source.find("\n\nPOLICIES['focused']");end=source.find('\n\ndef schema(',start)
    if start < 0 or end < start:return False
    for node in ast.parse(source[start:end]).body:
        if not isinstance(node,ast.Assign) or len(node.targets)!=1:return False
        target=node.targets[0]
        if not isinstance(target,ast.Subscript) or not isinstance(target.value,ast.Name) or target.value.id!='POLICIES' or not isinstance(target.slice,ast.Constant) or target.slice.value not in {'focused','focused_v2'}:return False
    legacy=source[:start]+source[end:]
    suffix=(ROOT/'evaluation/optimize_answers.py').read_bytes()+(ROOT/'notebooks/retrieval.py').read_bytes()
    return (hashlib.sha256(legacy.encode()+suffix).hexdigest()==base_config['pipeline_sha256'] and hashlib.sha256(source.encode()+suffix).hexdigest()==new_config['pipeline_sha256'])


def assemble(baseline_path,changed_path,retrieval_path,output_path):
    if output_path.resolve() in {baseline_path.resolve(),changed_path.resolve(),retrieval_path.resolve()}:raise ValueError('Output must not overwrite inputs')
    base=json.loads(baseline_path.read_text());changed=json.loads(changed_path.read_text());retrieval=json.loads(retrieval_path.read_text())
    benchmark=json.loads((ROOT/retrieval['benchmark']).read_text());snapshots=load_snapshot(retrieval,benchmark)
    policy_only_change=verified_policy_additions(base['run_config'],changed['run_config'])
    for key,value in base['run_config'].items():
        if key=='pipeline_sha256' and policy_only_change:continue
        if key not in {'ids','retrieval_sha256'} and changed['run_config'][key]!=value:raise ValueError('Different generation configuration: '+key)
    by_id={a['id']:a for a in base['answers']};new={a['id']:a for a in changed['answers']}
    result=copy.deepcopy(changed);result['answers']=[];result['run_config']['ids']=None;result['run_fingerprint']=json_digest(result['run_config'])
    strip=lambda passages:[{k:v for k,v in p.items() if k!='score'} for p in passages]
    for q in benchmark['queries']:
        key=q['id'];f=snapshots[key];a=copy.deepcopy(new.get(key,by_id.get(key)))
        if not a or a['query']!=q['query'] or a['generation_context']!=experiment_context(f,True,False) or a['source_list']!=f['source_list'] or strip(a['passages'])!=strip(f['retrieved_chunks']):raise ValueError('Different generation inputs: '+key)
        a['passages']=f['retrieved_chunks'];a['provenance']={'source_file':str(changed_path if key in new else baseline_path),'source_sha256':json_digest(changed if key in new else base),'reused_identical_generation_inputs':key not in new};result['answers'].append(a)
    result['verified_unused_policy_additions']=policy_only_change
    result['assembly_note']='Paired comparison; unchanged inputs reuse baseline outputs, with provenance. Not an independent repeat run.'
    output_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Assembled',len(result['answers']),'answers;',len(new),'fresh generations')
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('baseline','changed','retrieval','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();assemble(a.baseline,a.changed,a.retrieval,a.output)
