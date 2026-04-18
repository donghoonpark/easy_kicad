from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

PACKAGE_NAME = "easy-kicad"
APP_NAME = "easy_kicad"
APP_TITLE = "easy_kicad"
APP_TAGLINE = "LCSC to KiCad importer"
APP_DESCRIPTION = "Desktop GUI for importing LCSC parts into KiCad with live previews"


def package_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.1.2"
