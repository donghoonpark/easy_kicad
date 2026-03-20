from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from platformdirs import user_config_path

from easy_kicad.schemas.settings import AppSettings


def default_settings_path() -> Path:
    override = os.getenv("EASY_KICAD_CONFIG_PATH")
    if override:
        return Path(override)
    return user_config_path("easy_kicad", ensure_exists=False) / "settings.json"


class SettingsStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or default_settings_path()

    def load(self) -> AppSettings:
        if not self.path.exists():
            return self.save(AppSettings())

        raw_data = json.loads(self.path.read_text(encoding="utf-8"))
        settings = AppSettings.model_validate(raw_data)
        return settings

    def save(self, settings: AppSettings) -> AppSettings:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            settings.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return settings
