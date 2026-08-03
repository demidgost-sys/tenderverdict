#!/usr/bin/env python3
"""Build the native TenderVerdict desktop preview with the pinned toolchain."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "packaging" / "TenderVerdict.spec"


def _check_tk() -> None:
    try:
        import _tkinter  # noqa: F401
        import tkinter as tk
    except ImportError as exc:
        raise RuntimeError("this Python installation does not include Tk") from exc

    root = tk.Tk()
    try:
        root.withdraw()
        root.update_idletasks()
    finally:
        root.destroy()


def main() -> int:
    try:
        _check_tk()
        subprocess.run(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--noconfirm",
                "--clean",
                str(SPEC),
            ],
            check=True,
            cwd=ROOT,
        )
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"DESKTOP_BUILD_FAIL: {exc}", file=sys.stderr)
        return 1
    print("DESKTOP_BUILD_OK: native one-directory preview created under dist/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
