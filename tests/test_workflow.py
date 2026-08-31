from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from tenderverdict.models import (
    load_notices,
    load_profile,
    portfolio_workspace_from_dict,
)
from tenderverdict.qualification import qualify_notices
from tenderverdict.report import render_html, render_markdown, report_as_dict
from tenderverdict.workflow import (
    demo_run,
    portfolio_report_as_dict,
    qualify_files,
    qualify_portfolio_files,
    qualify_portfolio_inputs,
    render_portfolio_run,
    render_run,
    write_run,
)

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
            report_as_dict(
                profile,
                expected_results,
                as_of=date(2026, 8, 2),
                provenance=run.provenance,
            ),
        )

    def test_file_workflow_matches_direct_renderers(self) -> None:
        run = qualify_files(
            EXAMPLES / "profile.json",
            EXAMPLES / "notices.json",
            as_of=date(2026, 8, 2),
        )

        self.assertEqual(
            render_run(run, "markdown"),
            render_markdown(
                run.profile,
                run.results,
                as_of=run.as_of,
                provenance=run.provenance,
            ),
        )
        self.assertEqual(
            render_run(run, "html"),
            render_html(
                run.profile,
                run.results,
                as_of=run.as_of,
                provenance=run.provenance,
            ),
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
        self.assertEqual(csv_run.profile, run.profile)
        self.assertEqual(csv_run.results, run.results)
        self.assertEqual(csv_run.as_of, run.as_of)
        self.assertEqual(run.provenance.source_kind, "local_json")
        self.assertEqual(csv_run.provenance.source_kind, "local_csv")
        self.assertNotEqual(csv_run.provenance.notices_sha256, run.provenance.notices_sha256)

    def test_write_run_is_atomic_and_rejects_unknown_format(self) -> None:
        run = demo_run()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.html"
            write_run(run, output, "html")
            self.assertEqual(output.read_text(encoding="utf-8"), render_run(run, "html"))
            with self.assertRaisesRegex(ValueError, "unsupported format"):
                write_run(run, output, "pdf")
            self.assertEqual(output.read_text(encoding="utf-8"), render_run(run, "html"))

    def test_portfolio_file_workflow_preserves_shared_inputs_and_order(self) -> None:
        with patch("socket.socket.connect", side_effect=AssertionError("network forbidden")):
            run = qualify_portfolio_files(
                EXAMPLES / "portfolio-workspace.json",
                EXAMPLES / "notices.json",
                as_of=date(2026, 8, 2),
            )

        payload = portfolio_report_as_dict(run)
        profile_reports = payload["profile_reports"]
        self.assertIsInstance(profile_reports, list)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["kind"], "portfolio_workspace_report")
        self.assertEqual(payload["as_of"], "2026-08-02")
        self.assertEqual(payload["summary"], {"profile_count": 3, "notice_count": 3})
        self.assertEqual(
            [report["profile"]["name"] for report in profile_reports],
            [profile.name for profile in run.workspace.profiles],
        )
        self.assertEqual(
            profile_reports[0]["summary"],
            {"total": 3, "open_documents": 1, "watch": 1, "reject": 1},
        )

        expected_notice_order = [
            notice.publication_number for notice in load_notices(EXAMPLES / "notices.json")
        ]
        for report in profile_reports:
            self.assertEqual(report["schema_version"], 3)
            self.assertEqual(
                [result["publication_number"] for result in report["results"]],
                expected_notice_order,
            )

        profile_hashes = {profile_run.provenance.profile_sha256 for profile_run in run.profile_runs}
        notices_hashes = {profile_run.provenance.notices_sha256 for profile_run in run.profile_runs}
        self.assertEqual(len(profile_hashes), 3)
        self.assertEqual(len(notices_hashes), 1)

    def test_portfolio_render_is_deterministic_ascii_safe_and_has_no_ranking(self) -> None:
        workspace = portfolio_workspace_from_dict(
            {
                "schema_version": 1,
                "profiles": [
                    {
                        "schema_version": 1,
                        "name": "B\u00fcro\u202e Example",
                        "cpv_codes": ["72260000"],
                        "countries": ["AUT"],
                        "minimum_days_to_deadline": 14,
                    }
                ],
            }
        )
        run = qualify_portfolio_inputs(
            workspace,
            load_notices(EXAMPLES / "notices.json"),
            as_of=date(2026, 8, 2),
        )

        first = render_portfolio_run(run)
        second = render_portfolio_run(run)

        self.assertEqual(first, second)
        self.assertTrue(first.isascii())
        self.assertTrue(first.endswith("\n"))
        self.assertIn(r"\u00fc", first)
        self.assertIn(r"\u202e", first)
        self.assertNotIn("score", first.casefold())
        self.assertNotIn("ranking", first.casefold())

    def test_portfolio_empty_notice_set_keeps_per_profile_reports(self) -> None:
        workspace = portfolio_workspace_from_dict(
            {
                "schema_version": 1,
                "profiles": [
                    {
                        "schema_version": 1,
                        "name": "Example Empty Review",
                        "cpv_codes": ["72260000"],
                        "countries": ["AUT"],
                        "minimum_days_to_deadline": 14,
                    }
                ],
            }
        )
        payload = portfolio_report_as_dict(
            qualify_portfolio_inputs(workspace, (), as_of=date(2026, 8, 2))
        )

        self.assertEqual(payload["summary"], {"profile_count": 1, "notice_count": 0})
        self.assertEqual(payload["profile_reports"][0]["summary"]["total"], 0)


if __name__ == "__main__":
    unittest.main()
