"""Generate optional search rewrites, selected by question text only."""
import argparse,json,sys,time,hashlib,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'notebooks'))
from structured_answers import request
from experimental_retrieval import should_rewrite
from run_answers import json_digest
PROMPT='''Rewrite this question as a concise academic search query. Preserve every requested part, named entity, comparison and constraint. Use descriptive research terminology only when it preserves the original meaning. Do not answer the question. Do not invent facts, numbers, paper names, mechanisms or conclusions. Return only the search query in the query field.\n\nQuestion: '''
OPTIONS={'temperature':0,'seed':42,'num_ctx':4096,'num_predict':160}

def main(args):
    benchmark=json.loads(args.benchmark.read_text())
    with urllib.request.urlopen(args.host+'/api/tags',timeout=30) as response:models=json.load(response)['models']
    model_digest=next(m['digest'] for m in models if m['name']==args.model)
    config={'model':args.model,'model_digest':model_digest,'prompt':PROMPT,'options':OPTIONS,'benchmark_sha256':json_digest(benchmark),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()+(ROOT/'evaluation/experimental_retrieval.py').read_bytes()).hexdigest()}
    result={'config':config,'rewrites':[]}
    if args.output.exists():
        result=json.loads(args.output.read_text());assert result['config']==config,'Changed configuration: choose new output'
    completed={r['id'] for r in result['rewrites']}
    for q in benchmark['queries']:
        if not should_rewrite(q['query']) or q['id'] in completed:continue
        start=time.monotonic();response=request(PROMPT+q['query'],args.model,args.host,{'type':'object','properties':{'query':{'type':'string'}},'required':['query'],'additionalProperties':False},OPTIONS)
        payload=json.loads(response['response']);rewrite=payload['query'].strip();assert rewrite
        result['rewrites'].append(dict(id=q['id'],query=q['query'],rewrite=rewrite,seconds=round(time.monotonic()-start,1),raw=response['response']))
        args.output.parent.mkdir(exist_ok=True,parents=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(q['id'],rewrite,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--benchmark',type=Path,default=ROOT/'evaluation/benchmark.json');p.add_argument('--output',type=Path,required=True);p.add_argument('--model',default='qwen3.5:9b');p.add_argument('--host',default='http://127.0.0.1:11434');main(p.parse_args())
