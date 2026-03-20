from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path

import pytest

from easy_kicad.core.release import (
    archive_suffix,
    artifact_stem,
    create_release_archive,
    normalized_machine,
    platform_tag,
)


@pytest.mark.parametrize(
    ("raw_machine", "expected"),
    [
        ("x86_64", "x64"),
        ("AMD64", "x64"),
        ("arm64", "arm64"),
        ("aarch64", "arm64"),
        ("riscv64", "riscv64"),
    ],
)
def test_normalized_machine_aliases(raw_machine: str, expected: str):
    assert normalized_machine(raw_machine) == expected


@pytest.mark.parametrize(
    ("system", "machine", "expected"),
    [
        ("Darwin", "arm64", "macos-arm64"),
        ("Linux", "x86_64", "linux-x64"),
        ("Windows", "AMD64", "windows-x64"),
    ],
)
def test_platform_tag(system: str, machine: str, expected: str):
    assert platform_tag(system, machine) == expected


def test_archive_suffix():
    assert archive_suffix("Windows") == ".zip"
    assert archive_suffix("Darwin") == ".tar.gz"


def test_artifact_stem_uses_platform_tag():
    assert artifact_stem("0.4.0", system="Linux", machine="x86_64") == "easy_kicad-0.4.0-linux-x64"


def test_create_release_archive_for_zip(tmp_path: Path):
    bundle_dir = tmp_path / "dist" / "easy_kicad"
    bundle_dir.mkdir(parents=True)
    (bundle_dir / "app.txt").write_text("desktop bundle", encoding="utf-8")

    archive_path = create_release_archive(
        bundle_dir,
        tmp_path / "release",
        version="0.4.0",
        system="Windows",
        machine="AMD64",
    )

    assert archive_path.name == "easy_kicad-0.4.0-windows-x64.zip"
    with zipfile.ZipFile(archive_path) as archive:
        assert "easy_kicad/app.txt" in archive.namelist()


def test_create_release_archive_for_tar_gz(tmp_path: Path):
    bundle_dir = tmp_path / "dist" / "easy_kicad"
    bundle_dir.mkdir(parents=True)
    (bundle_dir / "app.txt").write_text("desktop bundle", encoding="utf-8")

    archive_path = create_release_archive(
        bundle_dir,
        tmp_path / "release",
        version="0.4.0",
        system="Darwin",
        machine="arm64",
    )

    assert archive_path.name == "easy_kicad-0.4.0-macos-arm64.tar.gz"
    with tarfile.open(archive_path, "r:gz") as archive:
        assert "easy_kicad/app.txt" in archive.getnames()


def test_create_release_archive_requires_bundle_dir(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        create_release_archive(tmp_path / "missing", tmp_path / "release", version="0.1.0")
