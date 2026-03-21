# easy_kicad

<p align="center">
  <a href="https://github.com/donghoonpark/easy_kicad/releases/latest">
    <img alt="Download for Windows" src="https://img.shields.io/badge/Windows-Download-0078D6?style=for-the-badge&logo=windows&logoColor=white">
  </a>
  <a href="https://github.com/donghoonpark/easy_kicad/releases/latest">
    <img alt="Download for macOS" src="https://img.shields.io/badge/macOS-Download-111827?style=for-the-badge&logo=apple&logoColor=white">
  </a>
  <a href="https://github.com/donghoonpark/easy_kicad/releases/latest">
    <img alt="Download for Linux" src="https://img.shields.io/badge/Linux-Download-F59E0B?style=for-the-badge&logo=linux&logoColor=white">
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
