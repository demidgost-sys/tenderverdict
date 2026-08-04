# TenderVerdict Next Gen — Devpost draft

> Draft only. Do not publish or submit until the final package, media, eligibility, and logged-out
> URL checks in `docs/HACKATHON_RUNBOOK.md` pass.

## Tagline

Explainable local tender triage across every supplier profile, with a RevenueCat-powered Portfolio
Workspace.

## Inspiration

A tender is not simply relevant or irrelevant to an entire company. The same notice may fit one
legal entity, country, service line, or deadline policy and fail another. Small supplier teams often
repeat that screening manually, lose the reasoning, and notice metadata gaps too late.

TenderVerdict began with a narrow promise: turn public-procurement metadata into an explainable
review queue, never a black-box bid decision. Next Gen extends that promise from one supplier
profile to a portfolio without taking the useful single-profile workflow away from free users.

## What it does

TenderVerdict reads normalized tender-notice metadata and applies deterministic rules for CPV fit,
geography, deadline lead time, notice type, and missing fields. Each notice becomes
`open_documents`, `watch`, or `reject`, with reasons, unknowns, and a concrete human next step.

The native macOS journey now starts before analysis:

- Profile Builder creates, reorders, validates, and saves one to five named profiles without manual
  JSON editing.
- Import preview shows CSV/JSON format, total records, the first normalized notices, warnings, and
  full-file metadata gaps before a run.
- Optional continuity remembers only security-scoped bookmarks for the two selected files. Tender
  contents, reports, review dates, and the RevenueCat key are never stored by that feature, and
  restored file selections are never analyzed automatically.
- The always-free first profile includes the complete review queue, deterministic JSON export,
  text search, buyer/deadline/verdict filters, progressive reasons, and safe supplied HTTPS links.
- Portfolio Workspace evaluates the same ordered notice set independently for up to five profiles.
  RevenueCat entitlement `supplier_profiles_plus` reveals every report and the shared comparison.
  Selecting any comparison cell opens that exact profile/notice verdict, reasons, unknowns, and
  next step.

TenderVerdict never adds a cross-profile score, ranking, legal conclusion, automatic bid, or
entitlement-dependent qualification result.

## How we built it

- Python 3.11+ qualification core with strict bounded schemas, deterministic JSON, atomic export,
  shared `as_of`, and SHA-256 provenance.
- A private embedded-core adapter for workspace normalization, notice previews, and portfolio runs;
  the public Apache-2.0 CLI remains a normal open-source interface rather than a payment boundary.
- SwiftUI macOS app that decodes canonical reports and rejects inconsistent profile counts, totals,
  provenance, shared notices, or ordering before presentation.
- Official RevenueCat Apple SDK `5.83.0`, pinned exactly with Swift Package Manager, using the
  current offering, Test Store purchase, `CustomerInfo` entitlement state, refresh, and restore.
- Fail-closed secure-key handling: only a process-local `test_` key is accepted, never committed or
  persisted by the app.
- Self-contained ad-hoc-signed `.app` builder with embedded offline Python runtime, licenses,
  fixtures, worktree-independent smoke test, archive, and checksum.
- Fifteen native contract checks, including a synthetic 125-notice filtering case with stable
  identities and pure Premium accessibility outcomes, plus Python regression, type/lint, security,
  public-tree, package, and CI gates.
- Accessibility-specific terminal state mapping, VoiceOver announcement routing, user-action focus
  recovery, flexible large-text layouts, and Increase Contrast/Reduce Transparency adaptations.

## Challenges

The first challenge was monetization without weakening trust. RevenueCat controls only the native
visibility projection; one qualification engine and one report contract produce identical results
before and after unlock.

The second was safe continuity. Convenience usually invites persistence, so the feature is explicit
opt-in and stores only file bookmarks—not notice data, generated reports, review dates, or billing
configuration.

The third was making larger portfolios inspectable without corrupting cross-profile alignment.
Filtering uses stable result identities, and comparison drill-down resolves by profile/result ID
instead of reusing a filtered array offset.

## Accomplishments

- One notice file is normalized once and evaluated consistently for one to five ordered profiles.
- Free mode remains a complete product: one full analysis, notice-level reasoning, filters, safe
  source access, and deterministic export.
- Premium solves a coherent repeated-work problem with comparison and drill-down instead of hiding
  basic reasoning.
- Profile Builder and import preview make the strict contracts usable without weakening validation.
- Invalid input does not replace the last valid report or export.
- RevenueCat missing/invalid configuration fails closed; there is no local Premium toggle.
- A packaged Debug baseline completed Test Store cancellation, failure, retry, success, entitlement
  unlock, relaunch refresh, restore, and dashboard readback without retaining a key or customer ID.
- A fresh current-source Release package passed embedded-core byte determinism and contract checks,
  ad-hoc signature verification, and worktree-independent app smoke, producing the `.app`, zip, and
  checksum.
- The current candidate passes all 15 native contract checks and the 122-test Python suite; CI on
  the exact submitted revision remains an explicit final gate.
- Shipaton Manager Perttu confirmed in writing that the Test Store-only purchase path is acceptable
  for Next Gen, and Shipaton confirmed macOS eligibility without a platform-only disadvantage.

## Proof for judging

| Review question | Concrete proof |
|---|---|
| Is the problem real and specific? | The same tender feed is screened against different legal-entity, geography, CPV, and lead-time policies; the UI demonstrates three differing profile outcomes. |
| Is it a functioning product? | Local files, strict Profile Builder, import preview, canonical run, filtered review, exact reasoning, comparison drill-down, and atomic export form one end-to-end macOS workflow. |
| Is RevenueCat substantive? | The current offering, purchase result, `CustomerInfo`, entitlement, refresh, relaunch recovery, and `restorePurchases()` determine access to the multi-profile workspace. |
| Does monetization fit the product? | Single-profile work remains useful and free; Premium saves repeated cross-profile review while preserving identical qualification bytes. |
| Is the implementation trustworthy? | Bounded offline contracts, deterministic output, provenance, stable identities, strict decoding, safe links, no stored key, and 15 native checks make failure modes visible. |
| Is the experience considered? | Native builder/preview, opt-in continuity, large-list filters, evidence drill-down, recovery focus, announcements, contrast/transparency response, and a sub-1:50 demo path address real workflow friction. |

## Eligibility evidence

- [Shipaton Manager Perttu: Test Store-only purchase is acceptable](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient)
- [Shipaton: macOS is eligible with no platform-only disadvantage](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44615-macos-app-submission)

These answers resolve those two interpretation questions. Academic-email/student eligibility and
all final submission fields still need owner verification.

## What we learned

Entitlement-backed UI is strongest when billing state and domain logic stay separate. A useful free
workflow makes the Premium value proposition clearer, not weaker. Import transparency and stable
identity matter as much as visual polish when people must defend a decision later.

## What is next

Build the exact final Release and Debug packages, refresh the current portrait and unlocked visual
evidence, manually verify VoiceOver announcements for asynchronous success/cancellation/failure,
confirm academic eligibility, publish the captioned sub-1:50 demo, run CI on the submitted commit,
and verify the repository/video/final entry while logged out.

## Links

- Repository: `https://github.com/demidgost-sys/tenderverdict`
- Demo video: `[PUBLIC YOUTUBE OR VIMEO URL]`
- Submitted revision: `[FULL COMMIT SHA]`
