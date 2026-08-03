"""Small, read-only adapter for the public TED Search API.

The adapter intentionally has no persistence or retry policy.  Callers receive a
complete, normalized list or an exception, which lets the CLI publish output
atomically after the request has succeeded.
"""

from __future__ import annotations

import json
import math
import re
import xml.etree.ElementTree as ElementTree
from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime
from http.client import HTTPException
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from ._version import __version__
from .models import (
    TED_SEARCH_URL,
    TED_SNAPSHOT_LOT_POLICY,
    notice_collection_from_json_bytes,
)

DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_MAX_RESPONSE_BYTES = 5_000_000
MAX_RESPONSE_BYTES = 10_000_000
MAX_NOTICES = 1_000
MAX_XML_DOCUMENTS = 100
MAX_PAGE_SIZE = 250
MAX_STALLED_PAGES = 3
MAX_QUERY_CHARACTERS = 10_000

# These fields are sufficient for the public TenderVerdict notice contract.
# TED includes its language-specific notice links alongside selected fields.
TED_FIELDS = (
    "publication-number",
    "publication-date",
    "form-type",
    "notice-title",
    "buyer-name",
    "main-classification-proc",
    "main-classification-lot",
    "additional-classification-proc",
    "additional-classification-lot",
    "place-of-performance-country-proc",
    "place-of-performance-country-lot",
    "deadline-receipt-tender-date-lot",
    "deadline-receipt-tender-time-lot",
    "identifier-lot",
)

_PUBLICATION_NUMBER_RE = re.compile(r"^[0-9]{6}-[0-9]{4}$")
_LOT_IDENTIFIER_RE = re.compile(r"^LOT-[A-Z0-9]{4,20}$")
_EFORMS_DATE_RE = re.compile(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})(Z|[+-][0-9]{2}:[0-9]{2})?$")
_EFORMS_TIME_RE = re.compile(r"^([0-9]{2}:[0-9]{2}:[0-9]{2})(Z|[+-][0-9]{2}:[0-9]{2})?$")
_UBL_NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


class TedApiError(RuntimeError):
    """Raised when TED cannot return a complete, valid search page."""


PageSearcher = Callable[..., Mapping[str, Any]]


def fetch_notices(
    query: str,
    *,
    max_notices: int,
    page_size: int = 100,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
    opener: Callable[..., Any] = urlopen,
    searcher: PageSearcher | None = None,
) -> list[dict[str, Any]]:
    """Fetch a bounded, deduplicated list of normalized TED notices.

    ``query`` is passed as a TED expert query.  The requested page size stays
    constant for the whole PAGE_NUMBER traversal so page offsets cannot shift
    merely because the final result target is smaller than a full page.

    ``searcher`` exists for deterministic tests and embedded use.  It must
    return the same page mapping as TED (including a ``notices`` list).
    """

    clean_query = _validate_options(
        query=query,
        max_notices=max_notices,
        page_size=page_size,
        timeout=timeout,
        max_response_bytes=max_response_bytes,
    )

    output: list[dict[str, Any]] = []
    seen_publications: set[str] = set()
    source_notice_count = 0
    xml_document_count = 0
    page = 1
    stalled_pages = 0
    expected_total: int | None = None
    expected_target: int | None = None
    # Pagination is bounded even if the remote dataset changes between pages.
    page_budget = math.ceil(max_notices / page_size) + MAX_STALLED_PAGES

    while source_notice_count < max_notices and page <= page_budget:
        if searcher is None:
            result = _search_page(
                clean_query,
                page=page,
                limit=page_size,
                timeout=timeout,
                max_response_bytes=max_response_bytes,
                opener=opener,
            )
        else:
            result = searcher(
                clean_query,
                page=page,
                limit=page_size,
                timeout=timeout,
                max_response_bytes=max_response_bytes,
            )

        raw_notices, total_count = _validate_page(result)
        if expected_total is None:
            expected_total = total_count
            expected_target = min(max_notices, total_count)
        elif total_count != expected_total:
            raise TedApiError(
                "TED totalNoticeCount changed during pagination; results may be incomplete"
            )

        count_before_page = source_notice_count
        for raw_notice in raw_notices:
            publication_number = _nonempty_text(raw_notice.get("publication-number"))
            if publication_number is None:
                raise TedApiError("TED notice is missing publication-number")
            if publication_number in seen_publications:
                continue
            lot_identifiers = _unique_strings(raw_notice.get("identifier-lot"))
            if len(lot_identifiers) > 1:
                xml_document_count += 1
                if xml_document_count > MAX_XML_DOCUMENTS:
                    raise TedApiError(
                        f"TED fetch requires more than {MAX_XML_DOCUMENTS} bounded XML documents"
                    )
                normalized_rows = _expand_multi_lot_notice(
                    raw_notice,
                    timeout=timeout,
                    max_response_bytes=max_response_bytes,
                    opener=opener,
                )
            else:
                normalized_rows = [normalize_notice(raw_notice)]
            if len(output) + len(normalized_rows) > MAX_NOTICES:
                raise TedApiError(
                    f"lot expansion exceeds the {MAX_NOTICES}-record snapshot safety limit"
                )
            seen_publications.add(publication_number)
            output.extend(normalized_rows)
            source_notice_count += 1
            if source_notice_count >= max_notices:
                break

        if source_notice_count == count_before_page:
            stalled_pages += 1
        else:
            stalled_pages = 0

        assert expected_target is not None
        if source_notice_count >= expected_target:
            return output
        if stalled_pages >= MAX_STALLED_PAGES:
            raise _incomplete_results_error(
                reason="pagination repeated rows without progress",
                collected=source_notice_count,
                expected=expected_target,
            )
        if len(raw_notices) < page_size:
            raise _incomplete_results_error(
                reason="TED returned a premature short page",
                collected=source_notice_count,
                expected=expected_target,
            )
        if page * page_size >= total_count:
            raise _incomplete_results_error(
                reason="reported page range ended before all unique rows were collected",
                collected=source_notice_count,
                expected=expected_target,
            )
        page += 1

    assert expected_target is not None
    raise _incomplete_results_error(
        reason="bounded pagination budget was exhausted",
        collected=source_notice_count,
        expected=expected_target,
    )


def normalize_notice(notice: Mapping[str, Any]) -> dict[str, Any]:
    """Convert one TED response row to the minimal public notice schema."""

    if not isinstance(notice, Mapping):
        raise TedApiError("TED response contains a notice that is not an object")

    publication_number = _nonempty_text(notice.get("publication-number"))
    if publication_number is None:
        raise TedApiError("TED notice is missing publication-number")

    lot_identifiers = _unique_strings(notice.get("identifier-lot"))
    if len(lot_identifiers) == 1:
        lot_id = lot_identifiers[0].upper()
        cpv_codes = _unique_strings(
            notice.get("main-classification-proc"),
            notice.get("main-classification-lot"),
            notice.get("additional-classification-proc"),
            notice.get("additional-classification-lot"),
        )
        countries = [
            value.upper()
            for value in _unique_strings(
                notice.get("place-of-performance-country-proc"),
                notice.get("place-of-performance-country-lot"),
            )
        ]
        metadata_warnings: list[str] = []
        deadline, deadline_at, deadline_warning = _single_lot_deadline(notice)
        if deadline_warning is not None:
            metadata_warnings.append(deadline_warning)
    elif len(lot_identifiers) > 1:
        lot_id = None
        cpv_codes = []
        countries = []
        deadline = None
        deadline_at = None
        metadata_warnings = [
            "TED returned multiple lots. Lot-level CPV, country, and deadline values were "
            "withheld because the notice-level Search API does not preserve their associations."
        ]
    else:
        lot_id = None
        cpv_codes = []
        countries = []
        deadline = None
        deadline_at = None
        metadata_warnings = [
            "TED did not return a lot identifier. Lot-level CPV, country, and deadline values "
            "were withheld because their scope cannot be verified."
        ]

    return {
        "publication_number": publication_number,
        "lot_id": lot_id,
        "notice_type": _nonempty_text(notice.get("form-type")),
        "title": _preferred_text(notice.get("notice-title")),
        "buyer": _preferred_text(notice.get("buyer-name")),
        "cpv_codes": cpv_codes,
        "countries": countries,
        "deadline": deadline,
        "deadline_at": deadline_at,
        "publication_date": _earliest_iso_date(notice.get("publication-date")),
        "source_url": _source_url(notice.get("links")),
        "metadata_warnings": metadata_warnings,
    }


def _single_lot_deadline(notice: Mapping[str, Any]) -> tuple[str | None, str | None, str | None]:
    date_values = _unique_strings(notice.get("deadline-receipt-tender-date-lot"))
    time_values = _unique_strings(notice.get("deadline-receipt-tender-time-lot"))
    if not date_values:
        return None, None, None
    if len(date_values) != 1 or len(time_values) > 1:
        return (
            None,
            None,
            "TED returned ambiguous deadline values for one lot; deadline evidence was withheld.",
        )
    if not time_values:
        deadline = _strict_eforms_date(date_values[0])
        if deadline is None:
            return None, None, "TED returned an invalid lot deadline; it was withheld."
        return deadline, None, None
    deadline_at = _combine_eforms_datetime(date_values[0], time_values[0])
    if deadline_at is None:
        return (
            None,
            None,
            "TED returned an invalid or timezone-ambiguous lot deadline; it was withheld.",
        )
    return None, deadline_at, None


def _expand_multi_lot_notice(
    notice: Mapping[str, Any],
    *,
    timeout: float,
    max_response_bytes: int,
    opener: Callable[..., Any],
) -> list[dict[str, Any]]:
    publication_number = _nonempty_text(notice.get("publication-number"))
    if publication_number is None or not _PUBLICATION_NUMBER_RE.fullmatch(publication_number):
        raise TedApiError("multi-lot TED notice has an unsupported publication-number")
    expected_lots = tuple(value.upper() for value in _unique_strings(notice.get("identifier-lot")))
    if any(not _LOT_IDENTIFIER_RE.fullmatch(value) for value in expected_lots):
        raise TedApiError("multi-lot TED notice has an invalid lot identifier")

    xml_url = f"https://ted.europa.eu/en/notice/{publication_number}/xml"
    payload = _fetch_xml(
        xml_url,
        timeout=timeout,
        max_response_bytes=max_response_bytes,
        opener=opener,
    )
    return _parse_eforms_lots(notice, payload, expected_lots)


def _fetch_xml(
    url: str,
    *,
    timeout: float,
    max_response_bytes: int,
    opener: Callable[..., Any],
) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "application/xml, text/xml",
            "User-Agent": f"TenderVerdict/{__version__} (open-source read-only TED client)",
        },
        method="GET",
    )
    try:
        with opener(request, timeout=timeout) as response:
            content_type = _content_type(response)
            if not _is_xml_content_type(content_type):
                raise TedApiError(
                    "TED returned a non-XML Content-Type for a multi-lot notice"
                    + (f": {content_type}" if content_type else "")
                )
            payload = response.read(max_response_bytes + 1)
    except HTTPError as exc:
        raise TedApiError(f"TED XML returned HTTP {exc.code}") from exc
    except TimeoutError as exc:
        raise TedApiError("TED XML request timed out") from exc
    except URLError as exc:
        reason = "request timed out" if _is_timeout_reason(exc.reason) else "request failed"
        raise TedApiError(f"TED XML {reason}") from exc
    except (HTTPException, OSError) as exc:
        raise TedApiError("TED XML request failed") from exc
    if not isinstance(payload, bytes):
        raise TedApiError("TED XML response body is not bytes")
    if len(payload) > max_response_bytes:
        raise TedApiError(f"TED XML response exceeds the {max_response_bytes}-byte safety limit")
    return payload


def _parse_eforms_lots(
    notice: Mapping[str, Any],
    payload: bytes,
    expected_lots: tuple[str, ...],
) -> list[dict[str, Any]]:
    # The response is already bounded, so scan all bytes before handing them to
    # ElementTree. A long XML declaration or comment must not be able to push a
    # prohibited declaration beyond a prefix-only check.
    upper_payload = payload.upper()
    if b"<!DOCTYPE" in upper_payload or b"<!ENTITY" in upper_payload:
        raise TedApiError("TED XML contains a prohibited document type or entity declaration")
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as exc:
        raise TedApiError("TED returned invalid eForms XML") from exc

    lot_elements = root.findall(".//cac:ProcurementProjectLot", _UBL_NAMESPACES)
    parsed_lots: list[tuple[str, Any]] = []
    seen_lots: set[str] = set()
    for lot in lot_elements:
        lot_id = _xml_text(lot.find("cbc:ID", _UBL_NAMESPACES))
        if lot_id is None:
            raise TedApiError("TED eForms XML contains a lot without an identifier")
        lot_id = lot_id.upper()
        if not _LOT_IDENTIFIER_RE.fullmatch(lot_id) or lot_id in seen_lots:
            raise TedApiError("TED eForms XML contains an invalid or duplicate lot identifier")
        seen_lots.add(lot_id)
        parsed_lots.append((lot_id, lot))
    if len(parsed_lots) != len(expected_lots) or seen_lots != set(expected_lots):
        raise TedApiError(
            "TED Search and eForms XML lot identifiers differ; no snapshot was created"
        )

    notice_title = _preferred_text(notice.get("notice-title"))
    buyer = _preferred_text(notice.get("buyer-name"))
    source_url = _source_url(notice.get("links"))
    publication_date = _earliest_iso_date(notice.get("publication-date"))
    rows: list[dict[str, Any]] = []
    for lot_id, lot in parsed_lots:
        project = lot.find("cac:ProcurementProject", _UBL_NAMESPACES)
        process = lot.find("cac:TenderingProcess", _UBL_NAMESPACES)
        lot_title = None
        cpv_codes: list[str] = []
        countries: list[str] = []
        if project is not None:
            lot_title = _xml_text(project.find("cbc:Name", _UBL_NAMESPACES))
            cpv_codes = _unique_xml_values(
                project.findall(".//cbc:ItemClassificationCode", _UBL_NAMESPACES),
                list_name="cpv",
            )
            countries = [
                value.upper()
                for value in _unique_xml_values(
                    project.findall(".//cac:Country/cbc:IdentificationCode", _UBL_NAMESPACES),
                    list_name="country",
                )
            ]
        deadline_at = None
        metadata_warnings: list[str] = []
        if process is not None:
            period = process.find("cac:TenderSubmissionDeadlinePeriod", _UBL_NAMESPACES)
            if period is not None:
                deadline_at = _combine_eforms_datetime(
                    _xml_text(period.find("cbc:EndDate", _UBL_NAMESPACES)),
                    _xml_text(period.find("cbc:EndTime", _UBL_NAMESPACES)),
                )
                if deadline_at is None:
                    metadata_warnings.append(
                        "TED eForms XML did not provide a valid timezone-aware submission deadline."
                    )
        title = _lot_title(notice_title, lot_title)
        rows.append(
            {
                "publication_number": _nonempty_text(notice.get("publication-number")),
                "lot_id": lot_id,
                "notice_type": _nonempty_text(notice.get("form-type")),
                "title": title,
                "buyer": buyer,
                "cpv_codes": cpv_codes,
                "countries": countries,
                "deadline": None,
                "deadline_at": deadline_at,
                "publication_date": publication_date,
                "source_url": source_url,
                "metadata_warnings": metadata_warnings,
            }
        )
    return rows


def _unique_xml_values(elements: list[Any], *, list_name: str) -> list[str]:
    output: list[str] = []
    for element in elements:
        if str(element.attrib.get("listName", "")).casefold() != list_name:
            continue
        value = _xml_text(element)
        if value is not None and value not in output:
            output.append(value)
    return output


def _xml_text(element: Any) -> str | None:
    if element is None or not isinstance(element.text, str):
        return None
    text = element.text.strip()
    return text or None


def _lot_title(notice_title: str | None, lot_title: str | None) -> str | None:
    if notice_title and lot_title and notice_title != lot_title:
        return f"{notice_title} — {lot_title}"
    return lot_title or notice_title


def _strict_eforms_date(value: str) -> str | None:
    match = _EFORMS_DATE_RE.fullmatch(value)
    if match is None:
        return None
    try:
        return date.fromisoformat(match.group(1)).isoformat()
    except ValueError:
        return None


def _combine_eforms_datetime(date_value: str | None, time_value: str | None) -> str | None:
    if date_value is None or time_value is None:
        return None
    date_match = _EFORMS_DATE_RE.fullmatch(date_value)
    time_match = _EFORMS_TIME_RE.fullmatch(time_value)
    if date_match is None or time_match is None:
        return None
    date_offset = date_match.group(2)
    time_offset = time_match.group(2)
    if date_offset and time_offset and date_offset != time_offset:
        return None
    offset = time_offset or date_offset
    if offset is None:
        return None
    candidate = f"{date_match.group(1)}T{time_match.group(1)}{offset}"
    try:
        parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.utcoffset() is None:
        return None
    return parsed.isoformat()


def build_ted_snapshot(
    query: str,
    notices: list[dict[str, Any]],
    *,
    retrieved_at: str | None = None,
) -> dict[str, object]:
    """Wrap a complete fetch in a validated, traceable snapshot document."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty TED expert query")
    clean_query = query.strip()
    if len(clean_query) > MAX_QUERY_CHARACTERS:
        raise ValueError(f"query must not exceed {MAX_QUERY_CHARACTERS} characters")
    if retrieved_at is None:
        retrieved_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    snapshot: dict[str, object] = {
        "schema_version": 1,
        "source": {
            "kind": "ted_search_api",
            "endpoint": TED_SEARCH_URL,
            "query": clean_query,
            "retrieved_at": retrieved_at,
            "lot_policy": TED_SNAPSHOT_LOT_POLICY,
        },
        "notices": notices,
    }
    # Reuse the public input validator before a snapshot can reach an output file.
    encoded = json.dumps(snapshot, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    notice_collection_from_json_bytes(encoded, "TED snapshot")
    return snapshot


def _validate_options(
    *,
    query: str,
    max_notices: int,
    page_size: int,
    timeout: float,
    max_response_bytes: int,
) -> str:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty TED expert query")
    clean_query = query.strip()
    if len(clean_query) > MAX_QUERY_CHARACTERS:
        raise ValueError(f"query must not exceed {MAX_QUERY_CHARACTERS} characters")
    if isinstance(max_notices, bool) or not isinstance(max_notices, int):
        raise ValueError("max_notices must be an integer")
    if not 1 <= max_notices <= MAX_NOTICES:
        raise ValueError(f"max_notices must be between 1 and {MAX_NOTICES}")
    if isinstance(page_size, bool) or not isinstance(page_size, int):
        raise ValueError("page_size must be an integer")
    if not 1 <= page_size <= MAX_PAGE_SIZE:
        raise ValueError(f"page_size must be between 1 and {MAX_PAGE_SIZE}")
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("timeout must be a finite positive number")
    if not math.isfinite(float(timeout)) or timeout <= 0 or timeout > 120:
        raise ValueError("timeout must be greater than 0 and at most 120 seconds")
    if isinstance(max_response_bytes, bool) or not isinstance(max_response_bytes, int):
        raise ValueError("max_response_bytes must be an integer")
    if not 1 <= max_response_bytes <= MAX_RESPONSE_BYTES:
        raise ValueError(f"max_response_bytes must be between 1 and {MAX_RESPONSE_BYTES}")
    return clean_query


def _search_page(
    query: str,
    *,
    page: int,
    limit: int,
    timeout: float,
    max_response_bytes: int,
    opener: Callable[..., Any],
) -> Mapping[str, Any]:
    payload = {
        "query": query,
        "fields": list(TED_FIELDS),
        "page": page,
        "limit": limit,
        "scope": "ALL",
        # The live v3 endpoint currently returns a null count for valid queries when
        # this flag is true. Response validation below still fails closed.
        "checkQuerySyntax": False,
        "paginationMode": "PAGE_NUMBER",
        "onlyLatestVersions": True,
    }
    request = Request(
        TED_SEARCH_URL,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"TenderVerdict/{__version__} (open-source read-only TED client)",
        },
        method="POST",
    )

    try:
        with opener(request, timeout=timeout) as response:
            content_type = _content_type(response)
            if not _is_json_content_type(content_type):
                raise TedApiError(
                    "TED returned a non-JSON Content-Type"
                    + (f": {content_type}" if content_type else "")
                )
            body = response.read(max_response_bytes + 1)
    except HTTPError as exc:
        raise TedApiError(f"TED returned HTTP {exc.code}") from exc
    except TimeoutError as exc:
        raise TedApiError("TED request timed out") from exc
    except URLError as exc:
        reason = "request timed out" if _is_timeout_reason(exc.reason) else "request failed"
        raise TedApiError(f"TED {reason}") from exc
    except (HTTPException, OSError) as exc:
        raise TedApiError("TED request failed") from exc

    if not isinstance(body, bytes):
        raise TedApiError("TED response body is not bytes")
    if len(body) > max_response_bytes:
        raise TedApiError(f"TED response exceeds the {max_response_bytes}-byte safety limit")

    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TedApiError("TED returned invalid JSON") from exc
    if not isinstance(parsed, Mapping):
        raise TedApiError("TED response must be a JSON object")
    return parsed


def _validate_page(result: Mapping[str, Any]) -> tuple[list[Mapping[str, Any]], int]:
    if not isinstance(result, Mapping):
        raise TedApiError("TED response must be a JSON object")

    timed_out = result.get("timedOut", False)
    if not isinstance(timed_out, bool):
        raise TedApiError("TED response timedOut must be a boolean")
    if timed_out:
        raise TedApiError("TED reported a timed-out search; results may be incomplete")

    notices = result.get("notices")
    if not isinstance(notices, list):
        raise TedApiError("TED response does not contain a notices list")
    if any(not isinstance(notice, Mapping) for notice in notices):
        raise TedApiError("TED response contains a notice that is not an object")

    total_count = result.get("totalNoticeCount")
    if isinstance(total_count, bool) or not isinstance(total_count, int) or total_count < 0:
        raise TedApiError("TED response totalNoticeCount must be a non-negative integer")
    if len(notices) > total_count:
        raise TedApiError("TED response contains more rows than totalNoticeCount")
    return notices, total_count


def _incomplete_results_error(*, reason: str, collected: int, expected: int) -> TedApiError:
    return TedApiError(
        f"TED returned incomplete results ({reason}): collected {collected} of {expected}"
    )


def _content_type(response: Any) -> str:
    headers = getattr(response, "headers", None)
    if headers is not None:
        getter = getattr(headers, "get", None)
        if callable(getter):
            value = getter("Content-Type", "")
            if isinstance(value, str):
                return value
    getter = getattr(response, "getheader", None)
    if callable(getter):
        value = getter("Content-Type", "")
        if isinstance(value, str):
            return value
    return ""


def _is_json_content_type(content_type: str) -> bool:
    media_type = content_type.split(";", 1)[0].strip().lower()
    return media_type == "application/json" or media_type.endswith("+json")


def _is_xml_content_type(content_type: str) -> bool:
    media_type = content_type.split(";", 1)[0].strip().lower()
    return media_type in {"application/xml", "text/xml"} or media_type.endswith("+xml")


def _is_timeout_reason(reason: Any) -> bool:
    if isinstance(reason, TimeoutError):
        return True
    return "timed out" in str(reason).lower()


def _values(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [item for item in value if item is not None]
    return [value]


def _nonempty_text(value: Any) -> str | None:
    if not isinstance(value, (str, int)) or isinstance(value, bool):
        return None
    text = str(value).strip()
    return text or None


def _unique_strings(*values: Any) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        for item in _values(value):
            text = _nonempty_text(item)
            if text is not None and text not in seen:
                seen.add(text)
                output.append(text)
    return output


def _preferred_text(value: Any) -> str | None:
    direct = _nonempty_text(value)
    if direct is not None:
        return direct
    if not isinstance(value, Mapping):
        values = _unique_strings(value)
        return values[0] if values else None
    for language in ("eng", "deu"):
        candidates = _unique_strings(value.get(language))
        if candidates:
            return candidates[0]
    for candidates in value.values():
        values = _unique_strings(candidates)
        if values:
            return values[0]
    return None


def _earliest_iso_date(value: Any) -> str | None:
    dates: list[date] = []
    for item in _values(value):
        text = _nonempty_text(item)
        if text is None:
            continue
        try:
            dates.append(date.fromisoformat(text[:10]))
        except ValueError:
            continue
    return min(dates).isoformat() if dates else None


def _source_url(value: Any) -> str | None:
    if not isinstance(value, Mapping):
        return None
    for group_name in ("html", "htmlDirect", "xml"):
        group = value.get(group_name)
        if not isinstance(group, Mapping):
            continue
        candidates: list[Any] = [group.get(language) for language in ("ENG", "DEU", "MUL")]
        candidates.extend(group.values())
        for candidate in candidates:
            text = _nonempty_text(candidate)
            if text is None:
                continue
            parsed = urlsplit(text)
            if parsed.scheme == "https" and parsed.netloc:
                return text
    return None
