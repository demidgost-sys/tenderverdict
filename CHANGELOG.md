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
- Added an unreleased SwiftUI Next Gen app that consumes the canonical portfolio report,
  preserves one free profile, and presents all profiles for an active `supplier_profiles_plus`
  entitlement.
- Added the official RevenueCat Apple SDK pinned exactly to `5.83.0`, with fail-closed Test Store
  configuration plus offering, purchase, cancellation, restore, and entitlement source paths.
- Added standalone native contract checks, a headless Python-adapter smoke test, and a macOS CI job
  for the Swift package.
- Added native workspace/notices selection, explicit review-point input, selected-file execution,
  preserved prior results on failure, and atomic deterministic JSON export to the Next Gen app.
- Added a process-local secure Test Store key field; keys are not persisted and non-`test_` values
  are rejected before SDK configuration.
- Added a portfolio-only embedded Python runtime and reproducible self-contained macOS app builder
  with ad-hoc signature verification, packaged smoke test, archive, checksum, and CI artifact.
- Added an exact 1024×1024 icon, exact 1179×2556 pre-transaction screenshot, asset generators, a
  Devpost draft, timed demo script, architecture guide, user guide, UX audit, and hackathon runbook.
- Added a native Free review queue with verdict filters, expandable reasons and unknowns, human next
  steps, and safe supplied-source links.
- Added a Premium notice-by-profile comparison matrix that preserves independent verdicts without
  introducing score, ranking, or an automatic recommendation.
- Added complete native result-contract validation for totals, identities, ordered shared notices,
  and byte-stable portfolio consumption, plus a competition scorecard grounded in official rules
  and recent winner patterns.
- Added a canonical project-status ledger that separates local implementation progress, final
  submission readiness, verified evidence, previous-plan completion, and open owner gates.
- Added a native one-to-five-profile builder with reorder, reset, deterministic Save As, strict
  Swift decoding, and canonical Python vocabulary validation before a workspace is accepted.
- Added private offline `normalize-workspace` and `inspect-notices` bridge commands, a typed bounded
  CSV/JSON preview with full-file missing-field counts, and frozen-runtime determinism checks.
- Added explicit opt-in continuity for only the two security-scoped input bookmarks. Tender data,
  reports, review points, and RevenueCat configuration remain session-only, and reopening never
  starts an analysis automatically.
- Added text, buyer, deadline-presence, and verdict filtering for the Free review queue, plus
  searchable Premium comparison and stable-ID reasoning drill-down for each profile/notice cell.
- Added deterministic RevenueCat terminal-state announcements, user-initiated recovery focus,
  increased-contrast styling, reduced-transparency treatment, and a 125-notice native stress case.
- Added a layered documentation system with a repository agent guide, canonical developer map,
  documentation-governance contract, and dated code-to-document technical audit.
- Added native presentation-time escaping for C0, DEL/C1, and Unicode formatting controls without
  changing the underlying report or export evidence.

### Changed

- Extended the installed-wheel smoke test and public documentation to cover the new portfolio CLI
  while keeping the published single-profile CLI and desktop workflows unchanged.
- Refined the SwiftUI app hierarchy with one indigo accent, native file-type cues, calmer surfaces,
  clearer verdict metrics, and an honest profile-access preview in the locked Premium state.
- Made buyer Picker filters exact after normalization, replaced delimiter-based notice IDs with
  collision-safe structured identities, and hardened the release scanner against split Swift price
  literals without misclassifying closure shorthand.
- Reworked the self-contained HTML report into a responsive report surface with semantic outcome
  badges, safe supplied-source links, automatic light and dark appearances, keyboard focus
  treatment, and print-safe styling.
- Documented the conditional Shipaton Next Gen boundary: the portfolio, native app, packaging, and
  local submission assets and Test Store transaction evidence are implemented. Shipaton Managers
  have now confirmed that Test Store is sufficient for Next Gen and that macOS is eligible without
  a platform disadvantage; public video, student-account verification, private-form inspection,
  final accessibility evidence, and submission remain gated.
- Made RevenueCat Test Store configuration Debug-only and fail-closed in Release before any SDK
  call; exact offering, package, and product identifiers must match before purchase.
- Corrected the Free export boundary to emit only the first complete schema-3 report while Premium
  preserves the exact portfolio bytes and complete provenance.
- Aligned Python and Swift safe-source URL rejection, preserved full schema-3 provenance in native
  encoding, and enforced final stdout/stderr caps after child-process exit.
- Extended CI and the self-contained builder with Swift formatting plus configuration-specific
  Debug and Release contract checks, and recorded the full Python project version separately from
  the numeric bundle version.
- Clarified synthetic/current/previous report state, added strict inline review-point recovery and a
  **Use today** action, reset complete filter state across reports, exposed import warnings without
  hover, separated verdict drivers from passed checks, and made retained-report export wording
  explicit.
- Aligned the Profile Builder examples with the shipped workspace, repaired its compact-height
  footer, made field errors specific, and revised the synthetic portfolio and Reject next step so
  the Free demo shows one Open, one Watch, and one Reject without implying valid mismatches are bad
  metadata.

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
