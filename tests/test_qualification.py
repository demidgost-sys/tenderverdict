from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import date

from tenderverdict.models import Notice, Profile, Verdict
from tenderverdict.qualification import (
    is_verifiable_source_url,
    qualify_notice,
    qualify_notices,
)

AS_OF = date(2026, 8, 2)
PROFILE = Profile(
    schema_version=1,
    name="Example Software GmbH",
    cpv_codes=("72260000",),
    countries=("AUT", "DEU"),
    minimum_days_to_deadline=14,
)
OPEN_NOTICE = Notice(
    publication_number="SYN-OPEN-001",
    notice_type="competition",
    title="Application maintenance services",
    buyer="Example City Procurement Office",
    cpv_codes=("72260000",),
    countries=("AUT",),
    deadline=date(2026, 9, 15),
    source_url="https://procurement.example/notices/SYN-OPEN-001",
)


class QualificationTests(unittest.TestCase):
    def test_open_documents_requires_all_positive_metadata(self) -> None:
        result = qualify_notice(PROFILE, OPEN_NOTICE, AS_OF)

        self.assertEqual(result.verdict, Verdict.OPEN_DOCUMENTS)
        self.assertEqual(result.unknowns, ())
        self.assertIn("Exact CPV match: 72260000.", result.reasons)
        self.assertIn("Country match: AUT.", result.reasons)
        self.assertEqual(
            result.human_next_step,
            "Open and review the official procurement documents; "
            "a human decides whether to proceed.",
        )

    def test_four_digit_cpv_class_match_is_watch(self) -> None:
        result = qualify_notice(
            PROFILE,
            replace(OPEN_NOTICE, cpv_codes=("72261000",)),
            AS_OF,
        )

        self.assertEqual(result.verdict, Verdict.WATCH)
        self.assertIn(
            "Four-digit CPV class match only: profile 72260000, notice 72261000.",
            result.reasons,
        )
        self.assertEqual(
            result.human_next_step,
            "Verify the flagged metadata before opening the procurement documents.",
        )

    def test_missing_important_evidence_is_watch(self) -> None:
        variants = {
            "notice_type": replace(OPEN_NOTICE, notice_type=None),
            "title": replace(OPEN_NOTICE, title=None),
            "buyer": replace(OPEN_NOTICE, buyer=None),
            "cpv_codes": replace(OPEN_NOTICE, cpv_codes=()),
            "countries": replace(OPEN_NOTICE, countries=()),
            "deadline": replace(OPEN_NOTICE, deadline=None),
            "source_url": replace(OPEN_NOTICE, source_url=None),
            "unsafe_source": replace(OPEN_NOTICE, source_url="javascript:alert(1)"),
        }

        for label, notice in variants.items():
            with self.subTest(label=label):
                result = qualify_notice(PROFILE, notice, AS_OF)
                self.assertEqual(result.verdict, Verdict.WATCH)
                self.assertTrue(result.unknowns)

    def test_every_hard_stop_rejects(self) -> None:
        variants = {
            "not_competition": replace(OPEN_NOTICE, notice_type="award notice"),
            "closed": replace(OPEN_NOTICE, deadline=AS_OF),
            "too_close": replace(OPEN_NOTICE, deadline=date(2026, 8, 15)),
            "cpv_mismatch": replace(OPEN_NOTICE, cpv_codes=("48000000",)),
            "country_mismatch": replace(OPEN_NOTICE, countries=("FRA",)),
        }

        for label, notice in variants.items():
            with self.subTest(label=label):
                result = qualify_notice(PROFILE, notice, AS_OF)
                self.assertEqual(result.verdict, Verdict.REJECT)
                self.assertEqual(
                    result.human_next_step,
                    "Stop review unless the notice metadata is corrected.",
                )

    def test_hard_stop_takes_precedence_over_unknowns(self) -> None:
        notice = replace(
            OPEN_NOTICE,
            buyer=None,
            cpv_codes=("48000000",),
            source_url=None,
        )

        result = qualify_notice(PROFILE, notice, AS_OF)

        self.assertEqual(result.verdict, Verdict.REJECT)
        self.assertTrue(result.unknowns)

    def test_minimum_deadline_is_inclusive(self) -> None:
        notice = replace(OPEN_NOTICE, deadline=date(2026, 8, 16))

        result = qualify_notice(PROFILE, notice, AS_OF)

        self.assertEqual(result.verdict, Verdict.OPEN_DOCUMENTS)
        self.assertIn(
            "Submission deadline leaves 14 days, meeting the 14-day minimum.",
            result.reasons,
        )

    def test_input_order_is_preserved(self) -> None:
        notices = (
            replace(OPEN_NOTICE, publication_number="SYN-003"),
            replace(OPEN_NOTICE, publication_number="SYN-001"),
            replace(OPEN_NOTICE, publication_number="SYN-002"),
        )

        results = qualify_notices(PROFILE, notices, AS_OF)

        self.assertEqual(
            tuple(result.notice.publication_number for result in results),
            ("SYN-003", "SYN-001", "SYN-002"),
        )

    def test_output_contains_no_score(self) -> None:
        output = qualify_notice(PROFILE, OPEN_NOTICE, AS_OF).to_dict()

        self.assertNotIn("confidence", output)
        self.assertNotIn("score", output)

    def test_as_of_requires_date(self) -> None:
        with self.assertRaises(TypeError):
            qualify_notice(PROFILE, OPEN_NOTICE, "2026-08-02")  # type: ignore[arg-type]


class SourceUrlTests(unittest.TestCase):
    def test_https_absolute_url_is_accepted(self) -> None:
        self.assertTrue(is_verifiable_source_url("https://procurement.example/notices/SYN-001"))

    def test_unsafe_or_ambiguous_url_is_rejected(self) -> None:
        values = (
            "http://procurement.example/notices/SYN-001",
            "javascript:alert(1)",
            "https://user:password@procurement.example/notices/SYN-001",
            "https://procurement.example/notices/SYN-001#fragment",
            "https://procurement.example/a b",
            "https://procurement.example:bad/notices/SYN-001",
            "",
        )
        for value in values:
            with self.subTest(value=value):
                self.assertFalse(is_verifiable_source_url(value))


if __name__ == "__main__":
    unittest.main()
