from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable


ICONSET_SIZES = [16, 32, 64, 128, 256, 512, 1024]
ICO_SIZES = [16, 32, 48, 64, 128, 256]


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def build_png_sizes(source_png: Path, output_dir: Path, sizes: Iterable[int]) -> dict[int, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: dict[int, Path] = {}
    for size in sizes:
        output_path = output_dir / f"icon-{size}.png"
        run(["sips", "-z", str(size), str(size), str(source_png), "--out", str(output_path)])
        generated[size] = output_path
    return generated


def build_icns(source_png: Path, output_path: Path) -> None:
    if shutil.which("iconutil") is None:
        raise RuntimeError("iconutil is required to build macOS .icns assets")

    with tempfile.TemporaryDirectory() as tmpdir:
        iconset_dir = Path(tmpdir) / "easy_kicad.iconset"
        iconset_dir.mkdir(parents=True, exist_ok=True)
        pngs = build_png_sizes(source_png, iconset_dir, ICONSET_SIZES)

        mapping = {
            "icon_16x16.png": pngs[16],
            "icon_16x16@2x.png": pngs[32],
            "icon_32x32.png": pngs[32],
            "icon_32x32@2x.png": pngs[64],
            "icon_128x128.png": pngs[128],
            "icon_128x128@2x.png": pngs[256],
            "icon_256x256.png": pngs[256],
            "icon_256x256@2x.png": pngs[512],
            "icon_512x512.png": pngs[512],
            "icon_512x512@2x.png": pngs[1024],
        }
        for name, png_path in mapping.items():
            shutil.copyfile(png_path, iconset_dir / name)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        run(["iconutil", "-c", "icns", str(iconset_dir), "-o", str(output_path)])


def build_ico(source_png: Path, output_path: Path) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        pngs = build_png_sizes(source_png, Path(tmpdir), ICO_SIZES)
        entries = []
        payload = bytearray()
        offset = 6 + (16 * len(ICO_SIZES))

        for size in ICO_SIZES:
            png_bytes = pngs[size].read_bytes()
            width = 0 if size >= 256 else size
            height = 0 if size >= 256 else size
            entries.append(
                struct.pack(
                    "<BBBBHHII",
                    width,
                    height,
                    0,
                    0,
                    1,
                    32,
                    len(png_bytes),
                    offset,
                )
            )
            payload.extend(png_bytes)
            offset += len(png_bytes)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as file:
            file.write(struct.pack("<HHH", 0, 1, len(ICO_SIZES)))
            for entry in entries:
                file.write(entry)
            file.write(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build .ico and .icns icon assets from a source PNG")
    parser.add_argument("source_png", type=Path, help="High-resolution source PNG")
    parser.add_argument("--ico", type=Path, required=True, help="Output Windows .ico path")
    parser.add_argument("--icns", type=Path, required=True, help="Output macOS .icns path")
    args = parser.parse_args()

    build_ico(args.source_png, args.ico)
    build_icns(args.source_png, args.icns)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
