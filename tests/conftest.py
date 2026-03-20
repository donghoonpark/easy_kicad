from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from easy_kicad.app import create_app
from easy_kicad.core.settings import SettingsStore
from easy_kicad.schemas.settings import AppSettings
from tests.helpers import FakePartService


@pytest.fixture
def temp_settings(tmp_path) -> AppSettings:
    return AppSettings(library_root=str(tmp_path), library_name="easy_kicad")


@pytest.fixture
def settings_store(tmp_path, temp_settings: AppSettings) -> SettingsStore:
    store = SettingsStore(path=tmp_path / "settings.json")
    store.save(temp_settings)
    return store


@pytest.fixture
def client(settings_store: SettingsStore) -> TestClient:
    app = create_app(settings_store=settings_store, part_service=FakePartService())
    return TestClient(app)
