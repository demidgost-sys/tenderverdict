#!/usr/bin/env python3
"""Build a self-contained, ad-hoc-signed TenderVerdict Next Gen macOS app."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import plistlib
import shutil
import subprocess
import sys
import tomllib
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "macos" / "TenderVerdictNextGen"
CORE_SPEC = ROOT / "packaging" / "TenderVerdictNextGenCore.spec"
APP_NAME = "TenderVerdictNextGen"
BUNDLE_NAME = f"{APP_NAME}.app"
BUNDLE_IDENTIFIER = "io.github.demidgostsys.tenderverdict.nextgen"


class BuildError(RuntimeError):
    """A reproducible Next Gen build step failed."""


def _run(arguments: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> None:
    subprocess.run(arguments, cwd=cwd, env=env, check=True)


def _capture(arguments: list[str], *, cwd: Path = ROOT) -> str:
    return subprocess.run(
        arguments,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _safe_remove(path: Path, expected_parent: Path) -> None:
    if path.parent.resolve() != expected_parent.resolve():
        raise BuildError(f"refusing to replace path outside output directory: {path}")
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def _copy_swift_resources(bin_path: Path, resources: Path) -> None:
    for bundle in sorted(bin_path.glob("*.bundle")):
        shutil.copytree(bundle, resources / bundle.name)


def _write_info_plist(path: Path, bundle_version: str, project_version: str) -> None:
    payload = {
        "CFBundleDisplayName": "TenderVerdict Next Gen",
        "CFBundleExecutable": APP_NAME,
        "CFBundleIconFile": "tenderverdict-icon.icns",
        "CFBundleIdentifier": BUNDLE_IDENTIFIER,
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": "TenderVerdict Next Gen",
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": bundle_version,
        "CFBundleVersion": bundle_version,
        "CFBundleGetInfoString": f"TenderVerdict Next Gen {project_version} evaluation build",
        "LSApplicationCategoryType": "public.app-category.business",
        "LSMinimumSystemVersion": "13.0",
        "NSHighResolutionCapable": True,
        "NSHumanReadableCopyright": "Copyright 2026 Demid Valiullin",
        "NSSupportsAutomaticGraphicsSwitching": True,
    }
    with path.open("wb") as handle:
        plistlib.dump(payload, handle, sort_keys=True)


def _write_build_info(path: Path, version: str, configuration: str) -> None:
    revision = _capture(["git", "rev-parse", "HEAD"])
    status = _capture(["git", "status", "--porcelain"])
    lines = [
        "product=TenderVerdict Next Gen",
        f"version={version}",
        f"source_revision={revision}",
        f"source_dirty={str(bool(status)).lower()}",
        f"build_configuration={configuration}",
        f"test_store_enabled={str(configuration == 'debug').lower()}",
        "revenuecat_sdk=5.83.0",
        "entitlement=supplier_profiles_plus",
        "qualification_runtime=embedded-offline-python",
        "workspace_normalization=embedded-offline-python",
        "notice_import_preview=embedded-offline-python",
        "signature=adhoc",
        "notarized=false",
        "api_key_included=false",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def _verify_embedded_core(executable: Path) -> None:
    environment = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "LANG": os.environ.get("LANG", "en_US.UTF-8"),
    }
    examples = ROOT / "examples" / "synthetic"
    commands = {
        "workspace": [
            str(executable),
            "normalize-workspace",
            "--workspace",
            str(examples / "portfolio-workspace.json"),
        ],
        "notices": [
            str(executable),
            "inspect-notices",
            "--notices",
            str(examples / "notices.json"),
        ],
    }
    outputs: dict[str, bytes] = {}
    for label, command in commands.items():
        first = subprocess.run(
            command,
            cwd=Path("/"),
            env=environment,
            check=True,
            capture_output=True,
        ).stdout
        second = subprocess.run(
            command,
            cwd=Path("/"),
            env=environment,
            check=True,
            capture_output=True,
        ).stdout
        if first != second:
            raise BuildError(f"embedded {label} command is not byte-deterministic")
        outputs[label] = first

    workspace = json.loads(outputs["workspace"])
    if workspace.get("schema_version") != 1 or len(workspace.get("profiles", [])) != 3:
        raise BuildError("embedded workspace normalization returned an invalid contract")

    notices = json.loads(outputs["notices"])
    if (
        notices.get("schema_version") != 1
        or notices.get("kind") != "notice_import_preview"
        or notices.get("notice_count") != 3
        or len(notices.get("preview", [])) != 3
    ):
        raise BuildError("embedded notice inspection returned an invalid contract")


def _build(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    if sys.platform != "darwin":
        raise BuildError("the Next Gen application bundle can only be built on macOS")

    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project_version = metadata["project"]["version"]
    bundle_version = project_version.split("a", 1)[0]
    output_dir = args.output_dir.resolve()
    build_root = args.build_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    build_root.mkdir(parents=True, exist_ok=True)

    final_app = output_dir / BUNDLE_NAME
    final_zip = output_dir / f"{APP_NAME}-macos.zip"
    final_checksum = output_dir / f"{APP_NAME}-macos.sha256"
    existing = [path for path in (final_app, final_zip, final_checksum) if path.exists()]
    if existing and not args.replace:
        labels = ", ".join(path.name for path in existing)
        raise BuildError(f"output already exists ({labels}); pass --replace to rebuild it")

    stage = build_root / f"stage-{uuid.uuid4().hex}"
    pyinstaller_dist = build_root / f"pyinstaller-dist-{uuid.uuid4().hex}"
    pyinstaller_work = build_root / f"pyinstaller-work-{uuid.uuid4().hex}"
    stage.mkdir()
    try:
        swift_command = [
            "swift",
            "build",
            "-c",
            args.configuration,
            "--package-path",
            str(PACKAGE),
        ]
        if args.swift_scratch_path is not None:
            swift_command[4:4] = ["--scratch-path", str(args.swift_scratch_path.resolve())]
        _run(swift_command)

        show_bin_command = [
            "swift",
            "build",
            "-c",
            args.configuration,
            "--show-bin-path",
            "--package-path",
            str(PACKAGE),
        ]
        if args.swift_scratch_path is not None:
            show_bin_command[4:4] = [
                "--scratch-path",
                str(args.swift_scratch_path.resolve()),
            ]
        swift_bin_path = Path(_capture(show_bin_command))
        swift_executable = swift_bin_path / APP_NAME
        if not swift_executable.is_file():
            raise BuildError(f"Swift executable is missing: {swift_executable}")
        swift_checks = swift_bin_path / f"{APP_NAME}Checks"
        if not swift_checks.is_file():
            raise BuildError(f"Swift contract checks are missing: {swift_checks}")
        check_environment = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": os.environ.get("LANG", "en_US.UTF-8"),
            "TENDERVERDICT_WORKTREE": str(ROOT),
        }
        _run([str(swift_checks)], env=check_environment)

        pyinstaller_environment = os.environ.copy()
        pyinstaller_environment["PYINSTALLER_CONFIG_DIR"] = str(build_root / "pyinstaller-cache")
        _run(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--noconfirm",
                "--clean",
                "--distpath",
                str(pyinstaller_dist),
                "--workpath",
                str(pyinstaller_work),
                str(CORE_SPEC),
            ],
            env=pyinstaller_environment,
        )
        core = pyinstaller_dist / "TenderVerdictCore"
        core_executable = core / "TenderVerdictCore"
        if not core_executable.is_file():
            raise BuildError("PyInstaller did not produce the embedded core")
        _verify_embedded_core(core_executable)

        app = stage / BUNDLE_NAME
        contents = app / "Contents"
        macos = contents / "MacOS"
        resources = contents / "Resources"
        macos.mkdir(parents=True)
        resources.mkdir()
        shutil.copy2(swift_executable, macos / APP_NAME)
        shutil.copytree(core, resources / "TenderVerdictCore")
        shutil.copytree(ROOT / "examples" / "synthetic", resources / "Examples")
        shutil.copy2(ROOT / "packaging" / "tenderverdict-icon.icns", resources)
        shutil.copy2(ROOT / "LICENSE", resources)
        shutil.copy2(ROOT / "NOTICE", resources)
        shutil.copy2(ROOT / "packaging" / "THIRD_PARTY_NOTICES.md", resources)
        _copy_swift_resources(swift_bin_path, resources)
        _write_info_plist(contents / "Info.plist", bundle_version, project_version)
        (contents / "PkgInfo").write_bytes(b"APPL????")
        _write_build_info(resources / "BUILD_INFO.txt", project_version, args.configuration)

        _run(["codesign", "--force", "--deep", "--sign", "-", str(app)])
        _run(["codesign", "--verify", "--deep", "--strict", "--verbose=2", str(app)])
        smoke_environment = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": os.environ.get("LANG", "en_US.UTF-8"),
        }
        _run([str(macos / APP_NAME), "--smoke-test"], cwd=Path("/"), env=smoke_environment)

        for path in existing:
            _safe_remove(path, output_dir)
        shutil.move(str(app), final_app)
        _run(
            [
                "ditto",
                "-c",
                "-k",
                "--norsrc",
                "--keepParent",
                str(final_app),
                str(final_zip),
            ]
        )
        digest = hashlib.sha256(final_zip.read_bytes()).hexdigest()
        final_checksum.write_text(f"{digest} *{final_zip.name}\n", encoding="ascii")
        return final_app, final_zip, final_checksum
    finally:
        shutil.rmtree(stage, ignore_errors=True)
        shutil.rmtree(pyinstaller_dist, ignore_errors=True)
        shutil.rmtree(pyinstaller_work, ignore_errors=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--configuration",
        choices=("debug", "release"),
        default="release",
        help="Swift build configuration; Test Store transactions require debug",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "dist" / "next-gen",
        help="destination for the .app, zip, and checksum",
    )
    parser.add_argument(
        "--build-root",
        type=Path,
        default=ROOT / "build" / "next-gen",
        help="regenerable PyInstaller and staging directory",
    )
    parser.add_argument(
        "--swift-scratch-path",
        type=Path,
        help="optional SwiftPM scratch directory",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="replace only the exact three generated outputs",
    )
    return parser


def main() -> int:
    try:
        app, archive, checksum = _build(build_parser().parse_args())
    except (BuildError, OSError, subprocess.CalledProcessError) as exc:
        print(f"NEXT_GEN_BUILD_FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"NEXT_GEN_BUILD_OK app={app} archive={archive} checksum={checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
