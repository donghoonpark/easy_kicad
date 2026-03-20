from __future__ import annotations

import argparse
import importlib
import platform
import socket
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional

import uvicorn

from easy_kicad.app import create_app
from easy_kicad.metadata import APP_TITLE


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_server(port: int, timeout_seconds: float = 10.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise TimeoutError("Server did not start in time")


def _run_server(port: int) -> None:
    uvicorn.run(create_app(), host="127.0.0.1", port=port, log_level="info")


def _preferred_webview_gui(system: Optional[str] = None) -> Optional[str]:
    normalized = (system or platform.system() or "").strip().lower()
    if normalized in {"windows", "linux"}:
        return "qt"
    return None


def _is_debug_webview_runtime(executable: Optional[str] = None) -> bool:
    return Path(executable or sys.executable or "").stem.lower().endswith("_debug")


def _ensure_webview_backend(gui: Optional[str]) -> None:
    if gui == "qt":
        importlib.import_module("webview.platforms.qt")


def _start_desktop_window(webview_module, port: int) -> None:
    gui = _preferred_webview_gui()
    _ensure_webview_backend(gui)

    webview_module.create_window(
        APP_TITLE,
        f"http://127.0.0.1:{port}",
        width=1440,
        height=960,
        min_size=(1100, 760),
    )

    start_kwargs = {"debug": _is_debug_webview_runtime()}
    if gui is not None:
        start_kwargs["gui"] = gui
    webview_module.start(**start_kwargs)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=f"{APP_TITLE} desktop launcher")
    parser.add_argument("--serve-only", action="store_true", help="Run the FastAPI server without pywebview")
    parser.add_argument("--port", type=int, default=0, help="Port to bind the local server to")
    args = parser.parse_args(argv)

    port = args.port or _free_port()
    if args.serve_only:
        uvicorn.run(create_app(), host="127.0.0.1", port=port, log_level="info")
        return 0

    try:
        import webview
    except Exception:
        uvicorn.run(create_app(), host="127.0.0.1", port=port, log_level="info")
        return 0

    server_thread = threading.Thread(target=_run_server, args=(port,), daemon=True)
    server_thread.start()
    _wait_for_server(port)

    _start_desktop_window(webview, port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
