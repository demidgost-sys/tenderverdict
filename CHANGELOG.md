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

### Changed

- Moved the shared offline qualification and atomic output path behind a UI-neutral workflow.
- Reworked the desktop preview into a focused two-pane workspace with clearer action hierarchy,
  semantic status feedback, readable verdict metrics, and structured notice explanations.
- Added restrained light and dark palettes with tested text and status contrast.
- Extended the shared offline workflow and CLI to accept explicit `.csv` or `.json` notice files.
- Reworked the public README into a developer-focused project overview and corrected the macOS
  quick start to use `python3`.
- Added GitHub issue and pull-request templates for reproducible, non-confidential feedback.

## [0.1.0a1] - 2026-08-02

### Added

- Local deterministic qualification with `open_documents`, `watch`, and `reject` states.
- Offline synthetic demo in Markdown, JSON, and static HTML formats.
- Explicit read-only TED metadata adapter with bounded pagination and atomic output replacement.
- Traceable reasons, unresolved fields, and human review steps.
- Offline tests, package checks, public-tree validation, and conservative content scanning.

[0.1.0a1]: https://github.com/demidgost-sys/tenderverdict/releases/tag/v0.1.0-alpha.1
