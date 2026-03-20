from __future__ import annotations

import platform
import shutil
from pathlib import Path
from typing import Optional

from easy_kicad.metadata import APP_NAME, package_version

_ARCH_ALIASES = {
    "amd64": "x64",
    "arm64": "arm64",
    "aarch64": "arm64",
    "x86_64": "x64",
}

_SYSTEM_ALIASES = {
    "darwin": "macos",
    "linux": "linux",
    "windows": "windows",
}


def normalized_machine(machine: Optional[str] = None) -> str:
    raw_machine = (machine or platform.machine() or "unknown").strip().lower()
    return _ARCH_ALIASES.get(raw_machine, raw_machine)


def platform_tag(system: Optional[str] = None, machine: Optional[str] = None) -> str:
    raw_system = (system or platform.system() or "unknown").strip().lower()
    normalized_system = _SYSTEM_ALIASES.get(raw_system, raw_system)
    return f"{normalized_system}-{normalized_machine(machine)}"


def archive_suffix(system: Optional[str] = None) -> str:
    raw_system = (system or platform.system() or "unknown").strip().lower()
    return ".zip" if raw_system == "windows" else ".tar.gz"


def artifact_stem(
    version: Optional[str] = None,
    *,
    system: Optional[str] = None,
    machine: Optional[str] = None,
) -> str:
    return f"{APP_NAME}-{version or package_version()}-{platform_tag(system, machine)}"


def create_release_archive(
    bundle_dir: Path,
    output_dir: Path,
    *,
    version: Optional[str] = None,
    system: Optional[str] = None,
    machine: Optional[str] = None,
) -> Path:
    if not bundle_dir.exists():
        raise FileNotFoundError(f"Bundle directory does not exist: {bundle_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_base = output_dir / artifact_stem(version, system=system, machine=machine)
    archive_format = "zip" if archive_suffix(system) == ".zip" else "gztar"
    archive_path = shutil.make_archive(
        str(archive_base),
        archive_format,
        root_dir=str(bundle_dir.parent),
        base_dir=bundle_dir.name,
    )
    return Path(archive_path)
