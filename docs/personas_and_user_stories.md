# Personas and review journeys

This prototype follows the challenge overview's requirement for stakeholder review
before internal decisions or client discussions. Allison is the named Challenge
Advisor. The needs below are design assumptions supplied for this prototype, not
interview findings or quotations. Marcus, Elena, and Jordan are illustrative
personas. The CA Chat #1 notes and Christopher Jambor's guide are not committed
in this repository; validate these assumptions with stakeholders before claiming
research-backed persona fit.

Every persona uses the same evidence rules: numbered passage citations, verbatim
quote checks, explicit unknowns, and proportionate recommendations. The UI shows
the active pre-prompt. Personas alter review emphasis, never source content or
the standard of evidence. Jordan is documented but cannot be selected.

## Allison Tatterson — primary: AI Consulting Decision-Maker

**Empathy map:** Thinks about fit with active consulting workflows; feels time
pressure when screening research; asks for a plain-English takeaway; compares
citations and a bounded pilot before discussing an idea with colleagues.

**Journey:** Select Allison → ask a workflow question → inspect the three business
pillars → open the cited source → have a domain reviewer approve a small pilot.
The key friction is research language that hides assumptions or implies ROI.

**User story:** As a consulting decision-maker, I want a concise evidence-linked
business interpretation so I can decide whether a limited pilot merits review.

**INVEST:** Independent of a client system; wording is negotiable with reviewers;
valuable for screening; estimable as one query-to-insight flow; small enough for
one demo; testable with saved benchmark answers.

**Acceptance criteria:** Given a saved answer with mechanically valid evidence,
when Allison views it, then the UI separates findings from proposed Advisory
applications and shows pilot/human-review limitations. Given an unsupported
question, when its answer abstains, then no business action is recommended.

## Dr. Marcus Vance — primary: Trusted AI & Risk Assurance Lead

**Empathy map:** Thinks about unsupported claims and generalization; feels
accountable for assurance; asks which passage supports each number; checks quotes,
benchmark scope, and missing sample details before accepting a summary.

**Journey:** Select Marcus → inspect the technical answer → read mechanical
warnings → compare quotes with passages → record semantic concerns for human
review. Friction: valid citation numbers can still accompany a wrong explanation.

**User story:** As a risk assurance lead, I want visible claim-verification results
and sample limitations so I can identify outputs that need further review.

**INVEST:** Independent of live generation; review labels are negotiable; valuable
for preventing unsupported claims; estimable as one validation view; small enough
for one answer; testable with invalid citations and invented quotes.

**Acceptance criteria:** Given a quote absent from its passage, when validation
runs, then the UI displays the issue and the business formatter withholds action.
Given passing mechanical checks, when results render, then the UI still states
that interpretation requires human review and does not claim semantic assurance.

## Elena Sorensen — secondary: Knowledge & Corpus Curator

**Empathy map:** Thinks about provenance and coverage gaps; feels concerned about
missing metadata; asks for paper IDs and collection themes; opens sources and
compares the selected passages with the broader catalog.

**Journey:** Select Elena → choose a collection filter in live mode → inspect
retrieved cards → verify title, authors, date and chunk ID → identify missing
metadata or themes for catalog review. Friction: saved benchmark passages lack
some catalog fields and all ranking scores.

**User story:** As a corpus curator, I want source provenance and explicit missing
metadata so I can assess traceability without mistaking a sample for full coverage.

**INVEST:** Independent of answer generation; card fields are negotiable; valuable
for source review; estimable as one provenance view; small enough for one passage;
testable against saved passages and optional metadata fixtures.

**Acceptance criteria:** Given a saved passage without a score or authors, when
its card opens, then the UI says “Not saved” and preserves its citation number.
Given a collection-area selection in demo mode, when browsing a saved answer,
then the UI explains that retrieval controls apply only to live mode. Retrieved
collection areas describe selected passages, not complete corpus coverage.

## Jordan — anti-persona: Unverified Hype Seeker

**Empathy map:** Thinks strong claims will impress an executive; feels impatient
with uncertainty; asks for guaranteed gains without citations; skips sample limits.

**Journey:** Requests an overconfident recommendation → encounters evidence and
uncertainty requirements → must inspect sources and obtain human review. The
product deliberately does not satisfy demands for fabricated certainty.

**User story:** As a reviewer, I want unsupported certainty requests constrained
by the same evidence rules so executive outputs cannot bypass verification.

**INVEST:** Independent of persona selection; refusal wording is negotiable;
valuable for preserving trust; estimable as one guardrail scenario; small enough
for one unsupported query; testable with abstention and invalid-metric fixtures.

**Acceptance criteria:** Given the persona menu, when it opens, then Jordan is
absent. Given an answer with an unsupported metric, when mechanical validation
flags it, then no pilot recommendation is emitted. Given persona instructions
requesting unsupported certainty, when a prompt is built, then the evidence rules
explicitly take precedence.

## Demo and technical boundaries

- Start with `streamlit run app.py`; the default mode requires no model service.
- All 25 saved benchmark queries remain inspectable, including failures and the
  two unanswerable questions. Five expandable sample insights use one saved
  single-paper answer per committed paper; they are not new scientific results.
- Live mode opens the existing `research_mpnet_cosine_v3_citable` collection and
  local cached MPNet/cross-encoder models. Build/cache them using the team's
  notebook first; install the requirements supplied by the hygiene PR.
- Live settings: normalized MPNet, cosine retrieval, 60 candidates, four chunks
  per paper, MiniLM cross-encoder, gap 8, and vector ordering after reranking.
  Automatic synthesis reserves 2–3 paper slots when query intent warrants it.
  Reservations cannot guarantee that the candidate pool contains every paper.
- Missing index, missing models, and Ollama errors fall back to saved review.
  Generation has a 45-second timeout. No background downloads occur during UI
  initialization, and importing `app.py` starts no service.
- Citation checks establish mechanical traceability. They cannot establish
  factual interpretation, clinical suitability, KPMG ROI, or production readiness.
