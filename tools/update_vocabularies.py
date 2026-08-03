#!/usr/bin/env python3
"""Refresh the bundled CPV and country-code snapshots from the EU Cellar."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = ROOT / "src" / "tenderverdict" / "data"
SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"
MAX_RESPONSE_BYTES = 2_000_000
TIMEOUT_SECONDS = 30

CPV_QUERY = """\
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?notation WHERE {
  ?concept a skos:Concept ; skos:notation ?notation .
  FILTER(STRSTARTS(STR(?concept), "http://data.europa.eu/cpv/cpv/"))
}
ORDER BY ?notation
"""

COUNTRY_QUERY = """\
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX euvoc: <http://publications.europa.eu/ontology/euvoc#>
SELECT DISTINCT ?identifier WHERE {
  ?concept dc:identifier ?identifier ;
    euvoc:status <http://publications.europa.eu/resource/authority/concept-status/CURRENT> .
  FILTER(STRSTARTS(
    STR(?concept),
    "http://publications.europa.eu/resource/authority/country/"
  ))
  FILTER(REGEX(STR(?identifier), "^[A-Z]{3}$"))
}
ORDER BY ?identifier
"""


def _fetch_csv(query: str) -> str:
    request = Request(
        SPARQL_ENDPOINT + "?" + urlencode({"query": query, "format": "text/csv"}),
        headers={
            "Accept": "text/csv",
            "User-Agent": "TenderVerdict vocabulary snapshot maintainer",
        },
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/csv" not in content_type.casefold():
                raise RuntimeError(f"unexpected Content-Type: {content_type or '(missing)'}")
            payload = response.read(MAX_RESPONSE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise RuntimeError("unable to retrieve the official vocabulary snapshot") from exc
    if len(payload) > MAX_RESPONSE_BYTES:
        raise RuntimeError("official vocabulary response exceeded the safety limit")
    try:
        return payload.decode("utf-8-sig")
    except UnicodeError as exc:
        raise RuntimeError("official vocabulary response was not UTF-8") from exc


def _values(csv_text: str, column: str, pattern: re.Pattern[str]) -> list[str]:
    reader = csv.DictReader(io.StringIO(csv_text))
    if reader.fieldnames != [column]:
        raise RuntimeError(f"official vocabulary response did not contain only {column}")
    values = [row[column].strip() for row in reader]
    if not values or any(not pattern.fullmatch(value) for value in values):
        raise RuntimeError(f"official vocabulary response contained an invalid {column}")
    if values != sorted(set(values)):
        raise RuntimeError(f"official vocabulary response was not sorted and unique: {column}")
    return values


def _snapshot(values: list[str]) -> str:
    return "\n".join(values) + "\n"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def _write_atomically(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--retrieved-on",
        required=True,
        type=date.fromisoformat,
        help="explicit YYYY-MM-DD retrieval date recorded in the snapshot metadata",
    )
    args = parser.parse_args(argv)

    try:
        cpv_values = _values(_fetch_csv(CPV_QUERY), "notation", re.compile(r"[0-9]{8}"))
        country_values = _values(
            _fetch_csv(COUNTRY_QUERY),
            "identifier",
            re.compile(r"[A-Z]{3}"),
        )
        if len(cpv_values) < 9_000 or len(country_values) < 250:
            raise RuntimeError("official vocabulary response was unexpectedly incomplete")
        cpv_snapshot = _snapshot(cpv_values)
        country_snapshot = _snapshot(country_values)
        metadata = {
            "schema_version": 1,
            "retrieved_on": args.retrieved_on.isoformat(),
            "endpoint": SPARQL_ENDPOINT,
            "cpv": {
                "source": "Common Procurement Vocabulary",
                "query": CPV_QUERY.strip(),
                "records": len(cpv_values),
                "sha256": _sha256(cpv_snapshot),
            },
            "countries": {
                "source": "Countries and territories authority table (CURRENT concepts)",
                "query": COUNTRY_QUERY.strip(),
                "records": len(country_values),
                "sha256": _sha256(country_snapshot),
            },
        }
        DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
        _write_atomically(DATA_DIRECTORY / "cpv_codes.txt", cpv_snapshot)
        _write_atomically(DATA_DIRECTORY / "country_codes.txt", country_snapshot)
        _write_atomically(
            DATA_DIRECTORY / "VOCABULARY_SOURCES.json",
            json.dumps(metadata, ensure_ascii=True, indent=2) + "\n",
        )
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"VOCABULARY_REFRESH_FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        "VOCABULARY_REFRESH_OK: "
        f"{len(cpv_values)} CPV codes and {len(country_values)} country codes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
