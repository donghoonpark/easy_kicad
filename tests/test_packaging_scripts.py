from __future__ import annotations

from pathlib import Path

import pytest

from scripts.build_macos_dmg import build_macos_dmg, dmg_output_path
from scripts.build_windows_installer import build_windows_installer, installer_output_path


def test_installer_output_path_uses_setup_suffix(tmp_path: Path):
    output_path = installer_output_path(tmp_path, version="0.4.0")

    assert output_path == tmp_path / "easy_kicad-0.4.0-windows-x64-setup.exe"


def test_build_windows_installer_invokes_makensis(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dist_dir = tmp_path / "dist" / "easy_kicad"
    dist_dir.mkdir(parents=True)
    (dist_dir / "easy_kicad.exe").write_text("binary", encoding="utf-8")
    nsis_script = tmp_path / "easy_kicad_installer.nsi"
    nsis_script.write_text("OutFile installer.exe", encoding="utf-8")
    icon_file = tmp_path / "easy_kicad.ico"
    icon_file.write_text("icon", encoding="utf-8")

    calls: dict[str, object] = {}

    monkeypatch.setattr("scripts.build_windows_installer.shutil.which", lambda name: f"/usr/bin/{name}")

    def fake_run(command: list[str], check: bool):
        calls["command"] = command
        calls["check"] = check

    monkeypatch.setattr("scripts.build_windows_installer.subprocess.run", fake_run)

    output_path = build_windows_installer(
        dist_dir,
        tmp_path / "release",
        version="0.4.0",
        nsis_script=nsis_script,
        icon_file=icon_file,
    )

    assert output_path == tmp_path / "release" / "easy_kicad-0.4.0-windows-x64-setup.exe"
    assert calls["check"] is True
    command = calls["command"]
    assert command[0] == "makensis"
    assert f"/DDIST_DIR={dist_dir.resolve()}" in command
    assert f"/DOUTPUT_FILE={output_path.resolve()}" in command
    assert f"/DICON_FILE={icon_file.resolve()}" in command
    assert command[-1] == str(nsis_script.resolve())


def test_build_windows_installer_requires_existing_bundle_raises(tmp_path: Path):
    nsis_script = tmp_path / "easy_kicad_installer.nsi"
    nsis_script.write_text("OutFile installer.exe", encoding="utf-8")
    icon_file = tmp_path / "easy_kicad.ico"
    icon_file.write_text("icon", encoding="utf-8")

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("scripts.build_windows_installer.shutil.which", lambda name: f"/usr/bin/{name}")
        with pytest.raises(FileNotFoundError):
            build_windows_installer(
                tmp_path / "missing",
                tmp_path / "release",
                version="0.4.0",
                nsis_script=nsis_script,
                icon_file=icon_file,
                makensis_bin="makensis",
            )


def test_dmg_output_path_uses_platform_tag(tmp_path: Path):
    output_path = dmg_output_path(tmp_path, version="0.4.0", machine="arm64")

    assert output_path == tmp_path / "easy_kicad-0.4.0-macos-arm64.dmg"


def test_build_macos_dmg_invokes_hdiutil(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    app_bundle = tmp_path / "dist" / "easy_kicad.app"
    binary_path = app_bundle / "Contents" / "MacOS"
    binary_path.mkdir(parents=True)
    (binary_path / "easy_kicad").write_text("binary", encoding="utf-8")

    calls: dict[str, object] = {}

    monkeypatch.setattr("scripts.build_macos_dmg.shutil.which", lambda name: f"/usr/bin/{name}")

    def fake_run(command: list[str], check: bool):
        calls["command"] = command
        calls["check"] = check
        staging_dir = Path(command[command.index("-srcfolder") + 1])
        assert (staging_dir / "easy_kicad.app").exists()
        assert (staging_dir / "Applications").is_symlink()

    monkeypatch.setattr("scripts.build_macos_dmg.subprocess.run", fake_run)

    output_path = build_macos_dmg(
        app_bundle,
        tmp_path / "release",
        version="0.4.0",
        machine="arm64",
    )

    assert output_path == tmp_path / "release" / "easy_kicad-0.4.0-macos-arm64.dmg"
    assert calls["check"] is True
    command = calls["command"]
    assert command[0] == "hdiutil"
    assert "-srcfolder" in command
    assert command[-1] == str(output_path)


def test_build_macos_dmg_requires_existing_app_bundle(tmp_path: Path):
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr("scripts.build_macos_dmg.shutil.which", lambda name: f"/usr/bin/{name}")
        with pytest.raises(FileNotFoundError):
            build_macos_dmg(tmp_path / "missing.app", tmp_path / "release", version="0.4.0")
