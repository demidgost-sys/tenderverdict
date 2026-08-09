# TenderVerdict project status and Shipaton readiness

- Snapshot date: **2026-08-09**
- Competition branch: `hackathon/revenuecat-next-gen-2026`
- Audit baseline: `79186da7e83e40284cca9f34d658f6e2a0e1b335` (**superseded**)
- Pushed remediation baseline: `24b760a671efc9c2c2d54dc6cf4607ed730a293f`
- Current polished product revision: `cbe8b2071996edc2621a16cc9d10ce1ada63766e`
- Current hands-on evidence revision: `217c091d21d7b997f1271abc7e263e49e6de8478`
- Current candidate: **clean committed product revision, fresh Release and Debug packages,
  complete local gate, a final silent Test Store/Judge Access receipt, and draft-PR validation on
  the pushed competition-branch head**
- Local integration state: **the public-safe RevenueCat receipt and silent video-production handoff
  are combined on an isolated unpushed branch; the recorded/public video and exact pushed-head CI
  remain final gates**
- Review surface: [draft pull request #12](https://github.com/demidgost-sys/tenderverdict/pull/12)
- Competition-branch state: **current polish is committed for the draft PR; not released and not
  submitted to Devpost**

This is the canonical progress ledger for the competition branch. It records what was built, why
it matters, what evidence exists, and what remains. Detailed technical contracts stay in the
[architecture](ARCHITECTURE.md), competition facts stay in the
[evidence record](SHIPATON_EVIDENCE.md), and future ordering stays in the
[roadmap](../ROADMAP.md). The current source, package, RevenueCat, security, and silent
accessibility findings are consolidated in the [technical audit](TECHNICAL_AUDIT.md).

## Executive summary

TenderVerdict began the competition branch as a released local single-profile developer alpha.
The branch now adds a bounded Portfolio Workspace, a native SwiftUI macOS application, an official
RevenueCat Test Store flow, a self-contained app builder, a judge-facing Portfolio Signal plus
review and comparison UX, entitlement-aware shareable HTML review briefs, submission assets, and
reproducible quality gates without changing the existing three-verdict qualification semantics.

Competition implementation and final-submission readiness are intentionally kept separate:

| Readiness lens | Completed | Meaning |
|---|---:|---|
| Local Shipaton implementation | **Complete for the declared competition scope** | The product, monetization path, clean package, Profile Builder, guided import, continuity, large-list review, comparison drill-down, and silent settings QA are complete; VoiceOver and independent workflow validation are optional follow-ups |
| Final submission | **9 / 12 gates (75%)** | Public source, the working app, RevenueCat evidence, organizer clarification, assets, draft text, pushed-revision CI, and entrant verification exist; the private field inventory is complete, but a required form attestation conflicts with the store-exempt Next Gen route, and the public video/final-link gates remain |
| Public product release | **Not ready** | The app is an ad-hoc-signed competition prototype without notarization, a trusted installer, production billing, or demonstrated external workflow fit |

Only the final-submission percentage counts explicit equal-weight gates. Optional VoiceOver and
independent workflow validation do not reduce competition implementation readiness. None of these
labels is a probability of winning, a quality score, or a public-release claim.

## Why the competition work matters

The competition branch makes one product idea substantially clearer: a supplier can keep one
complete tender-analysis workflow free, while a team that repeatedly reviews the same notice feed
for several entities or service profiles can pay for a Portfolio Workspace.

The implementation preserves the trust model:

- one canonical Python engine owns `open_documents`, `watch`, and `reject`;
- the same notices, review point, order, and provenance are used for every profile;
- RevenueCat controls only the native presentation entitlement, not the qualification result;
- Free retains the complete first-profile queue, reasoning, source links, shareable review brief,
  and schema-3 JSON export;
- Premium reveals up to five independent reports, a comparison matrix, an all-profile review brief,
  and exact portfolio JSON without inventing a score, ranking, recommendation, or automatic bid
  decision;
- local files remain local and no account, first-party telemetry, hosted backend, or production
  payment was added; an explicitly configured Debug evaluation still uses RevenueCat's normal SDK
  identifiers and Test Store operations.

This turns the project from a monetization mock-up into a coherent repeated-use workflow while
keeping the published open-source CLI honest and useful.

## Completed capability map

| Layer | Delivered result | Evidence |
|---|---|---|
| Existing product | Single-profile CLI, library, Tk desktop, deterministic reports, TED metadata adapter, and `v0.2.0-alpha.1` remain available | Existing release plus regression suite |
| Portfolio core | Workspace schema v1, one to five profiles, strict validation, shared notice input, schema-3 nested reports, deterministic schema-1 aggregate JSON, stdout, and atomic output | Python models, workflow, CLI, fixtures, and tests |
| Native application | SwiftUI app loads local workspace/notices, validates an explicit review point, runs the canonical embedded core, preserves the last valid report after failure, distinguishes bundled/current/previous results, makes control/bidi metadata visible, and exports entitlement-appropriate deterministic HTML briefs or JSON | Source build, Debug/Release native checks, packaged smoke, and hands-on flow |
| Workspace authoring | Native Profile Builder creates, renames, reorders, validates, and saves one to five complete profiles; compact layouts retain their actions and field errors are specific; the strict Python normalizer remains the canonical acceptance boundary | Strict Swift workspace codec, private core normalizer, launcher tests, source smoke, and previous `682c040` compact-sheet inspection; this flow is unchanged in the current source |
| Notice import | CSV or JSON selection produces a bounded normalized preview, record count, canonical fields, visible warnings, and missing-field diagnostics before analysis | Private `inspect-notices` launcher contract, strict Swift decoder, and launcher/native checks |
| Free experience | Complete first-profile review queue with text, buyer, deadline-presence, and verdict filters; grouped verdict drivers/checks; complete filter reset; empty state; safe supplied-source links; a self-contained first-profile review brief; and one complete schema-3 export | Native query/export/brief checks, packaged headless render, source smoke, and existing accessibility inspection |
| Premium experience | Entitlement-backed access to all one to five profile reports, a searchable comparison matrix, stable notice/profile reasoning drill-down, an all-profile review brief, and a locked-state disagreement preview that discloses no gated reasoning | Stable-identity projection/disagreement/brief checks, packaged headless render, and Test Store unlock evidence |
| Product hierarchy | The first screen promises a clear next step for every supplier profile, shows shared notices/profile count/changed outcomes before file controls, and explains the complete Free profile versus the five-profile Portfolio value before technical Test Store status | Current packaged light/dark renders plus previous `682c040` hands-on scroll-state inspection |
| RevenueCat | Official Apple SDK `5.83.0`; Debug requires offering `supplier_profiles_plus`, package `$rc_monthly`, and product `supplier_profiles_plus_monthly`; cancellation, failure, retry, purchase, forced-current entitlement refresh, foreground refresh, restore-after-expiry offering recovery, and RevenueCat-backed Judge Access are implemented | Twenty native contract checks cover identifiers, access sources, the 2026 cutoff, truthful expiration copy, fail-closed builds, and accessibility outcomes; the final silent `217c091` receipt covers the complete Test Store lifecycle plus Judge refresh, Restore, foreground, relaunch, and the unmodified archive bundle |
| Secret boundary | No key committed or bundled; only process-local Debug `test_` configuration is accepted; Release exposes no key field and refuses configuration before any SDK call | Source review, scans, and Debug/Release native checks |
| Local continuity | File continuity is explicit opt-in and stores only two security-scoped bookmarks; Forget clears them, report data and review points are not persisted, and reopening never auto-runs analysis | Source review and native checks |
| Accessibility | Terminal RevenueCat and Judge Access states map to announcements and recovery focus; input controls and bidi-formatting characters render visibly; layout/color treatments respond to increased contrast and reduced transparency | Exact `cbe8b20` silent AX inspection found named native roles for the visible controls and comparison cells; spoken VoiceOver outcomes remain intentionally unverified |
| Packaging | Reproducible embedded-runtime `.app`, configuration-specific checks, ad-hoc signature, worktree-independent smoke and HTML-brief render, zip, SHA-256, and manifest | Fresh Release and Debug artifacts from exact clean revision `cbe8b20`; details below |
| Presentation | Exact icon, refreshed light/dark-reviewed portrait screenshot, current static report screenshot, genuine unlocked and VoiceOver evidence, human-facing Devpost copy, literal brief entry points, runbook, demo script, architecture, user guide, scorecard, and UX audit | `HACKATHON.md`, `submission/`, `demo/`, and `docs/` |
| Quality | 125 Python tests including 6 private-launcher and 3 release-scanner tests; 20 native contract checks in both Debug and Release; Ruff, Mypy, Swift format, public-tree validation, security scan, source smoke, package/distribution checks, platform builds, and CodeQL | The exact product revision has fresh local source/package evidence; draft PR #12 is the pushed-head CI record |

## Current clean evaluation artifact

| Fact | Evidence |
|---|---|
| Product revision | `cbe8b2071996edc2621a16cc9d10ce1ada63766e` |
| Artifact directory | `dist/next-gen-release-cbe8b20/` (ignored local output; SSD was not mounted) |
| App / archive | `TenderVerdictNextGen.app` (53 MiB) / `TenderVerdictNextGen-macos.zip` (18 MiB) |
| Archive SHA-256 | `77b25f7a0468603d49a3d65458540e34c9490097b5795c92c4c02034616dfa2f` |
| Manifest | `version=0.2.0a1`, `source_dirty=false`, `build_configuration=release`, `test_store_enabled=false`, RevenueCat `5.83.0`, `api_key_included=false`, `notarized=false` |
| Platform / trust | macOS 13+, arm64 host build, ad-hoc signature, no Team ID, not a universal or notarized app |
| Builder evidence | 20 Release-native checks, embedded workspace/notice contracts, signature verification, worktree-independent smoke, checksum creation, and ZIP integrity passed |

This package is the current self-contained no-key evaluation artifact. It is not Test Store
transaction evidence; that requires the separate Debug package and process-local key. The final
pass kept the small outputs in ignored `dist/` because the SSD was not mounted; older ignored
outputs must still be selected by the exact revision directory rather than filename alone.

## Current clean Debug entitlement artifact

| Fact | Evidence |
|---|---|
| Evidence revision | `217c091d21d7b997f1271abc7e263e49e6de8478` |
| Artifact directory | Ignored external QA output; no machine-local path is published |
| App / archive | `TenderVerdictNextGen.app` / `TenderVerdictNextGen-macos.zip` (21,793,093 bytes) |
| Archive SHA-256 | `ee1e30696deb5f322c81d8bdfd2e6b871d5467a7bc4a53f6dac7f12ab76f0f7a` |
| Manifest | `version=0.2.0a1`, `source_dirty=false`, `build_configuration=debug`, `test_store_enabled=true`, RevenueCat `5.83.0`, `api_key_included=false`, `notarized=false` |
| Builder evidence | 20 Debug-native checks, embedded smoke, ad-hoc signature verification, checksum creation, and ZIP integrity passed before the manual run |
| Current manual outcome | Missing/invalid key, offering, cancel, simulated failure, retry, Test Store success, immediate Restore, foreground, relaunch, natural accelerated-expiry locked/offering recovery, Judge refresh/Restore/foreground/relaunch, and the unmodified archive bundle passed; no real payment occurred |
| Judge window | Existing RevenueCat `Until` December 31, 2026 exceeds the safe October 14 boundary and was left unchanged |
| Silent boundary | VoiceOver, TTS, microphone, sound playback, and audio files were not launched |

The process-local key was supplied only to the launched process and is absent from both bundles and
the repository. The public-safe receipt in `submission/evidence/README.md` records the exact
outcome matrix and the observed roughly 30-minute live expiry as server-timing variance rather than
a broader guarantee. VoiceOver was never launched and system output remained silent.

## Local implementation and optional-validation ledger

| # | Milestone | State |
|---:|---|---|
| 1 | Immutable workspace and run models reuse the canonical profile/report types | `DONE` |
| 2 | Workspace accepts one to five normalized, uniquely named profiles and rejects invalid input as a unit | `DONE` |
| 3 | Notices are loaded once with shared order, review point, metadata, and provenance | `DONE` |
| 4 | `portfolio` provides deterministic stdout and atomic file output without changing existing commands | `DONE` |
| 5 | Boundary, ordering, empty-input, serialization, failure-retention, and network-isolation tests exist | `DONE` |
| 6 | Swift decodes and validates the complete portfolio contract before presentation | `DONE` |
| 7 | Native local workspace/notices selection and explicit review-point execution work | `DONE` |
| 8 | Free exposes the complete first-profile report, HTML brief, and schema-3 JSON | `DONE` |
| 9 | Premium exposes all profile reports, comparison, HTML brief, and exact portfolio JSON without modifying verdict semantics | `DONE` |
| 10 | Invalid runs preserve the previous valid result and atomic export contract | `DONE` |
| 11 | Self-contained macOS packaging works without a source checkout or system Python | `DONE` |
| 12 | Official RevenueCat Apple SDK is pinned and linked | `DONE` |
| 13 | Offering, cancel, failure, retry, purchase, and entitlement unlock paths work in Test Store | `DONE` |
| 14 | Relaunch refresh and `restorePurchases()` recover the entitlement | `DONE` |
| 15 | Missing, non-Test, and retained-secret cases fail closed | `DONE` |
| 16 | Free review queue, verdict filters, disclosure, human next steps, and empty state are implemented | `DONE` |
| 17 | Premium comparison, safe source links, shareable HTML presentation, and offering recovery are implemented | `DONE` |
| 18 | Submission assets and the public documentation package, including the original brief's literal entry-point filenames, are generated and validated | `DONE` |
| 19 | The complete local/repository gate set passed on one clean pushed implementation commit | `DONE` — current product revision `cbe8b20` has the complete local/package evidence above; draft PR #12 records the branch checks |
| 20 | VoiceOver asynchronous outcomes plus Increase Contrast, Reduce Transparency, and large-text variants | `OPTIONAL_ACCESSIBILITY_FOLLOW_UP` — keyboard, Increase Contrast, Reduce Transparency, and temporary large-text rendering passed on the fresh Debug revision; hands-on VoiceOver speech/focus remains unverified and is not a submission gate |
| 21 | Independent workflow sessions and evidence-backed product changes | `OPTIONAL_FUTURE_VALIDATION` — two maintainer-observed filter micro-fixes are complete; no external workflow session or user-value result is claimed or required for the current submission |
| 22 | Native profile builder/editor for one to five complete profiles | `DONE` |

**Result: the declared competition implementation scope is complete.** Items 20–21 are explicitly
optional follow-ups and are excluded from readiness. Any later accessibility pass still uses Test
Store only and does not require a real payment, production API key, hosted backend, or App Store
release.

## Final submission gate ledger

| # | Gate | State |
|---:|---|---|
| 1 | Public repository contains source, assets, instructions, and Apache-2.0 license | `READY` |
| 2 | Working macOS source and self-contained app path are reproducible | `READY` |
| 3 | Official RevenueCat SDK and substantive Test Store entitlement flow are evidenced | `READY_TECHNICALLY` |
| 4 | 1024×1024 icon is generated and structure-checked | `READY` |
| 5 | 1179×2556 frameless portrait screenshot is generated and structure-checked | `READY` |
| 6 | Devpost copy exists without a key, private identifier, or unsupported payment claim | `READY_DRAFT` |
| 7 | Current pushed implementation revision passes all required CI checks | `READY` — draft PR #12 is the authoritative pushed-head CI record at `217c091`; the isolated integration head remains unpushed |
| 8 | Organizer confirms Test Store-only eligibility | `READY` — Shipaton Manager Perttu Lähteenlahti answered on 2026-08-05 that Test Store is enough for Next Gen |
| 9 | Active-student status and qualifying academic email are verified in the entrant account | `READY` — current-student status, TU Graz affiliation, July 2028 graduation, and the academic-domain email were confirmed in Devpost |
| 10 | Exact private Devpost project fields are inspected and every required attestation has a truthful path | `BLOCKED_FORM_RULE_CONFLICT` — the authenticated field inventory and saved draft readback are complete, but the required store-release checkbox has no No/Next Gen path; a field-specific organizer correction or written instruction is pending |
| 11 | Public captioned macOS demo under two minutes is published | `PRODUCTION_HANDOFF_READY / PUBLIC_MEDIA_OPEN` — the exact 1:49 silent animatic, captions, manifests, and owner-recording kit exist locally; no final recorded or public video is claimed |
| 12 | Final commit, repository URL, video URL, and submitted view are checked while logged out | `FINAL_GATE` |

**Result: 9 of 12 submission gates ready.** The remaining gates are a truthful resolution of the
private-form conflict, the recorded/public video, and the exact pushed-head logged-out
link/submission review. Completing a field inventory or a silent animatic does not close those
gates.

## Reconciliation with the previous plans

| Plan slice | Current result |
|---|---|
| Portfolio Workspace Python foundation | `COMPLETE` |
| Native SwiftUI shell and canonical JSON adapter | `COMPLETE` |
| Free/Premium RevenueCat projection | `COMPLETE` |
| Self-contained packaging and submission assets | `COMPLETE` |
| Test Store transaction, refresh, relaunch, and restore evidence | `COMPLETE_CURRENT_RUNTIME` — the clean `217c091` silent receipt covers the complete Test Store lifecycle, natural expiry recovery, Judge refresh/Restore/foreground/relaunch, and the unmodified checksummed archive bundle |
| Judge-facing review queue, comparison matrix, shareable brief, safe links, and visual QA | `COMPLETE` |
| Clean implementation commit and full PR CI | `COMPLETE_CURRENT` — product revision `cbe8b20` is clean, packaged, pushed, and covered by the current draft-PR head |
| Advanced macOS accessibility variants | `OPTIONAL_ACCESSIBILITY_FOLLOW_UP` — keyboard order, increased contrast, reduced transparency, and temporary large-text rendering passed; hands-on VoiceOver announcements/focus remain untested and are not a submission gate |
| Native Profile Builder | `COMPLETE` — creates, renames, reorders, validates, and saves one to five full profiles |
| Import wizard | `COMPLETE_BOUNDED` — normalized preview, canonical fields, and missing-field guidance exist; arbitrary user-defined column mapping is intentionally excluded |
| Workspace continuity | `COMPLETE_OPT_IN` — only security-scoped workspace/notices bookmarks are remembered, Forget is explicit, and no report, key, file content, review point, or automatic run is persisted |
| Matrix-cell reasoning drill-down | `COMPLETE` — stable result identity opens the matching profile/notice reasoning without relying on filtered offsets |
| Search and buyer/deadline filters for large files | `COMPLETE` — review and comparison surfaces use pure bounded queries and stable identities |
| Independent workflow validation | `OPTIONAL_FUTURE_VALIDATION` — no external-user outcome is claimed or required for the current competition entry |

## What is verified, and what must not be claimed

Verified:

- current product revision `cbe8b20` passes 125 Python tests, 20 native checks in both Debug
  and Release, Ruff, Mypy, Swift format, public-tree, security, source-smoke, asset, distribution,
  and diff gates locally; the linked draft PR is the authoritative live CI record;
- its clean Release package records `source_dirty=false`, disables Test Store in Release, passes the
  embedded-core/signature/checksum/ZIP/worktree-independent smoke gates, and is arm64/ad-hoc signed;
- the unchanged Free/Premium brief, light/dark rendering, and filter interactions retain their
  earlier package evidence and remain covered by the current native/source contracts;
- the clean `cbe8b20` Debug package passed granted-entitlement refresh without relaunch, Restore,
  foreground re-entry, full relaunch, and genuine unlocked capture; the earlier clean `3cf20ed`
  package remains the purchase/cancel/failure/retry baseline;
- keyboard navigation, Increase Contrast, Reduce Transparency, and a temporary large-text render
  were checked hands-on without retaining a source modification;
- Shipaton Manager Perttu Lähteenlahti confirmed on 2026-08-05 that Test Store is enough for the
  Next Gen category;
- Shipaton Manager Jaewoong Eum confirmed that a macOS app is eligible and has no judging
  disadvantage;
- the entrant's TU Graz academic-domain email and active-student profile are verified, and the
  entrant has joined the Shipaton in Devpost;
- the exact `217c091` Debug package passed the complete silent Test Store lifecycle, natural
  accelerated-expiry recovery, Judge Access refresh/Restore/foreground/relaunch, and an independent
  check of the unmodified checksummed archive; the existing grant remains unchanged through
  December 31, 2026;
- no real payment was made and no usable key is stored in the repository or evidence;
- Free is a complete single-profile workflow rather than a disabled demo;
- existing single-profile report semantics remain unchanged.

Not verified and therefore not claimable:

- that the required store-release attestation has a truthful Next Gen answer or that the final
  submitted view has been audited;
- that a public video exists;
- that actual post-change VoiceOver purchase/cancel/failure outcomes pass on a fresh final Debug
  package;
- that the app is notarized, suitable for a public consumer release, or validated by external
  procurement users;
- that the completed competition work stayed within the initial 25 active-hour target, because no
  reliable active-time timer was maintained;
- that TenderVerdict reads full procurement documents, provides legal advice, predicts outcomes,
  or decides whether to bid.

## Required submission order

1. Wait for a form correction or written field-specific organizer instruction; do not check the
   store-release attestation or save the prefilled Additional info as if a store release existed.
2. Record and finish the public demo from the exact final candidate, then publish only with owner
   authorization.
3. Push only with owner authorization, wait for exact-head CI, and verify the repository, commit,
   video, and entry while logged out.
4. Stop again before accepting Terms or submitting; both require explicit owner approval.

## Optional future validation

- When sound is appropriate, exercise success, cancellation, failure, retry, and restore with
  VoiceOver and confirm each spoken announcement and recovery focus exactly once.
- If future product validation is useful, run opt-in workflow sessions with public, synthetic, or
  fully de-identified notices and document only evidence-backed adjustments.
- Refresh the dashboard readback during a later continuous evidence take if stronger supplemental
  RevenueCat evidence is useful.

Cross-profile ranking, automatic bidding, confidential-document ingestion, hosted accounts,
analytics, production billing, and a verdict-engine rewrite remain outside the plan because they
increase risk without closing the current competition evidence gap.
