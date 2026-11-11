import copy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'evaluation'))
from assemble_paired_run import verified_policy_additions
from run_answers import json_digest
import hashlib
ROOT=Path(__file__).resolve().parents[1]

def test_unused_policy_compatibility_requires_exact_generation_code_hashes():
    source=(ROOT/'notebooks/structured_answers.py').read_text()
    start=source.index("\n\nPOLICIES['focused']");end=source.index('\n\ndef schema(',start)
    suffix=(ROOT/'evaluation/optimize_answers.py').read_bytes()+(ROOT/'notebooks/retrieval.py').read_bytes()
    old={'policy':'coverage','pipeline_sha256':hashlib.sha256((source[:start]+source[end:]).encode()+suffix).hexdigest()}
    new={'policy':'coverage','pipeline_sha256':hashlib.sha256(source.encode()+suffix).hexdigest()}
    assert verified_policy_additions(old,new)
    broken=dict(new,pipeline_sha256='changed-generator')
    assert not verified_policy_additions(old,broken)
    assert not verified_policy_additions(old,dict(new,policy='focused'))
