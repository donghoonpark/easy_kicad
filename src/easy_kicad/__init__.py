from easy_kicad.metadata import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_TAGLINE,
    APP_TITLE,
    PACKAGE_NAME,
    package_version,
)
from easy_kicad.main import main

__version__ = package_version()

__all__ = [
    "APP_DESCRIPTION",
    "APP_NAME",
    "APP_TAGLINE",
    "APP_TITLE",
    "PACKAGE_NAME",
    "__version__",
    "main",
]
