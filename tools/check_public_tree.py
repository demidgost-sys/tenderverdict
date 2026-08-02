#!/usr/bin/env python3
"""Fail closed when the candidate tree differs from its explicit allow-list."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

MAX_FILE_BYTES = 1024 * 1024
MAX_SCREENSHOT_BYTES = 500 * 1024
SCREENSHOT_PATH = "demo/screenshot.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FORBIDDEN_PNG_CHUNKS = {b"eXIf", b"tEXt", b"iTXt", b"zTXt"}
ALLOWLIST_NAME = "PUBLIC_TREE_ALLOWLIST.txt"
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


def _validate_screenshot(path: Path) -> None:
    payload = path.read_bytes()
    if len(payload) > MAX_SCREENSHOT_BYTES:
        raise TreeError(f"screenshot exceeds 500 KiB: {len(payload)} bytes")
    if not payload.startswith(PNG_SIGNATURE):
        raise TreeError("demo/screenshot.png does not have a valid PNG signature")

    offset = len(PNG_SIGNATURE)
    chunks: list[bytes] = []
    while offset < len(payload):
        if offset + 12 > len(payload):
            raise TreeError("demo/screenshot.png has a truncated PNG chunk")
        length = int.from_bytes(payload[offset : offset + 4], "big")
        chunk_type = payload[offset + 4 : offset + 8]
        end = offset + 12 + length
        if end > len(payload):
            raise TreeError("demo/screenshot.png has an invalid PNG chunk length")
        chunks.append(chunk_type)
        offset = end
        if chunk_type == b"IEND":
            break

    if not chunks or chunks[0] != b"IHDR" or chunks[-1] != b"IEND" or offset != len(payload):
        raise TreeError("demo/screenshot.png has an invalid PNG chunk structure")
    forbidden = sorted(set(chunks) & FORBIDDEN_PNG_CHUNKS)
    if forbidden:
        labels = ", ".join(chunk.decode("ascii") for chunk in forbidden)
        raise TreeError(f"demo/screenshot.png contains metadata chunks: {labels}")


def validate_tree(root: Path) -> list[str]:
    root = root.resolve()
    expected_list = read_allowlist(root)
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
    arguments = parser.parse_args(argv)
    try:
        files = validate_tree(arguments.root)
    except (OSError, TreeError, subprocess.CalledProcessError, UnicodeDecodeError) as error:
        print(f"PUBLIC_TREE_FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PUBLIC_TREE_OK: {len(files)} explicitly allowed files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
