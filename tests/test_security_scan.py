from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from security_scan import _scan_text  # noqa: E402


class SecurityScanTests(unittest.TestCase):
    def test_swift_closure_arguments_are_not_prices(self) -> None:
        errors: list[str] = []
        shorthand = chr(36)

        _scan_text(
            "Example.swift",
            (
                f"let values = rows.filter {{ {shorthand}0.count > 0 }}"
                f".sorted {{ {shorthand}0.id < {shorthand}1.id }}"
            ),
            errors,
        )

        self.assertEqual(errors, [])

    def test_swift_string_price_is_still_rejected(self) -> None:
        errors: list[str] = []

        price_marker = chr(36) + "19.99"
        _scan_text("Example.swift", f'let label = "Unlock for {price_marker}"', errors)

        self.assertEqual(
            errors,
            ["Example.swift: commercial call-to-action or price marker"],
        )

    def test_concatenated_swift_string_price_is_rejected(self) -> None:
        shorthand = chr(36)
        cases = (
            f'"{shorthand}" + "19.99"',
            f'"{shorthand}" + /* format */ "19.99"',
            f'#"{shorthand}"# + #"19.99"#',
        )
        for expression in cases:
            with self.subTest(expression=expression):
                errors: list[str] = []
                _scan_text(
                    "Example.swift",
                    f"let label = {expression}",
                    errors,
                )

                self.assertEqual(
                    errors,
                    ["Example.swift: commercial call-to-action or price marker"],
                )


if __name__ == "__main__":
    unittest.main()
