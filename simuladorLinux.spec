# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['interfaz_gui.py'],
    pathex=[],
    binaries=[('/usr/lib/x86_64-linux-gnu/libtk8.6.so', '.'), ('/usr/lib/x86_64-linux-gnu/libtcl8.6.so', '.')],
    datas=[],
    hiddenimports=['PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='simuladorLinux',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
