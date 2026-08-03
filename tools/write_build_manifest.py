#!/usr/bin/env python3
"""Write deterministic provenance metadata next to a desktop CI artifact."""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import re
import sys
import tkinter as tk
from pathlib import Path

import PyInstaller

from tenderverdict import __version__
from tenderverdict.output import write_text_atomically

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "macos-arm64": ("Darwin", {"arm64", "aarch64"}, "adhoc"),
    "macos-x64": ("Darwin", {"x86_64", "amd64"}, "adhoc"),
    "windows-x64": ("Windows", {"amd64", "x86_64"}, "not-signed"),
}
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_environment(target: str, signature_state: str, *, ci: bool) -> dict[str, str]:
    expected_system, expected_machines, expected_signature = TARGETS[target]
    actual_system = platform.system()
    actual_machine = platform.machine().casefold()
    if actual_system != expected_system or actual_machine not in expected_machines:
        raise ValueError(f"target {target} does not match {actual_system}/{platform.machine()}")
    if signature_state != expected_signature:
        raise ValueError(f"target {target} requires signature state {expected_signature}")

    commit = os.environ.get("GITHUB_SHA", "local")
    image_os = os.environ.get("ImageOS", "local")
    image_version = os.environ.get("ImageVersion", "local")
    if ci:
        if os.environ.get("GITHUB_ACTIONS") != "true":
            raise ValueError("--ci requires the GitHub Actions environment")
        if not COMMIT_RE.fullmatch(commit):
            raise ValueError("GITHUB_SHA must be a full lowercase 40-character commit SHA")
        if image_os == "local" or image_version == "local":
            raise ValueError("hosted-runner ImageOS and ImageVersion are required in CI")
    return {"commit": commit, "image_os": image_os, "image_version": image_version}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=tuple(TARGETS))
    parser.add_argument(
        "--signature-state",
        required=True,
        choices=("adhoc", "not-signed"),
    )
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        provenance = _validate_environment(args.target, args.signature_state, ci=args.ci)
    except ValueError as exc:
        print(f"BUILD_MANIFEST_FAIL: {exc}", file=sys.stderr)
        return 1

    requirements = ROOT / "requirements-desktop-build.txt"
    lines = [
        "TenderVerdict desktop developer artifact",
        f"target={args.target}",
        f"commit={provenance['commit']}",
        f"tenderverdict={__version__}",
        f"python={platform.python_version()}",
        f"python_implementation={platform.python_implementation()}",
        f"architecture={platform.machine()}",
        f"operating_system={platform.system()} {platform.release()}",
        f"tcl={tk.TclVersion}",
        f"tk={tk.TkVersion}",
        f"pyinstaller={PyInstaller.__version__}",
        f"build_requirements_sha256={_sha256(requirements)}",
        f"runner_image={provenance['image_os']}",
        f"runner_image_version={provenance['image_version']}",
        f"signature_state={args.signature_state}",
        "developer_id_signed=false",
        "notarized=false",
        "public_release=false",
        "",
    ]
    try:
        write_text_atomically(args.output, "\n".join(lines))
    except OSError as exc:
        print(f"BUILD_MANIFEST_FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"BUILD_MANIFEST_OK: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
