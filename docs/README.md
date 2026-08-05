# TenderVerdict documentation

This is the navigation hub for the current source tree. The immutable `v0.2.0-alpha.1` release is
documented by the files at that tag; current pages also describe unreleased Portfolio Workspace and
Shipaton Next Gen work.

## Choose a path

| You want to… | Start here | Then read |
|---|---|---|
| Try the published alpha | [Root README](../README.md) | [Desktop preview](../DESKTOP.md), [limitations](../LIMITATIONS.md) |
| Use the Next Gen macOS app | [User guide](USER_GUIDE.md) | [Next Gen README](../macos/TenderVerdictNextGen/README.md) |
| Change code | [Developer guide](DEVELOPMENT.md) | [Architecture](ARCHITECTURE.md), [contributing](../CONTRIBUTING.md) |
| Hand work to another agent | [Repository agent guide](../AGENTS.md) | [Project status](PROJECT_STATUS.md), [latest audit](TECHNICAL_AUDIT.md) |
| Understand what is actually ready | [Project status](PROJECT_STATUS.md) | [Technical audit](TECHNICAL_AUDIT.md), [UX audit](UX_AUDIT.md) |
| Understand the competition project | [Hackathon overview](../HACKATHON.md) | [Evidence](SHIPATON_EVIDENCE.md), [project status](PROJECT_STATUS.md) |
| Prepare the competition entry | [Hackathon runbook](HACKATHON_RUNBOOK.md) | [Demo script](SHIPATON_DEMO_SCRIPT.md), [Devpost draft](DEVPOST_DRAFT.md), [submission assets](../submission/README.md) |
| Review future work | [Roadmap](../ROADMAP.md) | [Competition scorecard](COMPETITION_SCORECARD.md) |

## Documentation layers

| Layer | Documents | Owns |
|---|---|---|
| Product landing | [README](../README.md), [desktop](../DESKTOP.md) | First run and published surfaces |
| Durable contracts | [Architecture](ARCHITECTURE.md), [user guide](USER_GUIDE.md), [limitations](../LIMITATIONS.md), [security](../SECURITY.md), [data sources](../DATA_SOURCES.md) | Behavior, trust, inputs, and boundaries |
| Engineering | [Developer guide](DEVELOPMENT.md), [agent guide](../AGENTS.md), [contributing](../CONTRIBUTING.md) | Repository map, gates, and change workflow |
| Current evidence | [Project status](PROJECT_STATUS.md), [technical audit](TECHNICAL_AUDIT.md), [UX audit](UX_AUDIT.md) | Current totals, revision evidence, manual/automated split, and open gates |
| Competition | [Overview](../HACKATHON.md), [Shipaton evidence](SHIPATON_EVIDENCE.md), [scorecard](COMPETITION_SCORECARD.md), [runbook](HACKATHON_RUNBOOK.md), [demo script](DEMO_SCRIPT.md) | Stable pitch, rules, strategy, reproducible submission steps, and claims |
| Submission package | [Asset inventory](../submission/README.md), [evidence inventory](../submission/evidence/README.md), [Devpost draft](../submission/devpost-draft.md) | Files and draft copy, not proof of submission |
| History and future | [Changelog](../CHANGELOG.md), [roadmap](../ROADMAP.md) | Shipped changes and evidence-gated next work |

Read [documentation governance](DOCUMENTATION.md) for source-of-truth ownership, evidence labels,
release terminology, and update triggers. Mutable suite totals, revision evidence, and readiness
percentages belong in `PROJECT_STATUS.md`, not in every layer.

The original brief's literal paths remain available as routing entry points:
[HACKATHON.md](../HACKATHON.md), [SHIPATON_DEMO_SCRIPT.md](SHIPATON_DEMO_SCRIPT.md), and
[DEVPOST_DRAFT.md](DEVPOST_DRAFT.md). Their linked canonical documents remain the only editable
owners of mutable operations, timing, and submission copy.

## Stable public contracts

- Profile input: schema version 1.
- Single-profile JSON report: schema version 3.
- Portfolio workspace input: schema version 1 with one to five profiles.
- Portfolio workspace report: schema version 1 containing complete schema-3 profile reports.
- Verdicts: `open_documents`, `watch`, and `reject`.
- Premium entitlement: `supplier_profiles_plus`.

TenderVerdict does not add a cross-profile score, ranking, recommendation, or automatic bid
decision. The Python CLI remains Apache-2.0 source and is not a tamper-resistant payment boundary.

## Next Gen flow

The current native source supports this bounded journey:

1. Build or choose a strict schema-1 workspace with one to five ordered profiles.
2. Choose normalized CSV/JSON notices and inspect a full-file validation preview before analysis.
3. Optionally remember only security-scoped bookmarks for the two input files; data, reports,
   review points, and RevenueCat configuration stay session-only.
4. Run the canonical local core, search/filter the complete first-profile review queue, and export
   deterministic JSON for free.
5. Use RevenueCat entitlement `supplier_profiles_plus` to reveal the remaining reports and shared
   comparison, then open a cell for exact profile/notice reasoning.

The [UX audit](UX_AUDIT.md) separates source inspection, automated checks, dated hands-on evidence,
the completed silent final-product Debug/settings pass, and pending VoiceOver work. Written organizer answers confirm the narrow
Test Store-only path and macOS eligibility; the [evidence record](SHIPATON_EVIDENCE.md) owns those
primary sources and the remaining personal/submission gates.
