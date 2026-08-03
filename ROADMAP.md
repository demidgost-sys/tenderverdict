# Roadmap

This roadmap records the intended evaluation sequence for TenderVerdict. It is not a promise of
dates, support, compatibility, or continued development. A milestone advances only after its
documented evidence gates pass.

## Current state

| Surface | State | Intended user |
|---|---|---|
| `v0.1.0-alpha.1` | Published, immutable CLI developer alpha | Python-capable evaluator |
| `main` / `0.2.0a1` | Unreleased source preview with CLI, library, and desktop UI | Contributor or technical evaluator |
| Native desktop archives | Short-lived, unsigned CI artifacts | Maintainer testing only |
| Hosted service, accounts, payments, analytics | Not implemented | Nobody |

The current product contract remains narrow: local, deterministic pre-qualification of supplied
public-procurement notice metadata. It does not read full tender documents, provide legal advice,
or decide whether to participate.

The source candidate now includes offline official-code validation, timezone-aware deadline
support, verified eForms XML expansion for multi-lot TED results, result filtering/sorting/copy,
hash-locked Python build dependencies, and a first-run handoff inside native archives. These are source
capabilities, not evidence that a desktop release or a platform usability gate has passed.

## Next milestone: `v0.2.0-alpha.1`

The next milestone is an honest desktop developer alpha, not a consumer installer. It may be tagged
only after every gate below has evidence attached to the candidate commit:

1. Required CI and CodeQL checks pass on the exact commit.
2. Wheel, source distribution, `git archive`, and the explicit public-tree allow-list agree.
3. Frozen macOS arm64, macOS Intel, and Windows x64 builds complete and pass their automated smoke
   tests.
4. A person completes the packaged demo, CSV import, review, and HTML export on macOS and Windows.
5. Archive checksums and `BUILD_INFO.txt` match the downloaded artifacts.
6. Unsigned-code, privacy, input-format, accessibility, and support limitations remain visible in
   the release notes and desktop documentation.
7. No open critical or high security finding is accepted into the candidate.
8. The maintainer explicitly approves the final commit, tag, release notes, and public artifacts.

There is currently no supported one-click installation path. Users should not be told to disable
operating-system security controls to run an unsigned preview.

Code can satisfy gates 1-3, 5-7, and prepare gate 8. Gate 4 requires hands-on use of the exact
packaged commit on both operating-system families. Signing/notarization requires external platform
accounts and certificates and is deliberately not simulated by CI.

## Evaluation after the desktop alpha

Feedback remains opt-in through public GitHub issues using synthetic, public, or fully de-identified
examples. TenderVerdict does not collect telemetry or contact prospective users automatically.

Continue desktop work only if the evaluation produces at least:

- three independent successful runs across at least two operating-system families;
- two concrete workflow observations from procurement, supplier, research, or procurement-tech
  perspectives;
- reproducible evidence for the next problem worth solving;
- no unresolved critical or high security issue.

If those signals do not appear, keeping the CLI available and archiving further desktop work is a
valid outcome.

## Candidate follow-on work

Priorities are ordered by evidence value rather than feature count:

1. Run the exact candidate archive through demo, CSV import, filtering, copy, and HTML export on a
   real Windows x64 machine; repeat the accessibility portion with NVDA.
2. Repeat the packaged flow on macOS with VoiceOver and record which controls are exposed.
3. Obtain three independent opt-in runs and two concrete procurement-workflow observations using
   synthetic, public, or fully de-identified data.
4. Decide whether demonstrated use justifies paid signing/notarization and a trusted installer.
5. Consider an updater or desktop TED action only after a signed distribution and privacy design
   exist; until then the desktop remains local-only and updates remain manual.

Automatic bidding, bidder scoring, legal conclusions, confidential-document ingestion, accounts,
hosted execution, payments, and analytics are outside the current roadmap.
