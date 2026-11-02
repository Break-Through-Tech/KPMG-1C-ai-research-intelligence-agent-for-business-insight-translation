"""Compare templates with fixed evidence; missing business inputs block model calls."""
import argparse
import hashlib
import importlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def prepare(case, suite, evidence):
    """Prepare render fields and blockers without invoking a model."""
    if suite == 'stress':
        return dict(context=case['context'], business_context=case['business_context'], sources=[], prior_answer=''), []
    item = evidence.get(case['evidence_key'], {})
    if not isinstance(item, dict):
        raise ValueError('Each evidence entry must be an object')
    context = item.get('context', '')
    sources = item.get('sources', [])
    topic = item.get('research_topic', '')
    prior = item.get('prior_answer', '') if case.get('requires_prior_answer') else ''
    if not all(isinstance(v, str) for v in [context, topic, prior, item.get('evidence_id', '')]):
        raise ValueError('Evidence context, topic, history, and identifier must be strings')
    blockers = []
    if not context.strip():
        blockers.append('missing_research_passages')
    if not topic.strip():
        blockers.append('missing_research_topic')
    if not item.get('evidence_id', '').strip():
        blockers.append('missing_evidence_id')
    if not isinstance(sources, list) or not sources:
        blockers.append('missing_source_records')
        sources = []
    else:
        numbers = [s.get('number') for s in sources if isinstance(s, dict)]
        if len(numbers) != len(sources) or any(type(n) is not int or n < 1 for n in numbers):
            blockers.append('invalid_source_numbers')
        elif len(set(numbers)) != len(numbers):
            blockers.append('duplicate_source_numbers')
        elif {int(n) for n in re.findall(r'\[(\d+)\]', context)} != set(numbers):
            blockers.append('source_passage_number_mismatch')
        if any(not isinstance(s, dict) or not s.get('title') or not (s.get('paper_id') or s.get('source_url')) for s in sources):
            blockers.append('unidentifiable_source_record')
    if case.get('requires_prior_answer') and not prior.strip():
        blockers.append('missing_prior_answer')
    fields = dict(context=context, business_context='Professional-services product owner with no AI background preparing a business discussion. Research topic or technique: ' + topic, sources=sources, prior_answer=prior, evidence_id=item.get('evidence_id', ''))
    return fields, blockers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter', help='Importable module:function accepting a prompt and returning text')
    parser.add_argument('--model', required=True, help='Exact model identifier; use not_called for dry runs')
    parser.add_argument('--settings', default='{}', help='JSON settings actually enforced by the adapter')
    parser.add_argument('--suite', choices=['business', 'stress'], default='business')
    parser.add_argument('--evidence', type=Path, help='JSON object keyed by A29, A30, A31, A32, A34, A40')
    parser.add_argument('--split', choices=['development', 'held_out', 'all'], default='development')
    parser.add_argument('--variant', choices=['original', 'paraphrase', 'all'], default='all')
    parser.add_argument('--case-ids', nargs='+', help='Restrict to exact case IDs')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--output', type=Path, required=True, help='New path, never overwritten')
    args = parser.parse_args()
    settings = json.loads(args.settings)
    if not isinstance(settings, dict):
        parser.error('--settings must be a JSON object')
    if not args.dry_run and not args.adapter:
        parser.error('--adapter is required unless --dry-run is set')
    evidence = json.loads(args.evidence.read_text(encoding='utf-8-sig')) if args.evidence else {}
    if not isinstance(evidence, dict):
        parser.error('--evidence must contain a JSON object')
    filename = 'test_cases.json' if args.suite == 'business' else 'stress_cases.json'
    all_cases = json.loads((ROOT / filename).read_text(encoding='utf-8'))
    if args.case_ids and set(args.case_ids) - {c['id'] for c in all_cases}:
        parser.error('Unknown case ID')
    cases = [c for c in all_cases if (args.split == 'all' or c['split'] == args.split)
             and (args.variant == 'all' or c.get('variant') == args.variant)
             and (not args.case_ids or c['id'] in args.case_ids)]
    cases.sort(key=lambda c: c.get('variant') == 'paraphrase')
    if not cases:
        parser.error('No cases match the selection')
    prepared = [(case, *prepare(case, args.suite, evidence)) for case in cases]
    templates = {label: (ROOT / f'template_{label.lower()}.txt').read_text(encoding='utf-8') for label in ['A', 'B']}
    records = []
    with args.output.open('x', encoding='utf-8') as target:
        generate = None
        if not args.dry_run and any(not blockers for _, _, blockers in prepared):
            module, function = args.adapter.split(':', 1)
            generate = getattr(importlib.import_module(module), function)
        for case, fields, blockers in prepared:
            for label, template in templates.items():
                context = fields['context']
                if fields['sources']:
                    context += '\n\nSource metadata (not additional findings):\n' + json.dumps(fields['sources'], ensure_ascii=False)
                prompt = template.format(question=case['question'], business_context=fields['business_context'], context=context)
                if fields['prior_answer']:
                    prompt += '\n\nPrior answer for the follow-up (conversation history, not independent evidence):\n' + fields['prior_answer']
                row = dict(case_id=case['id'], suite=args.suite, allison_prompt=case.get('allison_prompt'), variant=case.get('variant'), model=args.model, settings=settings, template=label, template_sha256=hashlib.sha256(template.encode()).hexdigest(), evidence_sha256=fingerprint(fields), evidence_id=fields.get('evidence_id'), sources=fields['sources'], timestamp=datetime.now(timezone.utc).isoformat(), prompt=prompt, answer=None, blockers=blockers, status='dry_run' if args.dry_run else 'blocked_missing_inputs')
                if not args.dry_run and not blockers:
                    try:
                        answer = generate(prompt)
                        if not isinstance(answer, str) or not answer.strip():
                            raise ValueError('Adapter must return nonempty text')
                        row.update(answer=answer, source_list=fields['sources'], status='generated')
                    except Exception as error:
                        row.update(status='error', error_type=type(error).__name__)
                records.append(row)
                target.seek(0)
                json.dump(records, target, indent=2)
                target.truncate()
                target.flush()
    counts = {status: sum(r['status'] == status for r in records) for status in {r['status'] for r in records}}
    print(f'Saved {len(records)} records: {counts}')


if __name__ == '__main__':
    main()
