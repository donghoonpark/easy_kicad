from __future__ import annotations

import argparse
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from easy_kicad.core.release import artifact_stem
from easy_kicad.metadata import APP_NAME, package_version


def default_dmg_path() -> Path:
    return Path("release") / f"{artifact_stem(package_version(), system='Darwin')}.dmg"


def available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def mounted_app_bundle(mount_dir: Path) -> Path:
    app_bundle = mount_dir / f"{APP_NAME}.app"
    if app_bundle.exists():
        return app_bundle

    matches = sorted(mount_dir.glob("*.app"))
    if not matches:
        raise FileNotFoundError(f"Could not find an app bundle in mounted DMG: {mount_dir}")
    return matches[0]


def app_binary_path(app_bundle: Path) -> Path:
    direct_binary = app_bundle / "Contents" / "MacOS" / APP_NAME
    if direct_binary.exists():
        return direct_binary

    macos_dir = app_bundle / "Contents" / "MacOS"
    matches = sorted(macos_dir.iterdir())
    if not matches:
        raise FileNotFoundError(f"Could not find a runnable binary in {macos_dir}")
    return matches[0]


def poll_ready(url: str, *, timeout_seconds: int, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout is not None else ""
            raise RuntimeError(f"Mounted app exited early with code {process.returncode}\n{output}".strip())
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
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def smoke_test_dmg(
    dmg_path: Path,
    *,
    timeout_seconds: int = 45,
    port: int | None = None,
    hdiutil_bin: str = "hdiutil",
) -> Path:
    if shutil.which(hdiutil_bin) is None:
        raise FileNotFoundError(f"Could not find hdiutil executable: {hdiutil_bin}")
    if not dmg_path.exists():
        raise FileNotFoundError(f"DMG does not exist: {dmg_path}")

    launch_port = port or available_port()

    with tempfile.TemporaryDirectory(prefix="easy-kicad-mount-") as mount_root:
        mount_dir = Path(mount_root) / APP_NAME
        mount_dir.mkdir(parents=True)

        subprocess.run(
            [
                hdiutil_bin,
                "attach",
                str(dmg_path.resolve()),
                "-nobrowse",
                "-mountpoint",
                str(mount_dir),
            ],
            check=True,
        )

        process: subprocess.Popen[str] | None = None
        try:
            binary_path = app_binary_path(mounted_app_bundle(mount_dir))
            process = subprocess.Popen(
                [str(binary_path), "--serve-only", "--port", str(launch_port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            poll_ready(
                f"http://127.0.0.1:{launch_port}/api/settings",
                timeout_seconds=timeout_seconds,
                process=process,
            )
            return binary_path
        finally:
            if process is not None:
                stop_process(process)
            subprocess.run(
                [hdiutil_bin, "detach", str(mount_dir), "-quiet"],
                check=True,
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Mount the macOS DMG artifact and verify the app launches")
    parser.add_argument(
        "--dmg",
        type=Path,
        default=default_dmg_path(),
        help="Path to the DMG file to smoke test",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=45,
        help="How long to wait for the mounted app to answer HTTP requests",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Port for the launched app; defaults to a random free port",
    )
    parser.add_argument(
        "--hdiutil-bin",
        default="hdiutil",
        help="Name or path of the hdiutil executable",
    )
    args = parser.parse_args()

    binary_path = smoke_test_dmg(
        args.dmg,
        timeout_seconds=args.timeout_seconds,
        port=args.port or None,
        hdiutil_bin=args.hdiutil_bin,
    )
    print(binary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
