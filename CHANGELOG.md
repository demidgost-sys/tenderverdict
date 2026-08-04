# Changelog

All notable changes to TenderVerdict are documented here.

The format follows the principles of Keep a Changelog. The project uses Python-compatible version
identifiers and may change interfaces during the alpha period.

## [Unreleased]

### Added

- Added a bounded Portfolio Workspace v1 contract for one to five uniquely named supplier profiles.
- Added the offline `portfolio` command, which evaluates one shared notice set independently for
  every profile and emits deterministic JSON containing canonical schema-3 profile reports.
- Added a three-profile synthetic workspace plus validation, ordering, provenance, empty-input,
  terminal-safety, atomic-output, and network-isolation regression coverage.
- Added an unreleased SwiftUI Next Gen source shell that consumes the canonical portfolio report,
  preserves one free profile, and presents all profiles for an active `supplier_profiles_plus`
  entitlement.
- Added the official RevenueCat Apple SDK pinned exactly to `5.83.0`, with fail-closed Test Store
  configuration plus offering, purchase, cancellation, restore, and entitlement source paths.
- Added standalone native contract checks, a headless Python-adapter smoke test, and a macOS CI job
  for the Swift package.

### Changed

- Extended the installed-wheel smoke test and public documentation to cover the new portfolio CLI
  while keeping the published single-profile CLI and desktop workflows unchanged.
- Documented the conditional Shipaton Next Gen boundary: the portfolio and native source
  foundations are implemented, while dashboard configuration, a Test Store transaction, packaged
  app evidence, and eligibility remain gated.

## [0.2.0a1] - 2026-08-04

### Added

- Added an unreleased local desktop preview for editing supplier profiles, reviewing normalized
  notices, inspecting explainable results, and exporting reports.
- Added short-lived macOS arm64, macOS Intel, and Windows x64 developer-artifact builds.
- Added bounded input snapshots and provenance checks so changed notices cannot export a stale
  report.
- Added normalized UTF-8 CSV notice import with row-level validation, common spreadsheet delimiter
  support, and an editable synthetic CSV example in the desktop preview.
- Added report provenance with generator version, input SHA-256 digests, optional TED query and UTC
  retrieval time, plus notice publication dates.
- Added bounded record and field counts, case-insensitive publication-number uniqueness, and a
  consistent zero-notice policy for CSV and JSON.
- Added a version-based roadmap with explicit desktop-release, manual-platform, security, and
  evaluation gates.
- Added source-traceable offline validation against bundled EU CPV and current country authority
  snapshots, plus a bounded maintainer refresh tool with atomic per-file replacement.
- Added optional lot identifiers and timezone-aware RFC 3339 deadlines while preserving v0.1 CSV
  and JSON input compatibility.
- Added verified multi-lot expansion through bounded official eForms XML with fail-closed
  Search/XML identifier matching.
- Added desktop verdict filters, sortable result headings, and explicit plain-text copy.
- Added hash-locked package and desktop build dependencies plus a first-run guide with synthetic
  data inside every native developer archive.

### Changed

- Moved the shared offline qualification and atomic output path behind a UI-neutral workflow.
- Reworked the desktop preview into a focused two-pane workspace with clearer action hierarchy,
  semantic status feedback, readable verdict metrics, and structured notice explanations.
- Added restrained light and dark palettes with tested text and status contrast.
- Extended the shared offline workflow and CLI to accept explicit `.csv` or `.json` notice files.
- Reworked the public README into a developer-focused project overview and corrected the macOS
  quick start to use `python3`.
- Added GitHub issue and pull-request templates for reproducible, non-confidential feedback.
- Changed TED snapshots to `xml_expanded_lots_v1`: single-lot Search fields remain direct,
  multi-lot results require verified eForms XML, and zero-lot ambiguity remains withheld.
- Added one aggregate desktop CI gate, a dedicated application icon, and the project version in
  macOS bundle metadata. Binary release checks now verify icon structure, PNG checksums, dimensions,
  and the absence of embedded metadata chunks. Generated sdist metadata is explicitly bounded and
  scanned instead of being deleted before validation.
- Fixed text checkout to use LF on every platform so vocabulary and provenance digests remain
  identical on Windows, macOS, and Linux.
- Clarified the published CLI, unreleased source preview, short-lived native artifacts, and lack of
  a supported one-click desktop installation path across public documentation.
- Published checksum-paired macOS arm64, macOS Intel, and Windows x64 archives as an unsigned
  desktop developer alpha for opt-in evaluation.
- Made hands-on Windows use post-release evidence rather than an alpha release blocker while
  retaining native Windows build and frozen smoke-test requirements.
- Deferred Apple Developer Program membership until three independent packaged installations or
  one explicit request for a signed and notarized macOS build.

## [0.1.0a1] - 2026-08-02

### Added

- Local deterministic qualification with `open_documents`, `watch`, and `reject` states.
- Offline synthetic demo in Markdown, JSON, and static HTML formats.
- Explicit read-only TED metadata adapter with bounded pagination and atomic output replacement.
- Traceable reasons, unresolved fields, and human review steps.
- Offline tests, package checks, public-tree validation, and conservative content scanning.

[0.1.0a1]: https://github.com/demidgost-sys/tenderverdict/releases/tag/v0.1.0-alpha.1
[0.2.0a1]: https://github.com/demidgost-sys/tenderverdict/releases/tag/v0.2.0-alpha.1
[Unreleased]: https://github.com/demidgost-sys/tenderverdict/compare/v0.2.0-alpha.1...HEAD
