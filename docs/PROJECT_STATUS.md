# TenderVerdict project status and Shipaton readiness

- Snapshot date: **2026-08-05**
- Competition branch: `hackathon/revenuecat-next-gen-2026`
- Audit baseline: `79186da7e83e40284cca9f34d658f6e2a0e1b335` (**superseded**)
- Remediated product revision: **pending the clean audit commit**
- Current local candidate: **remediated source and complete source gate green; fresh clean package
  pending**
- Review surface: [draft pull request #12](https://github.com/demidgost-sys/tenderverdict/pull/12)
- Competition-branch state: **not released and not submitted to Devpost**

This is the canonical progress ledger for the competition branch. It records what was built, why
it matters, what evidence exists, and what remains. Detailed technical contracts stay in the
[architecture](ARCHITECTURE.md), competition facts stay in the
[evidence record](SHIPATON_EVIDENCE.md), and future ordering stays in the
[roadmap](../ROADMAP.md).

## Executive summary

TenderVerdict began the competition branch as a released local single-profile developer alpha.
The branch now adds a bounded Portfolio Workspace, a native SwiftUI macOS application, an official
RevenueCat Test Store flow, a self-contained app builder, judge-facing review and comparison UX,
submission assets, and reproducible quality gates without changing the existing three-verdict
qualification semantics.

Two readiness numbers are intentionally kept separate:

| Readiness lens | Completed | Meaning |
|---|---:|---|
| Local Shipaton implementation | **19 / 22 milestones (86%)** | The product, monetization path, Profile Builder, guided import, continuity, large-list review, and comparison drill-down are implemented; the clean remediation commit/package, post-change accessibility QA, and user validation remain |
| Final submission | **7 / 12 gates (58%)** | Public source, the working app, RevenueCat evidence, organizer clarification, assets, and draft text exist; refreshed current-revision CI, entrant, private-form, video, and final-link gates remain |
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
- Free retains the complete first-profile queue, reasoning, source links, and export;
- Premium reveals up to five independent reports and a comparison matrix without inventing a
  score, ranking, recommendation, or automatic bid decision;
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
| Native application | SwiftUI app loads local workspace/notices, accepts an explicit review point, runs the canonical embedded core, preserves the last valid report after failure, makes control/bidi metadata visible, and exports entitlement-appropriate deterministic JSON | Source build, Debug/Release native checks, packaged smoke, and hands-on flow |
| Workspace authoring | Native Profile Builder creates, renames, reorders, validates, and saves one to five complete profiles; the strict Python normalizer remains the canonical acceptance boundary | Strict Swift workspace codec, private core normalizer, launcher tests, and source smoke |
| Notice import | CSV or JSON selection produces a bounded normalized preview, record count, canonical fields, and missing-field diagnostics before analysis | Private `inspect-notices` launcher contract, strict Swift decoder, and launcher/native checks |
| Free experience | Complete first-profile review queue with text, buyer, deadline-presence, and verdict filters; progressive reasons/unknowns; empty state; safe supplied-source links; and one complete schema-3 export | Native query/export checks, source smoke, and existing accessibility inspection |
| Premium experience | Entitlement-backed access to all one to five profile reports, a searchable comparison matrix, and stable notice/profile reasoning drill-down | Stable-identity projection checks and Test Store unlock evidence |
| RevenueCat | Official Apple SDK `5.83.0`; Debug requires offering `supplier_profiles_plus`, package `$rc_monthly`, and product `supplier_profiles_plus_monthly`; cancellation, failure, retry, purchase, entitlement refresh, relaunch, and restore are implemented | Configuration-specific native checks plus historical packaged Debug Test Store/dashboard evidence |
| Secret boundary | No key committed or bundled; only process-local Debug `test_` configuration is accepted; Release exposes no key field and refuses configuration before any SDK call | Source review, scans, and Debug/Release native checks |
| Local continuity | File continuity is explicit opt-in and stores only two security-scoped bookmarks; Forget clears them, report data and review points are not persisted, and reopening never auto-runs analysis | Source review and native checks |
| Accessibility | Terminal RevenueCat states map to announcements and recovery focus; input controls and bidi-formatting characters render visibly; layout/color treatments respond to increased contrast and reduced transparency | Pure mapping/display checks and green source build; actual post-change async purchase outcome QA remains open |
| Packaging | Reproducible embedded-runtime `.app`, configuration-specific checks, ad-hoc signature, worktree-independent smoke, zip, SHA-256, and manifest | The `79186da` artifact is superseded by the audit; a clean artifact from the remediated product commit is pending |
| Presentation | Exact icon and portrait screenshot, genuine unlocked and VoiceOver evidence, Devpost draft, runbook, demo script, architecture, user guide, scorecard, and UX audit | `submission/` and `docs/` |
| Quality | 122 Python tests including 6 private-launcher and 3 release-scanner tests; 16 native contract checks in both Debug and Release; Ruff, Mypy, Swift format, public-tree validation, security scan, source smoke, package/distribution checks, platform builds, and CodeQL | Complete local source gate; refreshed packaged and pushed revision evidence pending |

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
| 8 | Free exposes the complete first-profile report and export | `DONE` |
| 9 | Premium exposes all profile reports without modifying verdict semantics | `DONE` |
| 10 | Invalid runs preserve the previous valid result and atomic export contract | `DONE` |
| 11 | Self-contained macOS packaging works without a source checkout or system Python | `DONE` |
| 12 | Official RevenueCat Apple SDK is pinned and linked | `DONE` |
| 13 | Offering, cancel, failure, retry, purchase, and entitlement unlock paths work in Test Store | `DONE` |
| 14 | Relaunch refresh and `restorePurchases()` recover the entitlement | `DONE` |
| 15 | Missing, non-Test, and retained-secret cases fail closed | `DONE` |
| 16 | Free review queue, verdict filters, disclosure, human next steps, and empty state are implemented | `DONE` |
| 17 | Premium comparison, safe source links, HTML polish, and offering recovery are implemented | `DONE` |
| 18 | Submission assets and the public documentation package are generated and validated | `DONE` |
| 19 | The complete local/repository gate set passed on one clean pushed implementation commit | `PARTIAL` — local gate is green; clean commit and refreshed PR CI are pending |
| 20 | VoiceOver asynchronous outcomes plus Increase Contrast, Reduce Transparency, and large-text variants | `PARTIAL` — implementation and pure checks are present; actual post-change purchase/cancel/failure announcement QA remains |
| 21 | Three opt-in workflow sessions and two evidence-backed product changes | `OPEN` |
| 22 | Native profile builder/editor for one to five complete profiles | `DONE` |

**Result: 19 of 22 milestones complete.** Items 19–21 are the remaining commit/evidence work. The
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
| 7 | Current pushed implementation revision passes all required CI checks | `PENDING_REFRESH` — the audited baseline is green; the remediation is not pushed yet |
| 8 | Organizer confirms Test Store-only eligibility | `READY` — Shipaton Manager Perttu Lähteenlahti answered on 2026-08-05 that Test Store is enough for Next Gen |
| 9 | Active-student status and qualifying academic email are verified in the entrant account | `OWNER_GATE` |
| 10 | Exact private Devpost fields are inspected after joining and signing in | `OWNER_GATE` |
| 11 | Public captioned macOS demo under two minutes is published | `OPEN_LATER` |
| 12 | Final commit, repository URL, video URL, and submitted view are checked while logged out | `FINAL_GATE` |

**Result: 7 of 12 submission gates ready.** The missing video is deliberately outside the current
product-development pass, but it remains necessary before final submission.

## Reconciliation with the previous plans

| Plan slice | Current result |
|---|---|
| Portfolio Workspace Python foundation | `COMPLETE` |
| Native SwiftUI shell and canonical JSON adapter | `COMPLETE` |
| Free/Premium RevenueCat projection | `COMPLETE` |
| Self-contained packaging and submission assets | `COMPLETE` |
| Test Store transaction, refresh, relaunch, and restore evidence | `COMPLETE` |
| Judge-facing review queue, comparison matrix, safe links, and visual QA | `COMPLETE` |
| Clean implementation commit and full PR CI | `IN_PROGRESS` — local gate is green; clean commit and refreshed PR CI are pending |
| Advanced macOS accessibility variants | `IMPLEMENTED_PENDING_MANUAL_QA` — terminal-state mapping, VoiceOver announcements, focus recovery, increased contrast, and reduced transparency are implemented; actual post-change async Test Store outcomes remain |
| Native Profile Builder | `COMPLETE` — creates, renames, reorders, validates, and saves one to five full profiles |
| Import wizard | `COMPLETE_BOUNDED` — normalized preview, canonical fields, and missing-field guidance exist; arbitrary user-defined column mapping is intentionally excluded |
| Workspace continuity | `COMPLETE_OPT_IN` — only security-scoped workspace/notices bookmarks are remembered, Forget is explicit, and no report, key, file content, review point, or automatic run is persisted |
| Matrix-cell reasoning drill-down | `COMPLETE` — stable result identity opens the matching profile/notice reasoning without relying on filtered offsets |
| Search and buyer/deadline filters for large files | `COMPLETE` — review and comparison surfaces use pure bounded queries and stable identities |
| Three real-user workflow sessions | `OPEN` |

## What is verified, and what must not be claimed

Verified:

- audited baseline `79186da` is public and its 18 PR checks passed; the linked draft PR is the
  authoritative check record for each newer pushed revision;
- the remediated source passes 122 Python tests, 16 native checks in both Debug and Release, Ruff,
  Mypy, Swift format, public-tree, security, source-smoke, asset, distribution, and diff gates;
- the previous packaged local-file flow and embedded-core smoke passed, but that artifact is
  superseded until the remediated product revision is packaged cleanly;
- Test Store purchase and restore changed the real entitlement-backed UI;
- Shipaton Manager Perttu Lähteenlahti confirmed on 2026-08-05 that Test Store is enough for the
  Next Gen category;
- Shipaton Manager Jaewoong Eum confirmed that a macOS app is eligible and has no judging
  disadvantage;
- no real payment was made and no usable key is stored in the repository or evidence;
- Free is a complete single-profile workflow rather than a disabled demo;
- existing single-profile report semantics remain unchanged.

Not verified and therefore not claimable:

- that entrant student/email requirements are complete;
- that private Devpost fields or the final submitted view have been audited;
- that a public video exists;
- that actual post-change VoiceOver purchase/cancel/failure outcomes pass on a fresh final Debug
  package;
- that the app is notarized, suitable for a public consumer release, or validated by external
  procurement users;
- that TenderVerdict reads full procurement documents, provides legal advice, predicts outcomes,
  or decides whether to bid.

## Next implementation order

1. Build a fresh final-revision Debug app and exercise actual Test Store purchase, cancel, failure,
   refresh, and restore outcomes with VoiceOver, Increase Contrast, Reduce Transparency, and a
   large-text setting; record pass/fail without retaining a key or customer identifier.
2. Run three opt-in workflow sessions with public, synthetic, or fully de-identified notices and
   document only evidence-backed adjustments.
3. Confirm the entrant student/email gate and inspect the private Devpost fields.
4. Only then finish the public demo and final logged-out repository/video/submission checks.

Cross-profile ranking, automatic bidding, confidential-document ingestion, hosted accounts,
analytics, production billing, and a verdict-engine rewrite remain outside the plan because they
increase risk without closing the current competition evidence gap.
