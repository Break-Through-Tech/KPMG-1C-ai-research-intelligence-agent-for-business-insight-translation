"""Mechanical checks for passage citations and verbatim supporting quotes.

These checks catch formatting and source mismatches. They cannot decide whether
the prose accurately interprets the research; that still needs review.
"""

import re

ABSTENTION = "The provided papers do not address this question."
CITATION = re.compile(r"\[(\d+)\]")
QUOTE_CITATION = re.compile(r'["“]([^"”]{20,})["”]\s*\[(\d+)\]')
NUMBER = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*%?(?!\w)")


def compact(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def answer_issues(answer, chunks):
    """Return actionable failures for a drafted answer and numbered chunks."""
    issues = []
    cited = {int(n) for n in CITATION.findall(answer)}
    allowed = set(range(1, len(chunks) + 1))
    if cited - allowed:
        issues.append(f"Unknown passage citations: {sorted(cited - allowed)}")
    abstained = ABSTENTION in answer
    if abstained:
        if cited:
            issues.append("The answer both abstains and cites an answer.")
        return issues
    if not cited:
        issues.append("No passage citation appears in the answer.")

    quotes = QUOTE_CITATION.findall(answer)
    verified_papers = set()
    for quote, number in quotes:
        index = int(number) - 1
        if index not in range(len(chunks)):
            continue
        if len(quote.split()) < 5 or compact(quote) not in compact(chunks[index].text):
            issues.append(f"Quoted text for [{number}] is not verbatim in that passage.")
        else:
            verified_papers.add(chunks[index].paper_id)
    cited_papers = {chunks[n - 1].paper_id for n in cited & allowed}
    if not quotes or cited_papers - verified_papers:
        issues.append("Include one verified, verbatim Evidence quote per cited paper.")

    # This is a review signal. A number can be supported by a different chunk
    # or be calculated from evidence, so it should not automatically reject text.
    body = answer.split("Evidence:", 1)[0]
    body = CITATION.sub("", body)
    source = compact(" ".join(chunks[n - 1].text for n in cited & allowed))
    unsupported = sorted({number for number in NUMBER.findall(body)
                          if compact(number) not in source})
    if unsupported:
        issues.append(f"Check numbers absent from cited passages: {unsupported}")
    return issues


def repair_prompt(original_prompt, answer, issues):
    return (f"{original_prompt}\n\nYour draft answer was:\n{answer}\n\n"
            f"Fix these source checks: {'; '.join(issues)}. "
            "Return the entire corrected answer, including Evidence quotes. "
            "If the passages do not support an answer, use the required abstention sentence.")
