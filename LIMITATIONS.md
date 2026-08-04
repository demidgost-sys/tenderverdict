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
- Portfolio Workspace repeats the same metadata checks independently for each profile. It does not
  compare, rank, score, or recommend profiles, and its top-level notice count is the size of the
  shared input rather than a sum of repeated profile evaluations.

## Input and source risk

Metadata can be missing, stale, mistranslated, inconsistent, or changed after collection. CPV codes
and country fields are coarse indicators. The schema checks membership against bundled snapshots
retrieved from the EU Publications Office, but a bundled snapshot can age and membership still does
not establish that a code is appropriate for the actual scope. A source URL is checked for safe
absolute HTTPS syntax; it establishes traceability, not correctness or live availability. Deadlines
can be amended or subject to procedural rules not represented in the input.

The model supports either a calendar date or a timezone-aware RFC 3339 deadline. Calendar dates
retain the conservative v0.1 rule. An exact timestamp is compared precisely only when the review
point is also a timezone-aware instant; a date-only boundary becomes `watch`. No deadline rule in
TenderVerdict interprets extensions, time-zone law, portal availability, or procedural exceptions.

TED Search API output is notice-level. Multi-lot fetches are expanded only after a bounded official
eForms XML document preserves each lot's identifier and fields, and Search/XML identifiers agree.
XML failure, mismatch, unsafe structure, excessive size, or an expansion beyond the configured
limit fails the entire fetch. Zero-lot and unsupported legacy records continue to withhold
scope-ambiguous CPV, country, and deadline evidence rather than inventing an association.

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
- A portfolio workspace is limited to five profiles and 256 KiB. Its JSON output is a machine
  contract; combined Markdown and HTML are not implemented. The only multi-profile presentation is
  an unreleased macOS SwiftUI competition shell, not the published Tk desktop.
- The Next Gen source links the official RevenueCat SDK and implements offering, Test Store
  purchase, restore, and entitlement-driven presentation states. It has no committed or configured
  key, verified transaction, packaged application, account system, production billing, or organizer
  eligibility confirmation. The open-source portfolio CLI is not a payment-enforcement boundary.
- The unsigned desktop preview has no trusted installer or update channel. The Windows x64 alpha
  has native automated startup and synthetic-flow evidence but no hands-on usability run.
  Automated platform smoke tests do not replace hands-on Windows, VoiceOver, or NVDA validation.

The software is provided under the warranty disclaimer in the Apache License 2.0. Nothing in this
repository is legal advice or a professional procurement opinion.
