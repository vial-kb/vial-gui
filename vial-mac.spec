# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

REPO = Path(SPECPATH)
SRC = REPO / "src" / "main" / "python"
RES = REPO / "src" / "main" / "resources" / "base"

a = Analysis(
    [str(SRC / "main.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=[(str(p), ".") for p in RES.iterdir()],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="Vial",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    target_arch=None,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False, name="Vial",
)
app = BUNDLE(
    coll,
    name="Vial.app",
    icon=str(REPO / "src" / "main" / "icons" / "Icon.icns"),
    bundle_identifier="today.vial",
    info_plist={
        "CFBundleShortVersionString": "0.7.5",
        "CFBundleVersion": "0.7.5",
        "NSHighResolutionCapable": True,
        "CFBundleIconFile": "Icon.icns",
    },
)
