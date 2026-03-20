from __future__ import annotations

from easy_kicad.core.settings import SettingsStore
from easy_kicad.schemas.settings import AppSettings


def test_settings_store_creates_default_file(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.json")
    settings = store.load()
    assert settings.library_name == "easy_kicad"
    assert (tmp_path / "settings.json").exists()


def test_settings_store_persists_changes(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.json")
    store.save(AppSettings(library_root=str(tmp_path), overwrite=True))
    loaded = store.load()
    assert loaded.overwrite is True
