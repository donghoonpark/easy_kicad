from __future__ import annotations

import argparse
import socket
import threading
import time
from typing import List, Optional

import uvicorn

from easy_kicad.app import create_app


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


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="easy_kicad desktop launcher")
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

    webview.create_window(
        "easy_kicad",
        f"http://127.0.0.1:{port}",
        width=1440,
        height=960,
        min_size=(1100, 760),
    )
    webview.start()
    return 0
