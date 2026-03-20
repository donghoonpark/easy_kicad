from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from easy_kicad.api.routes import router
from easy_kicad.core.settings import SettingsStore
from easy_kicad.metadata import APP_TITLE
from easy_kicad.services.easyeda_adapter import EasyedaPartService


def create_app(
    *,
    settings_store: Optional[SettingsStore] = None,
    part_service: Optional[EasyedaPartService] = None,
) -> FastAPI:
    app = FastAPI(title=APP_TITLE)
    app.state.settings_store = settings_store or SettingsStore()
    app.state.part_service = part_service or EasyedaPartService()
    app.include_router(router)

    web_dir = Path(__file__).resolve().parent / "web"
    assets_dir = web_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend(full_path: str = ""):
        index_path = web_dir / "index.html"
        if index_path.exists():
            return HTMLResponse(index_path.read_text(encoding="utf-8"))
        return JSONResponse(
            {
                "message": "easy_kicad backend is running",
                "frontendBuilt": False,
                "hint": "Run the frontend build to generate src/easy_kicad/web/index.html",
            }
        )

    return app
