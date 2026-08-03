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

If desktop packaging changed, list the affected native targets and the completed manual or visual
checks below.
