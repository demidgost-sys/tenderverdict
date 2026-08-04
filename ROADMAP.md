# Roadmap

This roadmap records the intended evaluation sequence for TenderVerdict. It is not a promise of
dates, support, compatibility, or continued development. A milestone advances only after its
documented evidence gates pass.

## Current state

| Surface | State | Intended user |
|---|---|---|
| `v0.1.0-alpha.1` | Published, immutable CLI developer alpha | Python-capable evaluator |
| `v0.2.0-alpha.1` | Desktop developer alpha with CLI, library, and local UI | Technical evaluator |
| Native desktop archives | Unsigned prerelease archives with checksums and build manifests | Opt-in evaluation only |
| Portfolio Workspace in current source | Offline JSON CLI for one to five profiles | Technical evaluator |
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
[`docs/SHIPATON_EVIDENCE.md`](docs/SHIPATON_EVIDENCE.md). The offline Portfolio Workspace core is
implemented, but it does not satisfy the Shipaton RevenueCat requirement on its own. Native work
remains gated on a written organizer answer confirming whether an official SDK flow using only
RevenueCat Test Store is sufficient for the store-exempt Next Gen path.

If that answer is positive, the remaining order is:

1. install and select a compatible full Xcode toolchain;
2. add a minimal SwiftUI macOS shell that consumes the documented portfolio JSON contract;
3. integrate the official pinned RevenueCat Apple SDK for offering, purchase, restore, and
   `supplier_profiles_plus` entitlement states;
4. keep Test Store configuration fail-closed and out of committed source;
5. test success, failure, cancellation, restore, missing configuration, and offline entitlement
   presentation;
6. produce the required public demo video, icon, screenshot, repository instructions, and final
   evidence audit.

No App Store release, real payment, hosted backend, account system, or production API key belongs
to this conditional Next Gen implementation.

## Candidate follow-on work

Priorities are ordered by evidence value rather than feature count:

1. Run the released archive through demo, CSV import, filtering, copy, and HTML export on a real
   Windows x64 machine; repeat the accessibility portion with NVDA.
2. Repeat the packaged flow on macOS with VoiceOver and record which controls are exposed.
3. Obtain three independent opt-in runs and two concrete procurement-workflow observations using
   synthetic, public, or fully de-identified data.
4. Decide whether demonstrated use justifies paid signing/notarization and a trusted installer.
5. Consider an updater or desktop TED action only after a signed distribution and privacy design
   exist; until then the desktop remains local-only and updates remain manual.

Automatic bidding, bidder or profile scoring, legal conclusions, confidential-document ingestion,
accounts, hosted execution, production payments, and analytics are outside the current roadmap.
