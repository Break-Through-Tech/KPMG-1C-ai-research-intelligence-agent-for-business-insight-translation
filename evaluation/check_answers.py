"""Mechanical citation, quote, and abstention checks on fresh answers.

These checks do not judge whether every claim is true; human review remains
necessary for factual accuracy and semantic completeness.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CITATION = re.compile(r"\[(\d+)\]")
QUOTED = re.compile(r'[“"]([^“”"]{20,})[”"]')


def compact(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def main():
    data = json.loads((ROOT / "evaluation/results/answers.json").read_text())
    benchmark = {q["id"]: q for q in json.loads(
        (ROOT / "evaluation/benchmark.json").read_text())["queries"]}
    rows = []
    for item in data["answers"]:
        allowed = set(CITATION.findall(item["source_list"]))
        cited = set(CITATION.findall(item["answer"]))
        passages = [compact(p["text"]) for p in item["passages"]]
        quotes = [q for q in QUOTED.findall(item["answer"]) if len(q.split()) >= 5]
        verified_quotes = [q for q in quotes if any(compact(q) in p for p in passages)]
        negative = not benchmark[item["id"]]["relevant_papers"]
        rows.append({"id": item["id"], "cited_numbers": sorted(cited),
                     "invalid_citations": sorted(cited - allowed),
                     "has_citation": bool(cited),
                     "verified_direct_quote": bool(verified_quotes),
                     "is_negative": negative,
                     "abstention_phrase": "The provided papers do not address this question."
                     in item["answer"]})
    positives = [r for r in rows if not r["is_negative"]]
    negatives = [r for r in rows if r["is_negative"]]
    summary = {
        "answer_count": len(rows),
        "positive_answers_with_citation": sum(r["has_citation"] for r in positives),
        "positive_answers": len(positives),
        "answers_with_invalid_citation": sum(bool(r["invalid_citations"]) for r in rows),
        "positive_answers_with_verified_direct_quote": sum(r["verified_direct_quote"] for r in positives),
        "negative_answers_with_abstention_phrase": sum(r["abstention_phrase"] for r in negatives),
        "negative_answers": len(negatives),
    }
    result = {"summary": summary, "answers": rows}
    target = ROOT / "evaluation/results/answer_checks.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
