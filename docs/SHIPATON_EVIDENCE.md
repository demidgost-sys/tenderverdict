# Shipaton 2026 Next Gen evidence and implementation gate

- Overall status: **GO — TEST STORE PATH ORGANIZER-CONFIRMED; PUBLIC VIDEO AND SUBMISSION GATES OPEN**
- RevenueCat-independent Portfolio Workspace: **IMPLEMENTED LOCALLY**
- RevenueCat SDK purchase and entitlement source flow: **IMPLEMENTED AND TEST STORE-VERIFIED**
- Repository evidence rechecked: **2026-08-05**
- Official sources last rechecked: **2026-08-05**
- Competition branch: `hackathon/revenuecat-next-gen-2026`
- Base before competition changes: `2f4f3855fbc9c7263f8822ace0b6b661ca959ab3`

This file separates `official_rule`, `repository_evidence`, `manual_evidence`, entrant-specific
owner gates, and facts that remain open. It records the organizer clarification but is not proof
of active-student status or a Devpost submission.

The countable implementation and submission snapshot is maintained in
[PROJECT_STATUS.md](PROJECT_STATUS.md). It does not replace this evidence classification.

## Current decision

The store-exempt Next Gen path is implemented and transaction-verified through RevenueCat Test
Store. Shipaton Manager Perttu Lähteenlahti answered the exact public Devpost question on
2026-08-05: “Test Store is enough for the Next Gen category.” This is direct `manual_evidence` from
the organizer, so Test Store-only is now a **GO** for this category rather than a disclosed
eligibility risk.

The controlling rules still require the RevenueCat SDK and the Next Gen public-source/video path.
RevenueCat documents Test Store as an SDK test flow that returns offerings, simulates purchase
outcomes, updates `CustomerInfo`, and activates entitlements without a real charge. TenderVerdict
uses that exact path; it does not claim a real payment or App Store transaction.

Shipaton Manager Jaewoong Eum separately confirmed in the public Devpost forum that a macOS app is
eligible and has no disadvantage compared with iOS or Android. This reinforces the existing
`official_rule` platform reading with direct `manual_evidence`.

The repository now contains the complete local product path: SwiftUI inputs, native Profile
Builder, canonical import preview, strict Swift/Python contracts, exact official SDK pin,
fail-closed RevenueCat access, opt-in bookmark-only continuity, embedded offline runtime,
reproducible Release and Debug `.app` builders, actionable Free review, stable Premium comparison
drill-down, competition assets, and local Test Store evidence. No usable key, customer identifier,
or account screenshot is retained. Draft PR #12 is the authoritative pushed-revision check record;
the exact audited revision, local-gate totals, and current SSD package live in
[project status](PROJECT_STATUS.md). Post-change asynchronous VoiceOver outcomes, a
fresh final Debug transaction pass, public video, academic-email verification, private Devpost
audit, and submission remain open.

## Requirement matrix

| Requirement | Evidence class | Current finding | Gate |
|---|---|---|---|
| Submission window | `official_rule` | The controlling Official Rules state July 31, 2026 at 08:00 PDT through September 30, 2026 at 23:45 PDT. The FAQ rounds the opening to August 1; this document uses the Rules. | `CONFIRMED` |
| Repository chronology | `repository_evidence` | The first commit was authored August 2, 2026 at 22:25 CEST, after either published opening description. The public developer alpha followed on August 4. | `CONFIRMED` |
| Next Gen store exception | `official_rule` | Active students may submit a public open-source repository and video without a paid Apple or Google developer account or store release. | `CONFIRMED` |
| Student and academic email | `owner_attested_required` | Active enrollment and the exact Devpost email are entrant-specific and were not verified by this code audit. | `OWNER_CHECK` |
| Public functional repository | `official_rule` + `repository_evidence` | The public draft branch contains the Python product, Apache-2.0 license, fixtures, SwiftUI source, exact SDK pin, self-contained app builder, run instructions, and packaged smoke/UX/Test Store evidence. Project status names the exact audited revision and gate result; draft PR #12 is the authoritative pushed-revision check record. | `PUBLIC_DRAFT_READY` |
| Supported platform | `official_rule` + `manual_evidence` | macOS is explicitly allowed by the rules and FAQ. Shipaton Manager Jaewoong Eum also confirmed that macOS is eligible and has no judging disadvantage. | `CONFIRMED` |
| RevenueCat is substantive | `official_rule` + `manual_evidence` | The official SDK loaded the current offering, executed cancel/failure/success, activated `supplier_profiles_plus`, restored access, and reported the sandbox subscription in RevenueCat. This is a Test Store transaction, not a real payment. | `VERIFIED_TEST_STORE` |
| Test Store technical capability | `official_rule` + `repository_evidence` | Apple SDK 5.43.0 or newer can use a Test Store key for offerings, simulated outcomes, `CustomerInfo`, and entitlements; the repository pins 5.83.0 and the local flow exercised those outcomes. | `CONFIRMED_TECHNICALLY` |
| Test Store-only eligibility | `manual_evidence` | Shipaton Manager Perttu Lähteenlahti answered on 2026-08-05: “Test Store is enough for the Next Gen category.” | `ORGANIZER_CONFIRMED` |
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
- [Next Gen Test Store clarification](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient):
  Shipaton Manager Perttu Lähteenlahti confirms that Test Store is enough for Next Gen.
- [macOS submission clarification](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44615-macos-app-submission):
  Shipaton Manager Jaewoong Eum confirms macOS eligibility and no platform disadvantage.

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
- private app-bridge commands normalize a workspace and inspect CSV/JSON notices without changing
  the public CLI: `normalize-workspace` returns canonical strict workspace JSON and
  `inspect-notices` returns a bounded deterministic preview, canonical fields, metadata warnings,
  and missing-field counts;
- the existing `demo`, `qualify`, `fetch-ted`, and Tk desktop contracts remain unchanged.

The public synthetic command remains:

```text
tenderverdict portfolio \
  --workspace examples/synthetic/portfolio-workspace.json \
  --notices examples/synthetic/notices.json \
  --as-of 2026-08-02 \
  --output portfolio-report.json
```

The complete current totals and local result are recorded in [project status](PROJECT_STATUS.md).
The gate covers offline Python behavior, the private launcher, release-scanner regressions,
public-tree, conservative content, format, type, Debug/Release native contracts, source smoke,
assets, signature, embedded core, and package smoke. Pushed CI must still match the exact final
submitted revision. Portfolio Workspace is public Apache-2.0 code and is not an anti-tamper or
payment-enforcement boundary.

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
- a native Profile Builder that creates, renames, reorders, validates, and saves one to five full
  supplier profiles through strict Swift decoding and the canonical Python normalizer;
- a deterministic CSV/JSON import preview with record count, canonical fields, metadata warnings,
  and missing-field diagnostics before analysis;
- `purchases-ios` pinned exactly to `5.83.0` and revision
  `c69a23f56c63bdfe96096fa64a1c65334d2592db`;
- current-offering, package purchase, restore, cancellation, error, and
  `supplier_profiles_plus` entitlement code paths through the official SDK;
- a Debug-only configuration boundary that accepts only a locally supplied `test_` key, requires
  the exact offering/package/product identifiers, makes no RevenueCat request when configuration is
  absent, and commits no usable key; Release refuses configuration before any SDK call;
- native workspace/notices selection, explicit review point, local run, preserved prior result on
  error, Free text/buyer/deadline-presence/verdict filtering and reasoning review, safe
  supplied-source links, and atomic deterministic JSON export;
- explicit continuity that persists only opt-in security-scoped file bookmarks, provides Forget,
  stores no tender content, report, review point, or key, and never auto-runs analysis;
- an entitlement-only Premium comparison that aligns the same notices across profiles, supports
  bounded search, and opens the exact profile/notice reasoning through stable result identity,
  without a score, ranking, or automatic recommendation;
- a local process adapter that invokes a private source/embedded core launcher, enforces a
  30-second execution boundary, and validates workspace/import/report schema, counts,
  result arrays, verdict totals, unique identities, profile order, the ordered shared notice set,
  shared notice digest, and distinct profile digests before presentation;
- a Debug-only in-app process secure field for Test Store configuration in addition to the optional
  local environment variable;
- terminal RevenueCat state mapping, AppKit-backed VoiceOver announcements, recovery-focus mapping,
  and increased-contrast/reduced-transparency-aware presentation;
- standalone Debug and Release native contract checks, including schema-3 Free export isolation,
  visible control/bidi text, exact RevenueCat identifiers, and pure terminal accessibility outcomes,
  plus source and packaged end-to-end smoke paths;
- a reproducible builder that embeds Python, fixtures, licenses, Swift package resources, and build
  provenance, applies an ad-hoc signature, verifies it, and creates a checksum-paired archive;
- a 1024×1024 icon and a 1179×2556 pre-transaction screenshot generated from reviewed source.

The clean release-configuration builder pass named in project status ran on the SSD. It passed
configuration-specific native checks, executed embedded `normalize-workspace` and
`inspect-notices` twice with byte-identical output, verified the ad-hoc signature, passed
worktree-independent app smoke, and produced verified `.app`, `.zip`, and SHA-256 files.
[Project status](PROJECT_STATUS.md) owns the exact path, manifest, checksum, and sizes. This closes
the scoped package gate; it does not replace interactive final-Debug Test Store or manual
accessibility evidence.

The local Command Line Tools build, interactive app, self-contained packaging, and screenshot
generation now succeed. Full Xcode is not a prerequisite for this competition workflow. It may be
needed only if a later Apple-specific signing, scheme, or debugging step actually requires it.

The packaged hands-on audit selected the committed workspace and notices through native panels,
ran them through the embedded core, exported JSON, and matched the CLI output byte-for-byte. An
invalid review point produced exit status 2 while preserving the previous valid report. Missing
configuration and an `appl_` fixture both stayed fail-closed. See [UX_AUDIT.md](UX_AUDIT.md).

The Test Store evidence pass used the separately packaged Debug app because the SDK does not support
Test Store configuration in Release; TenderVerdict now blocks that path before the SDK. The key was
pasted only into the process-local secure field and was not logged, captured, bundled, or committed.
The current offering loaded with a
localized `0,99 $` monthly package. Cancellation kept the app locked; simulated failure produced a
retry state and remained locked; success activated `supplier_profiles_plus` and revealed all three
profile reports. Relaunch required re-entering the process-local key and then recovered the same
active entitlement without a second purchase. `restorePurchases()` preserved unlocked access, and
the RevenueCat dashboard showed the corresponding sandbox subscription. The anonymous customer
identifier was deliberately not recorded.

In the previously packaged baseline, VoiceOver exposed distinct names and states for the
inputs, review point, demo, export, and restore controls. Keyboard focus followed the logical order
and skipped the disabled Run button. Restore was activated through the VoiceOver command and the
entitlement remained active. VoiceOver was switched off again after the pass. Supplemental local
artifacts are stored in `submission/evidence/`; neither image contains a key or customer identifier.

The current UX worktree adds deterministic terminal-state announcements and recovery-focus mapping
plus increased-contrast and reduced-transparency styling. Pure mapping checks and source smoke are
green. Actual purchase, cancel, failure, refresh, and restore announcements in a freshly packaged
build have not yet been manually re-exercised and must not be claimed as complete.

## Remaining evidence path

The organizer gate is closed with a positive answer. The remaining minimum is:

1. run the complete Python, native, public-tree, security, package, and deterministic smoke gate on
   the final source revision;
2. use the fresh self-contained Release app for the interactive local-file, import-preview, Profile
   Builder, review, drill-down, export, and failure-retention pass; refresh and inspect the
   icon/screenshot because the visible UI changed;
3. manually exercise actual Test Store purchase, cancel, failure, refresh, and restore announcements
   with VoiceOver plus Increase Contrast, Reduce Transparency, and a large-text setting;
4. run three opt-in workflow sessions and document only evidence-backed product changes;
5. inspect the exact private Devpost fields after the owner signs in and joins;
6. record a concise captioned demo from the packaged app and publish it to YouTube or Vimeo with a
   verified duration below two minutes;
7. confirm active-student status and complete Devpost with the qualifying academic email;
8. verify the final public repository and video while logged out, and then complete the Devpost
   submission without claiming a real payment or App Store transaction.

A direct Python-to-RevenueCat REST integration, custom fake SDK, production billing, hosted
backend, account system, telemetry, and a rewrite of the verdict engine remain out of scope.

The previous active-hour estimate is no longer treated as an authoritative ledger: the Portfolio
Workspace, native application, packaging, interactive Test Store setup, transaction evidence, and
local submission assets are complete, while the public video and final submission gates remain.
Remaining work must be re-estimated from a verified timer state before claiming compliance with any
owner-imposed active-hour cap.

## Organizer clarification — verified public reply

The owner asked whether the store-exempt macOS Next Gen build could use the official SDK and Test
Store entitlement path without an App Store product or real payment. Shipaton Manager Perttu
Lähteenlahti replied on 2026-08-05:

> Test Store is enough for the Next Gen category.

Source: [public Devpost forum reply](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient).

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
- Devpost organizer question: **answered publicly by Shipaton Manager Perttu Lähteenlahti on
  2026-08-05; Test Store is enough for Next Gen**.
- Account registration email confirmation: **not completed; the observed verification messages
  contained a literal `{link}` placeholder, and the owner directed work to continue without it**.
- Current UX release-configuration package: **the exact SSD path, revision, manifest, and complete
  verification result are recorded in project status; this is not a notarized public release**.
- Public implementation branch and CI: **project status names the audited revision and local gate;
  draft PR #12 remains the authoritative pushed-revision CI record**.
- Submission gate: **open on student/academic-email confirmation, private Devpost audit, public
  sub-two-minute video, final Debug accessibility evidence, and final logged-out URL checks**.
