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
