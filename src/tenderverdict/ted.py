"""Small, read-only adapter for the public TED Search API.

The adapter intentionally has no persistence or retry policy.  Callers receive a
complete, normalized list or an exception, which lets the CLI publish output
atomically after the request has succeeded.
"""

from __future__ import annotations

import json
import math
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
DEFAULT_MAX_RESPONSE_BYTES = 2_000_000
MAX_RESPONSE_BYTES = 10_000_000
MAX_NOTICES = 1_000
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
    "identifier-lot",
)


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
    seen: set[str] = set()
    page = 1
    stalled_pages = 0
    expected_total: int | None = None
    expected_target: int | None = None
    # Pagination is bounded even if the remote dataset changes between pages.
    page_budget = math.ceil(max_notices / page_size) + MAX_STALLED_PAGES

    while len(output) < max_notices and page <= page_budget:
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

        count_before_page = len(output)
        for raw_notice in raw_notices:
            normalized = normalize_notice(raw_notice)
            identity = normalized["publication_number"]
            if identity not in seen:
                seen.add(identity)
                output.append(normalized)
            if len(output) >= max_notices:
                break

        if len(output) == count_before_page:
            stalled_pages += 1
        else:
            stalled_pages = 0

        assert expected_target is not None
        if len(output) >= expected_target:
            return output
        if stalled_pages >= MAX_STALLED_PAGES:
            raise _incomplete_results_error(
                reason="pagination repeated rows without progress",
                collected=len(output),
                expected=expected_target,
            )
        if len(raw_notices) < page_size:
            raise _incomplete_results_error(
                reason="TED returned a premature short page",
                collected=len(output),
                expected=expected_target,
            )
        if page * page_size >= total_count:
            raise _incomplete_results_error(
                reason="reported page range ended before all unique rows were collected",
                collected=len(output),
                expected=expected_target,
            )
        page += 1

    assert expected_target is not None
    raise _incomplete_results_error(
        reason="bounded pagination budget was exhausted",
        collected=len(output),
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
        deadline = _earliest_iso_date(notice.get("deadline-receipt-tender-date-lot"))
        metadata_warnings: list[str] = []
    elif len(lot_identifiers) > 1:
        cpv_codes = []
        countries = []
        deadline = None
        metadata_warnings = [
            "TED returned multiple lots. Lot-level CPV, country, and deadline values were "
            "withheld because the notice-level Search API does not preserve their associations."
        ]
    else:
        cpv_codes = []
        countries = []
        deadline = None
        metadata_warnings = [
            "TED did not return a lot identifier. Lot-level CPV, country, and deadline values "
            "were withheld because their scope cannot be verified."
        ]

    return {
        "publication_number": publication_number,
        "notice_type": _nonempty_text(notice.get("form-type")),
        "title": _preferred_text(notice.get("notice-title")),
        "buyer": _preferred_text(notice.get("buyer-name")),
        "cpv_codes": cpv_codes,
        "countries": countries,
        "deadline": deadline,
        "publication_date": _earliest_iso_date(notice.get("publication-date")),
        "source_url": _source_url(notice.get("links")),
        "metadata_warnings": metadata_warnings,
    }


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
