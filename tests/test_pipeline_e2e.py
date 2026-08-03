from __future__ import annotations

import json
import unittest
from pathlib import Path

from tenderverdict.demo_data import demo_notices, demo_profile
from tenderverdict.models import load_notices, render_notices_csv
from tenderverdict.workflow import demo_run, render_run

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
        run = demo_run()

        payload = json.loads(render_run(run, "json"))
        self.assertEqual(
            [result["verdict"] for result in payload["results"]],
            ["open_documents", "watch", "reject"],
        )
        self.assertEqual(
            render_run(run, "markdown"),
            (EXAMPLES / "expected-brief.md").read_text(encoding="utf-8"),
        )
        html = render_run(run, "html")
        self.assertEqual(html, (ROOT / "demo" / "index.html").read_text(encoding="utf-8"))
        lowered = html.lower()
        for forbidden in ("<script", "<form", "<iframe", " src=", " href=", "@import"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, lowered)
        self.assertEqual(lowered.count("<h1"), 1)
        self.assertIn('<meta name="viewport"', lowered)


if __name__ == "__main__":
    unittest.main()
