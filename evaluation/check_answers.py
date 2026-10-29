"""Mechanical citation, quote, and abstention checks on fresh answers.

These checks do not judge whether every claim is true; human review remains
necessary for factual accuracy and semantic completeness.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "notebooks"))
from answer_validation import answer_issues, QUOTE_CITATION, compact  # noqa: E402
CITATION = re.compile(r"\[(\d+)\]")


def main(args):
    data = json.loads(args.answers.read_text())
    benchmark = {q["id"]: q for q in json.loads(
        (ROOT / "evaluation/benchmark.json").read_text())["queries"]}
    rows = []
    for item in data["answers"]:
        allowed = set(CITATION.findall(item["source_list"]))
        cited = set(CITATION.findall(item["answer"]))
        passages = [SimpleNamespace(**passage) for passage in item["passages"]]
        quotes = QUOTE_CITATION.findall(item["answer"])
        verified_quotes = [quote for quote, number in quotes
                           if 1 <= int(number) <= len(passages)
                           and len(quote.split()) >= 5
                           and compact(quote) in compact(passages[int(number) - 1].text)]
        negative = not benchmark[item["id"]]["relevant_papers"]
        kind = item.get("response_kind", "answer")
        rows.append({"id": item["id"], "cited_numbers": sorted(cited),
                     "response_kind": kind,
                     "invalid_citations": sorted(cited - allowed),
                     "has_citation": bool(cited),
                     "verified_direct_quote": bool(verified_quotes),
                     "verified_quote_count": len(verified_quotes),
                     "issues": answer_issues(item["answer"], passages),
                     "is_negative": negative,
                     "abstention_phrase": "The provided papers do not address this question."
                     in item["answer"]})
    positives = [r for r in rows if not r["is_negative"]]
    negatives = [r for r in rows if r["is_negative"]]
    direct = [r for r in positives if r["response_kind"] == "answer"]
    summary = {
        "answer_count": len(rows),
        "positive_direct_answers": len(direct),
        "positive_direct_answers_with_citation": sum(r["has_citation"] for r in direct),
        "positive_direct_answers_with_verified_quote": sum(r["verified_direct_quote"] for r in direct),
        "positive_direct_answers_passing_source_checks": sum(not r["issues"] for r in direct),
        "positive_source_only_responses": sum(
            r["response_kind"] in {"paper_matches", "source_review"} for r in positives),
        "positive_abstentions": sum(r["response_kind"] == "abstention" for r in positives),
        "positive_answers_with_citation": sum(r["has_citation"] for r in positives),
        "positive_answers": len(positives),
        "answers_with_invalid_citation": sum(bool(r["invalid_citations"]) for r in rows),
        "positive_answers_with_verified_direct_quote": sum(r["verified_direct_quote"] for r in positives),
        "negative_answers_with_abstention_phrase": sum(r["abstention_phrase"] for r in negatives),
        "negative_answers": len(negatives),
    }
    result = {"summary": summary, "answers": rows}
    target = args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--answers", type=Path,
                        default=ROOT / "evaluation/results/answers.json")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "evaluation/results/answer_checks.json")
    main(parser.parse_args())
