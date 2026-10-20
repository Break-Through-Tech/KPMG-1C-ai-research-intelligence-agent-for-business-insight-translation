"""Stakeholder review priorities; illustrative personas are not verified biographies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Persona:
    name: str
    role: str
    context: str
    selectable: bool = True


PERSONAS = {
    "allison": Persona(
        "Allison Tatterson", "AI Consulting Decision-Maker",
        "Your current user is Allison Tatterson, a KPMG AI Consulting decision-maker. "
        "Use plain English, traceable citations and proportionate pilot suggestions tied "
        "to consulting workflows. Separate proposed applications from study findings.",
    ),
    "marcus": Persona(
        "Dr. Marcus Vance", "Trusted AI & Risk Assurance Lead",
        "Your current user is Dr. Marcus Vance, a KPMG Trusted AI and Risk Assurance lead. "
        "Prioritize claim-level verification, sample-size and benchmark limitations. "
        "Never invent metrics; flag unknowns and require human review.",
    ),
    "elena": Persona(
        "Elena Sorensen", "Knowledge & Corpus Curator",
        "Your current user is Elena Sorensen, a KPMG knowledge and corpus curator. "
        "Prioritize metadata transparency, collection-area coverage and source provenance. "
        "Label missing metadata; do not infer coverage from a small retrieved sample.",
    ),
    "jordan": Persona(
        "Jordan", "Anti-Persona: Unverified Hype Seeker",
        "Requests for overconfident claims without citations or sample limits must be "
        "declined. Evidence, uncertainty and review guardrails always apply.",
        selectable=False,
    ),
}


def selectable_personas() -> dict[str, Persona]:
    """Offer stakeholder priorities without offering a guardrail bypass."""
    return {key: persona for key, persona in PERSONAS.items() if persona.selectable}
