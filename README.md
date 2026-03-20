# easy_kicad

`easy_kicad` is a desktop-style GUI for importing LCSC parts into KiCad using
[`easyeda2kicad.py`](https://github.com/uPesy/easyeda2kicad.py).

The current MVP includes:

- LCSC number search
- Symbol preview
- Footprint preview
- WRL-based 3D model preview
- One-click KiCad import
- Settings for library path, proxy, custom CA bundle, SSL ignore, overwrite, and symbol format
- `pytest` unit coverage for settings, preview rendering, API endpoints, and import flow

## Stack

- Backend: Python, FastAPI, `easyeda2kicad`, `pywebview`
- Frontend: Vue 3, TypeScript, Naive UI, three.js, Vite
- Python package management: `uv`

## Project layout

```text
frontend/                Vue + TypeScript + Naive UI source
src/easy_kicad/          FastAPI app, desktop launcher, services
src/easy_kicad/web/      Built frontend assets served by FastAPI
tests/                   pytest-based unit and API tests
```

## Run locally

### 1. Sync Python dependencies

```bash
UV_CACHE_DIR=.uv-cache uv sync
```

### 2. Install and build the frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. Launch the app

Desktop window:

```bash
UV_CACHE_DIR=.uv-cache uv run easy-kicad
```

Browser/server only:

```bash
UV_CACHE_DIR=.uv-cache uv run easy-kicad --serve-only --port 8765
```

Then open `http://127.0.0.1:8765`.

## Test

```bash
UV_CACHE_DIR=.uv-cache uv run pytest
```

## Current MVP notes

- 3D preview is based on WRL for fast in-app rendering.
- STEP files are still exported during import when available.
- Preview rendering is intentionally lightweight and optimized for quick inspection rather than perfect KiCad parity.
- On this machine, `urllib3` emits a LibreSSL warning under Python 3.9. The test suite still passes.
