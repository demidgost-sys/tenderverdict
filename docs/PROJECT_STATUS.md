# TenderVerdict project status and Shipaton readiness

- Snapshot date: **2026-08-05**
- Competition branch: `hackathon/revenuecat-next-gen-2026`
- Verified implementation baseline: `33dbe87f928575dd168b64e6a10022cf79d1d000`
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
| Local Shipaton implementation | **19 / 22 milestones (86%)** | The product, monetization path, packaging, judge-facing UX, and current QA baseline are implemented; advanced accessibility, user validation, and the profile builder remain |
| Final submission | **7 / 12 gates (58%)** | Public source, the working app, RevenueCat evidence, assets, draft text, and current CI exist; entrant, organizer, private-form, video, and final-link gates remain |
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
- local files remain local and no account, telemetry, hosted backend, or production payment was
  added.

This turns the project from a monetization mock-up into a coherent repeated-use workflow while
keeping the published open-source CLI honest and useful.

## Completed capability map

| Layer | Delivered result | Evidence |
|---|---|---|
| Existing product | Single-profile CLI, library, Tk desktop, deterministic reports, TED metadata adapter, and `v0.2.0-alpha.1` remain available | Existing release plus regression suite |
| Portfolio core | Workspace schema v1, one to five profiles, strict validation, shared notice input, schema-3 nested reports, deterministic schema-1 aggregate JSON, stdout, and atomic output | Python models, workflow, CLI, fixtures, and tests |
| Native application | SwiftUI app loads local workspace/notices, accepts an explicit review point, runs the canonical embedded core, preserves the last valid report after failure, and exports exact JSON | Source build, native checks, packaged smoke, and hands-on flow |
| Free experience | Complete first-profile review queue with buyer, deadline, verdict, next step, filters, progressive reasons/unknowns, empty state, and safe supplied-source links | Native UX audit and accessibility tree inspection |
| Premium experience | Entitlement-backed access to all one to five profile reports and a notice-by-profile comparison matrix | Native projection checks and Test Store unlock evidence |
| RevenueCat | Official Apple SDK `5.83.0`, current offering, localized package, cancellation, failure, retry, purchase, entitlement refresh, relaunch, and restore | Packaged Debug Test Store pass and dashboard observation |
| Secret boundary | No key committed or bundled; only process-local `test_` configuration is accepted; missing/invalid configuration fails closed | Source review, scans, and packaged tests |
| Packaging | Reproducible embedded-runtime `.app`, ad-hoc signature check, worktree-independent smoke test, zip, and SHA-256 file | `tools/build_next_gen.py` and CI artifact |
| Presentation | Exact icon and portrait screenshot, genuine unlocked and VoiceOver evidence, Devpost draft, runbook, demo script, architecture, user guide, scorecard, and UX audit | `submission/` and `docs/` |
| Quality | 113 Python tests, 10 native contract checks, Ruff, Mypy, public-tree validation, security scan, package smoke, platform builds, CodeQL, and 18 green PR checks | Verified baseline `33dbe87` |

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
| 19 | The complete local/repository gate set passed on one clean pushed implementation commit | `DONE` |
| 20 | VoiceOver asynchronous outcomes plus Increase Contrast, Reduce Transparency, and large-text variants | `OPEN` |
| 21 | Three opt-in workflow sessions and two evidence-backed product changes | `OPEN` |
| 22 | Native profile builder/editor, if workflow evidence confirms JSON authoring is the main obstacle | `OPEN` |

**Result: 19 of 22 milestones complete.** Items 20–22 are the remaining local product work; they
do not require a real payment, production API key, hosted backend, or App Store release.

## Final submission gate ledger

| # | Gate | State |
|---:|---|---|
| 1 | Public repository contains source, assets, instructions, and Apache-2.0 license | `READY` |
| 2 | Working macOS source and self-contained app path are reproducible | `READY` |
| 3 | Official RevenueCat SDK and substantive Test Store entitlement flow are evidenced | `READY_TECHNICALLY` |
| 4 | 1024×1024 icon is generated and structure-checked | `READY` |
| 5 | 1179×2556 frameless portrait screenshot is generated and structure-checked | `READY` |
| 6 | Devpost copy exists without a key, private identifier, or unsupported payment claim | `READY_DRAFT` |
| 7 | Current pushed implementation revision passes all required CI checks | `READY_CURRENT_REVISION` |
| 8 | Organizer confirms Test Store-only eligibility, or the final entry explicitly accepts the disclosed risk | `OPEN` |
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
| Clean implementation commit and full PR CI | `COMPLETE` |
| Advanced macOS accessibility variants | `PARTIAL` — native semantics and VoiceOver restore pass; asynchronous and display-setting matrix remains |
| Native Profile Builder | `NOT STARTED` — intentionally waits for workflow evidence |
| Import wizard | `PARTIAL` — file selection and validation exist; mapping preview and guided correction do not |
| Workspace continuity | `NOT STARTED` — no silent persistence was added |
| Matrix-cell reasoning drill-down | `PARTIAL` — complete reasoning exists in reports and Free queue, but a matrix cell does not yet navigate to it |
| Search and buyer/deadline filters for large files | `NOT STARTED` — gated on a bounded 100+ notice fixture |
| Three real-user workflow sessions | `NOT STARTED` |

## What is verified, and what must not be claimed

Verified:

- the implementation baseline is pushed to a public draft branch and all 18 PR checks passed;
- the packaged local-file flow and embedded-core smoke test pass;
- Test Store purchase and restore changed the real entitlement-backed UI;
- no real payment was made and no usable key is stored in the repository or evidence;
- Free is a complete single-profile workflow rather than a disabled demo;
- existing single-profile report semantics remain unchanged.

Not verified and therefore not claimable:

- that Shipaton organizers accept Test Store-only as sufficient;
- that entrant student/email requirements are complete;
- that private Devpost fields or the final submitted view have been audited;
- that a public video exists;
- that the app is notarized, suitable for a public consumer release, or validated by external
  procurement users;
- that TenderVerdict reads full procurement documents, provides legal advice, predicts outcomes,
  or decides whether to bid.

## Next implementation order

1. Complete the bounded accessibility matrix and record pass/fail evidence.
2. Run three opt-in workflow sessions with public, synthetic, or fully de-identified notices.
3. Convert observed friction into at most two bounded changes; build the Profile Builder first only
   if JSON authoring is confirmed as the main obstacle.
4. Add a guided import preview, matrix drill-down, or large-list filters only when the workflow
   evidence selects that problem.
5. Re-run the complete gate set on the resulting implementation revision.
6. Resolve the organizer and entrant-account gates, inspect Devpost privately, and only then finish
   media and final submission work.

Cross-profile ranking, automatic bidding, confidential-document ingestion, hosted accounts,
analytics, production billing, and a verdict-engine rewrite remain outside the plan because they
increase risk without closing the current competition evidence gap.
