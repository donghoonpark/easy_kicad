# easy_kicad

<p align="center">
  <a href="https://github.com/donghoonpark/easy_kicad/releases/latest">
    <img alt="Download the latest release" src="https://img.shields.io/badge/Download-Latest%20Release-DD6B20?style=for-the-badge">
  </a>
</p>

<p align="center">
  <a href="https://github.com/donghoonpark/easy_kicad/releases/latest">
    <img alt="Latest version" src="https://img.shields.io/github/v/release/donghoonpark/easy_kicad?display_name=tag&label=Latest%20Version">
  </a>
</p>

![easy_kicad app screenshot](docs/assets/easy_kicad-ui.png)

`easy_kicad` lets you search an LCSC part number, preview the generated KiCad
symbol, footprint, and 3D model, and import everything into your KiCad library
in one flow.

It is powered by
[`easyeda2kicad.py`](https://github.com/uPesy/easyeda2kicad.py).

## What It Does

- Search parts by LCSC number
- Preview symbol, footprint, and 3D model before import
- Import KiCad-ready assets with one click
- Configure library path, proxy, custom CA bundle, overwrite mode, and SSL verification behavior

## Download

Get the newest build from the latest release page:

- [Latest release](https://github.com/donghoonpark/easy_kicad/releases/latest)

Recommended files:

- Windows: `easy_kicad-<version>-windows-x64-setup.exe`
- macOS: `easy_kicad-<version>-macos-arm64.dmg`
- Linux: `easy_kicad-<version>-linux-x64.tar.gz`

## Notes

- Windows builds include an installer.
- macOS builds are currently distributed as an unsigned DMG, so Gatekeeper may show the usual warning on first launch.
- Linux builds are provided as a portable archive.

## License

`easy_kicad` is released under the GNU Affero General Public License v3.0 or later.
