from __future__ import annotations

import runpy
import sys
from importlib import import_module
from pathlib import Path

import pytest

desktop_main = import_module("easy_kicad.main")


def test_main_serve_only_invokes_uvicorn(monkeypatch: pytest.MonkeyPatch):
    calls: dict[str, object] = {}

    def fake_run(app, *, host: str, port: int, log_level: str):
        calls["app"] = app
        calls["host"] = host
        calls["port"] = port
        calls["log_level"] = log_level

    monkeypatch.setattr(desktop_main.uvicorn, "run", fake_run)

    assert desktop_main.main(["--serve-only", "--port", "8765"]) == 0
    assert calls["host"] == "127.0.0.1"
    assert calls["port"] == 8765
    assert calls["log_level"] == "info"


def test_main_module_entrypoint_runs_main(monkeypatch: pytest.MonkeyPatch):
    calls: dict[str, object] = {}

    def fake_run(app, *, host: str, port: int, log_level: str):
        calls["app"] = app
        calls["host"] = host
        calls["port"] = port
        calls["log_level"] = log_level

    monkeypatch.setattr(desktop_main.uvicorn, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["main.py", "--serve-only", "--port", "8766"])

    with pytest.raises(SystemExit) as exc:
        runpy.run_path(
            str(Path(__file__).resolve().parents[1] / "src" / "easy_kicad" / "main.py"),
            run_name="__main__",
        )

    assert exc.value.code == 0
    assert calls["host"] == "127.0.0.1"
    assert calls["port"] == 8766
    assert calls["log_level"] == "info"
