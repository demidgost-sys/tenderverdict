#!/usr/bin/env python3
"""Fail closed when the candidate tree differs from its explicit allow-list."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import zlib
from pathlib import Path, PurePosixPath

MAX_FILE_BYTES = 1024 * 1024
MAX_SCREENSHOT_BYTES = 500 * 1024
SCREENSHOT_PATH = "demo/screenshot.png"
ICNS_PATH = "packaging/tenderverdict-icon.icns"
ICO_PATH = "packaging/tenderverdict-icon.ico"
SUBMISSION_ICON_PATH = "submission/icon-1024.png"
SUBMISSION_SCREENSHOT_PATH = "submission/screenshot-1179x2556.png"
JUDGE_ACCESS_EVIDENCE_PATH = "submission/evidence/unlocked-judge-access-2026-08-09.png"
UNLOCKED_EVIDENCE_PATH = "submission/evidence/unlocked-test-store-2026-08-04.png"
VOICEOVER_EVIDENCE_PATH = "submission/evidence/voiceover-restore-2026-08-04.png"
EVIDENCE_SCREENSHOT_PATHS = frozenset(
    {JUDGE_ACCESS_EVIDENCE_PATH, UNLOCKED_EVIDENCE_PATH, VOICEOVER_EVIDENCE_PATH}
)
BINARY_ASSET_PATHS = frozenset(
    {
        SCREENSHOT_PATH,
        ICNS_PATH,
        ICO_PATH,
        SUBMISSION_ICON_PATH,
        SUBMISSION_SCREENSHOT_PATH,
        *EVIDENCE_SCREENSHOT_PATHS,
    }
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FORBIDDEN_PNG_CHUNKS = {b"eXIf", b"tEXt", b"iTXt", b"zTXt"}
ALLOWED_PNG_CHUNKS = {b"IHDR", b"IDAT", b"IEND"}
ICNS_PNG_DIMENSIONS = {
    b"ic07": 128,
    b"ic08": 256,
    b"ic09": 512,
    b"ic10": 1024,
    b"ic11": 32,
    b"ic12": 64,
    b"ic13": 256,
    b"ic14": 512,
}
ALLOWLIST_NAME = "PUBLIC_TREE_ALLOWLIST.txt"
SDIST_METADATA_PATH = "PKG-INFO"
GLOB_CHARACTERS = frozenset("*?[]{}!")
IGNORED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
    }
)


class TreeError(ValueError):
    """A release-tree invariant was violated."""


def _run_git(root: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
    )


def _is_git_worktree(root: Path) -> bool:
    try:
        result = _run_git(root, "rev-parse", "--show-toplevel")
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    try:
        git_root = Path(result.stdout.decode("utf-8").strip()).resolve()
    except (OSError, UnicodeDecodeError):
        return False
    return git_root == root.resolve()


def read_allowlist(root: Path) -> list[str]:
    path = root / ALLOWLIST_NAME
    if not path.is_file() or path.is_symlink():
        raise TreeError(f"missing regular file: {ALLOWLIST_NAME}")

    entries = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    entries = [entry for entry in entries if entry]
    if not entries:
        raise TreeError("public-tree allow-list is empty")
    if len(entries) != len(set(entries)):
        raise TreeError("public-tree allow-list contains duplicate paths")
    if entries != sorted(entries):
        raise TreeError("public-tree allow-list must be bytewise sorted")
    if ALLOWLIST_NAME not in entries:
        raise TreeError(f"public-tree allow-list must include {ALLOWLIST_NAME}")

    for entry in entries:
        if any(character in entry for character in GLOB_CHARACTERS):
            raise TreeError(f"wildcards are forbidden in allow-list entry: {entry}")
        parsed = PurePosixPath(entry)
        if parsed.is_absolute() or ".." in parsed.parts or str(parsed) != entry:
            raise TreeError(f"unsafe or non-normalized allow-list entry: {entry}")
        if entry.startswith(".git/") or entry == ".git":
            raise TreeError(".git metadata cannot be part of the public tree")
    return entries


def _filesystem_files(root: Path) -> set[str]:
    files: set[str] = set()
    for current, directories, names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for directory in directories:
            path = current_path / directory
            if path.is_symlink():
                files.add(path.relative_to(root).as_posix())
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORY_NAMES and not directory.endswith(".egg-info")
        )
        for name in sorted(names):
            path = current_path / name
            files.add(path.relative_to(root).as_posix())
    return files


def _git_files_and_submodules(root: Path) -> tuple[set[str], set[str]]:
    tracked_raw = _run_git(root, "ls-files", "-z").stdout
    tracked = {item.decode("utf-8") for item in tracked_raw.split(b"\0") if item}

    stage_raw = _run_git(root, "ls-files", "--stage", "-z").stdout
    submodules: set[str] = set()
    for item in stage_raw.split(b"\0"):
        if not item:
            continue
        metadata, path = item.decode("utf-8").split("\t", 1)
        mode = metadata.split(" ", 1)[0]
        if mode == "160000":
            submodules.add(path)
    return tracked, submodules


def _looks_binary(path: Path) -> bool:
    with path.open("rb") as handle:
        sample = handle.read(8192)
    return b"\0" in sample


def _validate_png_payload(payload: bytes, label: str) -> tuple[int, int]:
    if not payload.startswith(PNG_SIGNATURE):
        raise TreeError(f"{label} does not have a valid PNG signature")

    offset = len(PNG_SIGNATURE)
    chunks: list[bytes] = []
    dimensions: tuple[int, int] | None = None
    while offset < len(payload):
        if offset + 12 > len(payload):
            raise TreeError(f"{label} has a truncated PNG chunk")
        length = int.from_bytes(payload[offset : offset + 4], "big")
        chunk_type = payload[offset + 4 : offset + 8]
        end = offset + 12 + length
        if end > len(payload):
            raise TreeError(f"{label} has an invalid PNG chunk length")
        chunk_data = payload[offset + 8 : offset + 8 + length]
        expected_crc = int.from_bytes(payload[offset + 8 + length : end], "big")
        actual_crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise TreeError(f"{label} has an invalid PNG chunk checksum")
        if chunk_type == b"IHDR":
            if chunks or length != 13:
                raise TreeError(f"{label} has an invalid PNG IHDR chunk")
            dimensions = (
                int.from_bytes(chunk_data[:4], "big"),
                int.from_bytes(chunk_data[4:8], "big"),
            )
        chunks.append(chunk_type)
        offset = end
        if chunk_type == b"IEND":
            break

    if not chunks or chunks[0] != b"IHDR" or chunks[-1] != b"IEND" or offset != len(payload):
        raise TreeError(f"{label} has an invalid PNG chunk structure")
    forbidden = sorted(set(chunks) & FORBIDDEN_PNG_CHUNKS)
    if forbidden:
        labels = ", ".join(chunk.decode("ascii") for chunk in forbidden)
        raise TreeError(f"{label} contains metadata chunks: {labels}")
    unsupported = sorted(set(chunks) - ALLOWED_PNG_CHUNKS)
    if unsupported:
        labels = ", ".join(
            chunk.decode("ascii", errors="backslashreplace") for chunk in unsupported
        )
        raise TreeError(f"{label} contains unsupported PNG chunks: {labels}")
    if chunks.count(b"IHDR") != 1 or chunks.count(b"IEND") != 1 or b"IDAT" not in chunks:
        raise TreeError(f"{label} has an invalid PNG image-data structure")
    if dimensions is None or dimensions[0] <= 0 or dimensions[1] <= 0:
        raise TreeError(f"{label} has invalid PNG dimensions")
    return dimensions


def _validate_screenshot(path: Path) -> None:
    payload = path.read_bytes()
    if len(payload) > MAX_SCREENSHOT_BYTES:
        raise TreeError(f"screenshot exceeds 500 KiB: {len(payload)} bytes")
    _validate_png_payload(payload, SCREENSHOT_PATH)


def _validate_submission_icon(path: Path) -> None:
    payload = path.read_bytes()
    dimensions = _validate_png_payload(payload, SUBMISSION_ICON_PATH)
    if dimensions != (1024, 1024):
        raise TreeError(f"{SUBMISSION_ICON_PATH} must be exactly 1024x1024, got {dimensions}")


def _validate_submission_screenshot(path: Path) -> None:
    payload = path.read_bytes()
    dimensions = _validate_png_payload(payload, SUBMISSION_SCREENSHOT_PATH)
    if dimensions != (1179, 2556):
        raise TreeError(f"{SUBMISSION_SCREENSHOT_PATH} must be exactly 1179x2556, got {dimensions}")


def _validate_evidence_screenshot(path: Path, relative: str) -> None:
    payload = path.read_bytes()
    dimensions = _validate_png_payload(payload, relative)
    if dimensions != (1020, 754):
        raise TreeError(f"{relative} must be exactly 1020x754, got {dimensions}")


def _validate_icns(path: Path) -> None:
    payload = path.read_bytes()
    if len(payload) < 16 or payload[:4] != b"icns":
        raise TreeError(f"{ICNS_PATH} does not have a valid ICNS header")
    if int.from_bytes(payload[4:8], "big") != len(payload):
        raise TreeError(f"{ICNS_PATH} has an invalid declared length")
    offset = 8
    chunks = 0
    icon_types: set[bytes] = set()
    table_of_contents: list[tuple[bytes, int]] | None = None
    image_entries: list[tuple[bytes, int]] = []
    while offset < len(payload):
        if offset + 8 > len(payload):
            raise TreeError(f"{ICNS_PATH} has a truncated chunk")
        chunk_type = payload[offset : offset + 4]
        chunk_length = int.from_bytes(payload[offset + 4 : offset + 8], "big")
        if chunk_length < 8 or offset + chunk_length > len(payload):
            raise TreeError(f"{ICNS_PATH} has an invalid chunk length")
        if chunk_type == b"TOC ":
            if table_of_contents is not None or (chunk_length - 8) % 8:
                raise TreeError(f"{ICNS_PATH} has an invalid table-of-contents chunk")
            table_of_contents = []
            toc_offset = offset + 8
            while toc_offset < offset + chunk_length:
                table_of_contents.append(
                    (
                        payload[toc_offset : toc_offset + 4],
                        int.from_bytes(payload[toc_offset + 4 : toc_offset + 8], "big"),
                    )
                )
                toc_offset += 8
        elif chunk_type in ICNS_PNG_DIMENSIONS:
            if chunk_type in icon_types:
                raise TreeError(f"{ICNS_PATH} contains a duplicate {chunk_type!r} chunk")
            icon_types.add(chunk_type)
            image_payload = payload[offset + 8 : offset + chunk_length]
            dimensions = _validate_png_payload(
                image_payload,
                f"{ICNS_PATH}:{chunk_type.decode('ascii')}",
            )
            expected = ICNS_PNG_DIMENSIONS[chunk_type]
            if dimensions != (expected, expected):
                raise TreeError(
                    f"{ICNS_PATH}:{chunk_type.decode('ascii')} has unexpected dimensions"
                )
            image_entries.append((chunk_type, chunk_length))
        else:
            raise TreeError(f"{ICNS_PATH} contains unsupported chunk type {chunk_type!r}")
        offset += chunk_length
        chunks += 1
    if (
        offset != len(payload)
        or chunks == 0
        or icon_types != set(ICNS_PNG_DIMENSIONS)
        or table_of_contents != image_entries
    ):
        raise TreeError(f"{ICNS_PATH} has an invalid chunk structure")


def _validate_ico(path: Path) -> None:
    payload = path.read_bytes()
    if len(payload) < 22 or payload[:4] != b"\x00\x00\x01\x00":
        raise TreeError(f"{ICO_PATH} does not have a valid ICO header")
    image_count = int.from_bytes(payload[4:6], "little")
    if not 1 <= image_count <= 20 or len(payload) < 6 + 16 * image_count:
        raise TreeError(f"{ICO_PATH} has an invalid image directory")
    resources: list[tuple[int, int]] = []
    for index in range(image_count):
        entry = 6 + index * 16
        size = int.from_bytes(payload[entry + 8 : entry + 12], "little")
        offset = int.from_bytes(payload[entry + 12 : entry + 16], "little")
        if size < len(PNG_SIGNATURE) or offset < 6 + 16 * image_count:
            raise TreeError(f"{ICO_PATH} has an invalid image entry")
        end = offset + size
        if end > len(payload) or payload[offset : offset + len(PNG_SIGNATURE)] != PNG_SIGNATURE:
            raise TreeError(f"{ICO_PATH} must contain bounded PNG image data")
        dimensions = _validate_png_payload(payload[offset:end], f"{ICO_PATH}:image-{index}")
        expected_width = payload[entry] or 256
        expected_height = payload[entry + 1] or 256
        if dimensions != (expected_width, expected_height):
            raise TreeError(f"{ICO_PATH}:image-{index} dimensions do not match its directory entry")
        resources.append((offset, end))
    expected_offset = 6 + 16 * image_count
    for offset, end in sorted(resources):
        if offset != expected_offset:
            raise TreeError(f"{ICO_PATH} contains overlapping or unreferenced data")
        expected_offset = end
    if expected_offset != len(payload):
        raise TreeError(f"{ICO_PATH} contains trailing or unreferenced data")


def validate_tree(root: Path, *, sdist: bool = False) -> list[str]:
    root = root.resolve()
    expected_list = read_allowlist(root)
    if sdist:
        if _is_git_worktree(root):
            raise TreeError("sdist mode requires an extracted source distribution")
        if SDIST_METADATA_PATH in expected_list:
            raise TreeError(f"{SDIST_METADATA_PATH} must remain generated distribution metadata")
        expected_list = [*expected_list, SDIST_METADATA_PATH]
    expected = set(expected_list)

    if _is_git_worktree(root):
        actual, submodules = _git_files_and_submodules(root)
        if submodules:
            raise TreeError(f"submodules are forbidden: {', '.join(sorted(submodules))}")
    else:
        actual = _filesystem_files(root)

    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if unexpected:
            details.append("unexpected: " + ", ".join(unexpected))
        raise TreeError("public tree differs from allow-list; " + "; ".join(details))

    for relative in expected_list:
        path = root / relative
        if path.is_symlink():
            raise TreeError(f"symlinks are forbidden: {relative}")
        if not path.is_file():
            raise TreeError(f"not a regular file: {relative}")
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise TreeError(f"file exceeds 1 MiB: {relative} ({size} bytes)")
        if relative == SCREENSHOT_PATH:
            _validate_screenshot(path)
        elif relative == SUBMISSION_ICON_PATH:
            _validate_submission_icon(path)
        elif relative == SUBMISSION_SCREENSHOT_PATH:
            _validate_submission_screenshot(path)
        elif relative in EVIDENCE_SCREENSHOT_PATHS:
            _validate_evidence_screenshot(path, relative)
        elif relative == ICNS_PATH:
            _validate_icns(path)
        elif relative == ICO_PATH:
            _validate_ico(path)
        elif _looks_binary(path):
            raise TreeError(f"binary files are forbidden: {relative}")
        else:
            try:
                path.read_text(encoding="utf-8")
            except UnicodeDecodeError as error:
                raise TreeError(f"non-UTF-8 text file is forbidden: {relative}") from error
        if path.read_bytes().startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise TreeError(f"Git LFS pointers are forbidden: {relative}")

    return expected_list


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--sdist",
        action="store_true",
        help="require and validate the single generated PKG-INFO file in an extracted sdist",
    )
    arguments = parser.parse_args(argv)
    try:
        files = validate_tree(arguments.root, sdist=arguments.sdist)
    except (OSError, TreeError, subprocess.CalledProcessError, UnicodeDecodeError) as error:
        print(f"PUBLIC_TREE_FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PUBLIC_TREE_OK: {len(files)} explicitly allowed files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
