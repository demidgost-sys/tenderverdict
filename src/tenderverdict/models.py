"""Validated, dependency-free data models for TenderVerdict."""

from __future__ import annotations

import csv
import io
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from .vocabularies import is_known_country, is_known_cpv

_CPV_RE = re.compile(r"^[0-9]{8}$")
_COUNTRY_RE = re.compile(r"^[A-Z]{3}$")
_DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_RFC3339_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
_LOT_ID_RE = re.compile(r"^(?:LOT|PAR|GLO)-[A-Z0-9]{4,20}$")
_CSV_LIST_SEPARATOR_RE = re.compile(r"[,;|\s]+")
_CSV_DELIMITERS = (",", ";", "\t")
_RFC3339_UTC_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
_MISSING = object()

MAX_PROFILE_FILE_BYTES = 256 * 1024
MAX_WORKSPACE_FILE_BYTES = 256 * 1024
MAX_NOTICES_FILE_BYTES = 10 * 1024 * 1024
MAX_NOTICE_COUNT = 1_000
MAX_PORTFOLIO_PROFILES = 5
MAX_PROFILE_NAME_CHARACTERS = 200
MAX_PUBLICATION_NUMBER_CHARACTERS = 200
MAX_LOT_ID_CHARACTERS = 24
MAX_NOTICE_TYPE_CHARACTERS = 100
MAX_TITLE_CHARACTERS = 2_000
MAX_BUYER_CHARACTERS = 500
MAX_SOURCE_URL_CHARACTERS = 2_048
MAX_METADATA_WARNING_CHARACTERS = 500
MAX_METADATA_WARNINGS = 10
MAX_CODES_PER_RECORD = 100
MAX_COUNTRIES_PER_RECORD = 100
MAX_MINIMUM_DAYS_TO_DEADLINE = 3_650
MAX_TED_QUERY_CHARACTERS = 10_000
TED_SEARCH_URL = "https://api.ted.europa.eu/v3/notices/search"
TED_SNAPSHOT_LOT_POLICY = "xml_expanded_lots_v1"
LEGACY_TED_SNAPSHOT_LOT_POLICY = "single_lot_only"
SUPPORTED_TED_SNAPSHOT_LOT_POLICIES = {
    LEGACY_TED_SNAPSHOT_LOT_POLICY,
    TED_SNAPSHOT_LOT_POLICY,
}

CSV_NOTICE_COLUMNS = (
    "publication_number",
    "lot_id",
    "notice_type",
    "title",
    "buyer",
    "cpv_codes",
    "countries",
    "deadline",
    "deadline_at",
    "publication_date",
    "source_url",
)
_REQUIRED_CSV_NOTICE_COLUMNS = tuple(
    column
    for column in CSV_NOTICE_COLUMNS
    if column not in {"lot_id", "deadline_at", "publication_date"}
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
class PortfolioWorkspace:
    """A bounded, ordered collection of independently evaluated profiles."""

    schema_version: int
    profiles: tuple[Profile, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "profiles": [profile.to_dict() for profile in self.profiles],
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
    lot_id: str | None = None
    deadline_at: datetime | None = None
    publication_date: date | None = None
    metadata_warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "publication_number": self.publication_number,
            "notice_type": self.notice_type,
            "title": self.title,
            "buyer": self.buyer,
            "cpv_codes": list(self.cpv_codes),
            "countries": list(self.countries),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "source_url": self.source_url,
        }
        if self.lot_id is not None:
            payload["lot_id"] = self.lot_id
        if self.deadline_at is not None:
            payload["deadline_at"] = self.deadline_at.isoformat()
        if self.publication_date is not None:
            payload["publication_date"] = self.publication_date.isoformat()
        if self.metadata_warnings:
            payload["metadata_warnings"] = list(self.metadata_warnings)
        return payload


@dataclass(frozen=True, slots=True)
class NoticeCollection:
    """Validated notices plus optional source metadata from a saved snapshot."""

    notices: tuple[Notice, ...]
    source_kind: str
    ted_query: str | None = None
    retrieved_at: str | None = None
    lot_policy: str | None = None


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
            "lot_id": self.notice.lot_id,
            "title": self.notice.title,
            "buyer": self.notice.buyer,
            "deadline": self.notice.deadline.isoformat() if self.notice.deadline else None,
            "deadline_at": (
                self.notice.deadline_at.isoformat() if self.notice.deadline_at else None
            ),
            "publication_date": self.notice.publication_date.isoformat()
            if self.notice.publication_date
            else None,
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


def parse_rfc3339_datetime(value: str, field_name: str = "datetime") -> datetime:
    """Parse an explicit, timezone-aware RFC 3339 timestamp without fractions."""

    if not isinstance(value, str):
        raise SchemaValidationError(f"{field_name} must be an RFC 3339 timestamp")
    if not _RFC3339_RE.fullmatch(value):
        raise SchemaValidationError(
            f"{field_name} must use YYYY-MM-DDTHH:MM:SSZ or an explicit UTC offset"
        )
    normalized = value.removesuffix("Z") + ("+00:00" if value.endswith("Z") else "")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SchemaValidationError(f"{field_name} is not a valid RFC 3339 timestamp") from exc
    if parsed.utcoffset() is None:
        raise SchemaValidationError(f"{field_name} must include a UTC offset")
    return parsed


def parse_review_point(value: str, field_name: str = "review point") -> date | datetime:
    """Parse a documented calendar date or an exact RFC 3339 review instant."""

    if isinstance(value, str) and _DATE_RE.fullmatch(value):
        return parse_iso_date(value, field_name)
    return parse_rfc3339_datetime(value, field_name)


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

    name = _required_nonempty_string(
        obj,
        "name",
        "profile",
        maximum_characters=MAX_PROFILE_NAME_CHARACTERS,
    )
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
    if minimum_days > MAX_MINIMUM_DAYS_TO_DEADLINE:
        raise SchemaValidationError(
            f"profile.minimum_days_to_deadline must be at most {MAX_MINIMUM_DAYS_TO_DEADLINE}"
        )

    return Profile(
        schema_version=schema_version,
        name=name,
        cpv_codes=cpv_codes,
        countries=countries,
        minimum_days_to_deadline=minimum_days,
    )


def portfolio_workspace_from_dict(data: Mapping[str, Any]) -> PortfolioWorkspace:
    """Validate a versioned workspace containing one to five named profiles."""

    obj = _require_mapping(data, "workspace")
    _reject_unknown_keys(obj, {"schema_version", "profiles"}, "workspace")

    schema_version = _required(obj, "schema_version", "workspace")
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        raise SchemaValidationError("workspace.schema_version must be an integer")
    if schema_version != 1:
        raise SchemaValidationError("workspace.schema_version must be 1")

    profile_data = _required(obj, "profiles", "workspace")
    if not isinstance(profile_data, list):
        raise SchemaValidationError("workspace.profiles must be an array")
    if not profile_data:
        raise SchemaValidationError("workspace.profiles must contain at least 1 profile")
    if len(profile_data) > MAX_PORTFOLIO_PROFILES:
        raise SchemaValidationError(
            f"workspace.profiles must contain at most {MAX_PORTFOLIO_PROFILES} profiles"
        )

    profiles: list[Profile] = []
    seen_names: dict[str, int] = {}
    for index, value in enumerate(profile_data):
        try:
            profile = profile_from_dict(_require_mapping(value, f"workspace.profiles[{index}]"))
        except SchemaValidationError as exc:
            message = str(exc)
            if not message.startswith(f"workspace.profiles[{index}]"):
                message = f"workspace.profiles[{index}]: {message}"
            raise SchemaValidationError(message) from exc

        normalized_name = profile.name.casefold()
        previous_index = seen_names.get(normalized_name)
        if previous_index is not None:
            raise SchemaValidationError(
                "workspace profile names must be unique case-insensitively: "
                f"profiles[{index}].name duplicates profiles[{previous_index}].name"
            )
        seen_names[normalized_name] = index
        profiles.append(profile)

    return PortfolioWorkspace(schema_version=schema_version, profiles=tuple(profiles))


def notice_from_dict(data: Mapping[str, Any], index: int | None = None) -> Notice:
    """Validate one normalized notice mapping.

    Missing evidence is represented by ``None`` or an empty list and remains a
    valid input so the qualification layer can return ``watch``.
    """

    label = f"notices[{index}]" if index is not None else "notice"
    obj = _require_mapping(data, label)
    allowed = {
        "publication_number",
        "lot_id",
        "notice_type",
        "title",
        "buyer",
        "cpv_codes",
        "countries",
        "deadline",
        "deadline_at",
        "publication_date",
        "source_url",
        "metadata_warnings",
    }
    _reject_unknown_keys(obj, allowed, label)

    publication_number = _required_nonempty_string(
        obj,
        "publication_number",
        label,
        maximum_characters=MAX_PUBLICATION_NUMBER_CHARACTERS,
    )
    lot_id = _optional_string(
        obj.get("lot_id"),
        f"{label}.lot_id",
        maximum_characters=MAX_LOT_ID_CHARACTERS,
    )
    if lot_id is not None:
        lot_id = lot_id.upper()
        if not _LOT_ID_RE.fullmatch(lot_id):
            raise SchemaValidationError(
                f"{label}.lot_id must use an official LOT-, PAR-, or GLO- identifier"
            )
    notice_type = _optional_string(
        obj.get("notice_type"),
        f"{label}.notice_type",
        maximum_characters=MAX_NOTICE_TYPE_CHARACTERS,
    )
    title = _optional_string(
        obj.get("title"),
        f"{label}.title",
        maximum_characters=MAX_TITLE_CHARACTERS,
    )
    buyer = _optional_string(
        obj.get("buyer"),
        f"{label}.buyer",
        maximum_characters=MAX_BUYER_CHARACTERS,
    )

    raw_cpvs = obj.get("cpv_codes")
    cpv_codes = () if raw_cpvs is None else _code_list(raw_cpvs, f"{label}.cpv_codes")
    raw_countries = obj.get("countries")
    countries = () if raw_countries is None else _country_list(raw_countries, f"{label}.countries")

    raw_deadline = obj.get("deadline")
    deadline = None if raw_deadline is None else parse_iso_date(raw_deadline, f"{label}.deadline")
    raw_deadline_at = obj.get("deadline_at")
    deadline_at = (
        None
        if raw_deadline_at is None
        else parse_rfc3339_datetime(raw_deadline_at, f"{label}.deadline_at")
    )
    if deadline is not None and deadline_at is not None:
        raise SchemaValidationError(f"{label} must not contain both deadline and deadline_at")
    raw_publication_date = obj.get("publication_date")
    publication_date = (
        None
        if raw_publication_date is None
        else parse_iso_date(raw_publication_date, f"{label}.publication_date")
    )
    source_url = _optional_string(
        obj.get("source_url"),
        f"{label}.source_url",
        maximum_characters=MAX_SOURCE_URL_CHARACTERS,
    )
    metadata_warnings = _bounded_string_list(
        obj.get("metadata_warnings", []),
        f"{label}.metadata_warnings",
        maximum_items=MAX_METADATA_WARNINGS,
        maximum_characters=MAX_METADATA_WARNING_CHARACTERS,
    )

    return Notice(
        publication_number=publication_number,
        notice_type=notice_type,
        title=title,
        buyer=buyer,
        cpv_codes=cpv_codes,
        countries=countries,
        deadline=deadline,
        publication_date=publication_date,
        source_url=source_url,
        lot_id=lot_id,
        deadline_at=deadline_at,
        metadata_warnings=metadata_warnings,
    )


def notices_from_data(data: object) -> tuple[Notice, ...]:
    """Validate an in-memory JSON-compatible notice array."""

    if not isinstance(data, list):
        raise SchemaValidationError("notices must be a JSON array")
    if len(data) > MAX_NOTICE_COUNT:
        raise SchemaValidationError(f"notices must contain at most {MAX_NOTICE_COUNT} records")
    notices = tuple(notice_from_dict(item, index) for index, item in enumerate(data))
    _reject_duplicate_notices(notices)
    return notices


def load_profile(path: str | Path) -> Profile:
    payload = _decode_json_bytes(
        read_bounded_file_bytes(path, MAX_PROFILE_FILE_BYTES, "profile"),
        path,
    )
    if not isinstance(payload, Mapping):
        raise SchemaValidationError("profile must be a JSON object")
    return profile_from_dict(payload)


def load_notices(path: str | Path) -> tuple[Notice, ...]:
    return load_notice_collection(path).notices


def load_notice_collection(path: str | Path) -> NoticeCollection:
    """Read one bounded local notice file together with its source metadata."""

    source = Path(path)
    payload = read_bounded_file_bytes(source, MAX_NOTICES_FILE_BYTES, "notices")
    return notice_collection_from_file_bytes(payload, source)


def read_bounded_file_bytes(path: str | Path, maximum_bytes: int, label: str) -> bytes:
    """Read at most one explicitly bounded local input file."""

    source = Path(path)
    try:
        with source.open("rb") as handle:
            payload = handle.read(maximum_bytes + 1)
    except OSError as exc:
        raise SchemaValidationError(f"Unable to read {label} from {source}.") from exc
    if len(payload) > maximum_bytes:
        maximum_mib = maximum_bytes // (1024 * 1024)
        limit = f"{maximum_mib} MiB" if maximum_mib else f"{maximum_bytes // 1024} KiB"
        raise SchemaValidationError(f"Choose a {label} file no larger than {limit}.")
    return payload


def profile_from_json_bytes(payload: bytes, source: str | Path = "profile") -> Profile:
    """Decode and validate one UTF-8 profile snapshot."""

    _ensure_payload_size(payload, MAX_PROFILE_FILE_BYTES, "profile")
    data = _decode_json_bytes(payload, source)
    if not isinstance(data, Mapping):
        raise SchemaValidationError("profile must be a JSON object")
    return profile_from_dict(data)


def portfolio_workspace_from_json_bytes(
    payload: bytes,
    source: str | Path = "workspace",
) -> PortfolioWorkspace:
    """Decode and validate one bounded UTF-8 portfolio workspace."""

    _ensure_payload_size(payload, MAX_WORKSPACE_FILE_BYTES, "workspace")
    data = _decode_json_bytes(payload, source)
    if not isinstance(data, Mapping):
        raise SchemaValidationError("workspace must be a JSON object")
    return portfolio_workspace_from_dict(data)


def notices_from_json_bytes(
    payload: bytes,
    source: str | Path = "notices",
) -> tuple[Notice, ...]:
    """Decode and validate one UTF-8 notices snapshot."""

    return notice_collection_from_json_bytes(payload, source).notices


def notice_collection_from_json_bytes(
    payload: bytes,
    source: str | Path = "notices",
) -> NoticeCollection:
    """Decode either a local JSON array or a traceable TED snapshot."""

    _ensure_payload_size(payload, MAX_NOTICES_FILE_BYTES, "notices")
    data = _decode_json_bytes(payload, source)
    if isinstance(data, list):
        return NoticeCollection(notices_from_data(data), source_kind="local_json")
    obj = _require_mapping(data, "notice snapshot")
    _reject_unknown_keys(obj, {"schema_version", "source", "notices"}, "notice snapshot")
    schema_version = _required(obj, "schema_version", "notice snapshot")
    if schema_version != 1 or isinstance(schema_version, bool):
        raise SchemaValidationError("notice snapshot.schema_version must be 1")
    source_obj = _require_mapping(
        _required(obj, "source", "notice snapshot"), "notice snapshot.source"
    )
    _reject_unknown_keys(
        source_obj,
        {"kind", "endpoint", "query", "retrieved_at", "lot_policy"},
        "notice snapshot.source",
    )
    kind = _required_nonempty_string(source_obj, "kind", "notice snapshot.source", 40)
    if kind != "ted_search_api":
        raise SchemaValidationError("notice snapshot.source.kind must be ted_search_api")
    endpoint = _required_nonempty_string(
        source_obj,
        "endpoint",
        "notice snapshot.source",
        maximum_characters=MAX_SOURCE_URL_CHARACTERS,
    )
    if endpoint != TED_SEARCH_URL:
        raise SchemaValidationError(
            "notice snapshot.source.endpoint is not the supported TED endpoint"
        )
    query = _required_nonempty_string(
        source_obj,
        "query",
        "notice snapshot.source",
        maximum_characters=MAX_TED_QUERY_CHARACTERS,
    )
    retrieved_at = _required_nonempty_string(
        source_obj,
        "retrieved_at",
        "notice snapshot.source",
        maximum_characters=20,
    )
    _validate_retrieved_at(retrieved_at)
    lot_policy = _required_nonempty_string(
        source_obj,
        "lot_policy",
        "notice snapshot.source",
        maximum_characters=40,
    )
    if lot_policy not in SUPPORTED_TED_SNAPSHOT_LOT_POLICIES:
        raise SchemaValidationError(
            "notice snapshot.source.lot_policy is not a supported TenderVerdict policy"
        )
    notices = notices_from_data(_required(obj, "notices", "notice snapshot"))
    return NoticeCollection(
        notices=notices,
        source_kind=kind,
        ted_query=query,
        retrieved_at=retrieved_at,
        lot_policy=lot_policy,
    )


def notices_from_csv_bytes(
    payload: bytes,
    source: str | Path = "notices.csv",
) -> tuple[Notice, ...]:
    """Decode a normalized UTF-8 CSV file and validate every notice row."""

    _ensure_payload_size(payload, MAX_NOTICES_FILE_BYTES, "notices")
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
                "lot_id": values.get("lot_id") or None,
                "notice_type": values["notice_type"] or None,
                "title": values["title"] or None,
                "buyer": values["buyer"] or None,
                "cpv_codes": _split_csv_list(values["cpv_codes"]),
                "countries": _split_csv_list(values["countries"]),
                "deadline": values["deadline"] or None,
                "deadline_at": values.get("deadline_at") or None,
                "publication_date": values.get("publication_date") or None,
                "source_url": values["source_url"] or None,
            }
            try:
                notices.append(notice_from_dict(data))
                if len(notices) > MAX_NOTICE_COUNT:
                    raise SchemaValidationError(
                        f"CSV contains more than {MAX_NOTICE_COUNT} notice rows."
                    )
            except SchemaValidationError as exc:
                message = str(exc).removeprefix("notice.")
                raise SchemaValidationError(f"CSV row {line_number}: {message}") from exc
    except StopIteration as exc:
        raise SchemaValidationError("Add the CSV header and at least one notice row.") from exc
    except csv.Error as exc:
        raise SchemaValidationError(f"Fix the malformed CSV near line {reader.line_num}.") from exc

    result = tuple(notices)
    _reject_duplicate_notices(result)
    return result


def notices_from_file_bytes(
    payload: bytes,
    source: str | Path,
) -> tuple[Notice, ...]:
    """Decode notices according to an explicit local ``.csv`` or ``.json`` suffix."""

    return notice_collection_from_file_bytes(payload, source).notices


def notice_collection_from_file_bytes(
    payload: bytes,
    source: str | Path,
) -> NoticeCollection:
    """Decode a bounded local file and preserve any embedded source metadata."""

    suffix = Path(source).suffix.casefold()
    if suffix == ".csv":
        return NoticeCollection(notices_from_csv_bytes(payload, source), source_kind="local_csv")
    if suffix == ".json":
        return notice_collection_from_json_bytes(payload, source)
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
                notice.lot_id or "",
                notice.notice_type or "",
                notice.title or "",
                notice.buyer or "",
                "|".join(notice.cpv_codes),
                "|".join(notice.countries),
                notice.deadline.isoformat() if notice.deadline else "",
                notice.deadline_at.isoformat() if notice.deadline_at else "",
                notice.publication_date.isoformat() if notice.publication_date else "",
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
    missing = sorted(set(_REQUIRED_CSV_NOTICE_COLUMNS) - actual)
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


def _required_nonempty_string(
    obj: Mapping[str, Any],
    key: str,
    label: str,
    maximum_characters: int,
) -> str:
    value = _required(obj, key, label)
    if not isinstance(value, str) or not value.strip():
        raise SchemaValidationError(f"{label}.{key} must be a non-empty string")
    stripped = value.strip()
    if len(stripped) > maximum_characters:
        raise SchemaValidationError(
            f"{label}.{key} must be at most {maximum_characters} characters"
        )
    return stripped


def _optional_string(value: object, label: str, maximum_characters: int) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise SchemaValidationError(f"{label} must be a string or null")
    stripped = value.strip()
    if len(stripped) > maximum_characters:
        raise SchemaValidationError(f"{label} must be at most {maximum_characters} characters")
    return stripped or None


def _code_list(value: object, label: str, allow_empty: bool = True) -> tuple[str, ...]:
    normalized = _validated_string_list(
        value,
        label,
        _CPV_RE,
        "an 8-digit CPV code",
        allow_empty,
        MAX_CODES_PER_RECORD,
    )
    for index, code in enumerate(normalized):
        if not is_known_cpv(code):
            raise SchemaValidationError(
                f"{label}[{index}] is not in the bundled official CPV vocabulary"
            )
    return normalized


def _country_list(value: object, label: str, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise SchemaValidationError(f"{label} must be an array")
    if len(value) > MAX_COUNTRIES_PER_RECORD:
        raise SchemaValidationError(
            f"{label} must contain at most {MAX_COUNTRIES_PER_RECORD} values"
        )
    normalized: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise SchemaValidationError(f"{label}[{index}] must be a string")
        country = item.strip().upper()
        if not _COUNTRY_RE.fullmatch(country):
            raise SchemaValidationError(f"{label}[{index}] must be a 3-letter country code")
        if not is_known_country(country):
            raise SchemaValidationError(
                f"{label}[{index}] is not in the bundled current country authority table"
            )
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
    maximum_items: int,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise SchemaValidationError(f"{label} must be an array")
    if len(value) > maximum_items:
        raise SchemaValidationError(f"{label} must contain at most {maximum_items} values")
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


def _bounded_string_list(
    value: object,
    label: str,
    *,
    maximum_items: int,
    maximum_characters: int,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise SchemaValidationError(f"{label} must be an array")
    if len(value) > maximum_items:
        raise SchemaValidationError(f"{label} must contain at most {maximum_items} values")
    normalized: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise SchemaValidationError(f"{label}[{index}] must be a non-empty string")
        text = item.strip()
        if len(text) > maximum_characters:
            raise SchemaValidationError(
                f"{label}[{index}] must be at most {maximum_characters} characters"
            )
        if text not in normalized:
            normalized.append(text)
    return tuple(normalized)


def _reject_duplicate_notices(notices: tuple[Notice, ...]) -> None:
    seen: dict[tuple[str, str], tuple[int, str]] = {}
    scopes: dict[str, tuple[bool, int]] = {}
    for index, notice in enumerate(notices):
        publication_identity = notice.publication_number.casefold()
        has_lot = notice.lot_id is not None
        previous_scope = scopes.get(publication_identity)
        if previous_scope is not None and previous_scope[0] != has_lot:
            raise SchemaValidationError(
                "publication_number mixes notice-level and lot-level rows: "
                f"{notice.publication_number!r} at notices[{index}]"
            )
        scopes[publication_identity] = (has_lot, index)
        identity = (publication_identity, (notice.lot_id or "").casefold())
        previous = seen.get(identity)
        if previous is not None:
            first_index, first_value = previous
            lot_suffix = f" and lot_id {notice.lot_id!r}" if notice.lot_id else ""
            raise SchemaValidationError(
                "duplicate publication_number "
                f"{notice.publication_number!r}{lot_suffix} at notices[{index}]; "
                f"first seen as {first_value!r} at notices[{first_index}]"
            )
        display_identity = (
            f"{notice.publication_number}/{notice.lot_id}"
            if notice.lot_id
            else notice.publication_number
        )
        seen[identity] = (index, display_identity)


def _validate_retrieved_at(value: str) -> None:
    if not _RFC3339_UTC_RE.fullmatch(value):
        raise SchemaValidationError(
            "notice snapshot.source.retrieved_at must use YYYY-MM-DDTHH:MM:SSZ"
        )
    try:
        datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise SchemaValidationError(
            "notice snapshot.source.retrieved_at is not a valid UTC timestamp"
        ) from exc


def _ensure_payload_size(payload: bytes, maximum_bytes: int, label: str) -> None:
    if len(payload) > maximum_bytes:
        maximum_mib = maximum_bytes // (1024 * 1024)
        limit = f"{maximum_mib} MiB" if maximum_mib else f"{maximum_bytes // 1024} KiB"
        raise SchemaValidationError(f"Choose a {label} file no larger than {limit}.")


def _reject_unknown_keys(obj: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(obj) - allowed)
    if unknown:
        raise SchemaValidationError(f"{label} has unknown field: {unknown[0]}")
