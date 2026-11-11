"""Generate fresh answers using the notebook's prompt and local Ollama model."""

import argparse
import ast
import hashlib
import json
import sys
import time
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "notebooks"))
from retrieval import ResearchRetriever, RetrievedChunk, needs_multiple_papers  # noqa: E402
from answer_validation import answer_issues, attach_evidence  # noqa: E402

GENERATION_OPTIONS = {"temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": 550}


def notebook_prompt():
    notebook = json.loads((ROOT / "notebooks/eda_workbook.ipynb").read_text())
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell.get("source", []))
        if "PROMPT =" not in source:
            continue
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "PROMPT"
                for target in node.targets
            ):
                return ast.literal_eval(node.value)
    raise RuntimeError("Notebook PROMPT assignment not found")


def ask_ollama(prompt, model, host):
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "options": GENERATION_OPTIONS}).encode()
    request = urllib.request.Request(
        f"{host.rstrip('/')}/api/generate", payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)


def json_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def load_snapshot(retrieval, benchmark):
    """Read the exact passages and prompt context saved by run_retrieval.py."""
    if retrieval.get("snapshot_version") != 1:
        raise ValueError("Retrieval report has no frozen passages. Run run_retrieval.py "
                         "with a new --output path, then pass that file as --retrieval.")
    if retrieval.get("benchmark_sha256") != json_digest(benchmark):
        raise ValueError("Benchmark differs from the retrieval snapshot. Regenerate retrieval.")
    expected = {item["id"]: item["query"] for item in benchmark["queries"]}
    if len(expected) != len(benchmark["queries"]):
        raise ValueError("Benchmark contains duplicate query IDs.")
    snapshots = {}
    formatter = ResearchRetriever(None)
    for row in retrieval["queries"]:
        query_id = row["id"]
        if query_id in snapshots or query_id not in expected or row["query"] != expected[query_id]:
            raise ValueError(f"Snapshot query mismatch: {query_id}")
        chunks = [RetrievedChunk(**chunk) for chunk in row["retrieved_chunks"]]
        if [c.rank for c in chunks] != list(range(1, len(chunks) + 1)):
            raise ValueError(f"Snapshot passage ranks must be consecutive: {query_id}")
        if (row["context"] != formatter.format_context(chunks)
                or row["source_list"] != formatter.format_sources(chunks)):
            raise ValueError(f"Snapshot context or sources differ from passages: {query_id}")
        snapshots[query_id] = row
    if set(snapshots) != set(expected):
        raise ValueError("Snapshot must contain every benchmark query.")
    return snapshots


def run_configuration(model, model_digest, template, retrieval, benchmark):
    if not model_digest:
        raise ValueError(f"Cannot fingerprint Ollama model {model!r}; pull the model first.")
    return {
        "model": model, "model_digest": model_digest,
        "notebook_prompt_sha256": hashlib.sha256(template.encode()).hexdigest(),
        "generation_options": dict(GENERATION_OPTIONS),
        # Includes corpus fingerprint, retrieval settings, passage text/order and metadata.
        "retrieval_sha256": json_digest(retrieval),
        "benchmark_sha256": json_digest(benchmark),
        "answer_pipeline_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
            + (ROOT / "notebooks/answer_validation.py").read_bytes()
            + (ROOT / "notebooks/retrieval.py").read_bytes()
        ).hexdigest(),
    }


def load_completed(path, config, snapshots):
    if not path.exists():
        return {}
    previous = json.loads(path.read_text())
    previous_config = previous.get("run_config")
    if previous.get("schema_version") != 2 or not isinstance(previous_config, dict):
        raise ValueError("Existing answers lack a verified run configuration. "
                         "Preserve that file and choose a new --output path.")
    if previous.get("run_fingerprint") != json_digest(previous_config):
        raise ValueError("Existing run fingerprint is invalid. Choose a new --output path.")
    if previous_config != config:
        changed = sorted(key for key in previous_config.keys() | config.keys()
                         if previous_config.get(key) != config.get(key))
        raise ValueError(f"Cannot resume: run configuration changed ({', '.join(changed)}). "
                         "Choose a new --output path.")
    completed = {}
    for row in previous["answers"]:
        query_id = row["id"]
        frozen = snapshots.get(query_id)
        if (query_id in completed or frozen is None
                or row["query"] != frozen["query"]
                or row["passages"] != frozen["retrieved_chunks"]
                or row["source_list"] != frozen["source_list"]):
            raise ValueError(f"Saved answer inputs differ from the snapshot: {query_id}")
        completed[query_id] = row
    return completed


def select_queries(benchmark, ids=None, limit=0):
    if ids and limit:
        raise ValueError('Use --ids or --limit, not both.')
    if ids:
        by_id = {q['id']: q for q in benchmark['queries']}
        if len(ids) != len(set(ids)) or any(key not in by_id for key in ids):
            raise ValueError('--ids must contain unique, known benchmark question IDs.')
        return [by_id[key] for key in ids]
    return benchmark['queries'][:limit or None]


def experiment_context(frozen, group_by_paper=False, selection_order=False):
    """Change presentation only; retain frozen passage IDs, text and sources.

    Reconstruct order_by_vector=False from saved reranker scores, including
    reserved distinct-paper slots. Original citation IDs remain stable.
    """
    chunks = [RetrievedChunk(**chunk) for chunk in frozen['retrieved_chunks']]
    if selection_order:
        ranked = sorted(chunks, key=lambda chunk: chunk.score, reverse=True)
        reserved = []
        if needs_multiple_papers(frozen['query']):
            seen = set()
            for chunk in ranked:
                if chunk.paper_id not in seen:
                    reserved.append(chunk)
                    seen.add(chunk.paper_id)
                    if len(seen) == 2:
                        break
        reserved_ids = {chunk.rank for chunk in reserved}
        chunks = reserved + [c for c in ranked if c.rank not in reserved_ids]
    return ResearchRetriever(None).format_context(chunks, group_by_paper=group_by_paper)


def main(args):
    if args.limit < 0:
        raise ValueError("--limit must be nonnegative.")
    retrieval = json.loads(args.retrieval.read_text())
    benchmark_path = ROOT / retrieval.get("benchmark", "evaluation/benchmark.json")
    if args.output.resolve() in {args.retrieval.resolve(), benchmark_path.resolve()}:
        raise ValueError("Answer output must differ from the retrieval and benchmark files.")
    benchmark = json.loads(benchmark_path.read_text())
    ids = getattr(args, 'ids', None)
    selected = select_queries(benchmark, ids, args.limit)
    snapshots = load_snapshot(retrieval, benchmark)
    template = notebook_prompt()
    with urllib.request.urlopen(f"{args.host.rstrip('/')}/api/tags", timeout=30) as response:
        models = json.load(response)["models"]
    model_digest = next((m["digest"] for m in models
                         if m["name"] in {args.model, f"{args.model}:latest"}), None)
    config = run_configuration(args.model, model_digest, template, retrieval, benchmark)
    group_by_paper = getattr(args, 'group_by_paper', False)
    selection_order = getattr(args, 'selection_order', False)
    if selection_order and not retrieval.get('rerank_model'):
        raise ValueError('--selection-order requires saved reranker scores.')
    config['context_presentation'] = {
        'group_by_paper': group_by_paper, 'selection_order': selection_order,
    }
    if ids:
        config['selected_question_ids'] = ids
    completed = load_completed(args.output, config, snapshots)
    for item in selected:
        if item["id"] in completed:
            continue
        frozen = snapshots[item["id"]]
        chunks = [RetrievedChunk(**chunk) for chunk in frozen["retrieved_chunks"]]
        context = experiment_context(frozen, group_by_paper, selection_order)
        prompt = template.format(context=context, question=item["query"])
        start = time.monotonic()
        response = ask_ollama(prompt, args.model, args.host)
        draft = response["response"].strip()
        answer = attach_evidence(draft, chunks, item["query"])
        completed[item["id"]] = {
            "id": item["id"], "query": item["query"],
            "answer": answer,
            "draft": draft,
            "generation_context": context,
            "remaining_issues": answer_issues(answer, chunks),
            "claim_support_status": "not_evaluated",
            "source_list": frozen["source_list"],
            "passages": frozen["retrieved_chunks"],
            "seconds": round(time.monotonic() - start, 1),
            "prompt_tokens": response.get("prompt_eval_count"),
            "answer_tokens": response.get("eval_count"),
        }
        save_answers(args.output, config, args.retrieval, benchmark, completed)
        print(f"{item['id']}: {completed[item['id']]['seconds']}s, "
              f"{completed[item['id']]['answer_tokens']} output tokens", flush=True)
    save_answers(args.output, config, args.retrieval, benchmark, completed)
    print(f"Saved {len(completed)} answers to {args.output}")


def save_answers(path, config, retrieval_path, benchmark, completed):
    """Replace the checkpoint atomically so interruption cannot truncate it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema_version": 2, "run_config": config,
        "run_fingerprint": json_digest(config),
        "model": config["model"], "model_digest": config["model_digest"],
        "notebook_prompt_sha256": config["notebook_prompt_sha256"],
        "retrieval_result": str(retrieval_path.resolve()),
        "benchmark": benchmark,
        "answers": list(completed.values()),
    }
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as file:
            temporary = Path(file.name)
            file.write(json.dumps(result, indent=2) + "\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="llama3.2")
    parser.add_argument("--host", default="http://127.0.0.1:11434")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "evaluation/results/answers.json")
    parser.add_argument("--retrieval", type=Path,
                        default=ROOT / "evaluation/results/retrieval.json")
    parser.add_argument("--limit", type=int, default=0,
                        help="Run only the first N questions (0 = all)")
    parser.add_argument('--ids', nargs='+', help='Generate only these benchmark question IDs, in this order')
    parser.add_argument('--group-by-paper', action='store_true', help='Group frozen passages under paper headings')
    parser.add_argument('--selection-order', action='store_true', help='Use saved reranker scores and reserved paper slots instead of vector order')
    main(parser.parse_args())
