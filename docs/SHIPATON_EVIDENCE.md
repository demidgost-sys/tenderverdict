# Shipaton 2026 Next Gen evidence and implementation gate

- Overall status: **CONDITIONAL — TEST STORE FLOW VERIFIED; PUBLIC VIDEO AND SUBMISSION GATES OPEN**
- RevenueCat-independent Portfolio Workspace: **IMPLEMENTED LOCALLY**
- RevenueCat SDK purchase and entitlement source flow: **IMPLEMENTED AND TEST STORE-VERIFIED**
- Evidence rechecked: **2026-08-04**
- Competition branch: `hackathon/revenuecat-next-gen-2026`
- Base before competition changes: `2f4f3855fbc9c7263f8822ace0b6b661ca959ab3`

This file separates official rules, repository evidence, owner-attested actions, technical
feasibility, and facts that remain unknown. It is not proof of eligibility or a Devpost
submission.

## Current decision

The store-exempt Next Gen path is implemented and transaction-verified through RevenueCat Test
Store, but it is not represented here as organizer-approved eligibility. Official materials require
every Project to use the RevenueCat SDK for a purchase or ads. They confirm that Next Gen entrants
can submit public source and a video without a store release or paid developer account, but they do
not explicitly say that a Test Store-only purchase satisfies the Project requirement.

RevenueCat documents Test Store as a real SDK test flow: it can return offerings, simulate purchase
outcomes, update `CustomerInfo`, and activate entitlements without a real charge. Shipaton lists a
first Test Store purchase as a milestone distinct from a real-store API call and a first real
purchase. That proves the technical path and milestone, not the unresolved eligibility
interpretation.

The owner reports that the exact clarification question below was sent through Devpost. No written
organizer answer or public response URL has been verified in this repository, and the owner has
directed the build work to continue without waiting for one. The repository now contains the
complete local product path: SwiftUI inputs, exact official SDK pin, canonical JSON adapter,
fail-closed RevenueCat access client, embedded offline runtime, reproducible Release and Debug
`.app` builders, competition assets, and local Test Store evidence. No usable key, customer
identifier, or account screenshot is retained. A public video, academic-email verification, public
branch update, and Devpost submission remain open.

## Requirement matrix

| Requirement | Evidence class | Current finding | Gate |
|---|---|---|---|
| Submission window | `official_rule` | The controlling Official Rules state July 31, 2026 at 08:00 PDT through September 30, 2026 at 23:45 PDT. The FAQ rounds the opening to August 1; this document uses the Rules. | `CONFIRMED` |
| Repository chronology | `repository_evidence` | The first commit was authored August 2, 2026 at 22:25 CEST, after either published opening description. The public developer alpha followed on August 4. | `CONFIRMED` |
| Next Gen store exception | `official_rule` | Active students may submit a public open-source repository and video without a paid Apple or Google developer account or store release. | `CONFIRMED` |
| Student and academic email | `owner_attested_required` | Active enrollment and the exact Devpost email are entrant-specific and were not verified by this code audit. | `OWNER_CHECK` |
| Public functional repository | `official_rule` + `repository_evidence` | The Python product, Apache-2.0 license, fixtures, SwiftUI source, exact SDK pin, self-contained app builder, run instructions, and local packaged smoke/UX/Test Store evidence are present. The new evidence is local until intentionally pushed. | `LOCAL_READY` |
| Supported platform | `official_rule` | macOS is explicitly allowed by the rules and FAQ. | `CONFIRMED` |
| RevenueCat is substantive | `official_rule` + `observed_test_store` | The official SDK loaded the current offering, executed cancel/failure/success, activated `supplier_profiles_plus`, restored access, and reported the sandbox subscription in RevenueCat. This is a Test Store transaction, not a real payment. | `VERIFIED_TEST_STORE` |
| Test Store technical capability | `official_sdk` | Apple SDK 5.43.0 or newer can use a Test Store key for offerings, simulated outcomes, `CustomerInfo`, and entitlements. | `CONFIRMED_TECHNICALLY` |
| Test Store-only eligibility | `UNKNOWN` | No checked rule, Next Gen page, FAQ, or resource page explicitly says Test Store-only is sufficient for the submission requirement. Work proceeds by owner direction, without claiming organizer approval. | `DISCLOSED_RISK` |
| Required submission media | `official_rule` + `repository_evidence` | The 1024×1024 icon and honest pre-transaction 1179×2556 screenshot are structure-checked. A genuine 1020×754 unlocked supplemental capture is recorded. A public YouTube/Vimeo demo under two minutes remains. | `PARTIAL` |

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

## RevenueCat feasibility history

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

This spike initially proved only that the official SDK could link through Swift Package Manager and
that a native process could consume the current Python CLI. It has now been superseded by the
packaged repository application described below. It remains no evidence of a Test Store
transaction, entitlement activation, or restore.

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
- native workspace/notices selection, explicit review point, local run, preserved prior result on
  error, and atomic deterministic JSON export;
- a local process adapter that invokes either the source Python `portfolio` command or an embedded
  portfolio-only runtime, enforces a 30-second execution boundary, and validates schema, counts,
  profile order, shared notice digest, and distinct profile digests before presentation;
- an in-app process-only secure field for Test Store configuration in addition to the optional
  local environment variable;
- six standalone native contract checks plus source and packaged end-to-end smoke tests;
- a reproducible builder that embeds Python, fixtures, licenses, Swift package resources, and build
  provenance, applies an ad-hoc signature, verifies it, and creates a checksum-paired archive;
- a 1024×1024 icon and a 1179×2556 pre-transaction screenshot generated from reviewed source.

The local Command Line Tools build, interactive app, self-contained packaging, and screenshot
generation now succeed. Full Xcode is not a prerequisite for this competition workflow. It may be
needed only if a later Apple-specific signing, scheme, or debugging step actually requires it.

The packaged hands-on audit selected the committed workspace and notices through native panels,
ran them through the embedded core, exported JSON, and matched the CLI output byte-for-byte. An
invalid review point produced exit status 2 while preserving the previous valid report. Missing
configuration and an `appl_` fixture both stayed fail-closed. See [UX_AUDIT.md](UX_AUDIT.md).

The Test Store evidence pass used the separately packaged Debug app because RevenueCat deliberately
rejects Test Store keys in Release builds. The key was pasted only into the process-local secure
field and was not logged, captured, bundled, or committed. The current offering loaded with a
localized `0,99 $` monthly package. Cancellation kept the app locked; simulated failure produced a
retry state and remained locked; success activated `supplier_profiles_plus` and revealed all three
profile reports. Relaunch required re-entering the process-local key and then recovered the same
active entitlement without a second purchase. `restorePurchases()` preserved unlocked access, and
the RevenueCat dashboard showed the corresponding sandbox subscription. The anonymous customer
identifier was deliberately not recorded.

With VoiceOver enabled, the native accessibility tree exposed distinct names and states for the
inputs, review point, demo, export, and restore controls. Keyboard focus followed the logical order
and skipped the disabled Run button. Restore was activated through the VoiceOver command and the
entitlement remained active. VoiceOver was switched off again after the pass. Supplemental local
artifacts are stored in `submission/evidence/`; neither image contains a key or customer identifier.

## Remaining evidence path

The owner has elected not to wait for an organizer response. The remaining minimum is:

1. repeat all local release gates on the evidence revision and retain the clean commit SHA;
2. record a concise captioned demo from the packaged app and publish it to YouTube or Vimeo with a
   verified duration below two minutes;
3. confirm active-student status and complete Devpost with the qualifying academic email;
4. intentionally publish the evidence revision, verify the public repository and video while
   logged out, and then complete the Devpost submission;
5. disclose the unresolved Test Store-only interpretation accurately and never claim a real
   payment, App Store transaction, or organizer approval.

A direct Python-to-RevenueCat REST integration, custom fake SDK, production billing, hosted
backend, account system, telemetry, and a rewrite of the verdict engine remain out of scope.

The previous active-hour estimate is no longer treated as an authoritative ledger: the Portfolio
Workspace, native application, packaging, interactive Test Store setup, transaction evidence, and
local submission assets are complete, while the public video and final submission gates remain.
Remaining work must be re-estimated from a verified timer state before claiming compliance with any
owner-imposed active-hour cap.

## Organizer question — owner-attested as sent

> For the store-exempt Shipaton 2026 Next Gen submission path, does a local macOS
> debug/developer build using the official RevenueCat Purchases SDK (5.43.0 or newer) with a
> RevenueCat Test Store API key count as the required RevenueCat purchase integration if the demo
> shows a Test Store purchase changing an entitlement-backed UI state, with no App Store product,
> real-store API call, or real payment?

No organizer answer has been verified as of the evidence date. Work continues by owner direction;
this does not convert the unresolved interpretation into an official answer.

## Current stop record

- RevenueCat-independent Portfolio Workspace: **implemented and locally validated**.
- Native SwiftUI source application: **implemented, compiled, and headless-smoke-tested locally**.
- Official RevenueCat Apple SDK: **pinned to 5.83.0 and linked by the repository build**.
- Self-contained macOS `.app`: **built, ad-hoc-signature-verified, and embedded-core-smoke-tested**.
- Native choose/run/export flow: **hands-on verified with exact CLI byte equality**.
- Competition icon and pre-transaction screenshot: **generated and exact-dimension validated**.
- RevenueCat Test Store project, offering, product, package, entitlement, and SDK key: **created and
  hands-on verified outside the repository**.
- RevenueCat API key committed, bundled, logged, or retained in evidence: **no**.
- Test Store purchase: **performed successfully after separate cancel and failure scenarios; no
  real payment was made**.
- Entitlement, relaunch refresh, and restore flow: **hands-on verified in the packaged Debug app**.
- Genuine unlocked and VoiceOver supplemental captures: **recorded locally without a key or
  customer identifier**.
- Public demo video, store submission, or Devpost project submission: **not performed in this audit**.
- Devpost organizer question: **sent according to the owner; response not verified**.
- Account registration email confirmation: **not completed; the observed verification messages
  contained a literal `{link}` placeholder, and the owner directed work to continue without it**.
- Submission gate: **open on student/academic-email confirmation, intentional public branch update,
  public sub-two-minute video, and final logged-out URL checks**.
