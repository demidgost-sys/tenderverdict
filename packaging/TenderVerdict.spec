# PyInstaller specification for native, one-directory desktop previews.

import sys
from pathlib import Path


ROOT = Path(SPECPATH).parent

analysis = Analysis(
    [str(ROOT / "tools" / "desktop_launcher.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=[
        (str(ROOT / "LICENSE"), "licenses"),
        (str(ROOT / "NOTICE"), "licenses"),
        (str(ROOT / "packaging" / "THIRD_PARTY_NOTICES.md"), "licenses"),
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
        icon=None,
        bundle_identifier="io.github.demidgostsys.tenderverdict",
    )
