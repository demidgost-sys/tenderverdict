#!/usr/bin/env python3
"""Strip all ancillary PNG chunks using the repository submission sanitizer."""

from __future__ import annotations

import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.prepare_submission_assets import _strip_png_metadata, _write_atomically  # noqa: E402


def main(arguments: list[str]) -> int:
    if not arguments:
        print("usage: sanitize_png.py <png> [<png> ...]", file=sys.stderr)
        return 2
    for value in arguments:
        path = Path(value).resolve()
        payload = _strip_png_metadata(path.read_bytes())
        _write_atomically(path, payload)
        print(f"VIDEO_PNG_SANITIZED path={path} bytes={len(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
