"""Mechanical checks for passage citations and verbatim supporting quotes.

These checks catch formatting and source mismatches. They cannot decide whether
the prose accurately interprets the research; that still needs review.
"""

import re

ABSTENTION = "The provided papers do not address this question."
NONANSWER = re.compile(
    r"\b(?:provided\s+)?(?:papers?|passages?)\s+(?:do|does)\s+not\s+"
    r"(?:directly\s+)?(?:address|answer|provide)\b", re.I,
)
CITATION = re.compile(r"\[(\d+)\]")
QUOTE_CITATION = re.compile(r'["“]([^"”]{20,})["”]\s*\[(\d+)\]')
NUMBER = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*%?(?!\w)")
WORDS = re.compile(r"[a-z0-9]+")
STOPWORDS = {"the", "and", "for", "with", "from", "that", "this", "when", "what",
             "which", "how", "does", "into", "their", "them", "they", "was", "were",
             "are", "have", "has", "paper", "papers", "using", "about"}
PAPER_SEARCH_STOPWORDS = STOPWORDS | {
    "these", "those", "address", "addresses", "discuss", "discusses",
    "evaluate", "evaluates", "report", "reports", "derived", "through",
    "any", "all", "one", "each", "both", "than", "not", "our", "its",
}


def search_word(word):
    """Normalize simple plurals for conservative paper-match screening."""
    return word[:-1] if len(word) > 4 and word.endswith("s") and not word.endswith("ss") else word


def compact(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


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
    """Attach one exact quote from each passage cited in the answer body.

    A literal quote is evidence a reviewer can inspect, not proof that the
    model's interpretation is correct.
    """
    body = re.split(r"\n\s*Evidence\s*:", answer, maxsplit=1, flags=re.I)[0].strip()
    if NONANSWER.search(body) and not CITATION.search(body):
        return body
    cited = list(dict.fromkeys(
        int(number) for number in CITATION.findall(body)
        if 1 <= int(number) <= len(chunks)
    ))
    if not cited:
        return body
    evidence = []
    focus = question + " " + CITATION.sub("", body)
    for number in cited:
        quote = _best_quote(chunks[number - 1].text, focus)
        evidence.append(f'- "{quote}" [{number}]')
    return body + "\n\nEvidence:\n" + "\n".join(evidence)


def paper_search_answer(chunks, question):
    """List retrieved paper matches with literal excerpts, without LLM claims.

    These are search results to inspect, not a claim that every paper fully
    answers every part of the question.
    """
    if not chunks:
        return ABSTENTION
    terms = {search_word(word) for word in WORDS.findall(question.lower())
             if len(word) > 2 and word not in PAPER_SEARCH_STOPWORDS
             and not word.isdigit()}
    first_by_paper = {}
    text_by_paper = {}
    for chunk in chunks:
        current = first_by_paper.get(chunk.paper_id)
        if current is None or getattr(chunk, "score", 0) > getattr(current, "score", 0):
            first_by_paper[chunk.paper_id] = chunk
        text_by_paper.setdefault(chunk.paper_id, []).append(chunk.title + " " + chunk.text)
    minimum = 1 if len(terms) <= 2 else 2
    first_by_paper = {
        paper_id: chunk for paper_id, chunk in first_by_paper.items()
        if len(terms & {search_word(word) for word in WORDS.findall(
            " ".join(text_by_paper[paper_id]).lower())}) >= minimum
    }
    if not first_by_paper:
        return ABSTENTION
    body = "Top matching papers (check the excerpts for relevance):\n" + "\n".join(
        f"- {chunk.title} [{chunk.rank}]" for chunk in first_by_paper.values()
    )
    return attach_evidence(body, chunks, question)


def answer_issues(answer, chunks):
    """Return actionable failures for a drafted answer and numbered chunks."""
    issues = []
    body = re.split(r"\n\s*Evidence\s*:", answer, maxsplit=1, flags=re.I)[0]
    cited = {int(n) for n in CITATION.findall(body)}
    allowed = set(range(1, len(chunks) + 1))
    if cited - allowed:
        issues.append(f"Unknown passage citations: {sorted(cited - allowed)}")
    abstained = bool(NONANSWER.search(body))
    if abstained:
        if cited:
            issues.append("The answer both abstains and cites an answer.")
        return issues
    if not cited:
        issues.append("No passage citation appears in the answer.")

    quotes = QUOTE_CITATION.findall(answer)
    verified_passages = set()
    for quote, number in quotes:
        index = int(number) - 1
        if index not in range(len(chunks)):
            continue
        if len(quote.split()) < 5 or compact(quote) not in compact(chunks[index].text):
            issues.append(f"Quoted text for [{number}] is not verbatim in that passage.")
        else:
            verified_passages.add(index + 1)
    if not quotes or (cited & allowed) - verified_passages:
        issues.append("Include one verified, verbatim Evidence quote per cited passage.")

    # This is a review signal. A number can be supported by a different chunk
    # or be calculated from evidence, so it should not automatically reject text.
    body = CITATION.sub("", body)
    source = compact(" ".join(chunks[n - 1].text for n in cited & allowed))
    unsupported = sorted({number for number in NUMBER.findall(body)
                          if compact(number) not in source})
    if unsupported:
        issues.append(f"Check numbers absent from cited passages: {unsupported}")
    return issues


