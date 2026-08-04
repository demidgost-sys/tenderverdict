# Security policy

## Supported version

Security fixes are considered on a best-effort basis for the latest published `0.x` alpha and the
current `main` branch. Older commits and short-lived CI artifacts are not supported. This is an
experimental project and no response or remediation deadline is guaranteed.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature for this repository. Include:

- the affected command and version;
- a minimal synthetic reproducer;
- the expected and observed behaviour;
- the likely impact;
- any safe mitigation you have identified.

Do not include credentials, confidential tender documents, personal data, or exploit details in a
public issue. If private reporting is unavailable, open a minimal public issue asking the maintainer
to establish a private channel, without disclosing the vulnerability itself.

Ordinary correctness errors, source-data corrections, and feature requests can use public issues.

## Security boundaries

- `demo`, `qualify`, and `portfolio` operate on local files and require no network access.
- `fetch-ted` is the only command that intentionally contacts an external service.
- The desktop preview does not call `fetch-ted`; it accepts local normalized notice metadata.
- Portfolio Workspace parses one bounded workspace and one bounded notice file before atomically
  emitting JSON; one invalid nested profile fails the whole run.
- The tool does not require credentials and should not be given secrets.
- The unreleased Next Gen shell contains a pinned official RevenueCat SDK integration, but no API
  key. It accepts only a locally supplied Test Store-shaped key, stays locked without one, and does
  not configure the SDK or make a RevenueCat request in that default state.
- A configured Next Gen launch can contact RevenueCat and initiate Test Store purchase or restore
  only after the evaluator supplies local configuration and activates the corresponding UI
  control. Do not put a key in source, reports, logs, issues, or build artifacts.
- The native shell passes only a minimal environment to its Python child process; RevenueCat
  configuration and unrelated parent-process variables are not forwarded.
- The open-source Python CLI and local input files remain directly accessible. The SwiftUI
  entitlement state is a product presentation boundary, not an anti-tamper or confidentiality
  control.
- Output can contain content copied from input metadata. Treat generated files as untrusted data.
- A verdict is not a security, legal, eligibility, or procurement decision.

The repository CI performs offline tests, public-tree and distribution validation, a conservative
content scan, CodeQL analysis, and native-build smoke tests. Required checks reduce accidental
exposure; they are not a warranty that the software is free of vulnerabilities.
