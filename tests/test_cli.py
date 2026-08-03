from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tenderverdict.cli import main
from tenderverdict.ted import TedApiError

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "synthetic"


class CliTests(unittest.TestCase):
    def test_desktop_command_delegates_without_changing_cli_contract(self) -> None:
        with patch("tenderverdict.desktop.main", return_value=0) as desktop_main:
            exit_code = main(["desktop"])

        self.assertEqual(exit_code, 0)
        desktop_main.assert_called_once_with([])

    def test_demo_defaults_to_markdown_stdout(self) -> None:
        stdout = io.StringIO()
        with (
            patch("socket.socket.connect", side_effect=AssertionError("network forbidden")),
            contextlib.redirect_stdout(stdout),
        ):
            exit_code = main(["demo"])

        self.assertEqual(exit_code, 0)
        self.assertIn("# TenderVerdict qualification report", stdout.getvalue())
        self.assertIn("**open_documents:** 1", stdout.getvalue())
        self.assertIn("**watch:** 1", stdout.getvalue())
        self.assertIn("**reject:** 1", stdout.getvalue())

    def test_demo_can_write_json_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            exit_code = main(["demo", "--format", "json", "--output", str(output)])

            self.assertEqual(exit_code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["summary"],
                {"total": 3, "open_documents": 1, "watch": 1, "reject": 1},
            )

    def test_qualify_stdout_makes_terminal_controls_visible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = root / "profile.json"
            notices = root / "notices.json"
            profile.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "name": "Example\u001b]0;changed\u0007 Organization",
                        "cpv_codes": ["72260000"],
                        "countries": ["AUT"],
                        "minimum_days_to_deadline": 14,
                    }
                ),
                encoding="utf-8",
            )
            notices.write_text(
                json.dumps(
                    [
                        {
                            "publication_number": "SYN-CONTROL-001",
                            "notice_type": "competition",
                            "title": "Synthetic\u202e title",
                            "buyer": "Example Buyer",
                            "cpv_codes": ["72260000"],
                            "countries": ["AUT"],
                            "deadline": "2026-09-15",
                            "source_url": "https://procurement.example/notices/SYN-CONTROL-001",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "qualify",
                        "--profile",
                        str(profile),
                        "--notices",
                        str(notices),
                        "--as-of",
                        "2026-08-02",
                    ]
                )

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertNotIn("\x1b", output)
            self.assertNotIn("\x07", output)
            self.assertNotIn("\u202e", output)
            self.assertIn(r"\\u001b", output)
            self.assertIn(r"\\u0007", output)
            self.assertIn(r"\\u202e", output)

    def test_qualify_json_stdout_escapes_non_ascii_and_controls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = root / "profile.json"
            notices = root / "notices.json"
            profile.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "name": "B\u00fcro\u202e Example",
                        "cpv_codes": ["72260000"],
                        "countries": ["AUT"],
                        "minimum_days_to_deadline": 14,
                    }
                ),
                encoding="utf-8",
            )
            notices.write_text(
                json.dumps(
                    [
                        {
                            "publication_number": "SYN-JSON-001",
                            "notice_type": "competition",
                            "title": "Synthetic\u0085 title",
                            "buyer": "Example Buyer",
                            "cpv_codes": ["72260000"],
                            "countries": ["AUT"],
                            "deadline": "2026-09-15",
                            "source_url": "https://procurement.example/notices/SYN-JSON-001",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    [
                        "qualify",
                        "--profile",
                        str(profile),
                        "--notices",
                        str(notices),
                        "--as-of",
                        "2026-08-02",
                        "--format",
                        "json",
                    ]
                )

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertTrue(output.isascii())
            self.assertIn(r"\u00fc", output)
            self.assertIn(r"\u202e", output)
            self.assertIn(r"\u0085", output)
            self.assertEqual(json.loads(output)["profile"]["name"], "B\u00fcro\u202e Example")

    def test_invalid_input_does_not_replace_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = root / "profile.json"
            notices = root / "notices.json"
            output = root / "report.md"
            profile.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "name": "Example Software GmbH",
                        "cpv_codes": ["72260000"],
                        "countries": ["AUT"],
                        "minimum_days_to_deadline": 14,
                    }
                ),
                encoding="utf-8",
            )
            notices.write_text(
                json.dumps(
                    [
                        {
                            "publication_number": "SYN-BAD-DATE",
                            "notice_type": "competition",
                            "title": "Synthetic",
                            "buyer": "Example Buyer",
                            "cpv_codes": ["72260000"],
                            "countries": ["AUT"],
                            "deadline": "2026-99-01",
                            "source_url": "https://procurement.example/notices/SYN-BAD-DATE",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            output.write_text("keep-me\n", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                exit_code = main(
                    [
                        "qualify",
                        "--profile",
                        str(profile),
                        "--notices",
                        str(notices),
                        "--as-of",
                        "2026-08-02",
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(exit_code, 2)
            self.assertIn("deadline", stderr.getvalue())
            self.assertEqual(output.read_text(encoding="utf-8"), "keep-me\n")
            self.assertEqual(list(root.glob(f".{output.name}.*.tmp")), [])

    def test_invalid_csv_does_not_replace_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notices = root / "notices.csv"
            output = root / "report.md"
            notices.write_text(
                "publication_number,notice_type,title,buyer,cpv_codes,countries,"
                "deadline,source_url\n"
                "SYN-BAD-CSV,competition,Synthetic,Example Buyer,72260000,AUT,"
                "2026-99-01,https://procurement.example/notices/SYN-BAD-CSV\n",
                encoding="utf-8",
            )
            output.write_text("keep-me\n", encoding="utf-8")
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                exit_code = main(
                    [
                        "qualify",
                        "--profile",
                        str(EXAMPLES / "profile.json"),
                        "--notices",
                        str(notices),
                        "--as-of",
                        "2026-08-02",
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(exit_code, 2)
            self.assertIn("CSV row 2: deadline", stderr.getvalue())
            self.assertEqual(output.read_text(encoding="utf-8"), "keep-me\n")
            self.assertEqual(list(root.glob(f".{output.name}.*.tmp")), [])

    def test_failed_fetch_does_not_replace_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "notices.json"
            output.write_text("keep-me\n", encoding="utf-8")
            stderr = io.StringIO()

            with (
                patch(
                    "tenderverdict.cli.fetch_notices",
                    side_effect=TedApiError("synthetic failure"),
                ),
                contextlib.redirect_stderr(stderr),
            ):
                exit_code = main(
                    [
                        "fetch-ted",
                        "--query",
                        "form-type = competition",
                        "--max-notices",
                        "2",
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(exit_code, 2)
            self.assertIn("synthetic failure", stderr.getvalue())
            self.assertEqual(output.read_text(encoding="utf-8"), "keep-me\n")

    def test_successful_fetch_writes_normalized_json(self) -> None:
        notice = {
            "publication_number": "SYN-FETCH-001",
            "notice_type": "competition",
            "title": "Synthetic\u202e service",
            "buyer": "Example Buyer",
            "cpv_codes": ["72260000"],
            "countries": ["AUT"],
            "deadline": "2026-09-15",
            "source_url": "https://procurement.example/notices/SYN-FETCH-001",
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "notices.json"
            with patch("tenderverdict.cli.fetch_notices", return_value=[notice]):
                exit_code = main(
                    [
                        "fetch-ted",
                        "--query",
                        "form-type = competition",
                        "--max-notices",
                        "1",
                        "--output",
                        str(output),
                    ]
                )

            self.assertEqual(exit_code, 0)
            raw_output = output.read_text(encoding="utf-8")
            self.assertTrue(raw_output.isascii())
            self.assertIn(r"\u202e", raw_output)
            snapshot = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(snapshot["schema_version"], 1)
            self.assertEqual(snapshot["source"]["kind"], "ted_search_api")
            self.assertEqual(snapshot["source"]["query"], "form-type = competition")
            self.assertEqual(snapshot["source"]["lot_policy"], "xml_expanded_lots_v1")
            self.assertRegex(
                snapshot["source"]["retrieved_at"],
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
            )
            self.assertEqual(snapshot["notices"], [notice])


if __name__ == "__main__":
    unittest.main()
