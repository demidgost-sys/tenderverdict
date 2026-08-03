from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from tenderverdict.models import (
    SchemaValidationError,
    load_notices,
    load_profile,
    notice_from_dict,
    notices_from_csv_bytes,
    notices_from_data,
    notices_from_file_bytes,
    parse_iso_date,
    profile_from_dict,
    render_notices_csv,
)

VALID_PROFILE = {
    "schema_version": 1,
    "name": "Example Software GmbH",
    "cpv_codes": ["72260000"],
    "countries": ["AUT", "DEU"],
    "minimum_days_to_deadline": 14,
}


class ProfileValidationTests(unittest.TestCase):
    def test_profile_v1_is_normalized(self) -> None:
        data = {**VALID_PROFILE, "countries": ["aut", "AUT", "deu"]}

        profile = profile_from_dict(data)

        self.assertEqual(profile.schema_version, 1)
        self.assertEqual(profile.countries, ("AUT", "DEU"))
        self.assertEqual(profile.to_dict(), VALID_PROFILE)

    def test_profile_rejects_bad_schema_and_types(self) -> None:
        invalid_variants = (
            {**VALID_PROFILE, "schema_version": 2},
            {**VALID_PROFILE, "minimum_days_to_deadline": True},
            {**VALID_PROFILE, "minimum_days_to_deadline": -1},
            {**VALID_PROFILE, "cpv_codes": []},
            {**VALID_PROFILE, "countries": ["AT"]},
            {**VALID_PROFILE, "unexpected": "field"},
        )

        for value in invalid_variants:
            with self.subTest(value=value), self.assertRaises(SchemaValidationError):
                profile_from_dict(value)


class NoticeValidationTests(unittest.TestCase):
    def test_missing_optional_evidence_is_valid(self) -> None:
        notice = notice_from_dict({"publication_number": "SYN-EMPTY-001"})

        self.assertIsNone(notice.notice_type)
        self.assertIsNone(notice.title)
        self.assertIsNone(notice.buyer)
        self.assertEqual(notice.cpv_codes, ())
        self.assertEqual(notice.countries, ())
        self.assertIsNone(notice.deadline)
        self.assertIsNone(notice.source_url)

    def test_notice_normalizes_and_serializes(self) -> None:
        notice = notice_from_dict(
            {
                "publication_number": " SYN-001 ",
                "notice_type": " competition ",
                "title": " Example notice ",
                "buyer": " Example buyer ",
                "cpv_codes": ["72260000", "72260000"],
                "countries": ["aut", "AUT"],
                "deadline": "2026-09-15",
                "source_url": " https://procurement.example/notices/SYN-001 ",
            }
        )

        self.assertEqual(notice.publication_number, "SYN-001")
        self.assertEqual(notice.cpv_codes, ("72260000",))
        self.assertEqual(notice.countries, ("AUT",))
        self.assertEqual(notice.deadline, date(2026, 9, 15))
        self.assertEqual(notice.to_dict()["deadline"], "2026-09-15")

    def test_notice_rejects_invalid_shape(self) -> None:
        invalid_variants = (
            {},
            {"publication_number": 3},
            {"publication_number": "SYN-001", "title": 3},
            {"publication_number": "SYN-001", "cpv_codes": "72260000"},
            {"publication_number": "SYN-001", "cpv_codes": ["7226"]},
            {"publication_number": "SYN-001", "countries": [3]},
            {"publication_number": "SYN-001", "deadline": "2026-02-30"},
            {"publication_number": "SYN-001", "extra": True},
        )

        for value in invalid_variants:
            with self.subTest(value=value), self.assertRaises(SchemaValidationError):
                notice_from_dict(value)

    def test_notice_array_must_be_an_array(self) -> None:
        with self.assertRaisesRegex(SchemaValidationError, "JSON array"):
            notices_from_data({"publication_number": "SYN-001"})


class CsvNoticeTests(unittest.TestCase):
    HEADER = "publication_number,notice_type,title,buyer,cpv_codes,countries,deadline,source_url\n"
    ROW = (
        "SYN-CSV-001,competition,Synthetic service,Example Buyer,"
        "72260000|72261000,AUT|DEU,2026-09-15,"
        "https://procurement.example/notices/SYN-CSV-001\n"
    )

    def test_csv_accepts_utf8_bom_and_normalizes_lists(self) -> None:
        notices = notices_from_csv_bytes(("\ufeff" + self.HEADER + self.ROW).encode())

        self.assertEqual(len(notices), 1)
        self.assertEqual(notices[0].publication_number, "SYN-CSV-001")
        self.assertEqual(notices[0].cpv_codes, ("72260000", "72261000"))
        self.assertEqual(notices[0].countries, ("AUT", "DEU"))

    def test_csv_accepts_common_spreadsheet_delimiters(self) -> None:
        for delimiter in (";", "\t"):
            with self.subTest(delimiter=repr(delimiter)):
                payload = (self.HEADER + self.ROW).replace(",", delimiter).encode()
                notices = notices_from_csv_bytes(payload)
                self.assertEqual(notices[0].publication_number, "SYN-CSV-001")

    def test_csv_errors_name_the_row_and_fix(self) -> None:
        bad_date = self.ROW.replace("2026-09-15", "2026-99-15")
        with self.assertRaisesRegex(SchemaValidationError, r"CSV row 2: deadline"):
            notices_from_csv_bytes((self.HEADER + bad_date).encode())

        short_row = "SYN-CSV-001,competition\n"
        with self.assertRaisesRegex(SchemaValidationError, r"row 2 has 2 columns; use exactly 8"):
            notices_from_csv_bytes((self.HEADER + short_row).encode())

    def test_csv_header_is_strict_and_actionable(self) -> None:
        missing = self.HEADER.replace("deadline,", "")
        with self.assertRaisesRegex(SchemaValidationError, r"add columns: deadline"):
            notices_from_csv_bytes((missing + self.ROW).encode())

        duplicate = self.HEADER.replace("source_url", "publication_number")
        with self.assertRaisesRegex(SchemaValidationError, r"duplicate CSV columns"):
            notices_from_csv_bytes((duplicate + self.ROW).encode())

    def test_csv_requires_data_and_explicit_file_type(self) -> None:
        with self.assertRaisesRegex(SchemaValidationError, "at least one notice row"):
            notices_from_csv_bytes(self.HEADER.encode())
        with self.assertRaisesRegex(SchemaValidationError, r"ending in \.csv or \.json"):
            notices_from_file_bytes((self.HEADER + self.ROW).encode(), "notices.txt")

    def test_csv_renderer_round_trips_through_file_loader(self) -> None:
        notices = notices_from_csv_bytes((self.HEADER + self.ROW).encode())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notices.csv"
            path.write_text(render_notices_csv(notices), encoding="utf-8")
            self.assertEqual(load_notices(path), notices)


class JsonAndDateTests(unittest.TestCase):
    def test_parse_iso_date_is_strict(self) -> None:
        self.assertEqual(parse_iso_date("2026-08-02"), date(2026, 8, 2))
        for value in ("20260802", "2026-8-2", "2026-02-30"):
            with self.subTest(value=value), self.assertRaises(SchemaValidationError):
                parse_iso_date(value)

    def test_duplicate_json_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(
                '{"schema_version":1,"schema_version":1,"name":"Example",'
                '"cpv_codes":["72260000"],"countries":["AUT"],'
                '"minimum_days_to_deadline":14}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SchemaValidationError, "duplicate JSON key"):
                load_profile(path)

    def test_malformed_json_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text("{", encoding="utf-8")

            with self.assertRaisesRegex(SchemaValidationError, "valid UTF-8 JSON"):
                load_profile(path)


if __name__ == "__main__":
    unittest.main()
