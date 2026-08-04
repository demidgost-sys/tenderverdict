# PyInstaller specification for the offline core embedded in the Next Gen app.

from pathlib import Path


ROOT = Path(SPECPATH).parent

analysis = Analysis(
    [str(ROOT / "tools" / "next_gen_core_launcher.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=[
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
    excludes=[
        "tenderverdict.cli",
        "tenderverdict.desktop",
        "tenderverdict.ted",
        "tkinter",
    ],
    noarchive=False,
    optimize=0,
)

python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="TenderVerdictCore",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
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
    name="TenderVerdictCore",
)
