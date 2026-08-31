#!/usr/bin/env python3
"""Extract the canonical 1024px Shipaton icon from the reviewed ICNS asset."""

from __future__ import annotations

import argparse
import os
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packaging" / "tenderverdict-icon.icns"
DEFAULT_OUTPUT = ROOT / "submission" / "icon-1024.png"
DEFAULT_SCREENSHOT = ROOT / "submission" / "screenshot-1179x2556.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ALLOWED_PNG_CHUNKS = {b"IHDR", b"IDAT", b"IEND"}


def _extract_ic10(payload: bytes) -> bytes:
    if len(payload) < 16 or payload[:4] != b"icns":
        raise ValueError("source is not a valid ICNS container")
    if int.from_bytes(payload[4:8], "big") != len(payload):
        raise ValueError("ICNS declared length does not match its bytes")

    offset = 8
    while offset < len(payload):
        chunk_type = payload[offset : offset + 4]
        chunk_length = int.from_bytes(payload[offset + 4 : offset + 8], "big")
        if chunk_length < 8 or offset + chunk_length > len(payload):
            raise ValueError("ICNS contains an invalid chunk")
        if chunk_type == b"ic10":
            image = payload[offset + 8 : offset + chunk_length]
            if not image.startswith(PNG_SIGNATURE):
                raise ValueError("the ICNS 1024px chunk is not PNG")
            width = int.from_bytes(image[16:20], "big")
            height = int.from_bytes(image[20:24], "big")
            if (width, height) != (1024, 1024):
                raise ValueError(f"expected 1024x1024 icon, got {width}x{height}")
            return image
        offset += chunk_length
    raise ValueError("the ICNS source has no 1024px ic10 chunk")


def _write_atomically(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _strip_png_metadata(payload: bytes) -> bytes:
    if not payload.startswith(PNG_SIGNATURE):
        raise ValueError("submission screenshot is not PNG")
    output = bytearray(PNG_SIGNATURE)
    offset = len(PNG_SIGNATURE)
    retained: list[bytes] = []
    while offset < len(payload):
        if offset + 12 > len(payload):
            raise ValueError("submission screenshot contains a truncated PNG chunk")
        length = int.from_bytes(payload[offset : offset + 4], "big")
        chunk_type = payload[offset + 4 : offset + 8]
        end = offset + 12 + length
        if end > len(payload):
            raise ValueError("submission screenshot contains an invalid PNG chunk")
        chunk_data = payload[offset + 8 : offset + 8 + length]
        expected_crc = int.from_bytes(payload[offset + 8 + length : end], "big")
        if zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF != expected_crc:
            raise ValueError("submission screenshot contains an invalid PNG checksum")
        if chunk_type in ALLOWED_PNG_CHUNKS:
            output.extend(payload[offset:end])
            retained.append(chunk_type)
        offset = end
        if chunk_type == b"IEND":
            break
    if (
        retained[:1] != [b"IHDR"]
        or retained[-1:] != [b"IEND"]
        or b"IDAT" not in retained
        or offset != len(payload)
    ):
        raise ValueError("submission screenshot has an invalid PNG structure")
    return bytes(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--screenshot", type=Path, default=DEFAULT_SCREENSHOT)
    arguments = parser.parse_args()
    try:
        icon = _extract_ic10(SOURCE.read_bytes())
        _write_atomically(arguments.output, icon)
        screenshot_bytes = None
        if arguments.screenshot.is_file():
            screenshot_bytes = _strip_png_metadata(arguments.screenshot.read_bytes())
            _write_atomically(arguments.screenshot, screenshot_bytes)
    except (OSError, ValueError) as exc:
        print(f"SUBMISSION_ASSET_FAIL: {exc}")
        return 1
    print(f"SUBMISSION_ASSET_OK: {arguments.output} 1024x1024 bytes={len(icon)}")
    if screenshot_bytes is not None:
        print(
            f"SUBMISSION_SCREENSHOT_SANITIZED: {arguments.screenshot} bytes={len(screenshot_bytes)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
