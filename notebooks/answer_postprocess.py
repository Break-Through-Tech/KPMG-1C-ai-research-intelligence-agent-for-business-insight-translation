"""Deterministic clean-up of structured answers (no model calls).

1. Replace bare arXiv paper IDs with the paper's title, taken from the
   retrieved passages' metadata.
2. Drop claims that only repeat one earlier claim. A claim is dropped only when
   it has at least 8 content words, at least 85% of them appear in a single
   earlier kept claim, and it adds no new number or negation. Its citations
   move to that earlier claim, so no citation is lost.
"""
import re

STOP = set("""a an the of to in and or is are was were be been by for on with as at that this these those
it its from into than then which who whom whose what when where how why does do did can could may might
also both each such their there they them via using used use paper papers""".split())
NEGATION = {'not', 'no', 'never', 'without', 'cannot', 'neither', 'nor', 'unlike', 'only'}
PAPER_ID = re.compile(r"(?:\b[Pp]aper\s+(?:ID\s+)?|\barXiv\s*(?:ID\s*)?:?\s*)?\b(\d{4}\.\d{4,5})(?:v\d+)?\b")
NUMBER = re.compile(r"\d+(?:[.,]\d+)*%?")


def words(text):
    # Light stemming so "preference"/"preferences" count as the same word.
    found = re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", text.lower())
    return {w[:-1] if len(w) > 3 and w.endswith('s') and not w.endswith('ss') else w
            for w in found if w not in STOP}


def numbers(text):
    return {n.replace(',', '') for n in NUMBER.findall(text)}


def replace_paper_ids(text, titles):
    def sub(match):
        title = titles.get(match.group(1))
        return f"“{title}”" if title else match.group(0)
    return PAPER_ID.sub(sub, text)


MIN_WORDS = 8  # short claims that differ by one word ("format" vs "checklist" weight) are distinct facts


def redundant_with(claim, kept, threshold):
    """Return the single earlier claim that already says this, or None."""
    new = words(claim)
    if len(new) < MIN_WORDS:
        return None
    for earlier in kept:
        old = words(earlier['claim'])
        if numbers(claim) - numbers(earlier['claim']) or (new & NEGATION) - old:
            continue
        if len(new & old) / len(new) >= threshold:
            return earlier
    return None


def postprocess(structured, passages, threshold=0.85, titles=True, dedupe=True):
    """Return (claims, log) where claims are [{'claim', 'evidence'}] dicts."""
    title_map = {p['paper_id']: p['title'] for p in passages if p.get('paper_id') and p.get('title')}
    log = []
    kept = []
    for item in structured.get('claims', []):
        claim = item['claim']
        if titles:
            fixed = replace_paper_ids(claim, title_map)
            if fixed != claim:
                log.append(f'title: {claim[:60]!r}')
                claim = fixed
        ids = [e['passage_id'] for e in item.get('evidence', [])]
        target = redundant_with(claim, kept, threshold) if dedupe else None
        if target is not None:
            target['evidence'] += [i for i in ids if i not in target['evidence']]
            log.append(f'dropped: {claim[:60]!r}')
            continue
        kept.append({'claim': claim, 'evidence': ids})
    return kept, log


def render(claims, unanswered=''):
    """Same output format as structured_answers.render."""
    from structured_answers import render as base_render
    return base_render({'claims': [{'claim': c['claim'], 'evidence': [{'passage_id': i} for i in c['evidence']]}
                                   for c in claims], 'unanswered': unanswered or ''})
