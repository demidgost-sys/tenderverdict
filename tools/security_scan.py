#!/usr/bin/env python3
"""Conservative, dependency-free release scan for TenderVerdict."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import tomllib
from email import policy
from email.parser import Parser
from pathlib import Path
from urllib.parse import urlparse

from check_public_tree import BINARY_ASSET_PATHS, SDIST_METADATA_PATH, TreeError, validate_tree

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})\b", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://(?:\\[.-]|[^\s<>`\"')\\])+")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)(?:api[_-]?key|password|secret|access[_-]?token)\s*[:=]\s*"
    r"['\"][^'\"\n]{8,}"
)
REAL_TED_DETAIL_PATTERNS = (
    re.compile(r"https?://(?:www\.)?ted\.europa\.eu/[^\s]*?/detail/\d", re.IGNORECASE),
    re.compile(r"\b\d{6}-\d{4}\b"),
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    SECRET_ASSIGNMENT_PATTERN,
)
PRICE_MARKER_PATTERN = re.compile(r"(?:€|\$|EUR\s*)\s*\d+(?:[.,]\d{1,2})?")
COMMERCIAL_PATTERNS = (
    re.compile(r"(?i)\bstr[i]pe\b"),
    re.compile(r"(?i)\bpric[i]ng\b"),
    re.compile(r"(?i)\bpaid\s+pilot\b"),
    re.compile(r"(?i)\b(?:buy|purchase|subscribe|donate|pay)\s+(?:now|here|us)\b"),
    PRICE_MARKER_PATTERN,
)
_SWIFT_TRIVIA_SOURCE = r"(?:\s|//[^\n]*(?:\n|$)|/\*.*?\*/)*"
SWIFT_STRING_LITERAL_PATTERN = re.compile(
    r'(?P<raw_hashes>#+)"(?P<raw_body>.*?)"(?P=raw_hashes)'
    r'|"(?P<standard_body>(?:\\.|[^"\\])*)"',
    re.DOTALL,
)
SWIFT_CONCATENATION_LINK_PATTERN = re.compile(
    rf"{_SWIFT_TRIVIA_SOURCE}\+{_SWIFT_TRIVIA_SOURCE}", re.DOTALL
)
SWIFT_CLOSURE_ARGUMENT_PATTERN = re.compile(r"\$\d+\b")
WORKFLOW_USES_PATTERN = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)
PINNED_ACTION_PATTERN = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
_ORGANISATION_SUFFIXES = (
    "Gm" + "bH",
    "LL" + "C",
    "L" + r"td\.?",
    r"S\.A\.",
    r"s\.r\.o\.",
)
ORGANISATION_SUFFIX_PATTERN = re.compile(r"\b(?:" + "|".join(_ORGANISATION_SUFFIXES) + r")\b")
APPROVED_IDENTITY = "Demid Valiullin"
APPROVED_SYNTHETIC_ORGANISATION = "Example Software GmbH"
OFFICIAL_URL_HOSTS = {
    "api.ted.europa.eu",
    "data.europa.eu",
    "developer.apple.com",
    "devpost.com",
    "docs.ted.europa.eu",
    "git-lfs.github.com",
    "github.com",
    "op.europa.eu",
    "publications.europa.eu",
    "purl.org",
    "revenuecat-shipaton-2026.devpost.com",
    "ted.europa.eu",
    "www.apache.org",
    "www.revenuecat.com",
    "www.shipaton.com",
    "www.w3.org",
    "www.youtube.com",
}


def _private_literals() -> tuple[str, ...]:
    return (
        "/" + "Users" + "/",
        "Moser" + "hofgasse",
        "tender" + "-renewal-radar",
        "Date" + "Signal",
        "OPENAI" + "_API_KEY",
        "SMTP" + "_PASSWORD",
    )


def _scan_json_synthetic_fields(relative: str, text: str, errors: list[str]) -> None:
    if not relative.endswith(".json"):
        return
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        errors.append(f"{relative}: invalid JSON fixture ({error})")
        return

    def walk(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "publication_number" and isinstance(item, str):
                    if not item.startswith("SYN-"):
                        errors.append(
                            f"{relative}: committed publication_number must begin with SYN-"
                        )
                if key == "source_url" and isinstance(item, str):
                    hostname = (urlparse(item).hostname or "").lower()
                    if not hostname.endswith(".example"):
                        errors.append(
                            f"{relative}: committed source_url must use a reserved .example host"
                        )
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)


def _scan_csv_synthetic_fields(relative: str, text: str, errors: list[str]) -> None:
    if not relative.endswith(".csv"):
        return
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        for row_number, row in enumerate(reader, start=2):
            publication_number = row.get("publication_number")
            if not publication_number or not publication_number.startswith("SYN-"):
                errors.append(
                    f"{relative}:{row_number}: committed publication_number must begin with SYN-"
                )
            source_url = row.get("source_url")
            if source_url:
                hostname = (urlparse(source_url).hostname or "").lower()
                if not hostname.endswith(".example"):
                    errors.append(
                        f"{relative}:{row_number}: committed source_url must use a "
                        "reserved .example host"
                    )
    except (csv.Error, UnicodeError) as error:
        errors.append(f"{relative}: invalid CSV fixture ({error})")


def _scan_text(relative: str, text: str, errors: list[str]) -> None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append(f"{relative}: possible credential or private key")

    for literal in _private_literals():
        if literal.casefold() in text.casefold():
            errors.append(f"{relative}: private-project or local-machine marker")

    for match in EMAIL_PATTERN.finditer(text):
        domain = match.group(1).lower()
        if not domain.endswith(".example"):
            errors.append(f"{relative}: email address is not an approved synthetic address")

    for raw_url in URL_PATTERN.findall(text):
        normalized_url = raw_url.replace(r"\.", ".").replace(r"\-", "-")
        try:
            hostname = (urlparse(normalized_url.rstrip(".,;:")).hostname or "").lower()
        except ValueError:
            if ".example" not in normalized_url.casefold():
                errors.append(f"{relative}: malformed external URL-shaped text")
            continue
        if not hostname.endswith(".example") and hostname not in OFFICIAL_URL_HOSTS:
            errors.append(f"{relative}: unapproved external URL host: {hostname or '[missing]'}")

    for pattern in REAL_TED_DETAIL_PATTERNS:
        if pattern.search(text):
            errors.append(f"{relative}: real-looking TED notice detail or publication number")

    if relative != "LICENSE":
        for pattern in COMMERCIAL_PATTERNS:
            searchable_text = text
            if relative.endswith(".swift") and pattern is PRICE_MARKER_PATTERN:
                searchable_text = _swift_commercial_text(text)
            if pattern.search(searchable_text):
                errors.append(f"{relative}: commercial call-to-action or price marker")

    if ORGANISATION_SUFFIX_PATTERN.search(text):
        for line in text.splitlines():
            if ORGANISATION_SUFFIX_PATTERN.search(line):
                if APPROVED_SYNTHETIC_ORGANISATION not in line:
                    errors.append(f"{relative}: unapproved real-looking organisation name")

    if APPROVED_IDENTITY.casefold() not in text.casefold() and "Valiullin" in text:
        errors.append(f"{relative}: maintainer identity differs from approved public form")

    _scan_json_synthetic_fields(relative, text, errors)
    _scan_csv_synthetic_fields(relative, text, errors)


def _swift_commercial_text(text: str) -> str:
    """Mask closure shorthand outside literals while preserving visible string content."""
    pieces: list[str] = []
    cursor = 0
    literals = list(SWIFT_STRING_LITERAL_PATTERN.finditer(text))
    for match in literals:
        pieces.append(
            SWIFT_CLOSURE_ARGUMENT_PATTERN.sub("SWIFT_ARGUMENT", text[cursor : match.start()])
        )
        pieces.append(match.group(0))
        cursor = match.end()
    pieces.append(SWIFT_CLOSURE_ARGUMENT_PATTERN.sub("SWIFT_ARGUMENT", text[cursor:]))

    concatenated_values: list[str] = []
    current_value: str | None = None
    for previous, current in zip(literals, literals[1:], strict=False):
        link = text[previous.end() : current.start()]
        if SWIFT_CONCATENATION_LINK_PATTERN.fullmatch(link):
            if current_value is None:
                current_value = _swift_literal_body(previous)
            current_value += _swift_literal_body(current)
            concatenated_values.append(current_value)
        else:
            current_value = None
    return "".join(pieces) + "\n" + "\n".join(concatenated_values)


def _swift_literal_body(match: re.Match[str]) -> str:
    raw_body = match.group("raw_body")
    return raw_body if raw_body is not None else match.group("standard_body") or ""


def _scan_workflows(root: Path, files: list[str], errors: list[str]) -> None:
    workflows = [path for path in files if path.startswith(".github/workflows/")]
    if not workflows:
        errors.append("no GitHub Actions workflow is allow-listed")
        return
    for relative in workflows:
        text = (root / relative).read_text(encoding="utf-8")
        actions = WORKFLOW_USES_PATTERN.findall(text)
        for action in actions:
            if not PINNED_ACTION_PATTERN.fullmatch(action):
                errors.append(f"{relative}: action is not pinned to a full commit SHA: {action}")
        lowered = text.casefold()
        if "${{ secrets." in lowered:
            errors.append(f"{relative}: CI must not read repository secrets")
        if "fetch-ted" in lowered or "api.ted.europa.eu" in lowered:
            errors.append(f"{relative}: CI must not call the live TED adapter")
        if "permissions:" not in text or "contents: read" not in text:
            errors.append(f"{relative}: workflow must declare read-only contents permission")
        checkout_count = sum(action.startswith("actions/checkout@") for action in actions)
        if text.count("persist-credentials: false") < checkout_count:
            errors.append(f"{relative}: checkout must disable persisted credentials")
        if re.search(
            r"(?m)^\s+(?:contents|issues|packages|pull-requests|id-token):\s*write\s*$", text
        ):
            errors.append(f"{relative}: write permissions are forbidden")

        current_job: str | None = None
        current_has_timeout = False
        in_jobs = False
        for line in [*text.splitlines(), "END_OF_WORKFLOW"]:
            if line == "jobs:":
                in_jobs = True
                continue
            job_match = re.fullmatch(r"  ([A-Za-z0-9_-]+):", line) if in_jobs else None
            if job_match or line == "END_OF_WORKFLOW":
                if current_job is not None and not current_has_timeout:
                    errors.append(f"{relative}: job {current_job} has no finite timeout")
                if job_match:
                    current_job = job_match.group(1)
                    current_has_timeout = False
                continue
            if current_job is not None and re.fullmatch(r"    timeout-minutes:\s*[1-9]\d*", line):
                current_has_timeout = True


def _scan_metadata(root: Path, errors: list[str]) -> None:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject.get("project", {})
    if project.get("dependencies") != []:
        errors.append("pyproject.toml: runtime dependencies must remain empty")
    if project.get("requires-python") != ">=3.11":
        errors.append("pyproject.toml: requires-python must be >=3.11")
    if project.get("license") != "Apache-2.0":
        errors.append("pyproject.toml: project license must be Apache-2.0")
    build_requirements = pyproject.get("build-system", {}).get("requires")
    if build_requirements != ["hatchling==1.27.0"]:
        errors.append("pyproject.toml: hatchling build dependency must be exactly pinned")

    license_text = (root / "LICENSE").read_text(encoding="utf-8")
    if "Apache License" not in license_text or "Version 2.0, January 2004" not in license_text:
        errors.append("LICENSE: canonical Apache License 2.0 text not detected")
    if not (root / "NOTICE").is_file():
        errors.append("NOTICE: required attribution boundary is missing")

    sdist_metadata = root / SDIST_METADATA_PATH
    if sdist_metadata.is_file():
        message = Parser(policy=policy.default).parsestr(sdist_metadata.read_text(encoding="utf-8"))
        expected_headers = {
            "Metadata-Version": "2.4",
            "Name": project.get("name"),
            "Version": project.get("version"),
            "Summary": project.get("description"),
            "Author": project.get("authors", [{}])[0].get("name"),
            "License-Expression": project.get("license"),
            "Requires-Python": project.get("requires-python"),
            "Description-Content-Type": "text/markdown",
        }
        for header, expected in expected_headers.items():
            values = message.get_all(header, [])
            if values != [expected]:
                errors.append(
                    f"{SDIST_METADATA_PATH}: {header} must occur once and match pyproject.toml"
                )
        if message.get_all("Requires-Dist"):
            errors.append(f"{SDIST_METADATA_PATH}: runtime dependencies must remain empty")


def scan(root: Path, *, sdist: bool = False) -> list[str]:
    root = root.resolve()
    files = validate_tree(root, sdist=sdist)
    errors: list[str] = []
    for relative in files:
        if relative in BINARY_ASSET_PATHS:
            continue
        text = (root / relative).read_text(encoding="utf-8")
        _scan_text(relative, text, errors)
    _scan_workflows(root, files, errors)
    _scan_metadata(root, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--sdist",
        action="store_true",
        help="require and scan the generated PKG-INFO file in an extracted sdist",
    )
    arguments = parser.parse_args(argv)
    try:
        errors = scan(arguments.root, sdist=arguments.sdist)
    except (OSError, TreeError, UnicodeDecodeError, tomllib.TOMLDecodeError) as scan_error:
        print(f"SECURITY_SCAN_FAIL: {scan_error}", file=sys.stderr)
        return 1
    if errors:
        for scan_error in sorted(set(errors)):
            print(f"SECURITY_SCAN_FAIL: {scan_error}", file=sys.stderr)
        return 1
    print("SECURITY_SCAN_OK: no forbidden release markers detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
