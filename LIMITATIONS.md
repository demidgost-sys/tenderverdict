# Limitations

TenderVerdict is an experimental metadata pre-qualification tool. Its output is a review queue, not
a conclusion about whether an organisation can or should participate in a procurement procedure.

## Deliberate boundaries

- It processes structured notice metadata, not the full procurement documents or their legal
  hierarchy.
- It does not interpret eligibility, exclusion, selection, award, contractual, or procedural rules.
- It does not compare bidders, predict outcomes, calculate confidence, submit material, or take an
  autonomous action.
- `open_documents` means only that the configured deterministic metadata checks passed.
- `watch` means that a person must resolve missing or ambiguous metadata.
- `reject` records a configured metadata stop factor; it is not a legal disqualification.

## Input and source risk

Metadata can be missing, stale, mistranslated, inconsistent, or changed after collection. CPV codes
and country fields are coarse indicators. The current schema validates their shape, not membership
in a complete authoritative CPV or country vocabulary. A source URL establishes traceability, not
correctness.
Deadlines can be amended or subject to procedural rules not represented in the input.

The model stores calendar dates, not local deadline times. A deadline on the `as_of` date is treated
as closed. TED Search API output is notice-level; zero- and multi-lot records intentionally lose
lot-specific CPV, country, and deadline values and become a human-review case rather than risking a
false association.

Always inspect the current official notice, amendments, procurement documents, and applicable rules
before acting. When a field is unclear, preserve the uncertainty instead of inferring a favourable
answer.

## Operational risk

- Validate fixtures before using them in an internal workflow.
- Keep confidential material outside this experimental release.
- Treat input text and generated reports as untrusted content when embedding them elsewhere.
- Network collection can fail or return an incomplete provider response; a failed fetch must not be
  treated as an empty market.
- A successful zero-row snapshot is distinct from a failure and produces an explicit zero-notice
  report.

The software is provided under the warranty disclaimer in the Apache License 2.0. Nothing in this
repository is legal advice or a professional procurement opinion.
