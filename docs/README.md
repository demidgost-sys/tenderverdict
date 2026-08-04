# TenderVerdict documentation

This directory is the map for the current source tree. The immutable `v0.2.0-alpha.1` release is
documented by the files at that tag; the pages below also describe unreleased Portfolio Workspace
and Shipaton Next Gen work.

## Start here

| Need | Document |
|---|---|
| See what is finished, why it matters, and how readiness is counted | [Project status](PROJECT_STATUS.md) |
| Understand the product and choose a surface | [User guide](USER_GUIDE.md) |
| Understand components, contracts, and trust boundaries | [Architecture](ARCHITECTURE.md) |
| Build, test, and package the macOS app | [Next Gen macOS README](../macos/TenderVerdictNextGen/README.md) |
| Reproduce quality and accessibility checks | [UX and accessibility audit](UX_AUDIT.md) |
| Map judging criteria to product priorities | [Competition scorecard](COMPETITION_SCORECARD.md) |
| Prepare the Shipaton entry and RevenueCat evidence | [Hackathon runbook](HACKATHON_RUNBOOK.md) |
| Record a sub-two-minute demo | [Demo script](DEMO_SCRIPT.md) |
| Distinguish verified facts from open competition gates | [Shipaton evidence](SHIPATON_EVIDENCE.md) |
| Understand product and decision limits | [Limitations](../LIMITATIONS.md) |
| Review planned work | [Roadmap](../ROADMAP.md) |

## Stable public contracts

- Profile input: schema version 1.
- Single-profile JSON report: schema version 3.
- Portfolio workspace input: schema version 1, one to five profiles.
- Portfolio workspace report: schema version 1 containing complete schema-3 profile reports.
- Verdicts: `open_documents`, `watch`, and `reject`.
- Premium entitlement: `supplier_profiles_plus`.

TenderVerdict does not add a cross-profile score, ranking, recommendation, or automatic bid
decision. The Python CLI remains Apache-2.0 source and is not a tamper-resistant payment boundary.

## Next Gen product flow

The current native source supports the complete local workflow:

1. Build or choose a strict schema-1 workspace with one to five ordered profiles.
2. Choose normalized CSV/JSON notices and inspect an import preview before analysis.
3. Optionally remember only security-scoped bookmarks for the two input files; data, reports,
   review dates, and the RevenueCat key stay session-only.
4. Run the canonical local core, search/filter the complete first-profile review queue, and export
   deterministic JSON for free.
5. Use RevenueCat entitlement `supplier_profiles_plus` to reveal the remaining reports and shared
   comparison, then open a cell for exact profile/notice reasoning.

The native contract suite contains 15 checks, including a synthetic 125-notice filtering case with
stable result identities and pure terminal Premium accessibility outcomes. See the
[UX and accessibility audit](UX_AUDIT.md) for the exact split
between source inspection, automated checks, previous hands-on evidence, and pending final-package
verification.

## Competition state

Written organizer answers now confirm both the RevenueCat Test Store-only path and macOS eligibility
without a platform-only disadvantage. The [hackathon runbook](HACKATHON_RUNBOOK.md) links those
threads and keeps the remaining personal eligibility, final Debug Test Store/accessibility,
three-session validation, video, and final Devpost checks explicit.
