from __future__ import annotations

import runpy
import sys
from types import SimpleNamespace
from importlib import import_module
from pathlib import Path

import pytest

desktop_main = import_module("easy_kicad.main")


def test_preferred_webview_gui_prefers_qt_on_windows_and_linux():
    assert desktop_main._preferred_webview_gui("Windows") == "qt"
    assert desktop_main._preferred_webview_gui("Linux") == "qt"
    assert desktop_main._preferred_webview_gui("Darwin") is None


def test_is_debug_webview_runtime_uses_executable_name():
    assert desktop_main._is_debug_webview_runtime("easy_kicad_debug.exe") is True
    assert desktop_main._is_debug_webview_runtime("easy_kicad.exe") is False


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


def test_start_desktop_window_forces_qt_on_windows(monkeypatch: pytest.MonkeyPatch):
    calls: dict[str, object] = {}

    def fake_create_window(title: str, url: str, **kwargs):
        calls["title"] = title
        calls["url"] = url
        calls["window_kwargs"] = kwargs

    def fake_start(**kwargs):
        calls["start_kwargs"] = kwargs

    fake_webview = SimpleNamespace(create_window=fake_create_window, start=fake_start)

    monkeypatch.setattr(desktop_main.platform, "system", lambda: "Windows")
    monkeypatch.setattr(desktop_main, "_ensure_webview_backend", lambda gui: calls.setdefault("gui_checked", gui))
    monkeypatch.setattr(desktop_main, "_is_debug_webview_runtime", lambda executable=None: True)

    desktop_main._start_desktop_window(fake_webview, 8767)

    assert calls["gui_checked"] == "qt"
    assert calls["title"] == "easy_kicad"
    assert calls["url"] == "http://127.0.0.1:8767"
    assert calls["window_kwargs"]["min_size"] == (1100, 760)
    assert calls["start_kwargs"] == {"gui": "qt", "debug": True}


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
