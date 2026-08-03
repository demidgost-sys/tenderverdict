# Security policy

## Supported version

Security fixes are considered for the current `0.x` alpha line only. This is an experimental
project and no response or remediation deadline is guaranteed.

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

- `demo` and `qualify` operate on local files and require no network access.
- `fetch-ted` is the only command that intentionally contacts an external service.
- The desktop preview does not call `fetch-ted`; it accepts local normalized notice metadata.
- The tool does not require credentials and should not be given secrets.
- Output can contain content copied from input metadata. Treat generated files as untrusted data.
- A verdict is not a security, legal, eligibility, or procurement decision.

The repository CI performs offline tests, public-tree validation, and a conservative content scan.
These checks reduce accidental exposure; they are not a warranty that the software is free of
vulnerabilities.
