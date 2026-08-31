# TenderVerdict — Shipaton Next Gen

This is the brief-required front door for the competition project. It contains stable orientation,
not mutable readiness claims. Use the [Shipaton runbook](docs/HACKATHON_RUNBOOK.md) for the current
submission sequence and [project status](docs/PROJECT_STATUS.md) for exact evidence and open gates.

## Problem

Small supplier teams can spend hours opening public tenders that never matched a particular legal
entity, service line, country, or deadline policy. When several supplier profiles share one notice
feed, the same screening is repeated and its reasoning is easy to lose.

## User

TenderVerdict is for small supplier and procurement teams that need a first, explainable review of
structured public-tender notice metadata before deciding which full documents deserve attention.

## Solution

TenderVerdict runs locally and turns one normalized notice feed into independent
`open_documents`, `watch`, or `reject` queues for one to five supplier profiles. Every result keeps
its reasons, unknowns, source metadata, and a human next step. It does not score suppliers, read the
full procurement documents, or decide whether to bid.

## RevenueCat's role

One complete supplier-profile analysis, its reasoning, links, review brief, and JSON export remain
free. RevenueCat entitlement `supplier_profiles_plus` unlocks the Portfolio Workspace: up to five
complete profile reports, their comparison, and full portfolio exports. RevenueCat controls only
native presentation access; it never changes qualification output.

## Architecture

- The deterministic Python core owns schemas, qualification, provenance, and atomic output.
- The SwiftUI macOS app owns local file selection, review, comparison, export, and access UI.
- The official RevenueCat Apple SDK owns Test Store offering, purchase, entitlement, refresh, and
  restore state.
- Strict native decoding rejects inconsistent profile counts, notice order, totals, or provenance
  before presentation.

See [architecture](docs/ARCHITECTURE.md) for the complete trust and runtime boundaries.

## Privacy and IP boundaries

Local qualification has no account, hosted backend, first-party telemetry, or document upload.
Only synthetic, public, or fully de-identified inputs belong in competition evidence. No usable
RevenueCat key is committed or bundled; Test Store configuration is process-local and Debug-only.
The public CLI remains Apache-2.0 and is not treated as a tamper-resistant payment boundary.

## Run and verify

Run the offline Python example:

```bash
PYTHONPATH=src python3 -m tenderverdict portfolio \
  --workspace examples/synthetic/portfolio-workspace.json \
  --notices examples/synthetic/notices.csv \
  --as-of 2026-08-02
```

Build and verify the macOS competition app with the exact commands in the
[developer guide](docs/DEVELOPMENT.md#complete-source-gate) and
[runbook](docs/HACKATHON_RUNBOOK.md#reproducible-local-build).

## Limitations and evidence boundary

The app is an ad-hoc-signed competition evaluation build, not a notarized consumer release. The
public demo, private Devpost fields, final accessibility pass, real-user sessions, and final
submission remain separate gates tracked in [project status](docs/PROJECT_STATUS.md).

The original 25-hour target was not measured with a reliable active-time timer. Do not claim that
the completed work stayed within that cap. Any remaining-work estimate must start from a verified
timer state; elapsed app or process time is not active-development evidence.

## Required deliverable map

- Evidence and official sources: [docs/SHIPATON_EVIDENCE.md](docs/SHIPATON_EVIDENCE.md)
- Brief-required demo-script path: [docs/SHIPATON_DEMO_SCRIPT.md](docs/SHIPATON_DEMO_SCRIPT.md)
- Brief-required Devpost-draft path: [docs/DEVPOST_DRAFT.md](docs/DEVPOST_DRAFT.md)
- Submission assets and canonical draft: [submission/README.md](submission/README.md)
