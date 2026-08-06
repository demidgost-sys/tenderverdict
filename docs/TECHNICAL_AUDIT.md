# Technical audit

- Audit date: **2026-08-06**
- Baseline inspected: `79186da7e83e40284cca9f34d658f6e2a0e1b335`
- Remediated product revision and artifact: [project status](PROJECT_STATUS.md)
- Branch: `hackathon/revenuecat-next-gen-2026`
- Review surface: [draft pull request #12](https://github.com/demidgost-sys/tenderverdict/pull/12)
- Scope: Python and Swift source, tests, documentation, Git/CI state, public-tree policy, security
  boundaries, builder, the existing SSD evaluation artifact, and a documentation-only readiness
  reclassification against the official Next Gen requirements

## Outcome

The project is a strong **competition evaluation candidate**, but it is not a public macOS release
and is not yet a final Shipaton submission. The audit found one Release-crash path and several
material code-to-document gaps; it did not merely reorganize prose. The remediated source now makes
the Debug/Release RevenueCat boundary explicit, restores the promised Free export boundary, validates
the exact dashboard identifiers, preserves full provenance, aligns safe-link behavior, makes
untrusted controls visible in SwiftUI, and strengthens process/package checks.

The old artifact built from `79186da` was internally intact and correctly attributed, but it is
superseded because its Release UI could reach an SDK path that RevenueCat intentionally terminates.
Only the clean artifact named in project status is current remediation evidence.

This audit does not replace a hands-on Debug Test Store pass, manual accessibility/settings QA,
external user validation, entrant-account checks, notarization, or a verified Devpost submission.
It records VoiceOver and independent workflow validation as optional follow-up evidence rather than
silently treating unperformed work as complete or as an official submission requirement.

## Method

The pass compared four evidence layers rather than trusting any one of them:

1. implementation and executable contracts;
2. durable architecture/security/user documentation;
3. mutable status, evidence, and submission claims;
4. Git, CI, manifest, signature, archive, and packaged-smoke provenance.

Source inspection followed the flow from strict Python input models through qualification,
serialization, the private frozen bridge, strict Swift decoding, Free/Premium projection,
RevenueCat state, SwiftUI presentation, and packaging. The exact commands and rerun policy are owned
by [the developer guide](DEVELOPMENT.md); current totals and results are owned by
[project status](PROJECT_STATUS.md).

## Findings and remediation

| Severity | Baseline finding | Why it mattered | Remediation and regression evidence |
|---|---|---|---|
| P1 | Release showed a Test Store key field and could call `Purchases.configure` with a `test_` key; RevenueCat 5.83 terminates that configuration in Release | A judge following the visible UI could crash the packaged evaluation app | Test Store availability is compile-gated to Debug. Release exposes an explicit unavailable state and refuses both configure and purchase before any SDK call; native checks run in both configurations |
| P1 | Free export wrote the raw portfolio envelope containing every profile report | The visible lock and exported bytes disagreed, weakening the only meaningful Premium boundary | Free now emits the first complete deterministic ASCII-safe schema-3 report; Premium alone writes the exact portfolio bytes; native checks reject a portfolio envelope in Free export |
| P2 | Native re-encoding dropped schema-3 generator/source and optional TED provenance | Export/re-encoding could silently narrow audit evidence | Swift models now preserve complete provenance and fail closed on invalid generator/source data |
| P2 | Python and Swift disagreed about safe links; DEL and Unicode format controls were not rejected consistently | Input could become an active link on one surface but not another | Both implementations reject whitespace, Cc, and Cf characters before accepting an HTTPS URL; C0, DEL, and bidi regressions are covered |
| P2 | SwiftUI rendered profile, notice, buyer, reasoning, warning, path, and status text raw | Bidi/format controls could visually reorder or conceal untrusted metadata | Native presentation mirrors Python display normalization and visibly escapes C0, DEL/C1, and format controls while leaving evidence/export bytes unchanged |
| P2 | Purchase selected the first available package instead of the documented RevenueCat objects | A dashboard ordering change could sell or demonstrate the wrong product | The app now requires offering `supplier_profiles_plus`, package `$rc_monthly`, and product `supplier_profiles_plus_monthly`; unexpected shapes remain locked |
| P2 | Child-process stderr/stdout caps were checked while running but not again after a fast exit | A process could cross the bound immediately before termination | Final file sizes are checked before either stream is read; timeout and reduced-environment boundaries remain unchanged |
| P2 | The builder did not execute configuration-specific native checks and obscured the alpha suffix in provenance | A package could pass smoke without testing its exact Debug/Release contract, and manifest version evidence was ambiguous | Builder runs the matching native-check binary and records full project version, numeric bundle version, configuration, Test Store availability, revision, dirty state, architecture, signing, and key absence |
| P3 | Durable and submission documents copied suite totals, stale SHAs, package labels, and an obsolete Test Store uncertainty | Readers could not tell a current fact from a historical baseline | `PROJECT_STATUS.md` owns mutable values; durable pages link to it, organizer evidence remains in one ledger, and executable metadata tests validate the documentation on-ramp and links |

## Follow-up logical and UX audit

The post-remediation pass traced the real first-run, changed-input, failed-rerun, filtered-review,
builder, import-preview, and locked-Premium states. It closed these smaller but credibility-relevant
gaps without changing report schemas or qualification ownership:

| Finding | Risk | Closure |
|---|---|---|
| Startup showed a synthetic report beside empty input selectors with no explicit provenance state | A user could mistake demo evidence for a selected-input result | Demo, current, and retained previous reports now have distinct context cards and report-specific footer language |
| An accepted input/review-point change or failed rerun could leave old bytes exportable without prominent stale wording | Failure retention was correct but the presentation could overstate freshness | The old report is marked previous before rerun and after accepted input/date changes; export action, Save panel, and success message preserve that qualifier |
| Synthetic first profile showed no Watch despite the three-verdict product story | The first judging screen under-demonstrated the core workflow | Shared synthetic geography now produces one Open, one Watch, and one Reject for the Free profile; fixture parity and summary are regression-tested |
| Profile Builder footer reused a spacer in vertical fallback and returned one generic schema error | Compact-height layout and recovery were fragile | Message/actions are separate layout groups, example profiles match the shipped workspace, field-specific fixes and code-format help are visible |
| Passed checks buried Watch/Reject drivers; filters and import warnings had discoverability gaps | Human review took unnecessary scanning and could retain invisible state | Presentation separates drivers/confirmation/passed checks, Clear includes verdict, report identity resets filters, and preview warnings have a visible disclosure |
| Locked Premium named profiles but did not demonstrate why comparison matters | Upgrade value depended on explanation rather than product evidence | A bounded count shows how many shared notices differ across profiles while keeping gated reports hidden and adding no score |

Native checks cover the pure review-point, reason-grouping, disagreement-count, and deterministic
fixture contracts. Light/dark portrait inspection covers the generated first-run view. The fresh
`3cf20ed` Debug pass covers keyboard navigation, current Test Store outcomes, Increase Contrast,
Reduce Transparency, and bounded large text. The latest packaged Profile Builder evidence remains
dated, while hands-on VoiceOver speech/focus is an optional accessibility follow-up described
below.

## Contract reconciliation

| Contract | Audit conclusion |
|---|---|
| Verdict authority | Python remains the only implementation of `open_documents`, `watch`, and `reject`; Swift and Tk are presentation layers |
| Portfolio Workspace | Strict schema 1, one to five unique names, one shared ordered notice set and review point, complete schema-3 nested reports, distinct profile hashes, shared notice hash, and no ranking |
| Existing single-profile paths | `demo`, `qualify`, Tk UI, and single-profile reports keep their published behavior; Portfolio is additive |
| Private native bridge | Only portfolio execution, workspace normalization, and notice inspection are exposed; no shell and bounded output/time/environment |
| Native decoding | Envelope, profiles, totals, result identities, ordered shared metadata, digests, and provenance fail closed before presentation |
| Free/Premium | Free retains one complete analysis and schema-3 export; entitlement adds remaining reports, comparison, and exact portfolio export without changing verdict bytes |
| RevenueCat | Official SDK is pinned; Test Store is Debug-only and process-local; exact offering/package/product are required; Release cannot configure a key |
| Persistence | Only two opt-in security-scoped file bookmarks persist; files are revalidated and never auto-run; reports, review point, and key remain session-only |
| Failure retention | CLI atomic output preserves an old file; Next Gen preserves its last valid report; legacy Tk intentionally clears results when selected input changes |
| Privacy/network | Qualification stays local; `fetch-ted` is the only Python product fetch path; RevenueCat receives normal SDK identifiers/operations only after explicit Debug configuration |
| Packaging | Embedded private Python core, bundled fixtures/licenses, ad-hoc signature, checksum, manifest, worktree-independent smoke; no notarization or trusted installer |

## Documentation architecture delivered

The repository now has a deliberate reading order instead of one large narrative:

- root `AGENTS.md` gives agents a five-minute on-ramp, invariants, and external-action boundaries;
- `docs/DEVELOPMENT.md` owns the code map, exact gates, packaging provenance rules, change-impact
  map, and definition of done;
- `docs/DOCUMENTATION.md` defines layers, sources of truth, evidence vocabulary, release terms, and
  update triggers;
- `docs/README.md` routes users, maintainers, agents, auditors, and submission work to the right
  layer;
- `docs/PROJECT_STATUS.md` is the only owner of mutable totals, exact audited revisions, artifact
  provenance, and open readiness gates;
- architecture, security, limitations, user guidance, evidence, runbook, roadmap, and submission
  copy now link to their owner instead of silently diverging.

New public documents are in the exact allow-list and source distribution. Metadata tests validate
the root on-ramp, documentation links, CI/native gates, and public-tree membership.

## Release classification

| Surface | Audit conclusion |
|---|---|
| Published Python/Tk `v0.2.0-alpha.1` | Existing immutable developer prerelease; experimental and unsigned |
| Portfolio Workspace source | Implemented, deterministic, tested, and appropriate for source evaluation; not part of the published tag |
| Next Gen source | Remediated competition candidate with coherent Free/Premium and Debug/Release contracts |
| Current SSD `.app` | Self-contained release-configuration artifact named in project status; manifest/checksum/signature/ZIP/smoke verified, ad-hoc signed, not notarized, and not transaction evidence |
| External macOS product release | **Not ready**: no Developer ID/notarization, supported installer/update path, production billing decision, or external workflow validation |
| Final Shipaton submission | **Not ready**: the private Devpost, public video, and final-link/submission gates are open; VoiceOver and independent-user evidence are optional follow-ups |

“All checks green” means the scoped repository/package gate passed for the named revision. It does
not mean the app is publicly released, the manual evidence is current, or the Devpost form is
submitted.

## Residual risks and next evidence

Required submission work:

1. Complete the visual reCAPTCHA manually and inspect the private Devpost project fields without
   submitting.
2. Produce the public demo from the exact final candidate.
3. Re-run local and pushed CI gates, verify public repository/video links while logged out, and
   complete the final submission only after explicit owner approval.

Optional future evidence:

- when sound is appropriate, manually exercise Test Store success, cancellation, failure, retry,
  and restore with VoiceOver and verify spoken announcements plus recovery focus;
- if future product validation is useful, run opt-in supplier/procurement sessions with synthetic,
  public, or fully de-identified inputs and make only evidence-backed product changes;
- treat signing/notarization, trusted distribution, production billing, and public support as
  separate post-competition decisions rather than promoting the evaluation artifact by wording
  alone.

## Re-audit triggers

Repeat this reconciliation after a schema/verdict change, dependency update, native bridge,
persistence or entitlement change, new packaged candidate, completed manual evidence pass, or
release/submission decision. Start from [the developer guide](DEVELOPMENT.md), record current facts
in [project status](PROJECT_STATUS.md), and keep dated manual evidence attached to the exact build
that produced it.
