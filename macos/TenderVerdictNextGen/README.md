# TenderVerdict Next Gen for macOS

This unreleased SwiftUI app is the native Shipaton Next Gen surface. It consumes the canonical
Python Portfolio Workspace report, preserves the first profile as the Free experience, and reveals
the complete one-to-five-profile workspace only for an active RevenueCat
`supplier_profiles_plus` entitlement. The target requires macOS 13 or newer. The local builder emits
the current host architecture; the audited Apple Silicon artifact is `arm64`, not a universal app.

## Implemented product flow

- launches with a bundled three-profile synthetic portfolio whose Free profile shows one Open, one
  Watch, and one Reject;
- builds, reorders, removes, resets, validates, and saves one to five profiles without hand-editing
  JSON;
- strictly normalizes a chosen workspace v1 JSON through the canonical Python parser before use;
- fully validates chosen CSV/JSON notices, then previews the source format, total count, first five
  normalized records, and full-file gaps for type, title, buyer, CPV, country, deadline, and source;
- accepts an explicit date or whole-second timezone-aware RFC 3339 review point, validates it
  inline, and provides a local-calendar **Use today** action;
- runs the private deterministic Python bridge without a shell and with a 30-second boundary;
- distinguishes bundled demo, current selected-input, and retained previous report state; a failed
  run keeps previous bytes visible and makes previous export wording explicit;
- exposes the complete first-profile result as a Free review queue with verdict, text, buyer, and
  deadline-presence filters, full reset, progressive **Show more**, human next steps, separate
  verdict-driver/confirmation/passed-check groups, and safe supplied-source links;
- exports a deterministic schema-3 first-profile report in Free and the exact combined JSON bytes
  atomically only while Premium is active;
- exports a deterministic self-contained HTML review brief from the same accepted report: Free
  includes the complete first profile, Premium includes every profile in source order, and neither
  path adds scripts, remote assets, ranking, or new qualification logic;
- optionally remembers only the two selected-file security-scoped bookmarks, never file contents,
  reports, review dates, or a RevenueCat key, and never runs remembered inputs automatically;
- accepts a `test_` RevenueCat key in a process-only secure field in Debug builds only;
- loads only the expected `supplier_profiles_plus` offering, `$rc_monthly` package, and
  `supplier_profiles_plus_monthly` product; then runs a Test Store purchase, handles cancellation,
  restores, refreshes `CustomerInfo`, and projects access through the entitlement;
- searches and filters the Premium comparison, resolves every cell by stable profile/result IDs,
  and opens complete per-cell reasoning without score, ranking, or an automatic recommendation;
- previews only the number of shared notices with different profile verdicts while Premium is
  locked, without exposing gated report detail;
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
swift run -c release --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen --smoke-test
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen
```

`TenderVerdictNextGenChecks` covers portfolio projection, complete schema-3 Free export, full result
preservation, empty inputs, nested totals, result-summary consistency, shared notice digest and
order, strict workspace and import-preview contracts, large filtered-result identity stability,
review-point validation, reason grouping, disagreement counts, safe source links, review-brief
gating/escaping/determinism, exact RevenueCat dashboard identifiers, Debug/Release Test Store
boundaries, terminal accessibility outcomes, selected-file execution, and byte determinism. Run it
in both
configurations: Debug accepts a well-shaped Test Store key, while Release must make configuration
unavailable before any SDK call. The smoke test invokes the real private Python bridge without
launching a window or configuring RevenueCat.

For a deterministic visual check of the synthetic brief without opening a Save panel:

```bash
swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGen \
  --render-review-brief /tmp/tenderverdict-review-brief.html --premium
```

Omit `--premium` to render the Free first-profile projection. This developer flag uses the same
renderer as the in-app **Export review brief…** action.

The Python suite directly exercises the private launcher; current totals are maintained in
[project status](../../docs/PROJECT_STATUS.md):

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

By default the builder ad-hoc signs the bundle, verifies the signature, launches the app executable
from `/` with no worktree, runs configuration-specific native checks, confirms the embedded-core
smoke test, and writes a zip plus SHA-256 checksum. This remains the secret-free CI preview.

For direct distribution from a trusted Mac, pass `--signing-identity` and
`--notary-keychain-profile`. That Release-only path requires an existing Developer ID Application
identity and validated local `notarytool` profile. It enables the hardened runtime and secure
timestamp, requires an accepted notarization result, staples and validates the ticket, and runs a
Gatekeeper assessment before exposing output. Signing credentials remain outside the repository and
application. This does not add App Store distribution.

Use `--output-dir`, `--build-root`, `--swift-scratch-path`, and optionally
`--notary-keychain` to route generated artifacts, caches, and a non-default Keychain. Existing
output is preserved unless `--replace` is explicit.

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

1. create entitlement and current offering `supplier_profiles_plus`;
2. attach product `supplier_profiles_plus_monthly` to package `$rc_monthly`;
3. build the Debug evaluation app and paste the public Test Store `test_` key into the secure field
   for that launch;
4. verify offering, cancel, failure, success, relaunch/refresh, and restore states on the packaged
   app.

RevenueCat intentionally terminates a Release build that reaches SDK configuration with a Test Store
key. TenderVerdict therefore removes the key field and rejects configuration locally in Release.
Build the local transaction-evidence app with the same reproducible packager in Debug configuration:

```bash
.venv-build/bin/python tools/build_next_gen.py \
  --configuration debug \
  --output-dir dist/next-gen-debug \
  --build-root build/next-gen-debug
```

The normal builder default remains `release`; it is an offline-analysis evaluation artifact, not a
Premium transaction build. Never submit a Test Store key inside either bundle. If a Debug process
was configured with the wrong key, quit and reopen it before entering a replacement because the SDK
can be configured only once per process.

The environment variable `REVENUECAT_TEST_STORE_API_KEY` remains available for controlled local
automation. Never commit, log, screenshot, or publish a usable key.

## Evidence boundary

The remediated product revision named in project status passes configuration-specific native
contract checks, including Release Test Store fail-closed behavior, schema-3 Free export isolation,
visible control/bidi text, safe-link parity, exact dashboard identifiers, and the existing bridge
contracts. Its fresh self-contained release-configuration artifact passed package provenance,
signature, checksum, ZIP, and smoke verification; see
[project status](../../docs/PROJECT_STATUS.md) for the exact live result.

A fresh clean Debug Test Store pass on evidence revision `3cf20ed` covered offering, cancellation,
simulated failure, retry, purchase, entitlement activation, immediate restore, and relaunch refresh.
It is not a real payment. The earlier baseline remains the latest VoiceOver Restore and RevenueCat
dashboard readback evidence.

Exact current product revision `cbe8b20` adds the clean Judge Access evidence: a fresh
`CustomerInfo` read unlocked the RevenueCat grant without relaunch, and Restore, foreground
re-entry, and full process relaunch preserved it. The UI derives the visible expiration from the
active entitlement, bounds it to the local campaign cutoff, and states that no purchase was made.

Keyboard order, Increase Contrast, Reduce Transparency, and a temporary `.accessibility3`
screenshot-renderer pass remain evidenced by the clean `3cf20ed` package. A silent accessibility
tree and keyboard sample on `cbe8b20` confirmed useful native names for the visible controls and
comparison cells, but it is not presented as a spoken VoiceOver pass. Terminal VoiceOver
announcements/focus across purchase outcomes remain an optional accessibility follow-up; they are
not a Next Gen submission gate. The private Devpost form and final public submission are still
required. See
[the evidence record](../../docs/SHIPATON_EVIDENCE.md) and
[hackathon runbook](../../docs/HACKATHON_RUNBOOK.md).
