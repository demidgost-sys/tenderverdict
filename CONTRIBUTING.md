# Contributing

Issues, reproducible bug reports, and research feedback are welcome. The current evaluation order
and evidence gates are recorded in [ROADMAP.md](ROADMAP.md). Opening an issue or proposing a patch
does not imply that it will be accepted, merged, reviewed by a particular date, or answered
individually.

## Before opening an issue

1. Confirm the problem with the current `main` branch.
2. Use only synthetic, public, or fully de-identified material.
3. Reduce the example to the smallest profile and notice that reproduces the behaviour.
4. State the command, Python version, expected result, and actual result.

Security-sensitive reports follow [SECURITY.md](SECURITY.md), not the public issue tracker.

## Proposed changes

Start with an issue before doing substantial work. A focused patch should preserve these product
boundaries:

- local-first and deterministic qualification;
- no autonomous bid, eligibility, or award decision;
- no legal conclusions;
- no confidential or real-person fixtures;
- no runtime dependency unless the issue establishes a clear need;
- offline tests and reproducible synthetic examples.

Run the local checks before proposing a patch:

```bash
python -m pip install --require-hashes --only-binary=:all: --no-deps \
  -r requirements-package-build.txt
python -m pip install mypy==2.3.0 ruff==0.16.1
python -m pip check
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/check_public_tree.py
python tools/security_scan.py
ruff check .
ruff format --check .
mypy
python -m build --no-isolation
```

On macOS, changes under `macos/TenderVerdictNextGen`, `submission`, or the embedded runtime also
require:

```bash
swift build --package-path macos/TenderVerdictNextGen
swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks
TENDERVERDICT_WORKTREE="$PWD" \
  swift run --package-path macos/TenderVerdictNextGen \
  TenderVerdictNextGen --smoke-test
python3 tools/prepare_submission_assets.py
```

The self-contained app builder and manual evidence sequence are documented in the
[Next Gen README](macos/TenderVerdictNextGen/README.md) and
[UX audit](docs/UX_AUDIT.md).

`requirements-package-build.txt` is the reviewed, hash-locked package-build environment. Desktop
bundles use the separate `requirements-desktop-build.txt` lock. The vocabulary snapshots under
`src/tenderverdict/data/` are intentional release inputs: do not run
`tools/update_vocabularies.py` as a routine development step. A vocabulary refresh is a networked
maintainer operation and must include review of the source metadata, row counts, hashes, and diff.

Do not add files without also updating `PUBLIC_TREE_ALLOWLIST.txt`. Do not weaken a fail-closed check
merely to make a new fixture pass; make the fixture safely synthetic or document the required narrow
exception.

## Licensing

Unless explicitly stated otherwise, submitted contributions are provided under the Apache License
2.0 that covers this repository. You must have the right to submit the material. Do not copy tender
documents, third-party datasets, or code under incompatible terms into the repository.

Please follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) in all project spaces.
