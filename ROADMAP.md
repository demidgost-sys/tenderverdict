# Roadmap

This roadmap records the intended evaluation sequence for TenderVerdict. It is not a promise of
dates, support, compatibility, or continued development. A milestone advances only after its
documented evidence gates pass.

The current measured snapshot and the reconciliation with earlier plans live in
[`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md). As of 2026-08-05, 20 of 22 local Shipaton
implementation milestones are complete and 8 of 12 final-submission gates are ready. The counts
are a progress ledger, not a probability of winning or a public-release claim.

## Current state

| Surface | State | Intended user |
|---|---|---|
| `v0.1.0-alpha.1` | Published, immutable CLI developer alpha | Python-capable evaluator |
| `v0.2.0-alpha.1` | Desktop developer alpha with CLI, library, and local UI | Technical evaluator |
| Native desktop archives | Unsigned prerelease archives with checksums and build manifests | Opt-in evaluation only |
| Portfolio Workspace in current source | Offline JSON CLI for one to five profiles | Technical evaluator |
| Next Gen SwiftUI app in current source | Source-buildable and self-contained packaged macOS UI with pinned RevenueCat SDK | Competition prototype evaluator |
| Hosted service, accounts, production payments, analytics | Not implemented | Nobody |

The current product contract remains narrow: local, deterministic pre-qualification of supplied
public-procurement notice metadata. It does not read full tender documents, provide legal advice,
or decide whether to participate.

The desktop alpha includes offline official-code validation, timezone-aware deadline
support, verified eForms XML expansion for multi-lot TED results, result filtering/sorting/copy,
hash-locked Python build dependencies, and a first-run handoff inside native archives. The release
remains an evaluation build, not evidence that platform usability or procurement-workflow fit has
been established.

Current source also contains the RevenueCat-independent Portfolio Workspace foundation. It reuses
the canonical profile and qualification rules, evaluates one notice set independently for up to
five profiles, and emits JSON with one schema-3 report per profile. It is not included in the
published `v0.2.0-alpha.1` tag and is not exposed by the Tk desktop.

The competition branch additionally contains an unreleased SwiftUI app that consumes this JSON,
links the official `purchases-ios` `5.83.0` package, keeps one profile visible in free mode, and
maps the `supplier_profiles_plus` entitlement to the complete workspace. It now includes a native
one-to-five-profile builder, bounded CSV/JSON import preview, opt-in bookmark-only continuity,
large-list review filters, and stable comparison drill-down. Source and packaged smoke tests,
strict bridge contracts, native checks, local analysis, deterministic export, and invalid-input
retention pass locally. The reproducible builder produces an embedded-runtime, ad-hoc-signed app
and checksum-paired archive and verifies the private normalize/import commands inside the frozen
runtime. Exact-size icon and pre-transaction screenshot assets are also present. A separate
reproducible Debug artifact completed the configured RevenueCat Test Store offering, cancellation,
failure, retry, purchase, entitlement unlock, relaunch refresh, restore, and VoiceOver restore
path. No key is committed or bundled; this is not a real payment. A Shipaton Manager has now
confirmed that Test Store is sufficient for Next Gen, and another Manager confirmed that macOS is
eligible without a platform disadvantage. A public video and entrant-account eligibility check
have not been established.

## `v0.2.0-alpha.1` release contract

This milestone is an honest desktop developer alpha, not a consumer installer. Its tag and assets
must refer to one exact commit, and the following evidence gates apply:

1. Required CI and CodeQL checks pass on the exact commit.
2. Wheel, source distribution, `git archive`, and the explicit public-tree allow-list agree.
3. Frozen macOS arm64, macOS Intel, and Windows x64 builds complete and pass their automated smoke
   tests.
4. A person completes the packaged demo, CSV import, review, and HTML export on macOS arm64. The
   Windows x64 archive must pass its native frozen smoke test, but a hands-on Windows run is
   post-release evaluation evidence and does not block this developer alpha.
5. Archive checksums and `BUILD_INFO.txt` match the downloaded artifacts.
6. Unsigned-code, privacy, input-format, accessibility, and support limitations remain visible in
   the release notes and desktop documentation.
7. No open critical or high security finding is accepted into the candidate.
8. The maintainer explicitly approves the final commit, tag, release notes, and public artifacts.

There is currently no supported one-click installation path. Users should not be told to disable
operating-system security controls to run an unsigned preview.

Automated Windows evidence confirms startup and the synthetic flow on a native Windows runner; it
does not establish usability, assistive-technology compatibility, or a normal unsigned-download
experience. Signing/notarization requires external platform accounts and certificates and is
deliberately not simulated by CI.

## Evaluation after the desktop alpha

Feedback remains opt-in through public GitHub issues using synthetic, public, or fully de-identified
examples. The `v0.2.0-alpha.1` desktop evaluation is tracked in
[issue #9](https://github.com/demidgost-sys/tenderverdict/issues/9). TenderVerdict does not collect
telemetry or contact prospective users automatically.

Continue desktop work only if the evaluation produces at least:

- three independent successful runs across at least two operating-system families;
- two concrete workflow observations from procurement, supplier, research, or procurement-tech
  perspectives;
- reproducible evidence for the next problem worth solving;
- no unresolved critical or high security issue.

If those signals do not appear, keeping the CLI available and archiving further desktop work is a
valid outcome.

Paid Apple Developer Program membership is deliberately deferred. It may be considered only after
either three independent successful packaged desktop installations, including at least one on
macOS, or one explicit opt-in request for a Developer ID-signed and notarized macOS build.
Maintainer runs and CI jobs do not count toward this threshold.

## Shipaton Next Gen branch

The competition branch has a narrower conditional path documented in
[`docs/SHIPATON_EVIDENCE.md`](docs/SHIPATON_EVIDENCE.md). The Portfolio Workspace core, native app,
self-contained packaging, local submission assets, and hands-on Test Store transaction evidence are
implemented. The organizer gate is closed: a
[Shipaton Manager confirmed that Test Store is enough for Next Gen](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44695-next-gen-eligibility-is-a-test-store-only-purchase-sufficient),
and a separate
[Manager response confirms macOS eligibility without disadvantage](https://revenuecat-shipaton-2026.devpost.com/forum_topics/44615-macos-app-submission).

The remaining order is:

1. build a fresh final-revision Debug app and manually verify asynchronous RevenueCat
   announcements, Increase Contrast, Reduce Transparency, and large-text behavior without
   embedding a usable key;
2. run three opt-in workflow sessions and convert observed friction into bounded product changes;
3. verify the entrant's student/email eligibility and inspect the exact private Devpost fields
   after the owner joins and signs in;
4. only after owner approval, prepare the public demo and complete the final evidence and
   logged-out-link audit.

The pre-final pushed baseline is `67bb5557806279a7dcd6dfa1fcc467c7c41043d7`. The current candidate
adds the builder, import preview, continuity, filters, drill-down, and accessibility hardening and
passes its own complete local source, package, security, and asset gate. Draft PR #12 remains the
authoritative pushed-revision CI record.

No App Store release, real payment, hosted backend, account system, or production API key belongs
to this conditional Next Gen implementation.

## Candidate follow-on work

Priorities are ordered by evidence value rather than feature count:

1. Complete the final packaged accessibility/settings pass and preserve only evidence that cannot
   expose a Test Store key or customer identifier.
2. Run the Next Gen app with three opt-in procurement or supplier users and document two concrete
   workflow changes using public, synthetic, or fully de-identified data.
3. Revisit builder defaults, import guidance, and comparison wording only when those sessions show
   a repeated point of friction; the current bounded implementations are complete.
4. Run the released archive through demo, CSV import, filtering, copy, and HTML export on a real
   Windows x64 machine; repeat the accessibility portion with NVDA.
5. Decide whether demonstrated use justifies paid signing/notarization and a trusted installer.
6. Consider an updater or desktop TED action only after a signed distribution and privacy design
   exist; until then the desktop remains local-only and updates remain manual.

Automatic bidding, bidder or profile scoring, legal conclusions, confidential-document ingestion,
accounts, hosted execution, production payments, and analytics are outside the current roadmap.
