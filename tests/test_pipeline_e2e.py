from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path

from tenderverdict.demo_data import demo_notices, demo_profile
from tenderverdict.models import load_notices, load_profile, render_notices_csv
from tenderverdict.qualification import qualify_notices
from tenderverdict.report import render_html, render_markdown, report_as_dict

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "synthetic"


class OfflinePipelineTests(unittest.TestCase):
    def test_packaged_demo_data_matches_public_examples(self) -> None:
        self.assertEqual(
            demo_profile(),
            json.loads((EXAMPLES / "profile.json").read_text(encoding="utf-8")),
        )
        self.assertEqual(
            demo_notices(),
            json.loads((EXAMPLES / "notices.json").read_text(encoding="utf-8")),
        )
        csv_notices = load_notices(EXAMPLES / "notices.csv")
        self.assertEqual([notice.to_dict() for notice in csv_notices], demo_notices())
        self.assertEqual(
            render_notices_csv(csv_notices),
            (EXAMPLES / "notices.csv").read_text(encoding="utf-8"),
        )

    def test_demo_snapshots_are_reproducible(self) -> None:
        profile = load_profile(EXAMPLES / "profile.json")
        notices = load_notices(EXAMPLES / "notices.json")
        as_of = date(2026, 8, 2)
        results = qualify_notices(profile, notices, as_of=as_of)

        payload = report_as_dict(profile, results, as_of=as_of)
        self.assertEqual(
            [result["verdict"] for result in payload["results"]],
            ["open_documents", "watch", "reject"],
        )
        self.assertEqual(
            render_markdown(profile, results, as_of=as_of),
            (EXAMPLES / "expected-brief.md").read_text(encoding="utf-8"),
        )
        html = render_html(profile, results, as_of=as_of)
        self.assertEqual(html, (ROOT / "demo" / "index.html").read_text(encoding="utf-8"))
        lowered = html.lower()
        for forbidden in ("<script", "<form", "<iframe", " src=", " href=", "@import"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)
        self.assertEqual(lowered.count("<h1"), 1)
        self.assertIn('<meta name="viewport"', lowered)


if __name__ == "__main__":
    unittest.main()
