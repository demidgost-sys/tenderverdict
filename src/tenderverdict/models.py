"""Validated, dependency-free data models for TenderVerdict."""

from __future__ import annotations

import csv
import io
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Any

_CPV_RE = re.compile(r"^[0-9]{8}$")
_COUNTRY_RE = re.compile(r"^[A-Z]{3}$")
_DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_CSV_LIST_SEPARATOR_RE = re.compile(r"[,;|\s]+")
_CSV_DELIMITERS = (",", ";", "\t")
_MISSING = object()

CSV_NOTICE_COLUMNS = (
    "publication_number",
    "notice_type",
    "title",
    "buyer",
    "cpv_codes",
    "countries",
    "deadline",
    "source_url",
)


class SchemaValidationError(ValueError):
    """Raised when input does not conform to the public schema."""


class Verdict(StrEnum):
    """The three deterministic qualification outcomes."""

    OPEN_DOCUMENTS = "open_documents"
    WATCH = "watch"
    REJECT = "reject"


@dataclass(frozen=True, slots=True)
class Profile:
    schema_version: int
    name: str
    cpv_codes: tuple[str, ...]
    countries: tuple[str, ...]
    minimum_days_to_deadline: int

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "cpv_codes": list(self.cpv_codes),
            "countries": list(self.countries),
            "minimum_days_to_deadline": self.minimum_days_to_deadline,
        }


@dataclass(frozen=True, slots=True)
class Notice:
    publication_number: str
    notice_type: str | None
    title: str | None
    buyer: str | None
    cpv_codes: tuple[str, ...]
    countries: tuple[str, ...]
    deadline: date | None
    source_url: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "publication_number": self.publication_number,
            "notice_type": self.notice_type,
            "title": self.title,
            "buyer": self.buyer,
            "cpv_codes": list(self.cpv_codes),
            "countries": list(self.countries),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "source_url": self.source_url,
        }


@dataclass(frozen=True, slots=True)
class QualificationResult:
    notice: Notice
    verdict: Verdict
    reasons: tuple[str, ...]
    unknowns: tuple[str, ...]
    human_next_step: str

    def to_dict(self) -> dict[str, object]:
        return {
            "publication_number": self.notice.publication_number,
            "title": self.notice.title,
            "source_url": self.notice.source_url,
            "verdict": self.verdict.value,
            "reasons": list(self.reasons),
            "unknowns": list(self.unknowns),
            "human_next_step": self.human_next_step,
        }


def parse_iso_date(value: str, field_name: str = "date") -> date:
    """Parse only the documented ``YYYY-MM-DD`` form."""

    if not isinstance(value, str):
        raise SchemaValidationError(f"{field_name} must be a YYYY-MM-DD string")
    if not _DATE_RE.fullmatch(value):
        raise SchemaValidationError(f"{field_name} must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SchemaValidationError(f"{field_name} is not a valid calendar date") from exc


def profile_from_dict(data: Mapping[str, Any]) -> Profile:
    """Validate an in-memory profile mapping."""

    obj = _require_mapping(data, "profile")
    _reject_unknown_keys(
        obj,
        {
            "schema_version",
            "name",
            "cpv_codes",
            "countries",
            "minimum_days_to_deadline",
        },
        "profile",
    )

    schema_version = _required(obj, "schema_version", "profile")
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        raise SchemaValidationError("profile.schema_version must be an integer")
    if schema_version != 1:
        raise SchemaValidationError("profile.schema_version must be 1")

    name = _required_nonempty_string(obj, "name", "profile")
    cpv_codes = _code_list(
        _required(obj, "cpv_codes", "profile"), "profile.cpv_codes", allow_empty=False
    )
    countries = _country_list(
        _required(obj, "countries", "profile"), "profile.countries", allow_empty=False
    )

    minimum_days = _required(obj, "minimum_days_to_deadline", "profile")
    if isinstance(minimum_days, bool) or not isinstance(minimum_days, int):
        raise SchemaValidationError("profile.minimum_days_to_deadline must be an integer")
    if minimum_days < 0:
        raise SchemaValidationError("profile.minimum_days_to_deadline must be at least 0")

    return Profile(
        schema_version=schema_version,
        name=name,
        cpv_codes=cpv_codes,
        countries=countries,
        minimum_days_to_deadline=minimum_days,
    )


def notice_from_dict(data: Mapping[str, Any], index: int | None = None) -> Notice:
    """Validate one normalized notice mapping.

    Missing evidence is represented by ``None`` or an empty list and remains a
    valid input so the qualification layer can return ``watch``.
    """

    label = f"notices[{index}]" if index is not None else "notice"
    obj = _require_mapping(data, label)
    allowed = {
        "publication_number",
        "notice_type",
        "title",
        "buyer",
        "cpv_codes",
        "countries",
        "deadline",
        "source_url",
    }
    _reject_unknown_keys(obj, allowed, label)

    publication_number = _required_nonempty_string(obj, "publication_number", label)
    notice_type = _optional_string(obj.get("notice_type"), f"{label}.notice_type")
    title = _optional_string(obj.get("title"), f"{label}.title")
    buyer = _optional_string(obj.get("buyer"), f"{label}.buyer")

    raw_cpvs = obj.get("cpv_codes")
    cpv_codes = () if raw_cpvs is None else _code_list(raw_cpvs, f"{label}.cpv_codes")
    raw_countries = obj.get("countries")
    countries = () if raw_countries is None else _country_list(raw_countries, f"{label}.countries")

    raw_deadline = obj.get("deadline")
    deadline = None if raw_deadline is None else parse_iso_date(raw_deadline, f"{label}.deadline")
    source_url = _optional_string(obj.get("source_url"), f"{label}.source_url")

    return Notice(
        publication_number=publication_number,
        notice_type=notice_type,
        title=title,
        buyer=buyer,
        cpv_codes=cpv_codes,
        countries=countries,
        deadline=deadline,
        source_url=source_url,
    )


def notices_from_data(data: object) -> tuple[Notice, ...]:
    """Validate an in-memory JSON-compatible notice array."""

    if not isinstance(data, list):
        raise SchemaValidationError("notices must be a JSON array")
    return tuple(notice_from_dict(item, index) for index, item in enumerate(data))


def load_profile(path: str | Path) -> Profile:
    payload = _load_json(path)
    if not isinstance(payload, Mapping):
        raise SchemaValidationError("profile must be a JSON object")
    return profile_from_dict(payload)


def load_notices(path: str | Path) -> tuple[Notice, ...]:
    source = Path(path)
    try:
        payload = source.read_bytes()
    except OSError as exc:
        raise SchemaValidationError(f"Unable to read notices from {source}.") from exc
    return notices_from_file_bytes(payload, source)


def profile_from_json_bytes(payload: bytes, source: str | Path = "profile") -> Profile:
    """Decode and validate one UTF-8 profile snapshot."""

    data = _decode_json_bytes(payload, source)
    if not isinstance(data, Mapping):
        raise SchemaValidationError("profile must be a JSON object")
    return profile_from_dict(data)


def notices_from_json_bytes(
    payload: bytes,
    source: str | Path = "notices",
) -> tuple[Notice, ...]:
    """Decode and validate one UTF-8 notices snapshot."""

    return notices_from_data(_decode_json_bytes(payload, source))


def notices_from_csv_bytes(
    payload: bytes,
    source: str | Path = "notices.csv",
) -> tuple[Notice, ...]:
    """Decode a normalized UTF-8 CSV file and validate every notice row."""

    try:
        text = payload.decode("utf-8-sig")
    except UnicodeError as exc:
        raise SchemaValidationError(f"Save {source} as UTF-8 CSV and try again.") from exc
    if "\0" in text:
        raise SchemaValidationError(f"Remove the null byte from {source} and try again.")
    if not text.strip():
        raise SchemaValidationError("Add the CSV header and at least one notice row.")

    delimiter = _detect_csv_delimiter(text)
    try:
        reader = csv.reader(io.StringIO(text, newline=""), delimiter=delimiter, strict=True)
        raw_header = next(reader)
        header = _validate_csv_header(raw_header)
        notices: list[Notice] = []
        for row in reader:
            line_number = reader.line_num
            if not row or all(not value.strip() for value in row):
                continue
            if len(row) != len(header):
                raise SchemaValidationError(
                    f"CSV row {line_number} has {len(row)} columns; use exactly {len(header)}."
                )
            values = {name: value.strip() for name, value in zip(header, row, strict=True)}
            data: dict[str, object] = {
                "publication_number": values["publication_number"],
                "notice_type": values["notice_type"] or None,
                "title": values["title"] or None,
                "buyer": values["buyer"] or None,
                "cpv_codes": _split_csv_list(values["cpv_codes"]),
                "countries": _split_csv_list(values["countries"]),
                "deadline": values["deadline"] or None,
                "source_url": values["source_url"] or None,
            }
            try:
                notices.append(notice_from_dict(data))
            except SchemaValidationError as exc:
                message = str(exc).removeprefix("notice.")
                raise SchemaValidationError(f"CSV row {line_number}: {message}") from exc
    except StopIteration as exc:
        raise SchemaValidationError("Add the CSV header and at least one notice row.") from exc
    except csv.Error as exc:
        raise SchemaValidationError(f"Fix the malformed CSV near line {reader.line_num}.") from exc

    if not notices:
        raise SchemaValidationError("Add at least one notice row below the CSV header.")
    return tuple(notices)


def notices_from_file_bytes(
    payload: bytes,
    source: str | Path,
) -> tuple[Notice, ...]:
    """Decode notices according to an explicit local ``.csv`` or ``.json`` suffix."""

    suffix = Path(source).suffix.casefold()
    if suffix == ".csv":
        return notices_from_csv_bytes(payload, source)
    if suffix == ".json":
        return notices_from_json_bytes(payload, source)
    raise SchemaValidationError("Choose a notices file ending in .csv or .json.")


def render_notices_csv(notices: tuple[Notice, ...]) -> str:
    """Render normalized notices as an editable, spreadsheet-friendly CSV example."""

    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(CSV_NOTICE_COLUMNS)
    for notice in notices:
        writer.writerow(
            (
                notice.publication_number,
                notice.notice_type or "",
                notice.title or "",
                notice.buyer or "",
                "|".join(notice.cpv_codes),
                "|".join(notice.countries),
                notice.deadline.isoformat() if notice.deadline else "",
                notice.source_url or "",
            )
        )
    return buffer.getvalue()


def _detect_csv_delimiter(text: str) -> str:
    candidates: list[tuple[int, int, int, str]] = []
    expected = set(CSV_NOTICE_COLUMNS)
    for preference, delimiter in enumerate(_CSV_DELIMITERS):
        try:
            first_row = next(
                csv.reader(io.StringIO(text, newline=""), delimiter=delimiter, strict=True)
            )
        except (StopIteration, csv.Error):
            continue
        normalized = [value.strip().casefold() for value in first_row]
        recognized = len(expected.intersection(normalized))
        exact_shape = int(len(normalized) == len(CSV_NOTICE_COLUMNS))
        candidates.append((recognized, exact_shape, -preference, delimiter))
    if not candidates:
        raise SchemaValidationError("Add a valid comma-, semicolon-, or tab-separated CSV header.")
    return max(candidates)[-1]


def _validate_csv_header(raw_header: list[str]) -> tuple[str, ...]:
    header = tuple(value.strip().casefold() for value in raw_header)
    duplicates = sorted({name for name in header if name and header.count(name) > 1})
    if duplicates:
        raise SchemaValidationError("Remove duplicate CSV columns: " + ", ".join(duplicates) + ".")
    expected = set(CSV_NOTICE_COLUMNS)
    actual = set(header)
    missing = sorted(expected - actual)
    unsupported = sorted(name or "(blank)" for name in actual - expected)
    details: list[str] = []
    if missing:
        details.append("add columns: " + ", ".join(missing))
    if unsupported:
        details.append("remove unsupported columns: " + ", ".join(unsupported))
    if details:
        raise SchemaValidationError("Fix the CSV header: " + "; ".join(details) + ".")
    return header


def _split_csv_list(value: str) -> list[str]:
    return [token for token in _CSV_LIST_SEPARATOR_RE.split(value) if token]


def _load_json(path: str | Path) -> object:
    source = Path(path)
    try:
        payload = source.read_bytes()
    except OSError as exc:
        raise SchemaValidationError(f"cannot read valid UTF-8 JSON from {source}") from exc
    return _decode_json_bytes(payload, source)


def _decode_json_bytes(payload: bytes, source: str | Path) -> object:
    try:
        text = payload.decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=_object_without_duplicate_keys,
            parse_constant=_reject_nonfinite_number,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SchemaValidationError(f"cannot read valid UTF-8 JSON from {source}") from exc


def _object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise SchemaValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite_number(value: str) -> object:
    raise SchemaValidationError(f"non-finite JSON number is not allowed: {value}")


def _require_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SchemaValidationError(f"{label} must be a JSON object")
    return value


def _required(obj: Mapping[str, Any], key: str, label: str) -> object:
    value = obj.get(key, _MISSING)
    if value is _MISSING:
        raise SchemaValidationError(f"{label}.{key} is required")
    return value


def _required_nonempty_string(obj: Mapping[str, Any], key: str, label: str) -> str:
    value = _required(obj, key, label)
    if not isinstance(value, str) or not value.strip():
        raise SchemaValidationError(f"{label}.{key} must be a non-empty string")
    return value.strip()


def _optional_string(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise SchemaValidationError(f"{label} must be a string or null")
    stripped = value.strip()
    return stripped or None


def _code_list(value: object, label: str, allow_empty: bool = True) -> tuple[str, ...]:
    return _validated_string_list(value, label, _CPV_RE, "an 8-digit CPV code", allow_empty)


def _country_list(value: object, label: str, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise SchemaValidationError(f"{label} must be an array")
    normalized: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise SchemaValidationError(f"{label}[{index}] must be a string")
        country = item.strip().upper()
        if not _COUNTRY_RE.fullmatch(country):
            raise SchemaValidationError(f"{label}[{index}] must be a 3-letter country code")
        if country not in normalized:
            normalized.append(country)
    if not allow_empty and not normalized:
        raise SchemaValidationError(f"{label} must not be empty")
    return tuple(normalized)


def _validated_string_list(
    value: object,
    label: str,
    pattern: re.Pattern[str],
    expected: str,
    allow_empty: bool,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise SchemaValidationError(f"{label} must be an array")
    normalized: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise SchemaValidationError(f"{label}[{index}] must be a string")
        item = item.strip()
        if not pattern.fullmatch(item):
            raise SchemaValidationError(f"{label}[{index}] must be {expected}")
        if item not in normalized:
            normalized.append(item)
    if not allow_empty and not normalized:
        raise SchemaValidationError(f"{label} must not be empty")
    return tuple(normalized)


def _reject_unknown_keys(obj: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(obj) - allowed)
    if unknown:
        raise SchemaValidationError(f"{label} has unknown field: {unknown[0]}")
