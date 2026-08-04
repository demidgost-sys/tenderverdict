# TenderVerdict Next Gen — Devpost draft

## Tagline

Explainable local tender triage across every supplier profile, with a RevenueCat-powered Portfolio
Workspace.

## Inspiration

One tender feed can matter differently to several legal entities, countries, or service profiles.
Teams often repeat the same manual metadata screen and lose the reasoning behind each decision.

## What it does

TenderVerdict reads normalized public-procurement notice metadata and applies narrow,
deterministic rules for CPV fit, geography, deadline lead time, notice type, and missing fields. It
returns `open_documents`, `watch`, or `reject` with reasons and a human next step.

The free macOS experience keeps one complete supplier analysis and JSON export. Portfolio Workspace
evaluates the same ordered notice set independently for up to five named profiles. An active
RevenueCat entitlement, `supplier_profiles_plus`, reveals all profile reports. It never adds a
cross-profile score or automatic bid recommendation.

## How we built it

- Python 3.11+ deterministic qualification core with bounded schemas and SHA-256 provenance.
- SwiftUI macOS app consuming the canonical portfolio JSON rather than duplicating rules.
- Official RevenueCat Apple SDK `5.83.0`, pinned exactly with Swift Package Manager.
- Current offering, Test Store purchase, cancellation, restore, relaunch refresh, and
  `CustomerInfo` entitlement paths.
- Self-contained ad-hoc-signed `.app` with an embedded offline Python runtime, fixtures, licenses,
  smoke test, zip, and checksum.
- Offline Python tests, native contract checks, security/public-tree gates, and macOS CI artifact.

## Challenges

The hard part was preserving a trustworthy free product while adding a monetizable portfolio. We
kept one qualification engine and one report contract, then made RevenueCat control only the native
presentation projection. Packaging also had to work without a source checkout or system Python,
and invalid input had to preserve the last valid report.

## Accomplishments

- One notice set is parsed once and reviewed consistently for one to five profiles.
- Free mode preserves the existing single analysis and export.
- The packaged local-file flow produces JSON bytes identical to the CLI.
- Missing or non-Test RevenueCat configuration fails closed.
- Public icon and screenshot assets are generated and dimension-checked.

## What we learned

Entitlement-backed UI is strongest when billing state and domain logic stay separate. RevenueCat
owns access state; TenderVerdict owns explainable procurement metadata rules.

## What is next

`[REMOVE AFTER VERIFIED]` Complete and record the organizer-approved Test Store purchase, restore,
and relaunch evidence; publish the sub-two-minute demo; add the final public video and repository
URLs.

## Links

- Repository: `https://github.com/demidgost-sys/tenderverdict`
- Demo video: `[PUBLIC YOUTUBE OR VIMEO URL]`
- Submitted revision: `[FULL COMMIT SHA]`
