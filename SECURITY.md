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
- The current repository contains no RevenueCat API key or purchase implementation. A future
  native debug integration must keep Test Store configuration out of committed source and fail
  closed when configuration is absent.
- Output can contain content copied from input metadata. Treat generated files as untrusted data.
- A verdict is not a security, legal, eligibility, or procurement decision.

The repository CI performs offline tests, public-tree and distribution validation, a conservative
content scan, CodeQL analysis, and native-build smoke tests. Required checks reduce accidental
exposure; they are not a warranty that the software is free of vulnerabilities.
