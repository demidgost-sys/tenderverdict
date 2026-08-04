# TenderVerdict Next Gen for macOS

This unreleased SwiftUI app is the native Shipaton Next Gen surface. It consumes the canonical
Python Portfolio Workspace report, preserves the first profile as the Free experience, and reveals
the complete one-to-five-profile workspace only for an active RevenueCat
`supplier_profiles_plus` entitlement.

## Implemented product flow

- launches with a bundled three-profile synthetic portfolio;
- builds, reorders, removes, resets, validates, and saves one to five profiles without hand-editing
  JSON;
- strictly normalizes a chosen workspace v1 JSON through the canonical Python parser before use;
- fully validates chosen CSV/JSON notices, then previews the source format, total count, first five
  normalized records, and full-file gaps for type, title, buyer, CPV, country, deadline, and source;
- accepts an explicit date or timezone-aware RFC 3339 review point;
- runs the private deterministic Python bridge without a shell and with a 30-second boundary;
- keeps the previous valid report visible when a new run fails;
- exposes the complete first-profile result as a Free review queue with verdict, text, buyer, and
  deadline-presence filters, progressive **Show more**, human next steps, expandable reasoning,
  unknowns, and safe supplied-source links;
- exports the exact combined JSON bytes atomically;
- optionally remembers only the two selected-file security-scoped bookmarks, never file contents,
  reports, review dates, or a RevenueCat key, and never runs remembered inputs automatically;
- accepts a `test_` RevenueCat key in a process-only secure field;
- loads the current offering, runs a Test Store purchase, handles cancellation, restores, refreshes
  `CustomerInfo`, and projects access through `supplier_profiles_plus`;
- searches and filters the Premium comparison, resolves every cell by stable profile/result IDs,
  and opens complete per-cell reasoning without score, ranking, or an automatic recommendation;
- announces terminal Premium outcomes to VoiceOver when available, restores focus after an
  explicit purchase/retry/restore action, and adapts cards for Increase Contrast and Reduce
  Transparency;
- rejects missing and non-Test configuration before an SDK request.

The open-source CLI remains available and is not a tamper-resistant payment boundary. The app
stores no RevenueCat key and sends no profile or notice contents to RevenueCat. RevenueCat still
receives its normal SDK customer identifiers and Test Store operations after explicit
configuration; that SDK boundary is separate from the offline analysis path.

## Source build and checks

From the repository root on macOS with Swift 6 and Python 3.11+:

```bash
swift build --package-path macos/TenderVerdictNextGen
swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen --smoke-test
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen
```

`TenderVerdictNextGenChecks` runs 15 standalone checks for portfolio projection, full result
preservation, empty inputs, nested totals, result-summary consistency, shared notice digest and
order, strict workspace and import-preview contracts, large filtered-result identity stability,
Test Store key boundaries, terminal accessibility outcomes, selected-file execution, and byte
determinism. The smoke test invokes the real private Python bridge without launching a window or
configuring RevenueCat.

The Python suite currently has 122 tests in total. Six directly exercise the private launcher:

```bash
PYTHONPATH=src python3 -m unittest tests.test_next_gen_core_launcher -v
```

For bridge diagnostics only, the source adapter calls the same private commands used by the app:

```bash
PYTHONPATH=src python3 tools/next_gen_core_launcher.py \
  normalize-workspace --workspace examples/synthetic/portfolio-workspace.json
PYTHONPATH=src python3 tools/next_gen_core_launcher.py \
  inspect-notices --notices examples/synthetic/notices.csv --limit 5
```

These commands are an internal app contract, not an additional installed public CLI.

## Self-contained app bundle

Install the hash-locked packaging tools, then build:

```bash
python3 -m venv .venv-build
.venv-build/bin/python -m pip install \
  --require-hashes --only-binary=:all: --no-deps \
  -r requirements-desktop-build.txt
.venv-build/bin/python tools/build_next_gen.py
```

Outputs appear under `dist/next-gen/`. The `.app` contains:

- the release SwiftUI executable and RevenueCat Swift package resources;
- a PyInstaller-frozen `TenderVerdictCore` that supports only the offline `portfolio`,
  `normalize-workspace`, and `inspect-notices` app operations;
- synthetic fixtures, Apache-2.0 license, notice, third-party notices, icon, and build provenance.

The builder ad-hoc signs the bundle, verifies the signature, launches the app executable from `/`
with no worktree, confirms the embedded-core smoke test, and writes a zip plus SHA-256 checksum.
Full Xcode is not required for this source/package workflow; Apple Developer ID signing,
notarization, and App Store distribution are not provided.

Use `--output-dir`, `--build-root`, and `--swift-scratch-path` to route generated artifacts and
caches. Existing output is preserved unless `--replace` is explicit.

## Submission asset generation

```bash
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen --render-submission-screenshot \
  "$PWD/submission/screenshot-1179x2556.png"
python3 tools/prepare_submission_assets.py
```

This command produces the 1179×2556 pre-transaction view and canonical 1024×1024 icon. The current
assets were regenerated and structure-checked; the portrait was visually inspected in light and
dark appearance. Repeat the asset pass after any visual source change and complete the remaining
large-text, Increase Contrast, and Reduce Transparency inspection before submission. A
pre-transaction screenshot is not purchase evidence.

## RevenueCat configuration

The package pins the official Apple SDK to `5.83.0` and the resolved revision to
`c69a23f56c63bdfe96096fa64a1c65334d2592db`. The Shipaton Manager has confirmed that a Test Store
integration is sufficient for judging:
[official answer](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient).
The Manager also confirmed that macOS is accepted without a judging disadvantage:
[official answer](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44615-macos-app-submission).

For the accepted Test Store path:

1. create `supplier_profiles_plus` in a RevenueCat Test Store project;
2. attach a Test Store product to one package in the current offering;
3. paste the public Test Store `test_` key into the secure field for that launch;
4. verify offering, cancel, failure, success, relaunch/refresh, and restore states on the packaged
   app.

RevenueCat intentionally rejects a Test Store key in a Release build. Build the local transaction
evidence app with the same reproducible packager in Debug configuration:

```bash
.venv-build/bin/python tools/build_next_gen.py \
  --configuration debug \
  --output-dir dist/next-gen-debug \
  --build-root build/next-gen-debug
```

The normal builder default remains `release`; never submit a Test Store key inside either bundle.

The environment variable `REVENUECAT_TEST_STORE_API_KEY` remains available for controlled local
automation. Never commit, log, screenshot, or publish a usable key.

## Evidence boundary

Verified for the current source and Release package: 122 Python tests including six
private-launcher tests, 15 native contract checks, source compilation, strict workspace
normalization, CSV/JSON import preview, large-result filtering with stable-ID lookup, source smoke
execution, deterministic byte equality, invalid-input retention, missing-key state, and
non-Test-key rejection. The self-contained `.app`
also passed repeated embedded normalize/inspect contract and byte-determinism checks, ad-hoc
signature verification, and a worktree-independent smoke run from `/`; `.app`, zip, and SHA-256
outputs were created on the external build volume.

A previous Debug Test Store pass covered offering, cancellation, failure, purchase, entitlement
activation, relaunch refresh, restore, and VoiceOver activation of Restore. It remains historical
transaction evidence and is not a real payment or fresh visual QA for the current Release package.

Implemented but still requiring hands-on verification after the rebuild: terminal VoiceOver
announcements across every purchase outcome, focus recovery, Increase Contrast, Reduce
Transparency, large-text behavior, the private Devpost form, and the final public submission. See
[the evidence record](../../docs/SHIPATON_EVIDENCE.md) and
[hackathon runbook](../../docs/HACKATHON_RUNBOOK.md).
