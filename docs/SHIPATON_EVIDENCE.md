# Shipaton 2026 Next Gen evidence and implementation gate

- Overall status: **CONDITIONAL — NATIVE SOURCE BUILDS; TEST STORE EVIDENCE BLOCKED**
- RevenueCat-independent Portfolio Workspace: **IMPLEMENTED LOCALLY**
- RevenueCat SDK purchase and entitlement source flow: **IMPLEMENTED, NOT TRANSACTION-VERIFIED**
- Evidence rechecked: **2026-08-04**
- Competition branch: `hackathon/revenuecat-next-gen-2026`
- Base before competition changes: `2f4f3855fbc9c7263f8822ace0b6b661ca959ab3`

This file separates official rules, repository evidence, owner-attested actions, technical
feasibility, and facts that remain unknown. It is not proof of eligibility or a Devpost
submission.

## Current decision

The store-exempt Next Gen path is technically plausible but not cleared for a qualifying
transaction claim. Official materials require every Project to use the RevenueCat SDK for a
purchase or ads. They confirm that Next Gen entrants can submit public source and a video without a
store release or paid developer account, but they do not explicitly say that a Test Store-only
purchase satisfies the Project requirement.

RevenueCat documents Test Store as a real SDK test flow: it can return offerings, simulate purchase
outcomes, update `CustomerInfo`, and activate entitlements without a real charge. Shipaton lists a
first Test Store purchase as a milestone distinct from a real-store API call and a first real
purchase. That proves the technical path and milestone, not the unresolved eligibility
interpretation.

The owner reports that the exact clarification question below was sent through Devpost. No written
organizer answer or public response URL has been verified in this repository. The owner has since
requested the local native source foundation: a SwiftUI target, exact official SDK pin, JSON
adapter, and fail-closed RevenueCat access client are now implemented. RevenueCat dashboard
configuration, a usable key, any purchase or restore, and a submission claim remain blocked.

## Requirement matrix

| Requirement | Evidence class | Current finding | Gate |
|---|---|---|---|
| Submission window | `official_rule` | The controlling Official Rules state July 31, 2026 at 08:00 PDT through September 30, 2026 at 23:45 PDT. The FAQ rounds the opening to August 1; this document uses the Rules. | `CONFIRMED` |
| Repository chronology | `repository_evidence` | The first commit was authored August 2, 2026 at 22:25 CEST, after either published opening description. The public developer alpha followed on August 4. | `CONFIRMED` |
| Next Gen store exception | `official_rule` | Active students may submit a public open-source repository and video without a paid Apple or Google developer account or store release. | `CONFIRMED` |
| Student and academic email | `owner_attested_required` | Active enrollment and the exact Devpost email are entrant-specific and were not verified by this code audit. | `OWNER_CHECK` |
| Public functional repository | `official_rule` + `repository_evidence` | The Python product, Apache-2.0 license, synthetic fixtures, SwiftUI source target, exact SDK pin, and run instructions are present. There is no configured or transaction-verified RevenueCat app artifact. | `PARTIAL` |
| Supported platform | `official_rule` | macOS is explicitly allowed by the rules and FAQ. | `CONFIRMED` |
| RevenueCat is substantive | `official_rule` | The SDK must power at least one purchase or ads; documentation alone and the Python portfolio core do not satisfy this. | `BLOCKER` |
| Test Store technical capability | `official_sdk` | Apple SDK 5.43.0 or newer can use a Test Store key for offerings, simulated outcomes, `CustomerInfo`, and entitlements. | `CONFIRMED_TECHNICALLY` |
| Test Store-only eligibility | `UNKNOWN` | No checked rule, Next Gen page, FAQ, or resource page explicitly says Test Store-only is sufficient for the submission requirement. | `BLOCKER` |
| Required submission media | `official_rule` | A public YouTube or Vimeo demo under two minutes, a 1024×1024 icon, and at least one 1179×2556 screenshot without a device frame are still required. | `PENDING` |

## Official sources checked

- [Shipaton 2026 Official Rules](https://revenuecat-shipaton-2026.devpost.com/rules): exact dates,
  platform and SDK requirements, Next Gen exception, repository requirements, video, icon, and
  screenshot requirements.
- [Shipaton Next Gen Award](https://www.shipaton.com/next-gen): active-student scope, academic email
  check, public source plus video, and no required store submission or paid developer account.
- [Shipaton FAQ](https://www.shipaton.com/faq): macOS eligibility, required RevenueCat SDK, and the
  distinction between Next Gen and ordinary store submissions.
- [Shipaton resources](https://revenuecat-shipaton-2026.devpost.com/resources): Test Store purchase,
  real-store API call, and real purchase are separate Ship Kit milestones.
- [RevenueCat Test Store](https://www.revenuecat.com/docs/test-and-launch/sandbox/test-store):
  minimum Apple SDK version, Test Store configuration, simulated outcomes, sandbox reporting, and
  entitlement behavior.
- [RevenueCat macOS installation](https://www.revenuecat.com/docs/getting-started/installation/macos):
  the official Apple Purchases SDK supports macOS and Swift Package Manager.

## Implemented Portfolio Workspace foundation

The local Python foundation is additive and does not modify the three verdict rules or existing
single-profile outputs:

- `PortfolioWorkspace` v1 accepts one to five normalized profiles with case-insensitively unique
  names and rejects unknown fields or any invalid nested profile;
- one bounded notice file is parsed once and evaluated independently against every profile at the
  same explicit review point;
- the `portfolio` CLI emits schema-1 deterministic JSON containing one complete canonical schema-3
  report per profile;
- profile and notice input order are preserved;
- each nested report has its own canonical profile digest and the same notice-file digest;
- the top-level summary contains only `profile_count` and the shared `notice_count`, with no score,
  ranking, comparison, or combined verdict total;
- output is ASCII-safe and is written atomically when a destination is supplied;
- the existing `demo`, `qualify`, `fetch-ted`, and Tk desktop contracts remain unchanged.

The synthetic command is:

```text
tenderverdict portfolio \
  --workspace examples/synthetic/portfolio-workspace.json \
  --notices examples/synthetic/notices.json \
  --as-of 2026-08-02 \
  --output portfolio-report.json
```

The completed local audit runs 113 offline tests and includes public-tree, conservative content,
format, type, package, clean-wheel, and installed-CLI checks. Portfolio Workspace is public
Apache-2.0 code and is not an anti-tamper or payment-enforcement boundary.

## RevenueCat feasibility spike

The bounded spike is outside the repository and contains only public code, synthetic fixtures, and
the official `purchases-ios` package pinned to `5.83.0`. It supplies no API key and deliberately
makes no RevenueCat request.

Environment rechecked on 2026-08-04:

- macOS 26.5.2 on arm64;
- Apple Swift 6.3.3 with Command Line Tools 26.6 selected;
- full `/Applications/Xcode.app` absent and `xcodebuild` unavailable;
- Python 3.14.6;
- `swift build` succeeds for the compile-only spike;
- `swift run` references offerings, purchase, `CustomerInfo`, and entitlement APIs, then decodes
  the unchanged TenderVerdict schema-3 synthetic demo through the Python CLI.

Observed output:

```text
RevenueCat SDK linked for macOS; entitlement=supplier_profiles_plus
TenderVerdict core schema=3; total=3; open=1; watch=1; reject=1
```

This spike proved only that the official SDK could link through Swift Package Manager and that a
native process could consume the current Python CLI. It was not a macOS application, Test Store
transaction, entitlement activation, restore, packaged build, or submission artifact. The spike
has now been replaced by the repository source target described below.

## Implemented native source architecture

The repository now contains `macos/TenderVerdictNextGen`, an unreleased macOS Swift package with:

- a SwiftUI application target that shows the first canonical schema-3 report as the free surface
  and the complete one-to-five-profile workspace only for active Premium access;
- `purchases-ios` pinned exactly to `5.83.0` and revision
  `c69a23f56c63bdfe96096fa64a1c65334d2592db`;
- current-offering, package purchase, restore, cancellation, error, and
  `supplier_profiles_plus` entitlement code paths through the official SDK;
- a configuration boundary that accepts only a locally supplied `test_` key, makes no RevenueCat
  request when it is absent, and commits no usable key;
- a local process adapter that invokes the real Python `portfolio` command with a minimal child
  environment and validates schema, counts, profile order, shared notice digest, and distinct
  profile digests before presentation;
- five standalone native contract checks plus a headless end-to-end smoke test that proves the
  synthetic Python workspace projects to one free and three Premium-visible profiles.

The local Command Line Tools build now succeeds, so full Xcode is no longer a source-compilation
prerequisite. Full Xcode remains necessary for the intended interactive application workflow,
packaging, StoreKit/Test Store state verification, and submission media.

## Remaining evidence path

If the organizer confirms Test Store-only eligibility, the remaining minimum is:

1. install and select compatible full Xcode;
2. create the matching RevenueCat Test Store entitlement, product, package, and offering outside
   the repository;
3. supply the key only in a local scheme or launch environment;
4. verify offering load, success, cancellation, failure, restore, relaunch, stale access, and
   missing/offline configuration hands-on;
5. package the app and produce the required public video, icon, screenshot, and final evidence
   record.

A direct Python-to-RevenueCat REST integration, custom fake SDK, production billing, hosted
backend, account system, telemetry, and a rewrite of the verdict engine remain out of scope.

The previous active-hour estimate is no longer treated as an authoritative ledger: the Portfolio
Workspace and native source foundations are now complete, while the organizer answer, interactive
Test Store setup, and full Xcode workflow remain unresolved. Remaining work must be re-estimated
from a verified timer state before claiming compliance with any owner-imposed active-hour cap.

## Organizer question — owner-attested as sent

> For the store-exempt Shipaton 2026 Next Gen submission path, does a local macOS
> debug/developer build using the official RevenueCat Purchases SDK (5.43.0 or newer) with a
> RevenueCat Test Store API key count as the required RevenueCat purchase integration if the demo
> shows a Test Store purchase changing an entitlement-backed UI state, with no App Store product,
> real-store API call, or real payment?

No organizer answer has been verified as of the evidence date.

## Current stop record

- RevenueCat-independent Portfolio Workspace: **implemented and locally validated**.
- Native SwiftUI source application: **implemented, compiled, and headless-smoke-tested locally**.
- Official RevenueCat Apple SDK: **pinned to 5.83.0 and linked by the repository build**.
- RevenueCat project, offering, product, or dashboard configuration: **not created**.
- RevenueCat API key committed or configured: **no**.
- Real or Test Store purchase: **not performed**.
- Entitlement or restore flow: **not performed**.
- Push, pull request, release, store submission, or Devpost project submission: **not performed in
  this audit**.
- Devpost organizer question: **sent according to the owner; response not verified**.
- Transaction and submission gate: **blocked on written Test Store clarification, owner
  confirmation of student/email eligibility, a compatible full Xcode workflow, and configured
  hands-on evidence**.
