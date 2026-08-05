## Summary

Describe the narrow problem and the change that addresses it.

## Product boundaries

- [ ] Qualification remains local-first, deterministic, and explainable.
- [ ] The change does not introduce legal conclusions or autonomous procurement actions.
- [ ] Fixtures are synthetic, public, or fully de-identified.
- [ ] New files are listed explicitly in `PUBLIC_TREE_ALLOWLIST.txt`.

## Validation

- [ ] `PYTHONPATH=src python3 -m unittest discover -s tests -v`
- [ ] `python3 tools/check_public_tree.py`
- [ ] `python3 tools/security_scan.py`
- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy`
- [ ] `python -m build --no-isolation`

## Documentation impact

- [ ] The owning contract/status/evidence page was updated, or this change has no documentation impact.
- [ ] Mutable counts and revision claims live in `docs/PROJECT_STATUS.md` rather than being copied.
- [ ] New public files are linked from `docs/README.md` when appropriate and are in the allow-list.

If Next Gen code, packaging, or assets changed:

- [ ] `swift format lint --recursive --strict macos/TenderVerdictNextGen`
- [ ] `swift run --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks`
- [ ] `swift run -c release --package-path macos/TenderVerdictNextGen TenderVerdictNextGenChecks`
- [ ] Source smoke and applicable packaged/manual/visual checks are listed below.
