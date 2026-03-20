# easy_kicad

![easy_kicad banner](docs/assets/easy_kicad-banner.svg)

`easy_kicad` is a desktop-style importer that takes an LCSC part number,
previews the generated KiCad assets, and imports the symbol, footprint, and 3D
model into a local KiCad library in one flow.

It is built around
[`easyeda2kicad.py`](https://github.com/uPesy/easyeda2kicad.py),
with a Python desktop backend and a Vue 3 + Naive UI frontend.

## What You Get

- LCSC part lookup with one-click inspect
- Inline symbol preview
- Inline footprint preview
- WRL-based 3D preview
- Import into a KiCad symbol library, footprint library, and 3D model folder
- Settings for library path, proxy, CA bundle, SSL ignore, overwrite mode, and symbol format
- `pytest` coverage for API, import flow, preview rendering, settings storage, and release packaging
- GitHub Actions CI that runs tests, builds the frontend, and produces a PyInstaller desktop bundle

## Stack

- Backend: Python, FastAPI, `easyeda2kicad`, `pywebview`
- Frontend: Vue 3, TypeScript, Naive UI, three.js, Vite
- Python package management: `uv`
- Desktop packaging: PyInstaller

## Quick Start

### 1. Sync Python dependencies

```bash
UV_CACHE_DIR=.uv-cache uv sync --group dev
```

### 2. Install and build the frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. Run the app

Desktop window:

```bash
UV_CACHE_DIR=.uv-cache uv run easy-kicad
```

Browser/server only:

```bash
UV_CACHE_DIR=.uv-cache uv run easy-kicad --serve-only --port 8765
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) if you are using server-only mode.

## Test

```bash
UV_CACHE_DIR=.uv-cache uv run pytest
```

## Build A Desktop Bundle

Build the frontend first, then package the desktop app:

```bash
cd frontend
npm run build
cd ..
UV_CACHE_DIR=.uv-cache uv run pyinstaller easy_kicad.spec --noconfirm
UV_CACHE_DIR=.uv-cache uv run python scripts/build_release.py
```

PyInstaller produces an onedir bundle in `dist/easy_kicad/`, and the helper
script wraps that bundle into a platform-specific archive in `release/`.

## GitHub Setup

This repository includes:

- `.github/workflows/ci.yml` for push and pull request validation
- `.github/workflows/release.yml` for tag-based desktop release artifacts
- `.github/ISSUE_TEMPLATE/` for bug reports and feature requests
- `.github/pull_request_template.md` for a consistent review checklist

Recommended release flow:

1. Push to your default branch and let CI verify tests and packaging.
2. Tag a version like `v0.1.0`.
3. Push the tag to GitHub.
4. GitHub Actions will build desktop archives for each target OS and attach them to the release.

## Branding Surfaces

If you want to rebrand the app later, the main rename points are centralized:

- Python app metadata: `src/easy_kicad/metadata.py`
- Frontend marketing copy: `frontend/src/branding.ts`
- README banner art: `docs/assets/easy_kicad-banner.svg`
- Default KiCad library name: `src/easy_kicad/schemas/settings.py`

## Project Layout

```text
.github/                 GitHub Actions and repository templates
docs/assets/             README artwork
frontend/                Vue + TypeScript + Naive UI source
scripts/                 Build helpers used by CI and local packaging
src/easy_kicad/          FastAPI app, desktop launcher, services
src/easy_kicad/web/      Built frontend assets served by FastAPI
tests/                   pytest-based unit and API tests
```

## Notes

- 3D preview is based on WRL for fast in-app rendering.
- STEP files are still exported during import when available.
- Preview rendering is optimized for quick inspection rather than pixel-perfect KiCad parity.
- On this machine, `urllib3` can emit a LibreSSL warning under Python 3.9. The app and tests still run.

## License

`easy_kicad` is released under the GNU Affero General Public License v3.0 or later.
That choice keeps the project aligned with the licensing obligations of
`easyeda2kicad.py`.
