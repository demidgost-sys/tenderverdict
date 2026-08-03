from __future__ import annotations

import io
import json
import unittest
from http.client import IncompleteRead
from urllib.error import URLError

from tenderverdict.models import notice_collection_from_json_bytes
from tenderverdict.ted import (
    TED_SEARCH_URL,
    TedApiError,
    build_ted_snapshot,
    fetch_notices,
    normalize_notice,
)


def raw_notice(number: str, *, title: str = "Synthetic service notice") -> dict:
    return {
        "publication-number": number,
        "form-type": "competition",
        "notice-title": {"eng": [title]},
        "buyer-name": {"eng": ["Synthetic Buyer"]},
        "publication-date": "2030-08-01+02:00",
        "identifier-lot": ["LOT-0001"],
        "main-classification-proc": ["72260000"],
        "additional-classification-lot": ["72262000", "72260000"],
        "place-of-performance-country-proc": ["aut"],
        "deadline-receipt-tender-date-lot": ["2030-09-20", "2030-09-18"],
        "links": {"html": {"ENG": f"https://notices.example/{number}"}},
    }


class FakeResponse:
    def __init__(
        self,
        payload: object | None = None,
        *,
        body: bytes | None = None,
        content_type: str = "application/json; charset=utf-8",
    ) -> None:
        if body is None:
            body = json.dumps(payload).encode("utf-8")
        self._body = io.BytesIO(body)
        self.headers = {"Content-Type": content_type}

    def read(self, size: int = -1) -> bytes:
        return self._body.read(size)

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None


class TedAdapterTests(unittest.TestCase):
    def test_fetch_builds_bounded_request_and_normalizes_notice(self) -> None:
        captured: dict = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["method"] = request.method
            captured["timeout"] = timeout
            captured["body"] = json.loads(request.data)
            return FakeResponse(
                {
                    "notices": [raw_notice("SYN-001")],
                    "totalNoticeCount": 1,
                    "timedOut": False,
                }
            )

        notices = fetch_notices(
            "form-type = competition",
            max_notices=1,
            page_size=25,
            timeout=4.0,
            opener=opener,
        )

        self.assertEqual(captured["url"], TED_SEARCH_URL)
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["timeout"], 4.0)
        self.assertEqual(captured["body"]["limit"], 25)
        self.assertEqual(captured["body"]["page"], 1)
        self.assertEqual(captured["body"]["paginationMode"], "PAGE_NUMBER")
        self.assertTrue(captured["body"]["onlyLatestVersions"])
        self.assertFalse(captured["body"]["checkQuerySyntax"])
        self.assertIn("identifier-lot", captured["body"]["fields"])
        self.assertIn("publication-date", captured["body"]["fields"])
        self.assertEqual(
            notices,
            [
                {
                    "publication_number": "SYN-001",
                    "notice_type": "competition",
                    "title": "Synthetic service notice",
                    "buyer": "Synthetic Buyer",
                    "cpv_codes": ["72260000", "72262000"],
                    "countries": ["AUT"],
                    "deadline": "2030-09-18",
                    "publication_date": "2030-08-01",
                    "source_url": "https://notices.example/SYN-001",
                    "metadata_warnings": [],
                }
            ],
        )

    def test_pagination_keeps_page_size_constant_and_deduplicates(self) -> None:
        calls: list[dict] = []

        def searcher(query, **kwargs):
            calls.append({"query": query, **kwargs})
            page = kwargs["page"]
            rows = {
                1: [raw_notice("SYN-001"), raw_notice("SYN-002")],
                2: [raw_notice("SYN-002"), raw_notice("SYN-003")],
            }[page]
            return {
                "notices": rows,
                "totalNoticeCount": 4,
                "timedOut": False,
            }

        notices = fetch_notices(
            "form-type = competition",
            max_notices=3,
            page_size=2,
            searcher=searcher,
        )

        self.assertEqual(
            [notice["publication_number"] for notice in notices],
            ["SYN-001", "SYN-002", "SYN-003"],
        )
        self.assertEqual([call["limit"] for call in calls], [2, 2])
        self.assertEqual([call["page"] for call in calls], [1, 2])

    def test_three_stalled_full_pages_fail_closed(self) -> None:
        calls: list[int] = []

        def searcher(_query, **kwargs):
            calls.append(kwargs["page"])
            return {
                "notices": [raw_notice("SYN-SAME")],
                "totalNoticeCount": 100,
                "timedOut": False,
            }

        with self.assertRaisesRegex(TedApiError, "incomplete results"):
            fetch_notices(
                "form-type = competition",
                max_notices=10,
                page_size=1,
                searcher=searcher,
            )

        self.assertEqual(calls, [1, 2, 3, 4])

    def test_empty_page_with_positive_total_fails_closed(self) -> None:
        page = {"notices": [], "totalNoticeCount": 10, "timedOut": False}
        with self.assertRaisesRegex(TedApiError, "premature short page"):
            fetch_notices(
                "x",
                max_notices=10,
                page_size=5,
                searcher=lambda *_args, **_kwargs: page,
            )

    def test_successful_zero_match_query_is_an_explicit_empty_result(self) -> None:
        page = {"notices": [], "totalNoticeCount": 0, "timedOut": False}

        notices = fetch_notices(
            "x",
            max_notices=5,
            page_size=5,
            searcher=lambda *_args, **_kwargs: page,
        )

        self.assertEqual(notices, [])

    def test_short_page_before_reported_total_fails_closed(self) -> None:
        page = {
            "notices": [raw_notice("SYN-ONLY")],
            "totalNoticeCount": 5,
            "timedOut": False,
        }
        with self.assertRaisesRegex(TedApiError, "premature short page"):
            fetch_notices(
                "x",
                max_notices=5,
                page_size=2,
                searcher=lambda *_args, **_kwargs: page,
            )

    def test_changed_total_count_fails_closed(self) -> None:
        def searcher(_query, **kwargs):
            page = kwargs["page"]
            return {
                "notices": [
                    raw_notice(f"SYN-{page}-A"),
                    raw_notice(f"SYN-{page}-B"),
                ],
                "totalNoticeCount": 6 if page == 1 else 7,
                "timedOut": False,
            }

        with self.assertRaisesRegex(TedApiError, "totalNoticeCount changed"):
            fetch_notices("x", max_notices=5, page_size=2, searcher=searcher)

    def test_bounded_page_budget_fails_closed(self) -> None:
        calls: list[int] = []

        def searcher(_query, **kwargs):
            page = kwargs["page"]
            calls.append(page)
            return {
                "notices": [
                    raw_notice("SYN-SHARED"),
                    raw_notice(f"SYN-{page}"),
                ],
                "totalNoticeCount": 100,
                "timedOut": False,
            }

        with self.assertRaisesRegex(TedApiError, "budget was exhausted"):
            fetch_notices("x", max_notices=10, page_size=2, searcher=searcher)
        self.assertEqual(calls, list(range(1, 9)))

    def test_rejects_empty_query_and_out_of_bounds_options(self) -> None:
        invalid = (
            {"query": "", "max_notices": 1},
            {"query": "x", "max_notices": 0},
            {"query": "x", "max_notices": 1001},
            {"query": "x", "max_notices": 1, "page_size": 0},
            {"query": "x", "max_notices": 1, "page_size": 251},
            {"query": "x", "max_notices": 1, "timeout": 0},
            {"query": "x", "max_notices": 1, "max_response_bytes": 0},
        )
        for options in invalid:
            with self.subTest(options=options), self.assertRaises(ValueError):
                fetch_notices(**options, searcher=lambda *_args, **_kwargs: {})

    def test_timeout_and_url_errors_are_wrapped(self) -> None:
        failures = (TimeoutError("synthetic timeout"), URLError("offline"))
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):

                def opener(_request, timeout, failure=failure):
                    del timeout
                    raise failure

                with self.assertRaises(TedApiError):
                    fetch_notices("x", max_notices=1, opener=opener)

    def test_truncated_http_response_is_wrapped(self) -> None:
        class TruncatedResponse(FakeResponse):
            def read(self, size: int = -1) -> bytes:
                del size
                raise IncompleteRead(b"{", 10)

        def opener(_request, timeout):
            del timeout
            return TruncatedResponse({})

        with self.assertRaisesRegex(TedApiError, "request failed"):
            fetch_notices("x", max_notices=1, opener=opener)

    def test_rejects_non_json_content_type(self) -> None:
        def opener(_request, timeout):
            del timeout
            return FakeResponse(body=b"{}", content_type="text/html")

        with self.assertRaisesRegex(TedApiError, "non-JSON"):
            fetch_notices("x", max_notices=1, opener=opener)

    def test_rejects_oversized_response(self) -> None:
        def opener(_request, timeout):
            del timeout
            return FakeResponse(body=b"x" * 65)

        with self.assertRaisesRegex(TedApiError, "exceeds"):
            fetch_notices(
                "x",
                max_notices=1,
                max_response_bytes=64,
                opener=opener,
            )

    def test_rejects_invalid_json(self) -> None:
        def opener(_request, timeout):
            del timeout
            return FakeResponse(body=b"{not-json")

        with self.assertRaisesRegex(TedApiError, "invalid JSON"):
            fetch_notices("x", max_notices=1, opener=opener)

    def test_rejects_invalid_response_schemas(self) -> None:
        invalid_pages = (
            [],
            {},
            {"notices": "not-a-list"},
            {"notices": ["not-an-object"]},
            {"notices": [], "timedOut": "false"},
            {"notices": [], "timedOut": True},
            {"notices": [], "totalNoticeCount": -1},
        )
        for page in invalid_pages:
            with self.subTest(page=page), self.assertRaises(TedApiError):
                fetch_notices(
                    "x",
                    max_notices=1,
                    searcher=lambda *_args, page=page, **_kwargs: page,
                )

    def test_missing_publication_number_is_schema_error(self) -> None:
        page = {"notices": [{}], "totalNoticeCount": 1, "timedOut": False}
        with self.assertRaisesRegex(TedApiError, "publication-number"):
            fetch_notices(
                "x",
                max_notices=1,
                searcher=lambda *_args, **_kwargs: page,
            )

    def test_normalizer_keeps_unknowns_and_drops_unsafe_source_scheme(self) -> None:
        notice = normalize_notice(
            {
                "publication-number": "SYN-UNKNOWN",
                "links": {"html": {"ENG": "javascript:alert(1)"}},
                "deadline-receipt-tender-date-lot": ["not-a-date"],
            }
        )

        self.assertEqual(
            notice,
            {
                "publication_number": "SYN-UNKNOWN",
                "notice_type": None,
                "title": None,
                "buyer": None,
                "cpv_codes": [],
                "countries": [],
                "deadline": None,
                "publication_date": None,
                "source_url": None,
                "metadata_warnings": [
                    "TED did not return a lot identifier. Lot-level CPV, country, and deadline "
                    "values were withheld because their scope cannot be verified."
                ],
            },
        )

    def test_multi_lot_values_are_withheld_instead_of_flattened(self) -> None:
        notice = normalize_notice(
            {
                **raw_notice("SYN-MULTI"),
                "identifier-lot": ["LOT-0001", "LOT-0002"],
                "main-classification-lot": ["72260000", "48000000"],
                "place-of-performance-country-lot": ["AUT", "FRA"],
                "deadline-receipt-tender-date-lot": ["2030-09-01", "2030-10-01"],
            }
        )

        self.assertEqual(notice["cpv_codes"], [])
        self.assertEqual(notice["countries"], [])
        self.assertIsNone(notice["deadline"])
        self.assertIn("multiple lots", notice["metadata_warnings"][0])

    def test_snapshot_round_trips_with_query_retrieval_and_lot_policy(self) -> None:
        normalized = normalize_notice(raw_notice("SYN-SNAPSHOT"))
        snapshot = build_ted_snapshot(
            "form-type = competition SORT BY publication-date DESC",
            [normalized],
            retrieved_at="2030-08-02T12:30:00Z",
        )
        encoded = json.dumps(snapshot).encode("utf-8")

        collection = notice_collection_from_json_bytes(encoded, "snapshot.json")

        self.assertEqual(collection.source_kind, "ted_search_api")
        self.assertEqual(collection.retrieved_at, "2030-08-02T12:30:00Z")
        self.assertEqual(collection.lot_policy, "single_lot_only")
        self.assertEqual(collection.notices[0].publication_number, "SYN-SNAPSHOT")


if __name__ == "__main__":
    unittest.main()
