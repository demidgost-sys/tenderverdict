# Contributing

Issues, reproducible bug reports, and research feedback are welcome. TenderVerdict is in an early
30-day evaluation period: opening an issue or proposing a patch does not imply that it will be
accepted, merged, reviewed by a particular date, or answered individually.

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
python -m unittest discover -s tests -v
python tools/check_public_tree.py
python tools/security_scan.py
ruff check .
ruff format --check .
mypy
```

Do not add files without also updating `PUBLIC_TREE_ALLOWLIST.txt`. Do not weaken a fail-closed check
merely to make a new fixture pass; make the fixture safely synthetic or document the required narrow
exception.

## Licensing

Unless explicitly stated otherwise, submitted contributions are provided under the Apache License
2.0 that covers this repository. You must have the right to submit the material. Do not copy tender
documents, third-party datasets, or code under incompatible terms into the repository.

Please follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) in all project spaces.
