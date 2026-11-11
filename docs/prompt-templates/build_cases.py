"""Create a fresh review sheet from primary cases without overwriting results."""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New CSV path')
    args = parser.parse_args()
    cases = json.loads((ROOT / 'test_cases.json').read_text(encoding='utf-8'))
    fields = ['case_id', 'allison_prompt', 'variant', 'template', 'status', 'model', 'run_date', 'reviewer', 'retrieval_relevance', 'coverage', 'accuracy', 'citation_support', 'citation_metadata', 'clarity', 'business_usefulness', 'uncertainty', 'format_compliance', 'robustness', 'critical_failure', 'notes']
    with args.output.open('x', newline='', encoding='utf-8') as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            for template in ['A', 'B']:
                writer.writerow(dict(case_id=case['id'], allison_prompt=case['allison_prompt'], variant=case['variant'], template=template, status='awaiting_evidence'))
    print(f'Created {len(cases) * 2} unscored rows.')


if __name__ == '__main__':
    main()
