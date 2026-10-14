"""Generate fresh answers using the notebook's prompt and local Ollama model."""

import argparse
import ast
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "notebooks"))
from retrieval import ResearchRetriever  # noqa: E402


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
                          "options": {"temperature": 0, "seed": 42, "num_ctx": 8192,
                                      "num_predict": 350}}).encode()
    request = urllib.request.Request(
        f"{host.rstrip('/')}/api/generate", payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)


def main(args):
    from langchain_huggingface import HuggingFaceEmbeddings

    benchmark = json.loads((ROOT / "evaluation/benchmark.json").read_text())
    retrieval = json.loads((ROOT / "evaluation/results/retrieval.json").read_text())
    embeddings = HuggingFaceEmbeddings(
        model_name=retrieval["model"], encode_kwargs={"normalize_embeddings": True})
    retriever = ResearchRetriever.from_persisted(
        embeddings,
        persist_directory=ROOT / ".evaluation_cache" / retrieval["corpus_fingerprint"],
        collection_name="evaluation_mpnet_cosine",
        max_chunks_per_paper=retrieval["max_chunks_per_paper"],
    )
    template = notebook_prompt()
    with urllib.request.urlopen(f"{args.host.rstrip('/')}/api/tags", timeout=30) as response:
        models = json.load(response)["models"]
    model_digest = next((m["digest"] for m in models
                         if m["name"] in {args.model, f"{args.model}:latest"}), None)
    completed = {}
    if args.output.exists():
        previous = json.loads(args.output.read_text())
        completed = {row["id"]: row for row in previous["answers"]}
    for item in benchmark["queries"]:
        if args.limit and len(completed) >= args.limit:
            break
        if item["id"] in completed:
            continue
        chunks = retriever.retrieve(item["query"], k=retrieval["k_chunks"],
                                    fetch_k=retrieval["fetch_k"])
        # The notebook numbers chunks; the newer retriever numbers papers.
        # Use the newer source mapping so citations trace to a paper.
        context = retriever.format_context(chunks)
        prompt = template.format(context=context, question=item["query"])
        start = time.monotonic()
        response = ask_ollama(prompt, args.model, args.host)
        completed[item["id"]] = {
            "id": item["id"], "query": item["query"],
            "answer": response["response"].strip(),
            "source_list": retriever.format_sources(chunks),
            "passages": [{"paper_id": chunk.paper_id, "section": chunk.section,
                          "text": chunk.text} for chunk in chunks],
            "seconds": round(time.monotonic() - start, 1),
            "prompt_tokens": response.get("prompt_eval_count"),
            "answer_tokens": response.get("eval_count"),
        }
        save_answers(args.output, args.model, model_digest, template, completed)
        print(f"{item['id']}: {completed[item['id']]['seconds']}s, "
              f"{completed[item['id']]['answer_tokens']} output tokens", flush=True)
    save_answers(args.output, args.model, model_digest, template, completed)
    print(f"Saved {len(completed)} answers to {args.output}")


def save_answers(path, model, model_digest, prompt, completed):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "model": model, "model_digest": model_digest,
        "notebook_prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "retrieval_result": "evaluation/results/retrieval.json",
        "answers": list(completed.values()),
    }, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="llama3.2")
    parser.add_argument("--host", default="http://127.0.0.1:11434")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "evaluation/results/answers.json")
    parser.add_argument("--limit", type=int, default=0,
                        help="Run only the first N questions (0 = all)")
    main(parser.parse_args())
