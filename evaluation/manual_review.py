"""Offline answer checks and a source-backed worksheet for manual review. No model calls."""
import argparse
import html
import json
import math
import re
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'notebooks'))
from answer_validation import CITATION, NUMBER, NONANSWER, answer_issues, numeric_key

def read_inputs(path, benchmark_path=None):
    data = json.loads(path.read_text())
    benchmark = (json.loads(benchmark_path.read_text()) if benchmark_path else data.get('benchmark'))
    if benchmark is None:
        benchmark = json.loads((ROOT / 'evaluation/benchmark.json').read_text())
    gold = {q['id']: q for q in benchmark['queries']}
    if len(gold) != len(benchmark['queries']):
        raise ValueError('Duplicate benchmark IDs')
    seen = set()
    for answer in data['answers']:
        query_id = answer['id']
        if query_id in seen or query_id not in gold or answer['query'] != gold[query_id]['query']:
            raise ValueError(f'Unknown, duplicate or mismatched answer question: {query_id}')
        seen.add(query_id)
        if not isinstance(answer['answer'], str) or not answer['answer'].strip():
            raise ValueError(f'Empty answer: {query_id}')
        for number, passage in enumerate(answer['passages'], 1):
            if passage.get('rank', number) != number or not isinstance(passage.get('text'), str):
                raise ValueError(f'Invalid passage numbering or text: {query_id}')
    if not seen:
        raise ValueError('No answers to review')
    return data, benchmark, gold


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.' + path.name, delete=False) as file:
            temporary = Path(file.name)
            file.write(text)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def answer_body(text):
    return re.split(r'(?im)^\s*(?:#{1,6}\s*)?(?:Evidence|Sources|Source list|References)\s*:', text, maxsplit=1)[0].strip()


def source_units(passages, max_chars=480):
    """Split into contiguous verbatim word spans; retain offsets for auditability."""
    units = []
    for pnum, passage in enumerate(passages, 1):
        text = passage['text']
        words = list(re.finditer(r'\S+', text))
        start = 0
        number = 1
        while start < len(words):
            end = start + 1
            while end < len(words) and words[end].end() - words[start].start() <= max_chars:
                end += 1
            lo, hi = words[start].start(), words[end - 1].end()
            units.append({'id': f'p{pnum}.{number}', 'passage_id': pnum,
                          'paper_id': passage.get('paper_id'), 'title': passage.get('title', ''),
                          'start': lo, 'end': hi, 'text': text[lo:hi]})
            number += 1
            start = end
    return units


def load_checklists(path, gold):
    data = json.loads(path.read_text())
    rows = data['queries']
    mapped = {q['id']: q for q in rows}
    if len(mapped) != len(rows) or set(mapped) != set(gold):
        raise ValueError('Checklist IDs must match all benchmark question IDs exactly')
    for key, q in mapped.items():
        if q['query'] != gold[key]['query'] or not q['required_checks']:
            raise ValueError(f'Checklist question mismatch or empty checklist: {key}')
        ids = [c['id'] for c in q['required_checks']]
        if len(set(ids)) != len(ids) or any(not c['label'] or not c['requirement'] for c in q['required_checks']):
            raise ValueError(f'Invalid checklist requirements: {key}')
    return data, mapped


def automatic_checks(answer, gold, checklist, max_words=120):
    body = answer_body(answer['answer'])
    passages = answer['passages']
    citations = {int(n) for n in CITATION.findall(body)}
    allowed = set(range(1, len(passages) + 1))
    refused = bool(NONANSWER.search(body))
    checks = []
    def add(name, status, message):
        checks.append({'name': name, 'status': status, 'message': message})
    if not gold['relevant_papers'] and refused and not citations:
        add('citations', 'not_applicable', 'No source reference is required for this refusal.')
    elif not citations:
        add('citations', 'attention', 'Add source references to the answer itself.')
    elif citations - allowed:
        add('citations', 'attention', 'Some source references point to passages that were not supplied.')
    else:
        add('citations', 'pass', 'Source references exist; whether they support each claim still needs review.')
    plain = CITATION.sub('', body)
    plain = re.sub(r'(?m)^\s*\d+\.[ \t]+', '', plain)
    numbers = {numeric_key(n) for n in NUMBER.findall(plain)}
    source_numbers = {numeric_key(n) for i in citations & allowed for n in NUMBER.findall(passages[i-1]['text'])}
    absent = sorted({n for n in NUMBER.findall(plain) if numeric_key(n) not in source_numbers})
    expected_missing = [n for n in checklist.get('expected_numbers', []) if numeric_key(n) not in numbers]
    if (numbers or checklist.get('expected_numbers')) and not (refused and not gold['relevant_papers']):
        add('numbers', 'attention' if absent or expected_missing else 'pass',
            ('Check figures against their sources.' if absent else 'Expected figures were not found as digits.' if expected_missing else
             'Figures match available source values; their meaning and attribution still need review.'))
    word_count = len(plain.split())
    add('length', 'attention' if word_count > max_words else 'pass',
        f'Answer is {word_count} words; the review target is at most {max_words}.')
    # Preserve existing quote checks as diagnostic data, not an extra requirement for business prose.
    mechanical = answer_issues(answer['answer'], [SimpleNamespace(**p) for p in passages])
    bad_quotes = [m for m in mechanical if 'not verbatim' in m]
    if bad_quotes:
        add('quotes', 'attention', 'An answer quotation differs from its cited source.')
    retrieved = list(dict.fromkeys(p.get('paper_id') for p in passages))
    expected = set(gold['relevant_papers'])
    hits = [p for p in retrieved if p in expected]
    if expected:
        recall = len(hits) / len(expected)
        mrr = next((1/(i+1) for i,p in enumerate(retrieved) if p in expected), 0)
        dcg = sum(1/math.log2(i+2) for i,p in enumerate(retrieved) if p in expected)
        ideal = sum(1/math.log2(i+2) for i in range(min(len(expected), len(retrieved))))
        retrieval = {'expected_papers_found': len(hits), 'expected_papers': len(expected),
                     'paper_recall': recall, 'paper_mrr': mrr, 'paper_ndcg': dcg/ideal if ideal else 0,
                     'unique_paper_order': retrieved}
    else:
        retrieval = {'expected_papers_found': 0, 'expected_papers': 0, 'paper_recall': None,
                     'paper_mrr': None, 'paper_ndcg': None, 'unique_paper_order': retrieved}
    return {'checks': checks, 'retrieval': retrieval, 'word_count': word_count,
            'numbers_absent_from_cited_sources': absent, 'expected_numbers_not_found': expected_missing,
            'legacy_mechanical_issues': mechanical}


def safe(text):
    return html.escape(str(text), quote=False).replace('|', '\\|').replace('\n', ' ')


def preview(unit, limit=240, focus=''):
    text = ' '.join(unit['text'].split())
    if len(text) <= limit:
        return text
    words = list(re.finditer(r'\S+', text))
    wanted = {w.lower() for w in re.findall(r'[A-Za-z]{4,}', focus)} - {
        'that', 'with', 'from', 'this', 'answer', 'source', 'states', 'names', 'reports'}
    candidates = []
    for word in words:
        start = word.start()
        budget = limit - (1 if start else 0) - 1
        end = min(start + budget, len(text))
        if end < len(text):
            end = text.rfind(' ', start, end)
        if end <= start:
            continue
        span = text[start:end]
        score = len(set(re.findall(r'[a-z]{4,}', span.lower())) & wanted)
        candidates.append((score, -start, ('…' if start else '') + span + ('…' if end < len(text) else '')))
    return max(candidates)[2] if candidates else text[:limit-1]+'…'



def render_report(report):
    lines = ['# Answer review worksheet', '',
             f"{len(report['answers'])} answers · automatic checks complete · content awaits manual review.", '',
             'Checklists are assistant-prepared and pending human approval. Automatic checks do not establish factual accuracy.', '']
    for row in report['answers']:
        checks = row['automatic']['checks']
        issues = [c['message'] for c in checks if c['status']=='attention']
        lines += [f"## {row['id']} — Manual review needed", '', safe(row['query']), '',
                  '**Answer:** ' + safe(row['answer']), '',
                  '**Automatic findings:** ' + (safe(' '.join(issues)) if issues else
                    'No mechanical issues flagged. This does not mean the answer is correct.'), '',
                  '**Check these points:**', '']
        for c in row['checklist']['required_checks']:
            lines += ['- [ ] ' + safe(c['requirement'])]
        metrics = row['automatic']['retrieval']
        if metrics['expected_papers']:
            lines += ['', f"**Sources found:** {metrics['expected_papers_found']} of {metrics['expected_papers']} expected papers. "
                      'This measures paper retrieval, not whether the answer uses the right evidence.', '']
        # Heuristic previews are navigation aids, never evidence of correctness.
        focus = row['query']+' '+' '.join(c['requirement'] for c in row['checklist']['required_checks'])
        wanted = set(re.findall(r'[a-z]{4,}',focus.lower()))
        units = sorted(row['source_units'],key=lambda u: -len(set(re.findall(r'[a-z]{4,}',u['text'].lower())) & wanted))
        selected=[]
        for u in units:
            if u['passage_id'] not in {x['passage_id'] for x in selected}:
                selected.append(u)
            if len(selected)==2:break
        if selected:
            lines += ['**Source previews** — copied from saved passages, at most 240 characters each. '
                      'Selected by word overlap for navigation; inspect full passages to verify claims.', '']
        for u in selected:
            lines += [f"**Source {u['passage_id']}**", '', '> '+safe(preview(u,focus=focus)), '']
        lines += ['<details><summary>Full sources and automatic checks</summary>', '']
        for number,p in enumerate(row['passages'],1):
            lines += [f"**Source {number} — {safe(p.get('title',''))}**", '', safe(p['text']), '']
        lines += [safe(c['message'])+'\n' for c in checks]
        lines += ['', '</details>', '']
    return '\n'.join(lines)


def main(args):
    if args.max_words < 1:
        raise ValueError('--max-words must be positive')
    data, benchmark, gold = read_inputs(args.answers, args.benchmark)
    catalog, checklists = load_checklists(args.checklists,gold)
    protected = {args.answers.resolve(), args.checklists.resolve(),
                 (args.benchmark or ROOT/'evaluation/benchmark.json').resolve()}
    if args.output.suffix != '.json' or args.output.resolve() in protected:
        raise ValueError('Output must be a .json file separate from inputs')
    report = {'schema_version':1,'review_type':'automatic_checks_and_manual_review',
              'source_answers':str(args.answers.resolve()),'checklist_provenance':catalog['provenance'],
              'answers':[]}
    for answer in data['answers']:
        key=answer['id']
        report['answers'].append({'id':key,'query':answer['query'],'answer':answer_body(answer['answer']),
            'content_review_status':'pending_manual_review','checklist':checklists[key],
            'automatic':automatic_checks(answer,gold[key],checklists[key],args.max_words),
            'passages':answer['passages'],'source_units':source_units(answer['passages'])})
    atomic_write(args.output,json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    atomic_write(args.output.with_suffix('.md'),render_report(report))
    print(f"Checked {len(report['answers'])} answers without model calls.\nReport: {args.output.with_suffix('.md')}")
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--answers',type=Path,required=True)
    parser.add_argument('--benchmark',type=Path)
    parser.add_argument('--checklists',type=Path,default=ROOT/'evaluation/answer_checklists.json')
    parser.add_argument('--output',type=Path,default=ROOT/'evaluation/results/manual_review.json')
    parser.add_argument('--max-words',type=int,default=120)
    args=parser.parse_args()
    try:
        main(args)
    except (OSError,ValueError,KeyError) as exc:
        parser.exit(1,f'Error: {exc}\n')
