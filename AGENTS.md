# Repository guide for coding agents

This file applies to the whole TenderVerdict repository. It is intentionally short: durable product
contracts live in the documentation linked below, not in agent-specific instructions.

## First five minutes

1. Run `git status --short --branch` and preserve unrelated or pre-existing work.
2. Read [the documentation map](docs/README.md).
3. Read [project status](docs/PROJECT_STATUS.md) before making a readiness claim.
4. Read [architecture](docs/ARCHITECTURE.md) before changing a schema, boundary, or runtime.
5. Use [the developer guide](docs/DEVELOPMENT.md) for the repository map and exact verification
   commands.

## Canonical sources

| Question | Source of truth |
|---|---|
| What the product promises | `README.md`, `LIMITATIONS.md`, `docs/USER_GUIDE.md` |
| How data and runtimes interact | `docs/ARCHITECTURE.md` and the implementation |
| What is complete or still open | `docs/PROJECT_STATUS.md` |
| What the latest audit actually checked | `docs/TECHNICAL_AUDIT.md` |
| Which competition facts are verified | `docs/SHIPATON_EVIDENCE.md` |
| How to build, test, and package | `docs/DEVELOPMENT.md` and the surface-specific README |
| How documentation is organized | `docs/DOCUMENTATION.md` |

Do not copy mutable test counts, commit identifiers, readiness percentages, or manual-evidence
status into durable architecture pages. Link to `docs/PROJECT_STATUS.md` instead.

## Product invariants

- `demo`, `qualify`, and `portfolio` stay local and deterministic for explicit inputs and `as_of`.
- `fetch-ted` is the only intentional Python product network path.
- The three verdicts remain `open_documents`, `watch`, and `reject`; they are metadata triage, not
  legal advice or an autonomous bid decision.
- Portfolio reports reuse complete schema-3 single-profile reports. Do not add cross-profile score,
  ranking, recommendation, or combined verdict totals.
- Free keeps one complete profile analysis and a schema-3 single-profile export. RevenueCat
  entitlement `supplier_profiles_plus` controls the native multi-profile presentation and full
  portfolio export.
- Never commit or bundle a RevenueCat key. Production-shaped keys fail closed in the competition
  app; Test Store configuration is process-local and Debug-only, while Release refuses it before
  any RevenueCat SDK call.
- Invalid CLI output must not replace an existing file, and a failed Next Gen run must preserve its
  last valid report. The legacy Tk desktop intentionally clears results when its selected input
  changes; do not generalize one surface's retention behavior to every UI.
- Fixtures must be synthetic, public, or fully de-identified.

## Change workflow

- Keep Python qualification authority under `src/tenderverdict`; do not reimplement verdict logic in
  Swift or Tk.
- Update tests with behavior changes and keep all functional tests offline.
- Add every new public file to `PUBLIC_TREE_ALLOWLIST.txt`; keep that file bytewise sorted.
- Update the owning document named in [documentation governance](docs/DOCUMENTATION.md), then link
  to it rather than repeating a mutable claim.
- Run the scoped checks while iterating and the complete gate in
  [the developer guide](docs/DEVELOPMENT.md) before handoff.
- Use a focused commit. Do not mix an unrelated cleanup, generated cache, credential, or private
  evidence into the patch.

## External and release boundaries

Building and testing locally are normal development steps. A tag, GitHub Release, merge, Devpost
submission, production purchase, notarization, or publication is an external action and requires an
explicit task that names that action. A Swift `release` configuration is still only an evaluation
artifact unless the release gates say otherwise.
