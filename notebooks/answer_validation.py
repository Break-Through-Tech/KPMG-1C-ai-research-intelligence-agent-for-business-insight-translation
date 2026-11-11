"""Mechanical checks for passage citations and verbatim supporting quotes.

These checks catch formatting and source mismatches. They cannot decide whether
the prose accurately interprets the research; that still needs review.
"""

import re
from decimal import Decimal

ABSTENTION = "The provided papers do not address this question."
NONANSWER = re.compile(r"\b(?:provided\s+)?papers?\s+(?:do|does)\s+not\s+(?:address|answer)\b", re.I)
CITATION = re.compile(r"\[(\d+)\]")
QUOTE_CITATION = re.compile(r'["“]([^"”]{20,})["”]\s*\[(\d+)\]')
NUMBER = re.compile(
    r"(?<![\w.])[-+−]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)"
    r"(?:[eE][-+]?\d+)?"
    r"(?:[ \t]*(?:%|percent\b))?(?!\w|\.\d|,\d)", re.I,
)
WORDS = re.compile(r"[a-z0-9]+")
STOPWORDS = {"the", "and", "for", "with", "from", "that", "this", "when", "what",
             "which", "how", "does", "into", "their", "them", "they", "was", "were",
             "are", "have", "has", "paper", "papers", "using", "about"}


def compact(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def numeric_key(token):
    """Compare whole values, preserving signs and percentage units.

    English thousands separators and trailing decimal zeros are equivalent;
    92 vs 192, 9.2 vs 92, and 30 vs 30% are not.
    """
    token = token.lower().replace("−", "-").replace(",", "")
    percent = token.endswith(("%", "percent"))
    value = re.sub(r"(?:%|percent)$", "", token).strip()
    return Decimal(value), percent


def quote_matches(quote, text):
    """Allow PDF whitespace differences without erasing numeric punctuation."""
    quote = " ".join(quote.split())
    if not quote:
        return False
    left = r"(?<![\w.+−-])" if quote[0].isdigit() else r"(?<!\w)" if quote[0].isalnum() else ""
    right = r"(?![\w%]|\.\d|,\d)" if quote[-1].isdigit() else r"(?!\w)" if quote[-1].isalnum() else ""
    return re.search(left + re.escape(quote) + right, " ".join(text.split())) is not None


def _best_quote(text, focus):
    """Pick a literal, question-related word span; return its original PDF text."""
    matches = list(re.finditer(r"\S+", text))
    if len(matches) < 5:
        return text.strip()
    wanted = {word for word in WORDS.findall(focus.lower())
              if word not in STOPWORDS and len(word) > 2}
    best = (-1, "")
    for start in range(0, len(matches), 5):
        end = min(start + 24, len(matches))
        if end - start < 5:
            continue
        quote = text[matches[start].start():matches[end - 1].end()]
        words = WORDS.findall(quote.lower())
        overlap = len(set(words) & wanted)
        numbers = sum(word.isdigit() and len(word) > 1 and word in wanted for word in words)
        artifacts = sum(len(word) > 22 for word in words)
        math_symbols = len(re.findall(r"[𝑎-𝑧𝛼-𝜔]", quote))
        score = overlap + 2 * numbers - 2 * artifacts - math_symbols
        if score > best[0]:
            best = (score, quote)
    return best[1]


def attach_evidence(answer, chunks, question=""):
    """Attach one exact quote per cited paper, tied to its passage number.

    A literal quote is evidence a reviewer can inspect, not proof that the
    model's interpretation is correct.
    """
    body = re.split(r"\n\s*Evidence\s*:", answer, maxsplit=1, flags=re.I)[0].strip()
    if NONANSWER.search(body) and not CITATION.search(body):
        return body
    cited = [int(number) for number in CITATION.findall(body)
             if 1 <= int(number) <= len(chunks)]
    papers = list(dict.fromkeys(chunks[number - 1].paper_id for number in cited))
    if not papers:
        return body
    evidence = []
    for paper_id in papers:
        clean_body = re.sub(r"(?m)^\s*\d+\.\s*", "", body)
        answer_numbers = [number for number in NUMBER.findall(clean_body)
                          if len(compact(number)) > 1]
        focus = question + " " + " ".join(answer_numbers)
        wanted = set(WORDS.findall(focus.lower())) - STOPWORDS
        candidates = [(number, _best_quote(chunk.text, focus))
                      for number, chunk in enumerate(chunks, 1)
                      if chunk.paper_id == paper_id]
        number, quote = max(candidates, key=lambda pair: (
            len(set(WORDS.findall(pair[1].lower())) & wanted)
            - 2 * len(re.findall(r"[𝑎-𝑧𝛼-𝜔]", pair[1])),
            -abs(pair[0] - min(cited)),
        ))
        evidence.append(f'- "{quote}" [{number}]')
    return body + "\n\nEvidence:\n" + "\n".join(evidence)


def answer_issues(answer, chunks):
    """Return actionable failures for a drafted answer and numbered chunks."""
    issues = []
    cited = {int(n) for n in CITATION.findall(answer)}
    allowed = set(range(1, len(chunks) + 1))
    if cited - allowed:
        issues.append(f"Unknown passage citations: {sorted(cited - allowed)}")
    abstained = bool(NONANSWER.search(answer))
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
        if len(quote.split()) < 5 or not quote_matches(quote, chunks[index].text):
            issues.append(f"Quoted text for [{number}] is not verbatim in that passage.")
        else:
            verified_papers.add(chunks[index].paper_id)
    cited_papers = {chunks[n - 1].paper_id for n in cited & allowed}
    if not quotes or cited_papers - verified_papers:
        issues.append("Include one verified, verbatim Evidence quote per cited paper.")

    # This is a review signal. A number can be supported by a different chunk
    # or be calculated from evidence, so it should not automatically reject text.
    body = re.split(r"\bEvidence\s*:", answer, maxsplit=1, flags=re.I)[0]
    body_cited = {int(n) for n in CITATION.findall(body)} & allowed
    body = CITATION.sub("", body)
    body = re.sub(r"(?m)^\s*\d+\.[ \t]+", "", body)  # numbered list markers
    source_numbers = {numeric_key(number)
                      for n in body_cited for number in NUMBER.findall(chunks[n - 1].text)}
    unsupported = sorted({number for number in NUMBER.findall(body)
                          if numeric_key(number) not in source_numbers})
    if unsupported:
        issues.append(f"Check numbers absent from cited passages: {unsupported}")
    return issues


