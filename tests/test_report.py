from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import date

from tenderverdict.models import Notice, Profile, Verdict
from tenderverdict.qualification import qualify_notices
from tenderverdict.report import ReportProvenance, render_html, render_markdown, report_as_dict

AS_OF = date(2026, 8, 2)
PROFILE = Profile(1, "Example Software GmbH", ("72260000",), ("AUT",), 14)
NOTICES = (
    Notice(
        "SYN-OPEN-001",
        "competition",
        "Application maintenance services",
        "Example City Procurement Office",
        ("72260000",),
        ("AUT",),
        date(2026, 9, 15),
        "https://procurement.example/notices/SYN-OPEN-001",
    ),
    Notice(
        "SYN-WATCH-001",
        "competition",
        "Software support services",
        "Example Regional Authority",
        ("72261000",),
        ("AUT",),
        date(2026, 9, 20),
        "https://procurement.example/notices/SYN-WATCH-001",
    ),
    Notice(
        "SYN-REJECT-001",
        "competition",
        "Software implementation services",
        "Example Federal Agency",
        ("72260000",),
        ("AUT",),
        date(2026, 8, 5),
        "https://procurement.example/notices/SYN-REJECT-001",
    ),
)
PROVENANCE = ReportProvenance(
    generator_version="0.2.0a1",
    source_kind="synthetic_test",
    profile_sha256="a" * 64,
    notices_sha256="b" * 64,
)


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.results = qualify_notices(PROFILE, NOTICES, AS_OF)

    def test_structured_report_has_three_outcomes(self) -> None:
        report = report_as_dict(PROFILE, self.results, AS_OF, PROVENANCE)

        self.assertEqual(
            report["summary"],
            {"total": 3, "open_documents": 1, "watch": 1, "reject": 1},
        )
        verdicts = [item["verdict"] for item in report["results"]]  # type: ignore[index]
        self.assertEqual(verdicts, ["open_documents", "watch", "reject"])
        self.assertEqual(report["schema_version"], 3)
        self.assertEqual(report["provenance"]["profile_sha256"], "a" * 64)  # type: ignore[index]

    def test_markdown_is_deterministic_and_complete(self) -> None:
        first = render_markdown(PROFILE, self.results, AS_OF, PROVENANCE)
        second = render_markdown(PROFILE, self.results, AS_OF, PROVENANCE)

        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))
        self.assertIn("# TenderVerdict qualification report", first)
        self.assertIn("**open_documents:** 1", first)
        self.assertIn("**watch:** 1", first)
        self.assertIn("**reject:** 1", first)
        self.assertIn("## Provenance", first)
        self.assertNotIn("confidence", first.casefold())

    def test_html_is_static_semantic_and_mobile_safe(self) -> None:
        output = render_html(PROFILE, self.results, AS_OF, PROVENANCE)

        self.assertEqual(output.count("<h1>"), 1)
        self.assertEqual(output.count("<main>"), 1)
        self.assertIn('<meta name="viewport"', output)
        self.assertIn("overflow-wrap: anywhere", output)
        self.assertIn("@media (max-width: 32rem)", output)
        self.assertIn("prefers-color-scheme: dark", output)
        self.assertIn("@media print", output)
        self.assertIn("Review outcomes", output)
        self.assertIn("Open documents", output)
        self.assertNotIn(" — ", output)
        self.assertNotIn("<script", output.casefold())
        self.assertNotIn("<form", output.casefold())
        self.assertNotIn("<input", output.casefold())
        self.assertNotIn("src=", output.casefold())
        self.assertIn("Report provenance", output)
        self.assertIn(
            '<a class="source-link" href="https://procurement.example/notices/SYN-OPEN-001" ',
            output,
        )
        self.assertIn('rel="noopener noreferrer"', output)

    def test_user_content_is_escaped_in_both_formats(self) -> None:
        malicious_notice = replace(
            NOTICES[0],
            publication_number="SYN-<bad>",
            notice_type='<img src=x onerror="alert(1)">',
            title="<script>alert(1)</script>\n# injected",
            buyer="[click](javascript:alert(1))",
            source_url="javascript:alert(1)",
        )
        malicious_profile = replace(PROFILE, name="<svg onload=alert(1)>")
        result = qualify_notices(malicious_profile, (malicious_notice,), AS_OF)

        malicious_provenance = replace(PROVENANCE, source_kind="<img src=x>")
        markdown = render_markdown(malicious_profile, result, AS_OF, malicious_provenance)
        html = render_html(malicious_profile, result, AS_OF, malicious_provenance)

        self.assertNotIn("<script>", markdown.casefold())
        self.assertNotIn("<svg", markdown.casefold())
        self.assertIn("&lt;script&gt;", markdown)
        self.assertNotIn("<script", html.casefold())
        self.assertNotIn("<svg", html.casefold())
        self.assertNotIn("<img", html.casefold())
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", html)
        self.assertNotIn('href="javascript:', html.casefold())
        self.assertEqual(result[0].verdict, Verdict.REJECT)

    def test_terminal_and_bidi_controls_are_rendered_visibly(self) -> None:
        controlled_notice = replace(
            NOTICES[0],
            title="safe\x1b]8;;https://evil.example\x07label\x1b]8;;\x07\u202ereversed",
            buyer="Example\x00Buyer",
        )
        controlled_profile = replace(PROFILE, name="Example\u2066 Organization")
        result = qualify_notices(controlled_profile, (controlled_notice,), AS_OF)

        markdown = render_markdown(controlled_profile, result, AS_OF, PROVENANCE)
        html = render_html(controlled_profile, result, AS_OF, PROVENANCE)

        for output in (markdown, html):
            self.assertNotIn("\x00", output)
            self.assertNotIn("\x07", output)
            self.assertNotIn("\x1b", output)
            self.assertNotIn("\u202e", output)
            self.assertNotIn("\u2066", output)
        self.assertIn(r"\\u001b", markdown)
        self.assertIn(r"\\u0007", markdown)
        self.assertIn(r"\\u202e", markdown)
        self.assertIn(r"\\u2066", markdown)
        self.assertIn(r"\u001b", html)
        self.assertIn(r"\u0000", html)
        self.assertIn(r"\u202e", html)
        self.assertIn(r"\u2066", html)

    def test_missing_values_render_as_explicit_unknowns(self) -> None:
        missing = replace(
            NOTICES[0],
            title=None,
            buyer=None,
            deadline=None,
            source_url=None,
        )
        result = qualify_notices(PROFILE, (missing,), AS_OF)

        markdown = render_markdown(PROFILE, result, AS_OF, PROVENANCE)
        html = render_html(PROFILE, result, AS_OF, PROVENANCE)

        self.assertIn(r"\(title missing\)", markdown)
        self.assertIn("(missing)", html)
        self.assertEqual(result[0].verdict, Verdict.WATCH)


if __name__ == "__main__":
    unittest.main()
