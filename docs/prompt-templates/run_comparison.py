"""Provider-neutral runner. No network calls occur without an explicit adapter."""
import argparse
import hashlib
import importlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter', help='Importable module:function accepting one prompt string and returning one answer string')
    parser.add_argument('--model', required=True, help='Exact model identifier; use not_called for a dry run')
    parser.add_argument('--settings', default='{}', help='JSON documenting settings actually enforced by the adapter')
    parser.add_argument('--split', choices=['development', 'held_out', 'all'], default='development')
    parser.add_argument('--dry-run', action='store_true', help='Render inputs without generating answers')
    parser.add_argument('--output', required=True, help='New output path; existing files are never overwritten')
    args = parser.parse_args()
    settings = json.loads(args.settings)
    if not isinstance(settings, dict):
        parser.error('--settings must be a JSON object')
    if not args.dry_run and not args.adapter:
        parser.error('--adapter is required unless --dry-run is set')
    # Reserve the file before invoking any model, avoiding accidental repeat charges.
    with Path(args.output).open('x', encoding='utf-8') as target:
        generate = None
        if not args.dry_run:
            module, function = args.adapter.split(':', 1)
            generate = getattr(importlib.import_module(module), function)
        cases = json.loads((ROOT / 'test_cases.json').read_text(encoding='utf-8'))
        records = []
        for case in cases:
            if args.split != 'all' and case['split'] != args.split:
                continue
            for label in ['A', 'B']:
                template = (ROOT / f'template_{label.lower()}.txt').read_text(encoding='utf-8')
                prompt = template.format(question=case['question'], business_context=case['business_context'], context=case['context'])
                row = dict(case_id=case['id'], template=label, model=args.model, settings=settings, timestamp=datetime.now(timezone.utc).isoformat(), template_sha256=hashlib.sha256(template.encode()).hexdigest(), prompt=prompt, answer=None, status='dry_run')
                if generate:
                    try:
                        answer = generate(prompt)
                        if not isinstance(answer, str) or not answer.strip():
                            raise ValueError('Adapter must return a nonempty answer string')
                        row.update(answer=answer, status='generated')
                    except Exception as error:
                        # Avoid logging provider error bodies that might contain secrets.
                        row.update(status='error', error_type=type(error).__name__)
                records.append(row)
                target.seek(0)
                json.dump(records, target, indent=2)
                target.truncate()
                target.flush()
    print(f'Saved {len(records)} records. Dry run: {args.dry_run}.')

if __name__ == '__main__':
    main()
