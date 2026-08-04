# TenderVerdict Next Gen for macOS

This unreleased SwiftUI app is the native Shipaton Next Gen surface. It consumes the canonical
Python Portfolio Workspace report, preserves the first profile as the Free experience, and reveals
the complete one-to-five-profile workspace only for an active RevenueCat
`supplier_profiles_plus` entitlement.

## Implemented product flow

- launches with a bundled three-profile synthetic portfolio;
- chooses any local workspace v1 JSON and normalized CSV/JSON notices through native panels;
- accepts an explicit date or timezone-aware RFC 3339 review point;
- runs the embedded deterministic Python core with a 30-second boundary;
- keeps the previous valid report visible when a new run fails;
- exposes the complete first-profile result as a filterable Free review queue with human next
  steps, expandable reasoning, unknowns, and safe supplied-source links;
- exports the exact combined JSON bytes atomically;
- accepts a `test_` RevenueCat key in a process-only secure field;
- loads the current offering, runs a Test Store purchase, handles cancellation, restores, refreshes
  `CustomerInfo`, and projects access through `supplier_profiles_plus`;
- compares the same notices across all entitled profiles without score, ranking, or an automatic
  recommendation;
- rejects missing and non-Test configuration before an SDK request.

The open-source CLI remains available and is not a tamper-resistant payment boundary. The app
stores no RevenueCat key and sends no profile or notice contents to RevenueCat.

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

`TenderVerdictNextGenChecks` runs ten standalone checks for portfolio projection, full result
preservation, empty inputs, nested totals, result-summary consistency, shared notice digest and
order, Test Store key boundaries, selected-file execution, and byte determinism. The smoke test
invokes the real Python `portfolio` command without launching a window or configuring RevenueCat.

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
- a PyInstaller-frozen `TenderVerdictCore` that supports only the offline `portfolio` operation;
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

This produces the exact 1179×2556 pre-transaction view and canonical 1024×1024 icon. The committed
screenshot honestly shows missing Test Store configuration; it is not purchase evidence.

## RevenueCat configuration

The package pins the official Apple SDK to `5.83.0` and the resolved revision to
`c69a23f56c63bdfe96096fa64a1c65334d2592db`. For an organizer-approved test:

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

Verified locally: source build, ten native checks, source smoke test, self-contained app assembly,
ad-hoc signature verification, embedded-runtime smoke test, native file selection, selected-file
analysis, Free result review, Premium comparison contract, atomic export, byte equality with the
CLI, invalid-input retention, missing-key state, non-Test-key rejection, and a separately packaged
Debug Test Store pass covering offering, cancellation, failure, purchase, entitlement activation,
relaunch refresh, restore, and VoiceOver activation of Restore.

Not yet verified: organizer acceptance of a Test Store-only Shipaton integration, asynchronous
VoiceOver announcements across every purchase outcome, Increase Contrast, Reduce Transparency,
large-text behavior, the private Devpost form, or a public submission. See
[the evidence record](../../docs/SHIPATON_EVIDENCE.md) and
[hackathon runbook](../../docs/HACKATHON_RUNBOOK.md).
