# TenderVerdict Next Gen macOS shell

This unreleased SwiftUI target is the native presentation layer for the Shipaton Next Gen branch.
It consumes the canonical Python Portfolio Workspace JSON, links the official RevenueCat Apple SDK,
and keeps the qualification rules in the existing Python core.

## What is implemented

- one free schema-3 profile report remains visible;
- an active `supplier_profiles_plus` entitlement reveals the complete one-to-five-profile
  workspace;
- RevenueCat current-offering, purchase, restore, and `CustomerInfo` entitlement paths use
  `purchases-ios` `5.83.0`, pinned exactly in `Package.resolved`;
- a missing key leaves Premium locked and makes no RevenueCat request;
- a non-Test Store-shaped key is rejected before SDK configuration;
- the Python child process receives only a minimal environment and reads the bundled synthetic
  workspace and notices locally.

The committed source contains no usable API key. The open-source Python CLI remains available and
is not a payment-enforcement boundary.

## Build and verify

Run from the repository root on macOS with Swift 6 and Python 3.11 or newer:

```bash
swift build --package-path macos/TenderVerdictNextGen
swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGen --smoke-test
```

The smoke test invokes the real local `tenderverdict portfolio` command and checks the resulting
workspace contract without launching a window or configuring RevenueCat.

Launch the SwiftUI shell with:

```bash
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGen
```

Without local Test Store configuration, the expected UI state is locked. For a later organizer-
approved interactive test, provide `REVENUECAT_TEST_STORE_API_KEY` only in the local launch
environment or Xcode scheme. The source accepts only values beginning with `test_`; never commit a
key. A configured launch can contact RevenueCat, and the purchase and restore buttons can change
Test Store state.

## Evidence boundary

A successful build, contract-check run, and headless smoke test prove source compilation, SDK
linkage, JSON consumption, and fail-closed presentation logic. They do not prove a Test Store
transaction, entitlement activation, restore, cancellation, packaged `.app`, screenshot, or
Shipaton eligibility. Those require a configured RevenueCat project, a compatible full Xcode
workflow, hands-on state checks, and the still-unverified organizer clarification.
