"""Standard-library checks for evidence gating and comparison reproducibility."""
import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('comparison', ROOT / 'run_comparison.py')
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)
CASES = json.loads((ROOT / 'test_cases.json').read_text(encoding='utf-8'))


def fixture():
    # Synthetic input only; not evidence for any of Allison's research questions.
    return dict(research_topic='Synthetic test topic', context='[1] Synthetic test finding.',
                sources=[dict(number=1, title='Synthetic fixture', paper_id='fixture-only')],
                evidence_id='synthetic-unit-test', prior_answer='Synthetic prior answer. [1]')


class RunnerChecks(unittest.TestCase):
    def cli(self, output, *args):
        return subprocess.run([sys.executable, '-B', str(ROOT / 'run_comparison.py'),
                               '--model', 'test_no_provider', '--output', str(output), *args],
                              capture_output=True, text=True)

    def test_primary_matrix_and_blank_scores(self):
        self.assertEqual(len(CASES), 16)
        self.assertEqual(len({c['id'] for c in CASES}), 16)
        for number in [29, 30, 31, 32, 34, 40, 41, 42]:
            self.assertEqual({c['variant'] for c in CASES if c['allison_prompt'] == number},
                             {'original', 'paraphrase'})
        with (ROOT / 'evaluation_results.csv').open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 32)
        self.assertTrue(all(r['status'] == 'awaiting_evidence' and r['accuracy'] == '' for r in rows))

    def test_original_and_paraphrase_share_evidence(self):
        first = next(c for c in CASES if c['id'] == 'A29_original')
        second = next(c for c in CASES if c['id'] == 'A29_paraphrase')
        evidence = {'A29': fixture()}
        fields1, errors1 = comparison.prepare(first, 'business', evidence)
        fields2, errors2 = comparison.prepare(second, 'business', evidence)
        self.assertEqual(errors1 + errors2, [])
        self.assertEqual(comparison.fingerprint(fields1), comparison.fingerprint(fields2))

    def test_followup_requires_prior_answer(self):
        case = next(c for c in CASES if c['id'] == 'A41_original')
        item = fixture()
        item['prior_answer'] = ''
        _, errors = comparison.prepare(case, 'business', {'A31': item})
        self.assertIn('missing_prior_answer', errors)
        item['prior_answer'] = 'Checked prior answer. [1]'
        _, errors = comparison.prepare(case, 'business', {'A31': item})
        self.assertEqual(errors, [])

    def test_bad_source_numbers_block_generation(self):
        item = fixture()
        item['sources'][0]['number'] = 2
        _, errors = comparison.prepare(CASES[0], 'business', {'A29': item})
        self.assertIn('source_passage_number_mismatch', errors)

    def test_missing_evidence_never_imports_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'blocked.json'
            result = self.cli(output, '--adapter', 'nonexistent_adapter:generate', '--split', 'all')
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = json.loads(output.read_text())
            self.assertEqual(len(rows), 32)
            self.assertTrue(all(r['status'] == 'blocked_missing_inputs' and r['answer'] is None for r in rows))

    def test_dry_run_order_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'dry.json'
            result = self.cli(output, '--dry-run', '--split', 'all')
            self.assertEqual(result.returncode, 0, result.stderr)
            original = output.read_bytes()
            rows = json.loads(original)
            self.assertEqual(len(rows), 32)
            self.assertTrue(all(r['variant'] == 'original' for r in rows[:16]))
            self.assertTrue(all(r['status'] == 'dry_run' and r['answer'] is None for r in rows))
            repeat = self.cli(output, '--dry-run', '--split', 'all')
            self.assertNotEqual(repeat.returncode, 0)
            self.assertEqual(output.read_bytes(), original)

    def test_adapter_path_with_synthetic_data_and_saved_history(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            # The runner can import this fixture from its process working directory.
            (directory / 'test_adapter.py').write_text('def generate(prompt):\n    return "SYNTHETIC ADAPTER CHECK ONLY"\n')
            evidence_path = directory / 'evidence.json'
            evidence_path.write_text(json.dumps({'A31': fixture()}))
            output = directory / 'responses.json'
            # Import via module path added through a tiny wrapper, without altering environment secrets.
            wrapper = directory / 'invoke.py'
            wrapper.write_text('import runpy\nrunpy.run_path(' + repr(str(ROOT / 'run_comparison.py')) + ', run_name="__main__")\n')
            result = subprocess.run([sys.executable, '-B', str(wrapper), '--adapter', 'test_adapter:generate',
                                     '--model', 'synthetic_adapter_only', '--evidence', str(evidence_path),
                                     '--case-ids', 'A41_original', 'A41_paraphrase', '--output', str(output)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = json.loads(output.read_text())
            self.assertEqual(len(rows), 4)
            self.assertTrue(all(r['status'] == 'generated' for r in rows))
            self.assertEqual(len({r['evidence_sha256'] for r in rows}), 1)
            self.assertTrue(all('Synthetic prior answer.' in r['prompt'] for r in rows))
            self.assertTrue(all(r['source_list'][0]['paper_id'] == 'fixture-only' for r in rows))


if __name__ == '__main__':
    unittest.main()
