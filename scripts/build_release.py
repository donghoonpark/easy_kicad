from __future__ import annotations

import argparse
from pathlib import Path

from easy_kicad.core.release import create_release_archive
from easy_kicad.metadata import APP_NAME, package_version


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a release archive from a PyInstaller bundle")
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
        help="Directory to write the packaged release archive into",
    )
    parser.add_argument(
        "--version",
        default=package_version(),
        help="Version string to embed in the archive filename",
    )
    parser.add_argument(
        "--variant",
        default="",
        help="Optional artifact suffix such as 'debug'",
    )
    args = parser.parse_args()

    archive_path = create_release_archive(
        args.dist_dir,
        args.output_dir,
        version=args.version,
        variant=args.variant,
    )
    print(archive_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
