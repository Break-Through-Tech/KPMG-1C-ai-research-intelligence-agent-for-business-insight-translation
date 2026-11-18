"""Prevent an interrupted evaluation from mixing answers from different runs."""

import hashlib
import json

import pytest

from evaluation.run_answers import json_digest, load_completed


def config(prompt):
    return {"model": "qwen2.5:7b", "model_digest": "digest-1",
            "notebook_prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}


def test_resume_requires_same_model_prompt_retrieval_and_question(tmp_path):
    output = tmp_path / "answers.json"
    passages = [{"rank": 1, "text": "Passage."}]
    snapshots = {"q1": {"query": "What happened?", "retrieved_chunks": passages,
                        "source_list": "[1] Paper"}}
    row = {"id": "q1", "query": "What happened?", "answer": "Answer [1].",
           "passages": passages, "source_list": "[1] Paper"}
    saved = config("prompt-v1")
    output.write_text(json.dumps({"schema_version": 2, "run_config": saved,
                                  "run_fingerprint": json_digest(saved), "answers": [row]}))

    assert load_completed(output, config("prompt-v1"), snapshots) == {"q1": row}
    with pytest.raises(ValueError, match="configuration changed"):
        load_completed(output, config("prompt-v2"), snapshots)
    changed = {"q1": dict(snapshots["q1"], query="What changed?")}
    with pytest.raises(ValueError, match="differ from the snapshot"):
        load_completed(output, config("prompt-v1"), changed)
