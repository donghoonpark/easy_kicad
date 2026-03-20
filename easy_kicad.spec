# -*- mode: python ; coding: utf-8 -*-

import os
import platform
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

BUILD_VARIANT = os.environ.get("EASY_KICAD_BUILD_VARIANT", "release").strip().lower()
APP_BUNDLE_NAME = "easy_kicad_debug" if BUILD_VARIANT == "debug" else "easy_kicad"
ICON_DIR = Path("docs") / "assets" / "icons"

datas = collect_data_files("easy_kicad", includes=["web/**/*"])
hiddenimports = collect_submodules("webview.platforms")
excludes = ["PyQt5", "PySide2", "PySide6", "tkinter"]

if platform.system() != "Linux":
    excludes.append("PyQt6")

if platform.system() == "Windows":
    icon_path = ICON_DIR / "easy_kicad.ico"
elif platform.system() == "Darwin":
    icon_path = ICON_DIR / "easy_kicad.icns"
else:
    icon_path = None

icon = str(icon_path) if icon_path is not None and icon_path.exists() else None


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
    name=APP_BUNDLE_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=BUILD_VARIANT == "debug",
    icon=icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_BUNDLE_NAME,
)
