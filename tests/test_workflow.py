from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from tenderverdict.models import load_notices, load_profile
from tenderverdict.qualification import qualify_notices
from tenderverdict.report import render_html, render_markdown, report_as_dict
from tenderverdict.workflow import demo_run, qualify_files, render_run, write_run

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "synthetic"


class WorkflowTests(unittest.TestCase):
    def test_demo_run_matches_canonical_pipeline_and_snapshots(self) -> None:
        with patch("socket.socket.connect", side_effect=AssertionError("network forbidden")):
            run = demo_run()

        profile = load_profile(EXAMPLES / "profile.json")
        notices = load_notices(EXAMPLES / "notices.json")
        expected_results = qualify_notices(profile, notices, as_of=date(2026, 8, 2))

        self.assertEqual(run.profile, profile)
        self.assertEqual(run.results, expected_results)
        self.assertEqual(
            render_run(run, "markdown"),
            (EXAMPLES / "expected-brief.md").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            render_run(run, "html"),
            (ROOT / "demo" / "index.html").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            json.loads(render_run(run, "json")),
            report_as_dict(profile, expected_results, as_of=date(2026, 8, 2)),
        )

    def test_file_workflow_matches_direct_renderers(self) -> None:
        run = qualify_files(
            EXAMPLES / "profile.json",
            EXAMPLES / "notices.json",
            as_of=date(2026, 8, 2),
        )

        self.assertEqual(
            render_run(run, "markdown"),
            render_markdown(run.profile, run.results, as_of=run.as_of),
        )
        self.assertEqual(
            render_run(run, "html"),
            render_html(run.profile, run.results, as_of=run.as_of),
        )
        self.assertEqual(
            run.summary,
            {"total": 3, "open_documents": 1, "watch": 1, "reject": 1},
        )

        csv_run = qualify_files(
            EXAMPLES / "profile.json",
            EXAMPLES / "notices.csv",
            as_of=date(2026, 8, 2),
        )
        self.assertEqual(csv_run, run)

    def test_write_run_is_atomic_and_rejects_unknown_format(self) -> None:
        run = demo_run()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.html"
            write_run(run, output, "html")
            self.assertEqual(output.read_text(encoding="utf-8"), render_run(run, "html"))
            with self.assertRaisesRegex(ValueError, "unsupported format"):
                write_run(run, output, "pdf")
            self.assertEqual(output.read_text(encoding="utf-8"), render_run(run, "html"))


if __name__ == "__main__":
    unittest.main()
