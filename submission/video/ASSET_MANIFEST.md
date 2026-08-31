# Asset and claim manifest

Machine-verifiable hashes and dimensions live in [`asset-manifest.json`](asset-manifest.json).

| Asset | Evidence label | Used in shots | Claim limits |
|---|---|---:|---|
| `submission/screenshot-1179x2556.png` | Current deterministic render | 1–4 | Product hierarchy, local/synthetic workflow, three verdicts, complete Free surface; not manual footage |
| `demo/screenshot.png` | Current deterministic report render | Reference only | Report/source/provenance fallback; not native app footage |
| `submission/evidence/unlocked-judge-access-2026-08-09.png` | Current genuine `cbe8b20` evidence | 5, 8 | Comparison, RevenueCat grant, visible Restore, literal no-purchase copy; the screenshot alone does not prove the preceding relaunch action |
| `submission/evidence/unlocked-test-store-2026-08-04.png` | Dated genuine Test Store baseline | 7 | Historical entitlement result only; do not call it exact-final purchase evidence |
| `assets/test-store-purchase-sheet-baseline-2026-08-04.jpg` | Dated genuine JPEG baseline; metadata removed losslessly | 6 | Development-only Test Store UI, product identifier, localized price; no App Store/real-payment claim |
| `assets/entitlement-restored-on-relaunch-baseline-2026-08-04.jpg` | Dated genuine JPEG baseline; metadata removed losslessly | 9 | Historical relaunch result; current relaunch statement must cite the 2026-08-09 audit |
| `submission/icon-1024.png` | Current reviewed icon | 10 | Identity/end card only |

## Source-data provenance

- Workspace: `examples/synthetic/portfolio-workspace.json`.
- Notices: `examples/synthetic/notices.json` and `examples/synthetic/notices.csv`.
- The fixture contains three supplier profiles and three shared notices.
- The current submission render shows one Open, one Watch, and one Reject for the first profile.
- These are synthetic examples, not real procurement or customer outcomes.

## Claim provenance

- Product/Free/Premium boundaries: `docs/PROJECT_STATUS.md` and repository `AGENTS.md`.
- Current no-purchase entitlement, refresh, Restore, foreground, relaunch, and screenshot hash:
  `docs/TECHNICAL_AUDIT.md`.
- Historical Test Store purchase/cancel/failure/retry baseline: `docs/SHIPATON_EVIDENCE.md` and
  `docs/HACKATHON_RUNBOOK.md`.
- Official under-two-minute and Test Store eligibility gates: `docs/HACKATHON_RUNBOOK.md`.

No asset in this package is proof of notarization, production billing, public release, external-user
validation, legal accuracy, award prediction, or a completed Devpost submission.
