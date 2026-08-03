from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tenderverdict.desktop import (
    MAX_NOTICES_FILE_BYTES,
    TenderVerdictApp,
    desktop_palette,
    export_format_for_path,
    format_result_details,
    notice_count_label,
    profile_from_fields,
    read_local_snapshot,
    shortcut_action,
    visible_result_indices,
)
from tenderverdict.models import SchemaValidationError
from tenderverdict.workflow import demo_run

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "synthetic"


class DesktopInputTests(unittest.TestCase):
    def test_profile_fields_use_the_canonical_schema(self) -> None:
        profile = profile_from_fields(
            " Example Software GmbH ",
            "72260000, 72260000; 72261000",
            "aut deu AUT",
            "14",
        )

        self.assertEqual(profile.name, "Example Software GmbH")
        self.assertEqual(profile.cpv_codes, ("72260000", "72261000"))
        self.assertEqual(profile.countries, ("AUT", "DEU"))
        self.assertEqual(profile.minimum_days_to_deadline, 14)

    def test_profile_fields_give_recoverable_errors(self) -> None:
        cases = (
            (("Example", "", "AUT", "14"), "Add at least one 8-digit CPV code"),
            (("Example", "72260000", "", "14"), "Add at least one 3-letter country code"),
            (("Example", "72260000", "AUT", "14.5"), "whole number"),
            (("Example", "7226", "AUT", "14"), "8-digit CPV code"),
            (("Example", "99999999", "AUT", "14"), "official CPV vocabulary"),
        )
        for arguments, message in cases:
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(SchemaValidationError, message):
                    profile_from_fields(*arguments)

    def test_local_file_budget_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "notices.json"
            valid.write_text("[]", encoding="utf-8")
            self.assertEqual(
                read_local_snapshot(
                    str(valid),
                    label="notices",
                    maximum_bytes=MAX_NOTICES_FILE_BYTES,
                ).path,
                valid,
            )
            oversized = root / "oversized.json"
            oversized.write_bytes(b"x" * 8)
            with self.assertRaisesRegex(SchemaValidationError, "no larger than"):
                read_local_snapshot(
                    str(oversized),
                    label="notices",
                    maximum_bytes=4,
                )
            with self.assertRaisesRegex(SchemaValidationError, "Choose a notices file"):
                read_local_snapshot("", label="notices", maximum_bytes=4)

    def test_snapshot_digest_changes_when_same_path_content_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notices.json"
            path.write_text("[]", encoding="utf-8")
            first = read_local_snapshot(
                str(path),
                label="notices",
                maximum_bytes=MAX_NOTICES_FILE_BYTES,
            )

            path.write_text('[{"publication_number":"SYN-CHANGED"}]', encoding="utf-8")
            second = read_local_snapshot(
                str(path),
                label="notices",
                maximum_bytes=MAX_NOTICES_FILE_BYTES,
            )

            self.assertNotEqual(first.sha256, second.sha256)

    def test_stale_same_path_snapshot_blocks_export(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notices.json"
            path.write_text("[]", encoding="utf-8")
            original = read_local_snapshot(
                str(path),
                label="notices",
                maximum_bytes=MAX_NOTICES_FILE_BYTES,
            )
            path.write_text('[{"publication_number":"SYN-CHANGED"}]', encoding="utf-8")

            app = object.__new__(TenderVerdictApp)
            app._current_notices_sha256 = original.sha256
            app.notices_path_var = Mock(get=Mock(return_value=str(path)))
            app.run_button = Mock()
            app._clear_results = Mock()
            app._show_error = Mock()

            self.assertFalse(app._notices_are_current())
            app._clear_results.assert_called_once()
            app._show_error.assert_called_once()

    def test_failed_rerun_discards_previous_result(self) -> None:
        app = object.__new__(TenderVerdictApp)
        app._current_run = demo_run()

        def clear_result(_status: str) -> None:
            app._current_run = None

        app._clear_results = Mock(side_effect=clear_result)
        app._profile_from_form = Mock(side_effect=SchemaValidationError("profile.name is required"))
        app._show_error = Mock()
        app.name_entry = Mock()
        app.cpv_entry = Mock()
        app.countries_entry = Mock()
        app.minimum_days_entry = Mock()

        app._run_review()

        self.assertIsNone(app._current_run)
        app._clear_results.assert_called_once()
        app._show_error.assert_called_once()

    def test_export_suffix_is_explicit(self) -> None:
        self.assertEqual(export_format_for_path("report.html"), "html")
        self.assertEqual(export_format_for_path("report.MD"), "markdown")
        self.assertEqual(export_format_for_path("report.json"), "json")
        with self.assertRaisesRegex(SchemaValidationError, "as .html, .md, or .json"):
            export_format_for_path("report.pdf")

    def test_shortcuts_do_not_depend_on_latin_keysyms(self) -> None:
        self.assertEqual(shortcut_action("aqua", 0, "Cyrillic_ve"), "demo")
        self.assertEqual(shortcut_action("aqua", 0, "Cyrillic_ka"), "review")
        self.assertEqual(shortcut_action("win32", 0, "Cyrillic_shcha"), "open")
        self.assertEqual(shortcut_action("win32", 0, "Cyrillic_yeru"), "export")
        self.assertIsNone(shortcut_action("aqua", 0, "a"))

    def test_notice_count_label_uses_plain_grammar(self) -> None:
        self.assertEqual(notice_count_label(1), "1 notice")
        self.assertEqual(notice_count_label(3), "3 notices")

    def test_choose_notices_prevalidates_csv_before_accepting_it(self) -> None:
        app = object.__new__(TenderVerdictApp)
        app.filedialog = Mock(askopenfilename=Mock(return_value=str(EXAMPLES / "notices.csv")))
        app.choose_notices_button = Mock()
        app.notices_path_var = Mock()
        app.notices_display_var = Mock()
        app.as_of_entry = Mock()
        app._set_status = Mock()
        app._show_error = Mock()
        app._using_demo_notices = True

        app._choose_notices()

        self.assertFalse(app._using_demo_notices)
        app.notices_path_var.set.assert_called_once_with(str(EXAMPLES / "notices.csv"))
        app.notices_display_var.set.assert_called_once_with(str(EXAMPLES / "notices.csv"))
        app._set_status.assert_called_once_with(
            "3 notices ready · confirm the review date, then run the review.",
            "success",
        )
        app.as_of_entry.focus_set.assert_called_once()
        app._show_error.assert_not_called()

    def test_save_csv_example_creates_reusable_synthetic_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "example.csv"
            app = object.__new__(TenderVerdictApp)
            app.filedialog = Mock(asksaveasfilename=Mock(return_value=str(destination)))
            app.choose_notices_button = Mock()
            app._set_status = Mock()
            app._show_error = Mock()

            app._save_csv_example()

            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                (EXAMPLES / "notices.csv").read_text(encoding="utf-8"),
            )
            app._show_error.assert_not_called()
            app._set_status.assert_called_once_with(
                "Saved example.csv. Replace the synthetic rows, then choose that file.",
                "success",
            )

    def test_invalid_notice_file_is_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            invalid = Path(directory) / "notices.csv"
            invalid.write_text("wrong,header\nvalue,value\n", encoding="utf-8")
            app = object.__new__(TenderVerdictApp)
            app.filedialog = Mock(askopenfilename=Mock(return_value=str(invalid)))
            app.choose_notices_button = Mock()
            app.notices_path_var = Mock()
            app.notices_display_var = Mock()
            app._show_error = Mock()
            app._using_demo_notices = True

            app._choose_notices()

            self.assertTrue(app._using_demo_notices)
            app.notices_path_var.set.assert_not_called()
            app.notices_display_var.set.assert_not_called()
            app._show_error.assert_called_once()
            self.assertEqual(app._show_error.call_args.args[0], "Unable to use notice data")
            self.assertIs(app._show_error.call_args.args[2], app.choose_notices_button)


class DesktopPresentationTests(unittest.TestCase):
    def test_semantic_palettes_keep_readable_contrast(self) -> None:
        for is_dark in (False, True):
            with self.subTest(is_dark=is_dark):
                palette = desktop_palette(is_dark)
                pairs = (
                    (palette.text, palette.surface),
                    (palette.muted, palette.surface),
                    (palette.subtle, palette.surface),
                    (palette.accent_text, palette.accent),
                    (palette.success, palette.surface_alt),
                    (palette.warning, palette.surface_alt),
                    (palette.danger, palette.surface_alt),
                )
                for foreground, background in pairs:
                    self.assertGreaterEqual(_contrast_ratio(foreground, background), 4.5)

    def test_result_details_make_controls_visible(self) -> None:
        result = demo_run().results[0]
        unsafe = result.__class__(
            notice=result.notice.__class__(
                publication_number="SYN-CTRL\u202e",
                notice_type=result.notice.notice_type,
                title="Title\x1b<script>",
                buyer=result.notice.buyer,
                cpv_codes=result.notice.cpv_codes,
                countries=result.notice.countries,
                deadline=result.notice.deadline,
                source_url=result.notice.source_url,
            ),
            verdict=result.verdict,
            reasons=result.reasons,
            unknowns=result.unknowns,
            human_next_step=result.human_next_step,
        )

        details = format_result_details(unsafe)
        self.assertNotIn("\u202e", details)
        self.assertNotIn("\x1b", details)
        self.assertIn(r"\u202e", details)
        self.assertIn(r"\u001b", details)
        self.assertIn("<script>", details)
        self.assertIn("Verdict: Open documents", details)

    def test_demo_path_is_offline(self) -> None:
        with patch("socket.socket.connect", side_effect=AssertionError("network forbidden")):
            run = demo_run()
        self.assertEqual(run.summary["total"], 3)

    def test_result_queue_filters_and_sorts_without_changing_the_run(self) -> None:
        run = demo_run()

        self.assertEqual(
            visible_result_indices(run.results, "Watch", "input", False),
            [1],
        )
        self.assertEqual(
            visible_result_indices(run.results, "All verdicts", "verdict", False),
            [0, 1, 2],
        )
        by_notice = visible_result_indices(
            run.results,
            "All verdicts",
            "notice",
            True,
        )
        self.assertEqual(by_notice, [1, 2, 0])

    def test_copy_selected_result_is_explicit_plain_text(self) -> None:
        app = object.__new__(TenderVerdictApp)
        app._current_run = demo_run()
        app.results_tree = Mock(selection=Mock(return_value=("0",)))
        app.root = Mock()
        app._set_status = Mock()

        handled = app._copy_selected_result()

        self.assertEqual(handled, "break")
        app.root.clipboard_clear.assert_called_once_with()
        copied = app.root.clipboard_append.call_args.args[0]
        self.assertIn("Verdict: Open documents", copied)
        self.assertNotIn("<script", copied.casefold())
        app._set_status.assert_called_once_with(
            "Copied the selected result as plain text. No data was uploaded.",
            "success",
        )


def _relative_luminance(colour: str) -> float:
    channels = [int(colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first: str, second: str) -> float:
    brightest, darkest = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (brightest + 0.05) / (darkest + 0.05)


if __name__ == "__main__":
    unittest.main()
