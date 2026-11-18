# Review of the three-answer frozen-context pilot

Reviewed October 28, 2026. This is an assistant review against the exact saved
passages and benchmark requirements, not an independent human review or a fresh
inspection of the full source PDFs. Generated answers and scores were not edited.

Inputs: `answers_ordered_frozen.json`, `retrieval_ordered_frozen.json`, and
`answer_checks_ordered_frozen.json`. Model: `llama3.2`; temperature 0; seed 42.
Run fingerprint:
`fd9518ae54fd33fe03a676ee9d79b45a03d7e4e7a2cd2320b94cac32e877f40d`.

The run fingerprint, retrieval snapshot hash, benchmark hash, and all three
answers' saved passage inputs were verified as consistent. This run contains
q01–q03 only, all about the same paper. It does not evaluate abstention,
cross-paper synthesis, business translation, or the other 22 benchmark questions.

## Findings

| Question | Content assessment | Traceability | Overall assessment |
| --- | --- | --- | --- |
| q01: Router's decision rule | Fail for a Router-specific answer: correct opening concept, followed by substantial Bidder-related material that blurs the policy distinction; omits the explicit stopping rule | Valid citation numbers and one matching quote, but the quote describes Bidder behavior | Needs revision |
| q02: Router versus Bidder | Partial: some correct cost-sensitive behavior, but misses centralized versus decentralized decision-making and overstates a conditional result | Valid citation numbers and one matching quote; the quote does not directly substantiate the answer's claimed contrast | Needs revision |
| q03: Evaluation domains | Full content: all three domains are correct | No passage citations or evidence quote | Needs citations and evidence |

Full content: 1/3; partial: 1/3; fail: 1/3. All three require changes to meet
both content and citation requirements. These are qualitative judgments on a
tiny pilot, not an overall system accuracy estimate. Mechanical checks report
matching quotes in 2/3 answers and no out-of-range citations; those results do
not establish that the accompanying claims are correct.

## q01 — Correct opening, followed by policy confusion and repetition

Passage [1], chunk `2608.20316_4_1`, directly states that Router inspects
specialists in reservation-price order, stops when no remaining query is worth
its cost, and selects the best observed estimate. This evidence was available
at the first position in the context.

The answer starts with reservation prices and value of information, then spends
much of its response discussing posted prices, strategic specialists, accepting
prices, and claiming queries. Passages [3] and [4] describe those mechanisms as
the decentralized Bidder setting. Although the response mentions a decentralized
setting, it does not clearly separate that policy from the Router being asked
about. It also repeats the same general claim several times.

The draft contains roughly eleven explanatory sentences plus a generated source
list, despite the prompt's one-to-three-sentence requirement and instruction that
sources will be supplied separately. The model emitted 431 tokens, below its
550-token cap; the verbosity is not evidence of hitting the generation limit.

The automatically attached quote comes from Bidder passage [3] and ends mid-sentence.
It matches the source but does not directly explain Router's centralized stopping
rule. The generated source list also causes [2] to appear in the mechanical
citation inventory even though it is not cited in an explanatory sentence.

Suggested answer, using this question's saved passage numbering:

> Pandora's Router computes reservation prices from the expected value of obtaining
> a more accurate specialist estimate. It inspects specialists in reservation-price
> order and stops when no remaining inspection is worth its cost, then selects the
> specialist with the highest observed refined estimate. [1]

Primary diagnosis: generation relevance, policy attribution, completeness, and
length compliance. Retrieval supplied enough evidence for a concise answer.

## q02 — The defining comparison is missing

Passage [1], chunk `2608.20316_4_1`, explicitly labels Router a centralized policy
and Bidder a decentralized policy. Passage [3], chunk `2608.20316_5_5`, explains
that the centralized router internalizes costs and optimizes global welfare,
while maximizing a bidder's local surplus can reduce overall allocative efficiency.

The answer instead contrasts inspection-cost behavior. It describes Bidder as
querying when it has a true advantage and declining when costs are high. The source
describes observed low-cost behavior and says that at higher costs the bidder may
either use the cheap estimate or decline. The answer omits that alternative and
does not clearly state who makes the decisions or whose objective is optimized.

The attached quote mentions the centralized/global-welfare distinction, but that
distinction is absent from the answer body. An appended quote does not repair
incomplete explanatory prose.

Suggested answer:

> Pandora's Router is centralized: one router decides which specialists to inspect
> and selects a specialist while accounting for overall costs. Pandora's Bidder is
> decentralized: a specialist decides whether to refine its own estimate and accept
> a posted price; maximizing its own surplus may conflict with overall allocation
> efficiency. [1][3][4]

Primary diagnosis: comparison completeness and overgeneralization. The necessary
distinction was already present in the retrieved passages.

## q03 — Correct domains, missing citations

The answer correctly lists EmbedLLM/multi-LLM routing, retrieval-augmented
specialists, and variable inference-time reasoning. Passage [3], chunk
`2608.20316_1_4`, gives the explicit domains, and passage [4], chunk
`2608.20316_0_1`, supports the broader wording used in the answer.

The model supplies no passage citations. Consequently `attach_evidence()` cannot
select a cited paper and adds no quote. This is the citation failure already
reported by the mechanical checker.

Suggested answer:

> The policy was evaluated on a multi-LLM routing benchmark (EmbedLLM),
> retrieval-augmented specialists for factoid question answering, and variable
> inference-time computation for mathematical reasoning. [3][4]

Primary diagnosis: output-format compliance. Passages [3] and [4] provide enough
evidence, although unrelated mathematical material occupies the first position.

## Next experiment

Hold these frozen passages constant and test a prompt/output format that requires
one claim with its supporting passage at a time, explicitly addresses each part
of a comparison, and limits the rendered answer length. Compare against this
pilot before changing retrieval or swapping models. Evidence quotes should be
selected for the supported claim, not merely for overlap with the question.

The literal snippet metric misses q01 and q02, but both contexts contain sufficient
semantic evidence. Those exact-match misses should not automatically be classified
as retrieval failures. For q03, compare context ordering separately if further
testing shows it affects citation compliance; this run alone does not establish
that ordering caused the omission.

Complete the remaining benchmark questions as a separate evaluation step to
assess numerical interpretation, synthesis, and abstention. Do not extrapolate
the pilot's content ratings to all 25 questions.
