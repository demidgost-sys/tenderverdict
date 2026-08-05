# Technical audit

- Audit date: **2026-08-05**
- Baseline inspected: `79186da7e83e40284cca9f34d658f6e2a0e1b335`
- Remediated product revision and artifact: [project status](PROJECT_STATUS.md)
- Branch: `hackathon/revenuecat-next-gen-2026`
- Review surface: [draft pull request #12](https://github.com/demidgost-sys/tenderverdict/pull/12)
- Scope: Python and Swift source, tests, documentation, Git/CI state, public-tree policy, security
  boundaries, builder, and the existing SSD evaluation artifact

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
| Current SSD `.app` | **Pending rebuild** from the remediated product commit; the `79186da` artifact is superseded |
| External macOS product release | **Not ready**: no Developer ID/notarization, supported installer/update path, production billing decision, or external workflow validation |
| Final Shipaton submission | **Not ready**: final Debug transaction/accessibility evidence and remaining owner/submission gates are open |

“All checks green” means the scoped repository/package gate passed for the named revision. It does
not mean the app is publicly released, the manual evidence is current, or the Devpost form is
submitted.

## Residual risks and next evidence

1. Build a fresh Debug app from the eventual final product revision and manually exercise Test
   Store success, cancellation, failure, retry, refresh, relaunch, and restore with VoiceOver.
2. Inspect large text, Increase Contrast, and Reduce Transparency on that same final UX revision.
3. Run three opt-in supplier/procurement sessions with synthetic, public, or fully de-identified
   inputs and make only evidence-backed product changes.
4. Confirm entrant student/email state and inspect the private Devpost fields in the owner's
   account.
5. Re-run local, packaged, and pushed CI gates after any product, dependency, or asset change.
6. Treat signing/notarization, trusted distribution, production billing, and public support as
   separate decisions rather than promoting the competition artifact by wording alone.

## Re-audit triggers

Repeat this reconciliation after a schema/verdict change, dependency update, native bridge,
persistence or entitlement change, new packaged candidate, completed manual evidence pass, or
release/submission decision. Start from [the developer guide](DEVELOPMENT.md), record current facts
in [project status](PROJECT_STATUS.md), and keep dated manual evidence attached to the exact build
that produced it.
