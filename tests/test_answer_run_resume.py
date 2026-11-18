"""Prevent an interrupted evaluation from mixing answers from different runs."""

import hashlib
import json
from pathlib import Path

import pytest

from evaluation.run_answers import completed_answers

ROOT = Path(__file__).resolve().parents[1]


def test_resume_requires_same_model_prompt_retrieval_and_question(tmp_path):
    output = tmp_path / "answers.json"
    retrieval = ROOT / "evaluation/results/retrieval_after_parser_integrated.json"
    benchmark = {"queries": [{"id": "q1", "query": "What happened?"}]}
    row = {"id": "q1", "query": "What happened?", "answer": "Answer [1]."}
    output.write_text(json.dumps({
        "model": "qwen2.5:7b", "model_digest": "digest-1",
        "notebook_prompt_sha256": hashlib.sha256(b"prompt-v1").hexdigest(),
        "retrieval_result": "evaluation/results/retrieval_after_parser_integrated.json",
        "answers": [row],
    }))
    assert completed_answers(output, "qwen2.5:7b", "digest-1", "prompt-v1",
                             retrieval, benchmark) == {"q1": row}
    with pytest.raises(ValueError, match="different settings"):
        completed_answers(output, "qwen2.5:7b", "digest-1", "prompt-v2",
                          retrieval, benchmark)
    with pytest.raises(ValueError, match="mismatched questions"):
        completed_answers(output, "qwen2.5:7b", "digest-1", "prompt-v1",
                          retrieval, {"queries": [{"id": "q1", "query": "What changed?"}]})
