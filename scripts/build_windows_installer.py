from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from easy_kicad.core.release import artifact_stem
from easy_kicad.metadata import APP_NAME, package_version


def installer_output_path(
    output_dir: Path,
    *,
    version: str,
    system: str = "Windows",
    machine: str = "AMD64",
) -> Path:
    return output_dir / f"{artifact_stem(version, system=system, machine=machine, variant='setup')}.exe"


def build_windows_installer(
    dist_dir: Path,
    output_dir: Path,
    *,
    version: str,
    nsis_script: Path,
    icon_file: Path,
    makensis_bin: str = "makensis",
) -> Path:
    if shutil.which(makensis_bin) is None:
        raise FileNotFoundError(f"Could not find NSIS compiler: {makensis_bin}")
    if not dist_dir.exists():
        raise FileNotFoundError(f"Bundle directory does not exist: {dist_dir}")
    if not nsis_script.exists():
        raise FileNotFoundError(f"NSIS script does not exist: {nsis_script}")
    if not icon_file.exists():
        raise FileNotFoundError(f"Installer icon does not exist: {icon_file}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = installer_output_path(output_dir, version=version)
    subprocess.run(
        [
            makensis_bin,
            f"/DAPP_VERSION={version}",
            f"/DDIST_DIR={dist_dir.resolve()}",
            f"/DOUTPUT_FILE={output_path.resolve()}",
            f"/DICON_FILE={icon_file.resolve()}",
            str(nsis_script.resolve()),
        ],
        check=True,
    )
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Windows NSIS installer from a PyInstaller onedir bundle")
    parser.add_argument(
        "--dist-dir",
        type=Path,
        default=Path("dist") / APP_NAME,
        help="Path to the PyInstaller onedir bundle",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("release"),
        help="Directory to write the installer into",
    )
    parser.add_argument(
        "--version",
        default=package_version(),
        help="Version string to embed in the installer filename",
    )
    parser.add_argument(
        "--nsis-script",
        type=Path,
        default=Path("packaging") / "windows" / "easy_kicad_installer.nsi",
        help="Path to the NSIS installer script",
    )
    parser.add_argument(
        "--icon-file",
        type=Path,
        default=Path("docs") / "assets" / "icons" / "easy_kicad.ico",
        help="Path to the Windows installer icon",
    )
    parser.add_argument(
        "--makensis-bin",
        default="makensis",
        help="Name or path of the makensis executable",
    )
    args = parser.parse_args()

    installer_path = build_windows_installer(
        args.dist_dir,
        args.output_dir,
        version=args.version,
        nsis_script=args.nsis_script,
        icon_file=args.icon_file,
        makensis_bin=args.makensis_bin,
    )
    print(installer_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
