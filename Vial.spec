# -*- mode: python ; coding: utf-8 -*-
import json
import os

ROOT = os.path.abspath(os.getcwd())

SETTINGS_DIR = os.path.join(ROOT, "src", "build", "settings")
with open(os.path.join(SETTINGS_DIR, "base.json")) as f:
    base = json.load(f)
with open(os.path.join(SETTINGS_DIR, "mac.json")) as f:
    mac = json.load(f)

build_settings = {
    "app_name": base["app_name"],
    "author": base["author"],
    "version": base["version"],
}
os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
build_settings_path = os.path.join(ROOT, "build", "build_settings.json")
with open(build_settings_path, "w") as f:
    json.dump(build_settings, f)

datas = [
    (build_settings_path, "."),
    (os.path.join(ROOT, "src", "main", "resources", "base", "qmk_settings.json"), "."),
]

a = Analysis(
    [os.path.join(ROOT, "src", "main", "python", "main.py")],
    pathex=[os.path.join(ROOT, "src", "main", "python")],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=base["app_name"],
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    target_arch="arm64",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=base["app_name"],
)
app = BUNDLE(
    coll,
    name=base["app_name"] + ".app",
    icon=os.path.join(ROOT, "build", "icon.icns"),
    bundle_identifier=mac["mac_bundle_identifier"],
    version=base["version"],
    info_plist={
        "NSHighResolutionCapable": True,
        "CFBundleShortVersionString": base["version"],
        "LSMinimumSystemVersion": "11.0",
    },
)
