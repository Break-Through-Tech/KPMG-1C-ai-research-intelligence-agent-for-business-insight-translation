"""Apply deterministic answer clean-up to a saved run; writes a new file, never edits the input."""
import argparse,copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'notebooks'))
from answer_postprocess import postprocess,render
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--threshold',type=float,default=0.85);p.add_argument('--no-titles',action='store_true');p.add_argument('--no-dedupe',action='store_true')
a=p.parse_args();assert a.output.resolve()!=a.input.resolve()
run=json.loads(a.input.read_text());out=copy.deepcopy(run);out['postprocess']=dict(threshold=a.threshold,titles=not a.no_titles,dedupe=not a.no_dedupe,source=str(a.input))
for row in out['answers']:
    s=row.get('structured') or {}
    if not s.get('claims'):row['postprocess_log']=[];continue
    claims,log=postprocess(s,row['passages'],a.threshold,not a.no_titles,not a.no_dedupe)
    row['answer_before_postprocess']=row['answer'];row['answer']=render(claims,s.get('unanswered',''));row['postprocess_log']=log
    if log:print(row['id'],f"{len(s['claims'])}->{len(claims)} claims",sum(l.startswith('title') for l in log),'title fixes')
a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
