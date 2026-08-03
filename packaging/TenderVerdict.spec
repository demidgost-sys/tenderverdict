# PyInstaller specification for native, one-directory desktop previews.

import sys
import tomllib
from pathlib import Path


ROOT = Path(SPECPATH).parent
PROJECT_VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"][
    "version"
]
MACOS_BUNDLE_VERSION = PROJECT_VERSION.split("a", 1)[0]
ICON_PATH = ROOT / "packaging" / (
    "tenderverdict-icon.ico" if sys.platform == "win32" else "tenderverdict-icon.icns"
)

analysis = Analysis(
    [str(ROOT / "tools" / "desktop_launcher.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=[
        (str(ROOT / "LICENSE"), "licenses"),
        (str(ROOT / "NOTICE"), "licenses"),
        (str(ROOT / "packaging" / "THIRD_PARTY_NOTICES.md"), "licenses"),
        (str(ROOT / "src" / "tenderverdict" / "data" / "cpv_codes.txt"), "tenderverdict/data"),
        (
            str(ROOT / "src" / "tenderverdict" / "data" / "country_codes.txt"),
            "tenderverdict/data",
        ),
        (
            str(ROOT / "src" / "tenderverdict" / "data" / "VOCABULARY_SOURCES.json"),
            "tenderverdict/data",
        ),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tenderverdict.cli", "tenderverdict.ted"],
    noarchive=False,
    optimize=0,
)

python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="TenderVerdict",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_PATH),
)

collected = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="TenderVerdict",
)

if sys.platform == "darwin":
    application = BUNDLE(
        collected,
        name="TenderVerdict.app",
        icon=str(ICON_PATH),
        bundle_identifier="io.github.demidgostsys.tenderverdict",
        info_plist={
            "CFBundleShortVersionString": MACOS_BUNDLE_VERSION,
            "CFBundleVersion": MACOS_BUNDLE_VERSION,
            "NSHumanReadableCopyright": "Copyright 2026 Demid Valiullin",
        },
    )
