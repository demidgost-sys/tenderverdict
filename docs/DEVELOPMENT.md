# Developer guide

This is the canonical engineering entry point for the current TenderVerdict source tree. It covers
the published Python alpha and the unreleased Shipaton Next Gen macOS surface without treating the
latter as a consumer release.

## Prerequisites

- Python 3.11 or newer;
- Git;
- macOS with Swift 6 and Xcode command-line tools for the Next Gen app;
- pinned Python build tools from the checked-in requirements files when producing distributions or
  app bundles.

The Python runtime package has no third-party runtime dependencies. Swift Package Manager may need
network access the first time it resolves the exactly pinned RevenueCat package; normal product
tests and all local qualification commands are offline.

## Repository map

| Path | Responsibility | Primary checks |
|---|---|---|
| `src/tenderverdict/models.py` | Strict profile, workspace, notice, date, and snapshot parsing | `tests/test_models.py` |
| `src/tenderverdict/qualification.py` | The only verdict-rule implementation | `tests/test_qualification.py` |
| `src/tenderverdict/workflow.py` | Single-profile and portfolio orchestration, provenance, deterministic JSON | `tests/test_workflow.py`, `tests/test_pipeline_e2e.py` |
| `src/tenderverdict/report.py` | Schema-3 JSON plus Markdown and HTML rendering | `tests/test_report.py` |
| `src/tenderverdict/cli.py` | Public command-line interface and exit behavior | `tests/test_cli.py` |
| `src/tenderverdict/desktop.py` | Existing Tk single-profile developer alpha | `tests/test_desktop.py` |
| `src/tenderverdict/ted.py` | Explicit bounded TED network adapter | `tests/test_ted.py` |
| `tools/next_gen_core_launcher.py` | Private packaged bridge: portfolio, normalization, and notice preview only | `tests/test_next_gen_core_launcher.py` |
| `macos/TenderVerdictNextGen/Sources/TenderVerdictNextGenCore` | Strict native contracts, process adapter, queries, and RevenueCat state | Native contract executable |
| `macos/TenderVerdictNextGen/Sources/TenderVerdictNextGenApp` | SwiftUI presentation, file continuity, accessibility, and purchase controls | Source smoke plus manual UX evidence |
| `tools/build_next_gen.py` | Reproducible `.app`, embedded Python core, signing, smoke, ZIP, and checksum | Builder self-verification and packaged smoke |
| `tools/check_public_tree.py` | Exact public-tree and binary-asset policy | CI public-tree job |
| `tools/security_scan.py` | Conservative source, archive, and artifact scan | CI security job and regression tests |
| `docs/PROJECT_STATUS.md` | Mutable readiness and open gates | Documentation audit |

The data and trust flow is described in [architecture](ARCHITECTURE.md). The documentation ownership
rules are in [documentation governance](DOCUMENTATION.md).

## Local setup

For Python development:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m pip install mypy==2.3.0 ruff==0.16.1
PYTHONPATH=src .venv/bin/python -m tenderverdict demo
```

For a reproducible package build, use the reviewed hash lock instead of an unpinned global build
environment:

```bash
python3 -m venv .venv-build
.venv-build/bin/python -m pip install \
  --require-hashes --only-binary=:all: --no-deps \
  -r requirements-package-build.txt
.venv-build/bin/python -m pip check
```

Do not run `tools/update_vocabularies.py` as setup. It is an explicit networked maintainer workflow,
and a refresh changes release inputs.

## Fast feedback

Run the smallest relevant test while editing, then the complete gate before handoff. Examples:

```bash
PYTHONPATH=src python3 -m unittest tests.test_workflow -v
PYTHONPATH=src python3 -m unittest tests.test_next_gen_core_launcher -v
swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks
swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGen \
  --render-review-brief /tmp/tenderverdict-review-brief.html --premium
```

The native check executable validates pure contracts and process behavior. It is not proof of a
rendered accessibility experience or an actual Test Store transaction. The headless brief command
uses the in-app renderer and is intended for local visual review; omit `--premium` to inspect the
Free first-profile projection.

## Complete source gate

Run from the repository root:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/check_public_tree.py
.venv/bin/python tools/security_scan.py
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv-build/bin/python -m build --no-isolation
swift build --package-path macos/TenderVerdictNextGen
swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks
swift run -c release --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks
swift format lint --recursive --strict macos/TenderVerdictNextGen
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen --smoke-test
python3 tools/prepare_submission_assets.py
git diff --check
```

The editable environment owns test/lint/type feedback; the separate hash-locked environment owns
the distribution build. CI repeats the Python suite on every supported interpreter, validates the
exact sdist and wheel, builds legacy desktop targets, builds the Next Gen app, and runs CodeQL.

Exact current test/check totals and the last evidence-backed result belong only in
[project status](PROJECT_STATUS.md). A command returning zero is necessary evidence for the current
checkout; a sentence in a document is not.

## Source and packaged smoke tests

The source smoke uses the private launcher through the same native adapter used during development:

```bash
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen --smoke-test
```

Build the self-contained evaluation artifact only after native, bridge, packaging, dependency, or
bundled-resource changes:

```bash
python3 -m venv .venv-desktop-build
.venv-desktop-build/bin/python -m pip install \
  --require-hashes --only-binary=:all: --no-deps \
  -r requirements-desktop-build.txt
.venv-desktop-build/bin/python tools/build_next_gen.py
```

The target requires macOS 13 or newer. The local builder emits the current host architecture rather
than a universal binary; the audited Apple Silicon artifact is `arm64`. The default output uses the
Swift `release` configuration, embeds no key, disables Test Store configuration before the SDK can
reject it, is ad-hoc signed, and is not notarized. The word `release` here names a compiler
configuration, not a public product release.

On a trusted Mac that already holds a Developer ID Application identity and a validated local
`notarytool` Keychain profile, the same builder can produce the Gatekeeper-verifiable variant:

```bash
.venv-desktop-build/bin/python tools/build_next_gen.py \
  --signing-identity "$DEVELOPER_ID_IDENTITY" \
  --notary-keychain-profile "$NOTARY_PROFILE"
```

Notarization is fail-closed and Release-only. The builder applies the hardened runtime and secure
timestamp, verifies the Developer ID authority, waits at most 20 minutes for an accepted Apple
notary result, staples and validates the ticket, runs a Gatekeeper assessment, and only then exposes
the final app, ZIP, and checksum. Credentials remain in Keychain and are never copied into source,
the application, build metadata, or CI. The secret-free pull-request workflow intentionally keeps
building the ad-hoc evaluation preview.

Every builder mode must verify configuration-specific native checks, the embedded bridge,
signature, worktree-independent smoke test, ZIP, checksum, and build manifest before the artifact
can be called an evaluation candidate.

`build/` and `dist/` are ignored regenerable directories and may contain older candidates. Never
select an artifact by filename alone: inspect `Contents/Resources/BUILD_INFO.txt`, require the exact
intended `source_revision`, `source_dirty=false`, the expected architecture, and a matching checksum.

A separately built Debug artifact is required for hands-on RevenueCat Test Store evidence. Follow
[the hackathon runbook](HACKATHON_RUNBOOK.md); never place a usable key in source, a scheme, a log,
an artifact, or evidence.

## Change map

| If you change | Also inspect or update |
|---|---|
| Profile, notice, workspace, or report schema | Python parser/serializer tests, strict Swift decoder, `ARCHITECTURE.md`, `USER_GUIDE.md`, examples |
| Qualification semantics | Qualification/report regression tests, `README.md`, `LIMITATIONS.md`, changelog; preserve human decision boundary |
| Public CLI or exit behavior | CLI/end-to-end tests, `README.md`, user guide, changelog |
| Private native bridge | Launcher tests, Swift process checks, packaged-core spec, architecture, builder smoke |
| Free/Premium projection | Native contract checks, RevenueCat state model, architecture, user guide, UX audit |
| Native report presentation or export | Gating/escaping/determinism checks, architecture, user guide, UX audit, hands-on Save-panel and rendered-output review |
| Persistence or privacy | Native checks, `SECURITY.md`, architecture, user guide, manual recovery check |
| Native visual or accessibility behavior | Source smoke, native checks, UX audit, regenerated submission asset when appearance changed, manual settings pass |
| Dependency or package pin | Lock/resolution files, metadata tests, license/notices, clean build and security scan |
| Public file set or binary asset | `PUBLIC_TREE_ALLOWLIST.txt`, public-tree check, security scan, sdist inspection |
| Readiness, test totals, evidence, or open gates | `PROJECT_STATUS.md` only; link to it elsewhere |
| Competition rule or organizer response | `SHIPATON_EVIDENCE.md`, then the runbook/scorecard only as needed |

## Definition of done

A change is ready to hand off when:

1. the worktree contains only the intended patch;
2. implementation and tests agree with the documented contract;
3. the applicable complete gate passes;
4. public-tree, security, and Markdown-link checks pass;
5. manual-only evidence is still labelled manual or pending;
6. the owning documentation page is updated without duplicating mutable facts;
7. the commit is focused and the pushed revision's CI is checked when publication to a branch was
   part of the task.

Do not infer a GitHub Release, notarization, production payment, user validation, or Devpost
submission from a green local build.
