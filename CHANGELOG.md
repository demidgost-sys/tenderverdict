# Changelog

All notable changes to TenderVerdict are documented here.

The format follows the principles of Keep a Changelog. The project uses Python-compatible version
identifiers and may change interfaces during the alpha period.

## [Unreleased]

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

### Changed

- Moved the shared offline qualification and atomic output path behind a UI-neutral workflow.
- Reworked the desktop preview into a focused two-pane workspace with clearer action hierarchy,
  semantic status feedback, readable verdict metrics, and structured notice explanations.
- Added restrained light and dark palettes with tested text and status contrast.
- Extended the shared offline workflow and CLI to accept explicit `.csv` or `.json` notice files.
- Reworked the public README into a developer-focused project overview and corrected the macOS
  quick start to use `python3`.
- Added GitHub issue and pull-request templates for reproducible, non-confidential feedback.
- Changed TED snapshots to a traceable wrapper and withheld unsafe lot-level evidence whenever the
  Search API does not return exactly one lot identifier.
- Added one aggregate desktop CI gate, a dedicated application icon, and the project version in
  macOS bundle metadata. Binary release checks now verify icon structure, PNG checksums, dimensions,
  and the absence of embedded metadata chunks. Generated sdist metadata is explicitly bounded and
  scanned instead of being deleted before validation.
- Clarified the published CLI, unreleased source preview, short-lived native artifacts, and lack of
  a supported one-click desktop installation path across public documentation.

## [0.1.0a1] - 2026-08-02

### Added

- Local deterministic qualification with `open_documents`, `watch`, and `reject` states.
- Offline synthetic demo in Markdown, JSON, and static HTML formats.
- Explicit read-only TED metadata adapter with bounded pagination and atomic output replacement.
- Traceable reasons, unresolved fields, and human review steps.
- Offline tests, package checks, public-tree validation, and conservative content scanning.

[0.1.0a1]: https://github.com/demidgost-sys/tenderverdict/releases/tag/v0.1.0-alpha.1
