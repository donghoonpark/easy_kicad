from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from easy_kicad.core.release import artifact_stem
from easy_kicad.metadata import APP_NAME, package_version


def dmg_output_path(
    output_dir: Path,
    *,
    version: str,
    system: str = "Darwin",
    machine: str | None = None,
) -> Path:
    return output_dir / f"{artifact_stem(version, system=system, machine=machine)}.dmg"


def build_macos_dmg(
    app_bundle: Path,
    output_dir: Path,
    *,
    version: str,
    machine: str | None = None,
    volume_name: str = APP_NAME,
    hdiutil_bin: str = "hdiutil",
) -> Path:
    if shutil.which(hdiutil_bin) is None:
        raise FileNotFoundError(f"Could not find hdiutil executable: {hdiutil_bin}")
    if not app_bundle.exists():
        raise FileNotFoundError(f"App bundle does not exist: {app_bundle}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = dmg_output_path(output_dir, version=version, machine=machine)
    output_path.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="easy-kicad-dmg-") as staging_root:
        staging_dir = Path(staging_root) / APP_NAME
        staging_dir.mkdir(parents=True)

        staged_app = staging_dir / app_bundle.name
        shutil.copytree(app_bundle, staged_app, symlinks=True)
        (staging_dir / "Applications").symlink_to("/Applications")

        subprocess.run(
            [
                hdiutil_bin,
                "create",
                "-volname",
                volume_name,
                "-srcfolder",
                str(staging_dir),
                "-ov",
                "-format",
                "UDZO",
                str(output_path),
            ],
            check=True,
        )

    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an unsigned macOS DMG from a PyInstaller app bundle")
    parser.add_argument(
        "--app-bundle",
        type=Path,
        default=Path("dist") / f"{APP_NAME}.app",
        help="Path to the PyInstaller macOS app bundle",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("release"),
        help="Directory to write the DMG into",
    )
    parser.add_argument(
        "--version",
        default=package_version(),
        help="Version string to embed in the DMG filename",
    )
    parser.add_argument(
        "--machine",
        default=None,
        help="Optional architecture label to use in the DMG filename",
    )
    parser.add_argument(
        "--volume-name",
        default=APP_NAME,
        help="Volume name shown when the DMG is mounted",
    )
    parser.add_argument(
        "--hdiutil-bin",
        default="hdiutil",
        help="Name or path of the hdiutil executable",
    )
    args = parser.parse_args()

    dmg_path = build_macos_dmg(
        args.app_bundle,
        args.output_dir,
        version=args.version,
        machine=args.machine,
        volume_name=args.volume_name,
        hdiutil_bin=args.hdiutil_bin,
    )
    print(dmg_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
