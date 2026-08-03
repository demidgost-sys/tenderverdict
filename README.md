<p align="center">
  <img src="docs/assets/tenderverdict-banner.svg" alt="TenderVerdict turns supplied procurement notice metadata into an explainable local review queue with open_documents, watch, and reject states.">
</p>

<h1 align="center">TenderVerdict</h1>

<p align="center"><strong>Explainable procurement metadata triage, run locally.</strong></p>

<p align="center">
  <a href="https://github.com/demidgost-sys/tenderverdict/actions/workflows/ci.yml"><img src="https://github.com/demidgost-sys/tenderverdict/actions/workflows/ci.yml/badge.svg?branch=main&amp;event=push" alt="CI status for main"></a>
  &nbsp;·&nbsp; <a href="https://github.com/demidgost-sys/tenderverdict/releases/tag/v0.1.0-alpha.1">v0.1.0-alpha.1</a>
  &nbsp;·&nbsp; Python 3.11+
  &nbsp;·&nbsp; <a href="LICENSE">Apache-2.0</a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#desktop-preview">Desktop preview</a> ·
  <a href="#example-output">Example output</a> ·
  <a href="#verdicts">Verdicts</a> ·
  <a href="LIMITATIONS.md">Limitations</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

TenderVerdict is an experimental open-source CLI and Python library for supplier-side
pre-qualification of public-procurement **notice metadata**. You supply a company profile and
structured notices; TenderVerdict applies narrow, deterministic rules and produces a review queue
with reasons, unresolved fields, and a human next step.

It does not read full procurement documents or decide whether you should bid.

| Property | What it means |
|---|---|
| **Local-first** | `demo` and `qualify` read local files and make no network requests. |
| **Deterministic** | The same inputs and `--as-of` date produce the same verdicts. |
| **Traceable** | Every result preserves reasons, unknowns, and the supplied source URL. |
| **Fail closed** | Invalid input or a failed fetch returns an error without publishing partial output. |
| **Small footprint** | The installed package has no runtime dependencies. |

> [!IMPORTANT]
> `v0.1.0-alpha.1` is the immutable CLI developer alpha. The `main` branch also contains an
> unreleased `0.2.0a1` desktop preview. Interfaces and rules may change. Start with the bundled
> synthetic example and avoid confidential inputs while evaluating either version.

## Quick start

Requires Python 3.11 or newer. The commands below install the immutable developer alpha in an
isolated virtual environment.

### macOS or Linux

```bash
git clone --branch v0.1.0-alpha.1 --depth 1 \
  https://github.com/demidgost-sys/tenderverdict.git
cd tenderverdict
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/tenderverdict demo
```

### Windows PowerShell

```powershell
git clone --branch v0.1.0-alpha.1 --depth 1 `
  https://github.com/demidgost-sys/tenderverdict.git
cd tenderverdict
py -m venv .venv
.venv\Scripts\python -m pip install .
.venv\Scripts\tenderverdict demo
```

Once installed, the demo is fully offline and returns exactly one example of each verdict.
Installing from source may download the pinned build tool if it is not already cached.

## Desktop preview

The unreleased desktop preview on `main` removes the need to edit the supplier profile by hand. It
provides labelled fields for the supplier criteria, a file chooser for normalized notices, an
explicit review-date field, a result browser, and atomic HTML, Markdown, or JSON export.

It uses the same deterministic workflow as the CLI. It does not upload data, fetch TED metadata,
open source URLs automatically, or make a participation decision.

```bash
git clone https://github.com/demidgost-sys/tenderverdict.git
cd tenderverdict
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/tenderverdict desktop
```

This source preview requires Python 3.11+ with Tk. Packaged macOS and Windows builds are CI-only,
unsigned developer artifacts until they pass platform testing; they are not a public release. See
[`DESKTOP.md`](DESKTOP.md) for the exact trust, privacy, build, and accessibility boundaries.

## Example output

| Verdict | Why it appears | Human next step |
|---|---|---|
| `open_documents` | Exact CPV and geography match, sufficient lead time, competition notice, valid HTTPS source URL | Open and review the official documents. |
| `watch` | Important metadata is missing or only a broader CPV-family match is available | Resolve the flagged uncertainty first. |
| `reject` | A configured hard stop applies, such as a near deadline or explicit mismatch | Stop unless the metadata is corrected. |

<details>
<summary><strong>View the complete synthetic HTML report</strong></summary>

<p align="center">
  <img src="demo/screenshot.png" width="900" alt="Synthetic TenderVerdict report with one open_documents result, one watch result, and one reject result.">
</p>

The report is generated from fictional data committed to this repository. Reproduce it with:

```bash
tenderverdict demo --format html --output demo/index.html
```

</details>

## Qualify local notice metadata

```bash
tenderverdict qualify \
  --profile examples/synthetic/profile.json \
  --notices examples/synthetic/notices.json \
  --as-of 2026-08-02 \
  --format markdown \
  --output report.md
```

Use `--format json` for machine-readable output. Validation errors return a non-zero exit code and
do not replace an existing output file.

Minimal company profile:

```json
{
  "schema_version": 1,
  "name": "Example Software GmbH",
  "cpv_codes": ["72260000"],
  "countries": ["AUT", "DEU"],
  "minimum_days_to_deadline": 14
}
```

See [`examples/synthetic`](examples/synthetic) for the notice schema and a reproducible example.

## Verdicts

The qualification rules are deliberately narrow:

- `reject` — a closed or near deadline, explicit CPV/country mismatch, or non-competition notice;
- `watch` — missing important metadata, an invalid source URL, or only a CPV-family match;
- `open_documents` — exact CPV and geography match, sufficient lead time, competition notice, and
  a syntactically valid absolute HTTPS source URL.

`open_documents` means only that the configured metadata checks passed. TenderVerdict does not
provide legal advice, determine eligibility, compare bidders, predict outcomes, recommend bidding,
or take an autonomous procurement action. Read [`LIMITATIONS.md`](LIMITATIONS.md) before applying
the output to real work.

## Optional TED metadata fetch

`fetch-ted` is an explicit, read-only network operation. The demo, local qualification, tests, and
CI do not use it.

```bash
tenderverdict fetch-ted \
  --query "classification-cpv = 72260000" \
  --max-notices 10 \
  --output notices.json
```

The adapter uses the fixed HTTPS TED Search API endpoint, bounded pagination and response limits,
and atomic output replacement after a complete successful fetch. Review [`DATA_SOURCES.md`](DATA_SOURCES.md)
and the current source terms before relying on fetched metadata.

## Development

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 tools/check_public_tree.py
python3 tools/security_scan.py
ruff check .
ruff format --check .
mypy
```

The functional test suite is offline; TED behaviour is tested with mocked HTTP responses.
Reproducible bug reports and research feedback are welcome through
[`GitHub Issues`](https://github.com/demidgost-sys/tenderverdict/issues). There is no guaranteed
support or response time during the alpha period.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), and
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) before contributing.

## Deutsch

TenderVerdict ist ein experimentelles, quelloffenes und lokal ausgeführtes CLI zur
Vorqualifizierung von Metadaten öffentlicher Ausschreibungen aus Sicht von Anbietern. Ein lokales
Unternehmensprofil und strukturierte Notice-JSON-Daten werden nachvollziehbar als
`open_documents`, `watch` oder `reject` eingeordnet. Das Werkzeug bietet keine Rechtsberatung,
trifft keine Vergabe- oder Teilnahmeentscheidung und ersetzt nicht die Prüfung der
Ausschreibungsunterlagen.

## License and attribution

The code is licensed under the [`Apache License 2.0`](LICENSE). Procurement records, TED names,
logos, interfaces, and source data are not relicensed by this repository. See [`NOTICE`](NOTICE)
and [`DATA_SOURCES.md`](DATA_SOURCES.md).

Maintained by [Demid Valiullin](https://github.com/demidgost-sys) in Graz, Austria.
