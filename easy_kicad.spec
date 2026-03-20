# -*- mode: python ; coding: utf-8 -*-

import platform

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files("easy_kicad", includes=["web/**/*"])
hiddenimports = collect_submodules("webview.platforms")
excludes = ["PyQt5", "PySide2", "PySide6", "tkinter"]

if platform.system() != "Linux":
    excludes.append("PyQt6")


a = Analysis(
    ["src/easy_kicad/main.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="easy_kicad",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="easy_kicad",
)
