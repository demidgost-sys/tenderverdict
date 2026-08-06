from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tenderverdict.models import MAX_NOTICES_FILE_BYTES, MAX_WORKSPACE_FILE_BYTES
from tools.next_gen_core_launcher import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "synthetic"
CANONICAL_FIELDS = [
    "publication_number",
    "lot_id",
    "notice_type",
    "title",
    "buyer",
    "cpv_codes",
    "countries",
    "deadline",
    "deadline_at",
    "publication_date",
    "source_url",
    "metadata_warnings",
]


class NextGenCoreLauncherTests(unittest.TestCase):
    def test_normalize_workspace_is_strict_normalized_deterministic_and_ascii_safe(self) -> None:
        workspace = {
            "profiles": [
                {
                    "countries": [" aut ", "AUT"],
                    "minimum_days_to_deadline": 14,
                    "cpv_codes": [" 72260000 ", "72260000"],
                    "name": "  B\u00fcro\u202e\u001b Example  ",
                    "schema_version": 1,
                }
            ],
            "schema_version": 1,
        }
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "workspace.json"
            source.write_text(json.dumps(workspace, ensure_ascii=False), encoding="utf-8")

            first = self._invoke(["normalize-workspace", "--workspace", str(source)])
            second = self._invoke(["normalize-workspace", "--workspace", str(source)])

        self.assertEqual(first, second)
        code, stdout, stderr = first
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stderr, "")
        self.assertTrue(stdout.isascii())
        self.assertIn(r"\u00fc", stdout)
        self.assertIn(r"\u202e", stdout)
        self.assertIn(r"\u001b", stdout)
        self.assertEqual(
            json.loads(stdout),
            {
                "schema_version": 1,
                "profiles": [
                    {
                        "schema_version": 1,
                        "name": "B\u00fcro\u202e\u001b Example",
                        "cpv_codes": ["72260000"],
                        "countries": ["AUT"],
                        "minimum_days_to_deadline": 14,
                    }
                ],
            },
        )

    def test_normalize_workspace_errors_have_empty_stdout_and_enforce_file_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = root / "invalid.json"
            invalid.write_text(
                json.dumps({"schema_version": 1, "profiles": [], "unknown": True}),
                encoding="utf-8",
            )
            oversized = root / "oversized.json"
            oversized.write_bytes(b" " * (MAX_WORKSPACE_FILE_BYTES + 1))

            for source, expected in (
                (invalid, "unknown field"),
                (oversized, "no larger than 256 KiB"),
            ):
                with self.subTest(source=source.name):
                    code, stdout, stderr = self._invoke(
                        ["normalize-workspace", "--workspace", str(source)]
                    )
                    self.assertEqual(code, 2)
                    self.assertEqual(stdout, "")
                    self.assertIn(expected, stderr)

    def test_inspect_json_emits_exact_schema_missing_counts_and_safe_preview(self) -> None:
        notices = [
            {
                "publication_number": "SYN-FULL-001",
                "lot_id": "LOT-0001",
                "notice_type": " competition ",
                "title": " Full notice ",
                "buyer": " Example Buyer ",
                "cpv_codes": ["72260000"],
                "countries": ["aut"],
                "deadline_at": "2026-09-15T12:00:00+02:00",
                "publication_date": "2026-08-01",
                "source_url": "https://procurement.example/full",
                "metadata_warnings": [" Public warning "],
            },
            {
                "publication_number": "SYN-MISSING-001",
                "title": "B\u00fcro\u202e\u001b notice",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "notices.json"
            source.write_text(json.dumps(notices, ensure_ascii=False), encoding="utf-8")

            first = self._invoke(["inspect-notices", "--notices", str(source), "--limit", "1"])
            second = self._invoke(["inspect-notices", "--notices", str(source), "--limit", "1"])

        self.assertEqual(first, second)
        code, stdout, stderr = first
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stderr, "")
        self.assertTrue(stdout.isascii())
        payload = json.loads(stdout)
        self.assertEqual(
            list(payload),
            [
                "schema_version",
                "kind",
                "source_kind",
                "notice_count",
                "canonical_fields",
                "preview",
                "missing_field_counts",
            ],
        )
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["kind"], "notice_import_preview")
        self.assertEqual(payload["source_kind"], "local_json")
        self.assertEqual(payload["notice_count"], 2)
        self.assertEqual(payload["canonical_fields"], CANONICAL_FIELDS)
        self.assertEqual(len(payload["preview"]), 1)
        self.assertEqual(list(payload["preview"][0]), CANONICAL_FIELDS)
        self.assertEqual(
            payload["preview"][0],
            {
                "publication_number": "SYN-FULL-001",
                "lot_id": "LOT-0001",
                "notice_type": "competition",
                "title": "Full notice",
                "buyer": "Example Buyer",
                "cpv_codes": ["72260000"],
                "countries": ["AUT"],
                "deadline": None,
                "deadline_at": "2026-09-15T12:00:00+02:00",
                "publication_date": "2026-08-01",
                "source_url": "https://procurement.example/full",
                "metadata_warnings": ["Public warning"],
            },
        )
        self.assertEqual(
            payload["missing_field_counts"],
            {
                "notice_type": 1,
                "title": 0,
                "buyer": 1,
                "cpv_codes": 1,
                "countries": 1,
                "deadline": 1,
                "source_url": 1,
            },
        )

    def test_inspect_csv_uses_canonical_parser_and_default_limit_is_five(self) -> None:
        code, stdout, stderr = self._invoke(
            ["inspect-notices", "--notices", str(EXAMPLES / "notices.csv"), "--limit", "2"]
        )
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["source_kind"], "local_csv")
        self.assertEqual(payload["notice_count"], 3)
        self.assertEqual(len(payload["preview"]), 2)
        self.assertEqual(payload["preview"][0]["cpv_codes"], ["72260000"])
        self.assertEqual(payload["preview"][0]["deadline"], "2026-09-15")

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "six.json"
            source.write_text(
                json.dumps([{"publication_number": f"SYN-{index:03d}"} for index in range(6)]),
                encoding="utf-8",
            )
            code, stdout, stderr = self._invoke(["inspect-notices", "--notices", str(source)])
        self.assertEqual(code, 0, stderr)
        self.assertEqual(len(json.loads(stdout)["preview"]), 5)

    def test_inspect_errors_and_limit_bounds_exit_two_with_empty_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed = root / "malformed.json"
            malformed.write_text("{not-json", encoding="utf-8")
            unsupported = root / "notices.txt"
            unsupported.write_text("[]", encoding="utf-8")
            oversized = root / "oversized.json"
            oversized.write_bytes(b" " * (MAX_NOTICES_FILE_BYTES + 1))

            for source, expected in (
                (malformed, "valid UTF-8 JSON"),
                (unsupported, "ending in .csv or .json"),
                (oversized, "no larger than 10 MiB"),
            ):
                with self.subTest(source=source.name):
                    code, stdout, stderr = self._invoke(
                        ["inspect-notices", "--notices", str(source)]
                    )
                    self.assertEqual(code, 2)
                    self.assertEqual(stdout, "")
                    self.assertIn(expected, stderr)

            valid = root / "valid.json"
            valid.write_text("[]", encoding="ascii")
            for limit in ("0", "21", "not-an-integer"):
                with self.subTest(limit=limit):
                    code, stdout, stderr = self._invoke(
                        ["inspect-notices", "--notices", str(valid), "--limit", limit]
                    )
                    self.assertEqual(code, 2)
                    self.assertEqual(stdout, "")
                    self.assertIn("limit must be an integer from 1 through 20", stderr)

    def test_existing_portfolio_command_remains_offline(self) -> None:
        code, stdout, stderr = self._invoke(
            [
                "portfolio",
                "--workspace",
                str(EXAMPLES / "portfolio-workspace.json"),
                "--notices",
                str(EXAMPLES / "notices.json"),
                "--as-of",
                "2026-08-02",
            ]
        )
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stderr, "")
        self.assertEqual(json.loads(stdout)["kind"], "portfolio_workspace_report")

    def _invoke(self, arguments: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch("socket.socket.connect", side_effect=AssertionError("network forbidden")),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            try:
                code = main(arguments)
            except SystemExit as exc:
                code = int(exc.code)
        return code, stdout.getvalue(), stderr.getvalue()


if __name__ == "__main__":
    unittest.main()
