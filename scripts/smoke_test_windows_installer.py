from __future__ import annotations

import argparse
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from easy_kicad.core.release import artifact_stem
from easy_kicad.metadata import APP_NAME, package_version


def default_installer_path() -> Path:
    return Path("release") / f"{artifact_stem(package_version(), system='Windows', machine='AMD64', variant='setup')}.exe"


def available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def poll_ready(url: str, *, timeout_seconds: int, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout is not None else ""
            raise RuntimeError(f"Installed app exited early with code {process.returncode}\n{output}".strip())
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError) as exc:
            last_error = exc
            time.sleep(1)

    detail = f"\nLast connection error: {last_error}" if last_error is not None else ""
    raise TimeoutError(f"Timed out waiting for {url}{detail}")


def stop_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
        return
    except subprocess.TimeoutExpired:
        pass

    subprocess.run(
        ["taskkill", "/F", "/T", "/PID", str(process.pid)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    process.wait(timeout=10)


def smoke_test_installer(
    installer_path: Path,
    *,
    timeout_seconds: int = 45,
    port: int | None = None,
) -> Path:
    if not installer_path.exists():
        raise FileNotFoundError(f"Installer does not exist: {installer_path}")

    with tempfile.TemporaryDirectory(prefix="easy-kicad-installer-") as temp_root:
        install_dir = Path(temp_root) / APP_NAME
        subprocess.run(
            [
                str(installer_path.resolve()),
                "/S",
                f"/D={install_dir.resolve()}",
            ],
            check=True,
        )

        executable = install_dir / f"{APP_NAME}.exe"
        if not executable.exists():
            raise FileNotFoundError(f"Installed executable does not exist: {executable}")

        launch_port = port or available_port()
        process = subprocess.Popen(
            [str(executable), "--serve-only", "--port", str(launch_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        uninstall_path = install_dir / "Uninstall.exe"
        try:
            poll_ready(
                f"http://127.0.0.1:{launch_port}/api/settings",
                timeout_seconds=timeout_seconds,
                process=process,
            )
        finally:
            stop_process(process)
            if uninstall_path.exists():
                subprocess.run([str(uninstall_path), "/S"], check=True)

        return executable


def main() -> int:
    parser = argparse.ArgumentParser(description="Silently install the Windows NSIS build and verify it launches")
    parser.add_argument(
        "--installer",
        type=Path,
        default=default_installer_path(),
        help="Path to the NSIS installer executable",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=45,
        help="How long to wait for the installed app to answer HTTP requests",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Port for the launched app; defaults to a random free port",
    )
    args = parser.parse_args()

    executable = smoke_test_installer(
        args.installer,
        timeout_seconds=args.timeout_seconds,
        port=args.port or None,
    )
    print(executable)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
