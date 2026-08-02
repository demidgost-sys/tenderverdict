# TenderVerdict

TenderVerdict is an experimental open-source, local-first command-line tool and Python library
for supplier-side pre-qualification of public-procurement notice metadata.

It compares a manually supplied company profile with structured notice metadata and produces one
of three review states:

- `open_documents`: the metadata passes the deterministic pre-qualification checks;
- `watch`: important metadata is missing or only a broader CPV-family match is available;
- `reject`: a deterministic exclusion rule applies.

Every result includes human-readable reasons, unresolved fields, and a next review step. The output
is decision support for a person. It is not legal advice, an eligibility determination, a bid/no-bid
recommendation, an award decision, or a substitute for reading the procurement documents.

> **Alpha status:** `0.1.0a1` is an experimental release candidate. Interfaces and rules can change.
> Use synthetic or non-confidential inputs while evaluating it.

## Synthetic offline demo

The demo uses only files committed to this repository and performs no network requests.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install .
tenderverdict demo
```

The generated demo contains exactly one example of each state. Use
`tenderverdict demo --format html --output demo/index.html` to reproduce the tracked HTML copy.

![Synthetic TenderVerdict qualification report](demo/screenshot.png)

The screenshot is generated from the fictional, fully offline example committed to this repository.

## Qualify local notice metadata

```bash
tenderverdict qualify \
  --profile examples/synthetic/profile.json \
  --notices examples/synthetic/notices.json \
  --as-of 2026-08-02 \
  --format markdown \
  --output report.md
```

Use `--format json` for machine-readable output. Input validation failures return a non-zero exit
code and do not replace an existing output file.

The minimal profile schema is:

```json
{
  "schema_version": 1,
  "name": "Example Software GmbH",
  "cpv_codes": ["72260000"],
  "countries": ["AUT", "DEU"],
  "minimum_days_to_deadline": 14
}
```

See the synthetic fixtures for the notice fields expected by the tool.

## Optional TED metadata fetch

`fetch-ted` is an explicit read-only network operation. It is not used by the demo, tests, or CI.

```bash
tenderverdict fetch-ted \
  --query "classification-cpv = 72260000" \
  --max-notices 10 \
  --output notices.json
```

The adapter uses the fixed HTTPS TED Search API endpoint, applies bounded pagination and response
limits, and replaces the output only after a complete successful fetch. Review the source data and
the current TED terms before relying on it. See [DATA_SOURCES.md](DATA_SOURCES.md).

## What the rules mean

The rules are intentionally narrow and deterministic:

- closed or too-near deadlines, explicit CPV/country mismatches, and non-competition notices are
  `reject`;
- missing required metadata, a missing or syntactically invalid absolute HTTPS source URL, or only
  a CPV-family match is `watch`;
- an exact CPV and geography match, enough lead time, a competition notice, and a syntactically
  valid absolute HTTPS source URL are `open_documents`.

There is no confidence score, prediction, bidder comparison, or autonomous procurement action.
Read [LIMITATIONS.md](LIMITATIONS.md) before applying the output to real work.

## Development

```bash
python -m unittest discover -s tests -v
python tools/check_public_tree.py
python tools/security_scan.py
ruff check .
ruff format --check .
```

The functional test suite is offline. TED behaviour is tested with mocked HTTP responses.

Issues and research feedback are welcome. During the first 30 days, opening an issue does not imply
that a change will be merged or that an individual response will be available. See
[CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Deutsch

TenderVerdict ist ein experimentelles, quelloffenes und lokal ausgeführtes Kommandozeilenwerkzeug
zur Vorqualifizierung von Metadaten öffentlicher Ausschreibungen aus Sicht von Anbietern. Es
erstellt nachvollziehbare Prüfhinweise für Menschen. Es bietet keine Rechtsberatung, trifft keine
Vergabe- oder Teilnahmeentscheidung und ersetzt nicht die Prüfung der Ausschreibungsunterlagen.

## License and attribution

The code is licensed under the [Apache License 2.0](LICENSE). Procurement records, TED names,
logos, interfaces, and source data are not relicensed by this repository. See [NOTICE](NOTICE) and
[DATA_SOURCES.md](DATA_SOURCES.md).

Maintained by Demid Valiullin in Graz, Austria.
