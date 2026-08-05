# TenderVerdict project status and Shipaton readiness

- Snapshot date: **2026-08-05**
- Competition branch: `hackathon/revenuecat-next-gen-2026`
- Audit baseline: `79186da7e83e40284cca9f34d658f6e2a0e1b335` (**superseded**)
- Pushed remediation baseline: `24b760a671efc9c2c2d54dc6cf4607ed730a293f`
- Current polished product revision: `34f100207e37e6b399c1ada2c65b4130c925b0df`
- Current hands-on evidence revision: `3cf20ed0d1607b7feb943109f72c1c528df55e5b`
- Current candidate: **clean committed product revision, fresh SSD package, complete local gate,
  fresh Debug Test Store/settings evidence, and draft-PR validation on the current branch head**
- Review surface: [draft pull request #12](https://github.com/demidgost-sys/tenderverdict/pull/12)
- Competition-branch state: **current polish is committed for the draft PR; not released and not
  submitted to Devpost**

This is the canonical progress ledger for the competition branch. It records what was built, why
it matters, what evidence exists, and what remains. Detailed technical contracts stay in the
[architecture](ARCHITECTURE.md), competition facts stay in the
[evidence record](SHIPATON_EVIDENCE.md), and future ordering stays in the
[roadmap](../ROADMAP.md).

## Executive summary

TenderVerdict began the competition branch as a released local single-profile developer alpha.
The branch now adds a bounded Portfolio Workspace, a native SwiftUI macOS application, an official
RevenueCat Test Store flow, a self-contained app builder, a judge-facing Portfolio Signal plus
review and comparison UX, entitlement-aware shareable HTML review briefs, submission assets, and
reproducible quality gates without changing the existing three-verdict qualification semantics.

Two readiness numbers are intentionally kept separate:

| Readiness lens | Completed | Meaning |
|---|---:|---|
| Local Shipaton implementation | **20 / 22 milestones (91%)** | The product, monetization path, clean package, Profile Builder, guided import, continuity, large-list review, and comparison drill-down are implemented; silent settings QA passed, while VoiceOver and independent user validation remain |
| Final submission | **9 / 12 gates (75%)** | Public source, the working app, RevenueCat evidence, organizer clarification, assets, draft text, current-revision CI, and entrant verification exist; the project form, video, and final-link gates remain |
| Public product release | **Not ready** | The app is an ad-hoc-signed competition prototype without notarization, a trusted installer, production billing, or demonstrated external workflow fit |

These percentages count the explicit equal-weight milestones below. They are not a probability of
winning, a quality score, or a substitute for the open eligibility and submission gates.

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
| RevenueCat | Official Apple SDK `5.83.0`; Debug requires offering `supplier_profiles_plus`, package `$rc_monthly`, and product `supplier_profiles_plus_monthly`; cancellation, failure, retry, purchase, entitlement refresh, relaunch, and restore are implemented | Configuration-specific native checks plus a fresh `3cf20ed` packaged Debug runtime pass; dashboard readback remains the dated baseline |
| Secret boundary | No key committed or bundled; only process-local Debug `test_` configuration is accepted; Release exposes no key field and refuses configuration before any SDK call | Source review, scans, and Debug/Release native checks |
| Local continuity | File continuity is explicit opt-in and stores only two security-scoped bookmarks; Forget clears them, report data and review points are not persisted, and reopening never auto-runs analysis | Source review and native checks |
| Accessibility | Terminal RevenueCat states map to announcements and recovery focus; input controls and bidi-formatting characters render visibly; layout/color treatments respond to increased contrast and reduced transparency | Keyboard order, Increase Contrast, Reduce Transparency, and a temporary large-text render passed on `3cf20ed`; VoiceOver speech/focus was explicitly deferred |
| Packaging | Reproducible embedded-runtime `.app`, configuration-specific checks, ad-hoc signature, worktree-independent smoke and HTML-brief render, zip, SHA-256, and manifest | Fresh Release-configuration artifact from exact clean revision `34f1002` on the SSD; details below |
| Presentation | Exact icon, refreshed light/dark-reviewed portrait screenshot, current static report screenshot, genuine unlocked and VoiceOver evidence, human-facing Devpost copy, literal brief entry points, runbook, demo script, architecture, user guide, scorecard, and UX audit | `HACKATHON.md`, `submission/`, `demo/`, and `docs/` |
| Quality | 125 Python tests including 6 private-launcher and 3 release-scanner tests; 19 native contract checks in both Debug and Release; Ruff, Mypy, Swift format, public-tree validation, security scan, source smoke, package/distribution checks, platform builds, and CodeQL | Complete local gate and exact-HEAD Debug builder pass for `3cf20ed`; draft PR #12 is the authoritative pushed-branch CI record |

## Current clean evaluation artifact

| Fact | Evidence |
|---|---|
| Product revision | `34f100207e37e6b399c1ada2c65b4130c925b0df` |
| Artifact directory | `/Volumes/DemidMathSSD/MachineCaches/TenderVerdictShipaton/next-gen-artifacts-34f1002/` |
| App / archive | `TenderVerdictNextGen.app` (53 MiB) / `TenderVerdictNextGen-macos.zip` (19 MiB) |
| Archive SHA-256 | `6622cb65008067e9da6a0879820185e21c318a839d4fab2675d6c365c7b1c525` |
| Manifest | `version=0.2.0a1`, `source_dirty=false`, `build_configuration=release`, `test_store_enabled=false`, RevenueCat `5.83.0`, `api_key_included=false`, `notarized=false` |
| Platform / trust | macOS 13+, arm64 host build, ad-hoc signature, no Team ID, not a universal or notarized app |
| Builder evidence | 19 Release-native checks, embedded workspace/notice contracts twice with byte-identical output, signature verification, worktree-independent smoke, packaged Free/Premium HTML-brief renders, byte-matched light/dark headline renders, checksum verification, and ZIP integrity passed; filter interactions remain evidenced by the unchanged `69eed54` package |

This package is the current self-contained no-key evaluation artifact. It is not Test Store
transaction evidence; that requires a separate Debug package and process-local key. The ignored
repository `dist/` directory may still contain older output and must not be selected by filename.

## Current clean Debug transaction artifact

| Fact | Evidence |
|---|---|
| Evidence revision | `3cf20ed0d1607b7feb943109f72c1c528df55e5b` |
| Artifact directory | `/Volumes/DemidMathSSD/MachineCaches/TenderVerdictShipaton/next-gen-debug-3cf20ed/` |
| App / archive | `TenderVerdictNextGen.app` (about 63 MiB) / `TenderVerdictNextGen-macos.zip` (about 21 MiB) |
| Archive SHA-256 | `8439a1e2a28510c350ddf72ca5b2653f4680daebf1c0b71886b77fc84675ef30` |
| Manifest | `version=0.2.0a1`, `source_dirty=false`, `build_configuration=debug`, `test_store_enabled=true`, RevenueCat `5.83.0`, `api_key_included=false`, `notarized=false` |
| Builder evidence | 19 Debug-native checks, embedded smoke, ad-hoc signature verification, checksum verification, and ZIP integrity passed before the manual run |
| Manual Test Store outcome | Offering at localized `0,99 $`, cancellation, simulated failure, retry, valid purchase, immediate restore, and relaunch refresh all passed; no real payment was made |
| Manual settings outcome | Full keyboard traversal, Increase Contrast, Reduce Transparency, and a temporary `.accessibility3` screenshot-renderer override passed without clipping; the override was immediately reverted |

The process-local key was re-entered after relaunch, never stored by TenderVerdict, cleared from the
clipboard after the pass, and is absent from the bundle and repository. Test Store subscriptions
expire on an accelerated schedule: a later restore after expiry correctly returned the locked
state, while an immediate restore preserved access. VoiceOver was never launched in this pass and
system output remained muted.

## Local implementation milestone ledger

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
| 19 | The complete local/repository gate set passed on one clean pushed implementation commit | `DONE` — current product revision `34f1002` has the complete local/package evidence above; draft PR #12 records the branch checks |
| 20 | VoiceOver asynchronous outcomes plus Increase Contrast, Reduce Transparency, and large-text variants | `PARTIAL` — keyboard, Increase Contrast, Reduce Transparency, and temporary large-text rendering passed on the fresh Debug revision; VoiceOver speech/focus remains deliberately deferred |
| 21 | Three opt-in workflow sessions and two evidence-backed product changes | `PARTIAL` — two maintainer-observed filter micro-fixes are complete; three independent opt-in workflow sessions remain open |
| 22 | Native profile builder/editor for one to five complete profiles | `DONE` |

**Result: 20 of 22 milestones complete.** Items 20–21 are the remaining local evidence work. The
post-change accessibility pass uses Test Store only and does not require a real payment,
production API key, hosted backend, or App Store release.

## Final submission gate ledger

| # | Gate | State |
|---:|---|---|
| 1 | Public repository contains source, assets, instructions, and Apache-2.0 license | `READY` |
| 2 | Working macOS source and self-contained app path are reproducible | `READY` |
| 3 | Official RevenueCat SDK and substantive Test Store entitlement flow are evidenced | `READY_TECHNICALLY` |
| 4 | 1024×1024 icon is generated and structure-checked | `READY` |
| 5 | 1179×2556 frameless portrait screenshot is generated and structure-checked | `READY` |
| 6 | Devpost copy exists without a key, private identifier, or unsupported payment claim | `READY_DRAFT` |
| 7 | Current pushed implementation revision passes all required CI checks | `READY` — draft PR #12 is green on pushed evidence revision `3cf20ed`, which contains product revision `34f1002` |
| 8 | Organizer confirms Test Store-only eligibility | `READY` — Shipaton Manager Perttu Lähteenlahti answered on 2026-08-05 that Test Store is enough for Next Gen |
| 9 | Active-student status and qualifying academic email are verified in the entrant account | `READY` — current-student status, TU Graz affiliation, July 2028 graduation, and the academic-domain email were confirmed in Devpost |
| 10 | Exact private Devpost project fields are inspected after joining and signing in | `OPEN` — hackathon registration is complete, but project creation still stops before the private fields at visual reCAPTCHA; no project was created or submitted |
| 11 | Public captioned macOS demo under two minutes is published | `OPEN_LATER` |
| 12 | Final commit, repository URL, video URL, and submitted view are checked while logged out | `FINAL_GATE` |

**Result: 9 of 12 submission gates ready.** The remaining gates are the private project form, the
public video, and the final logged-out link/submission review. The video is deliberately outside the
current product-development pass, but it remains necessary before final submission.

## Reconciliation with the previous plans

| Plan slice | Current result |
|---|---|
| Portfolio Workspace Python foundation | `COMPLETE` |
| Native SwiftUI shell and canonical JSON adapter | `COMPLETE` |
| Free/Premium RevenueCat projection | `COMPLETE` |
| Self-contained packaging and submission assets | `COMPLETE` |
| Test Store transaction, refresh, relaunch, and restore evidence | `COMPLETE_CURRENT_RUNTIME` — fresh on packaged Debug revision `3cf20ed`; dashboard readback remains the dated baseline |
| Judge-facing review queue, comparison matrix, shareable brief, safe links, and visual QA | `COMPLETE` |
| Clean implementation commit and full PR CI | `COMPLETE_CURRENT` — product revision `34f1002` is clean, packaged, pushed, and covered by the current green draft-PR head |
| Advanced macOS accessibility variants | `PARTIAL_MANUAL_QA` — keyboard order, increased contrast, reduced transparency, and temporary large-text rendering passed; VoiceOver announcements/focus remain untested by explicit owner choice |
| Native Profile Builder | `COMPLETE` — creates, renames, reorders, validates, and saves one to five full profiles |
| Import wizard | `COMPLETE_BOUNDED` — normalized preview, canonical fields, and missing-field guidance exist; arbitrary user-defined column mapping is intentionally excluded |
| Workspace continuity | `COMPLETE_OPT_IN` — only security-scoped workspace/notices bookmarks are remembered, Forget is explicit, and no report, key, file content, review point, or automatic run is persisted |
| Matrix-cell reasoning drill-down | `COMPLETE` — stable result identity opens the matching profile/notice reasoning without relying on filtered offsets |
| Search and buyer/deadline filters for large files | `COMPLETE` — review and comparison surfaces use pure bounded queries and stable identities |
| Three real-user workflow sessions | `OPEN` |

## What is verified, and what must not be claimed

Verified:

- current evidence revision `3cf20ed` passes 125 Python tests, 19 native checks in both Debug
  and Release, Ruff, Mypy, Swift format, public-tree, security, source-smoke, asset, distribution,
  and diff gates locally; the linked draft PR is the authoritative live CI record;
- its clean SSD package records `source_dirty=false`, disables Test Store in Release, passes the
  embedded-core/signature/checksum/ZIP/worktree-independent smoke gates, and is arm64/ad-hoc signed;
- that current package rendered both Free and Premium HTML briefs outside the worktree, produced
  one versus three ordered profile sections, rendered current light/dark native screenshots, and
  passed the one-result and no-match filter interactions in its accessibility tree;
- the clean `3cf20ed` Debug package passed offering, cancel, simulated failure, retry, valid
  purchase, immediate restore, and relaunch refresh in the real entitlement-backed UI;
- keyboard navigation, Increase Contrast, Reduce Transparency, and a temporary large-text render
  were checked hands-on without retaining a source modification;
- Shipaton Manager Perttu Lähteenlahti confirmed on 2026-08-05 that Test Store is enough for the
  Next Gen category;
- Shipaton Manager Jaewoong Eum confirmed that a macOS app is eligible and has no judging
  disadvantage;
- the entrant's TU Graz academic-domain email and active-student profile are verified, and the
  entrant has joined the Shipaton in Devpost;
- no real payment was made and no usable key is stored in the repository or evidence;
- Free is a complete single-profile workflow rather than a disabled demo;
- existing single-profile report semantics remain unchanged.

Not verified and therefore not claimable:

- that the private Devpost project-submission fields or the final submitted view have been audited;
- that a public video exists;
- that actual post-change VoiceOver purchase/cancel/failure outcomes pass on a fresh final Debug
  package;
- that the app is notarized, suitable for a public consumer release, or validated by external
  procurement users;
- that the completed competition work stayed within the initial 25 active-hour target, because no
  reliable active-time timer was maintained;
- that TenderVerdict reads full procurement documents, provides legal advice, predicts outcomes,
  or decides whether to bid.

## Next implementation order

1. When sound is allowed again, exercise success, cancellation, failure, retry, and restore with
   VoiceOver and confirm each spoken announcement and recovery focus exactly once.
2. Run three opt-in workflow sessions with public, synthetic, or fully de-identified notices and
   document only evidence-backed adjustments.
3. Solve the visual Devpost reCAPTCHA manually, create the private project draft, and inspect its
   exact fields without submitting it.
4. Only then finish the public demo and final logged-out repository/video/submission checks.

Cross-profile ranking, automatic bidding, confidential-document ingestion, hosted accounts,
analytics, production billing, and a verdict-engine rewrite remain outside the plan because they
increase risk without closing the current competition evidence gap.
