from __future__ import annotations

from pathlib import Path

import pytest

from easy_kicad.schemas.settings import AppSettings
from easy_kicad.services.import_service import import_part_bundle
from tests.helpers import make_bundle


def test_import_part_bundle_creates_kicad_artifacts(tmp_path: Path):
    settings = AppSettings(
        library_root=str(tmp_path),
        library_name="easy_kicad",
        overwrite=False,
    )
    bundle = make_bundle()

    result = import_part_bundle(bundle, settings)

    assert Path(result.symbol_library).exists()
    assert Path(result.footprint_file).exists()
    assert Path(result.model_directory, "TEST_0603.wrl").exists()
    assert Path(result.model_directory, "TEST_0603.step").exists()


def test_import_part_bundle_requires_overwrite_for_existing_files(tmp_path: Path):
    settings = AppSettings(
        library_root=str(tmp_path),
        library_name="easy_kicad",
        overwrite=False,
    )
    bundle = make_bundle()

    import_part_bundle(bundle, settings)
    with pytest.raises(FileExistsError):
        import_part_bundle(bundle, settings)

    overwrite_settings = settings.model_copy(update={"overwrite": True})
    result = import_part_bundle(bundle, overwrite_settings)
    assert result.success is True
