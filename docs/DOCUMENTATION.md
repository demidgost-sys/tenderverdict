# Documentation governance

TenderVerdict documentation is layered so a developer can find one authoritative answer and so
mutable competition state does not leak into durable product contracts.

## Layers

| Layer | Purpose | Documents |
|---|---|---|
| Landing | Explain the product, published surfaces, and first successful run | `README.md`, `DESKTOP.md` |
| Durable contract | Define behavior, trust boundaries, limitations, and user concepts | `ARCHITECTURE.md`, `USER_GUIDE.md`, `LIMITATIONS.md`, `SECURITY.md`, `DATA_SOURCES.md` |
| Engineering | Map ownership, commands, change impact, and contribution workflow | `DEVELOPMENT.md`, `AGENTS.md`, `CONTRIBUTING.md` |
| Current state | Record what is verified now, exact counts, open gates, and the latest audit | `PROJECT_STATUS.md`, `TECHNICAL_AUDIT.md`, `UX_AUDIT.md` |
| Competition evidence | Separate official facts, repository evidence, manual evidence, and owner-only gates | `SHIPATON_EVIDENCE.md`, `COMPETITION_SCORECARD.md` |
| Operations | Reproduce packaging, Test Store evidence, assets, demo, and submission checks | `HACKATHON_RUNBOOK.md`, `DEMO_SCRIPT.md`, `submission/` |
| Future | Order evidence-backed follow-on work without presenting it as delivered | `ROADMAP.md` |

The [documentation map](README.md) routes readers across these layers. A layer may summarize another
one, but it must link to the owner instead of becoming a second mutable ledger.

## Authority rules

| Fact type | Authoritative owner | Other pages should |
|---|---|---|
| Schema, runtime, privacy, and failure contract | `ARCHITECTURE.md` plus code/tests | Link or provide a stable user-facing summary |
| Current completion, exact suite totals, revision evidence, and open gates | `PROJECT_STATUS.md` | Avoid copying numbers or SHAs |
| Latest cross-layer audit result | `TECHNICAL_AUDIT.md` | Link to the dated scope and residual risks |
| Official competition rule or organizer clarification | `SHIPATON_EVIDENCE.md` | Cite the same primary source and avoid broader inference |
| Reproducible engineering commands | `DEVELOPMENT.md` | Keep only the smallest surface-specific quick start |
| Manual UX and accessibility outcome | `UX_AUDIT.md` | Preserve the evidence label and date |
| Submission wording and asset inventory | `submission/` | Never treat a draft or generated asset as a submitted entry |
| Future ordering | `ROADMAP.md` | Do not count planned work as complete |

The implementation and executable checks outrank prose when they disagree. A mismatch is a defect:
either correct the implementation or correct the owning document, then add a regression check when
practical.

## Evidence vocabulary

Use these labels consistently:

| Label | Meaning |
|---|---|
| `code_verified` | Source and contract inspected; no runtime outcome implied |
| `automated` | A deterministic command passed on the named checkout or artifact |
| `manual` | A person exercised the named build on the recorded date |
| `official_rule` | A primary competition source states the requirement |
| `organizer_confirmed` | A preserved organizer response resolves the narrow question |
| `owner_gate` | Account, identity, consent, or final-submission fact only the owner can establish |
| `pending` | Required evidence is absent for the current candidate |

Never silently promote `code_verified` to `manual`, an older manual pass to current-revision proof,
or a Test Store transaction to a real payment.

## Release vocabulary

- **Published developer alpha** means the immutable tagged `v0.2.0-alpha.1` source and assets.
- **Release-configuration evaluation artifact** means a Next Gen `.app` compiled with Swift's
  `release` configuration, ad-hoc signed, and locally verified. It is not notarized or published.
- **Final competition candidate** means one exact revision whose required local, packaged, manual,
  and pushed CI evidence all agree. It does not yet mean submitted.
- **Public product release** requires an intentional tag/release, supported distribution path, and
  the release gates appropriate to that surface.
- **Devpost submission** exists only after the owner completes and verifies the external form.

Avoid the bare phrase “release-ready” when one of these narrower states is intended.

## Update triggers

When a change lands:

1. update the durable owner if the contract changed;
2. update `PROJECT_STATUS.md` if current evidence, counts, or gates changed;
3. update the latest audit only when an actual cross-layer audit was performed;
4. update competition evidence only for a new primary source or completed evidence event;
5. update submission copy/assets only when their content actually changed;
6. add every new public file to `PUBLIC_TREE_ALLOWLIST.txt` and keep local Markdown links valid.

Historical evidence should retain its date and revision. Do not rewrite an old manual pass to sound
current; add a new result or state clearly why it remains baseline-only evidence.

## Review checklist

- Is there one owner for every mutable claim?
- Does `README.md` still lead to a successful first run without requiring competition context?
- Do code, tests, schemas, examples, and architecture agree?
- Are `release`, `manual`, `current`, and `submitted` used with a precise scope?
- Are unknown account or external facts still marked `owner_gate` or `pending`?
- Do local links, the public-tree allow-list, sdist contents, and the security scan pass?
- Would a new developer know which check to run and which document to update?

The pull-request template and repository metadata tests keep the most important navigation and
public-tree rules executable, but judgment about evidence scope still requires review.
