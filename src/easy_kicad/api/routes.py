from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import PlainTextResponse

from easy_kicad.schemas.part import ConnectionTestResponse, InspectResponse, LcscRequest
from easy_kicad.schemas.settings import AppSettings
from easy_kicad.services.easyeda_adapter import PartLookupError

router = APIRouter(prefix="/api")


def _settings(request: Request) -> AppSettings:
    return request.app.state.settings_store.load()


def _service(request: Request):
    return request.app.state.part_service


@router.get("/settings", response_model=AppSettings)
def get_settings(request: Request) -> AppSettings:
    return _settings(request)


@router.put("/settings", response_model=AppSettings)
def put_settings(settings: AppSettings, request: Request) -> AppSettings:
    return request.app.state.settings_store.save(settings)


@router.post("/settings/test-connection", response_model=ConnectionTestResponse)
def test_connection(
    request: Request,
    settings: Optional[AppSettings] = Body(default=None),
) -> ConnectionTestResponse:
    effective_settings = settings or _settings(request)
    try:
        return _service(request).test_connection(effective_settings)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/parts/inspect", response_model=InspectResponse)
def inspect_part(payload: LcscRequest, request: Request) -> InspectResponse:
    try:
        return _service(request).inspect_part(payload.lcsc_id, _settings(request))
    except PartLookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/parts/import")
def import_part(payload: LcscRequest, request: Request):
    try:
        return _service(request).import_part(payload.lcsc_id, _settings(request))
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PartLookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/parts/{lcsc_id}/model.wrl")
def get_model_wrl(lcsc_id: str, request: Request) -> PlainTextResponse:
    try:
        model = _service(request).get_wrl(lcsc_id.upper(), _settings(request))
        return PlainTextResponse(model, media_type="model/vrml")
    except PartLookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
