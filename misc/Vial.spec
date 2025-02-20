# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../src/main/python/main.py'],
    pathex=[],
    binaries=[],
    datas=[('../src/main/resources/base/qmk_settings.json', 'resources/base'), ('../src/build/settings/base.json', 'resources/settings'), ('../src/build/settings/linux.json', 'resources/settings'), ('../src/build/settings/mac.json', 'resources/settings')],
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
    name='Vial',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['../src/main/icons/Icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Vial',
)
app = BUNDLE(
    coll,
    name='Vial.app',
    icon='../src/main/icons/Icon.ico',
    bundle_identifier=None
)
