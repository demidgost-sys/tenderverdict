from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tenderverdict.output import write_text_atomically


class AtomicOutputTests(unittest.TestCase):
    def test_replace_failure_preserves_destination_and_cleans_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.txt"
            output.write_text("keep\n", encoding="utf-8")

            with (
                patch("tenderverdict.output.os.replace", side_effect=OSError("synthetic failure")),
                self.assertRaisesRegex(OSError, "synthetic failure"),
            ):
                write_text_atomically(output, "new\n")

            self.assertEqual(output.read_text(encoding="utf-8"), "keep\n")
            self.assertEqual(list(Path(directory).glob(".report.txt.*.tmp")), [])

    def test_missing_output_directory_fails_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "missing" / "report.txt"
            with self.assertRaisesRegex(OSError, "output directory does not exist"):
                write_text_atomically(output, "content")
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
