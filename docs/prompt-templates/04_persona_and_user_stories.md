# Draft persona and user stories

## Proposed persona

Alex is a fictional professional-services advisor preparing a client or internal discussion. Alex needs to understand an AI research topic quickly and explain what it might mean for a business decision. The pain point is limited time to read technical papers and distinguish demonstrated results from promising ideas. Likely questions include what changed, why it matters, what is ready to investigate, and which claims can be verified. Trust requires relevant sources, clear limitations, and no inflated benefits.

This is an assumption-based draft, not a user interview finding or a claim about KPMG employees. The product owner is the reviewer of usefulness; the advisor is the proposed end user. Start with no assumed AI knowledge unless a specific audience request says otherwise. Allison's guide explicitly makes personas optional; keep this only while it improves design or testing.

## Stories and observable checks

| ID | User story | Success checks | Effect on design |
|---|---|---|---|
| S1 | As an advisor, I want research explained as business implications so I can prepare a discussion. | Reader can explain the main finding without AI knowledge; implications address the question; interpretations are labeled. | Plain language, professional-services relevance, decision-focused answer. |
| S2 | As a business user, I want claims linked to their sources so I can verify them. | Key claims have supporting source numbers; papers can be identified from metadata; missing metadata is not invented. | Numbered evidence and application-attached source list. |
| S3 | As a business user, I want gaps and disagreements stated so I can avoid unsupported conclusions. | Material limitations remain visible; insufficient evidence is acknowledged; maturity and benefit claims have support. | Explicit uncertainty, premise correction, no forced item counts. |
| S4 | As an advisor, I want a shorter slide or table so I can reuse findings without losing caveats. | Requested format is followed; key caveats and citations survive; reformatting adds no unsupported claim. | Format overrides default headings; original evidence accompanies follow-up history. |

## Review questions

Does this user represent the intended audience? Which discussion or decision matters first? Can a reviewer identify a source and explain the uncertainty? Would a different audience need more technical detail? Update these assumptions when feedback changes the design.
