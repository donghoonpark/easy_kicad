from __future__ import annotations

from typing import Optional, Protocol

from easyeda2kicad.easyeda.easyeda_api import EasyedaApi
from easyeda2kicad.easyeda.easyeda_importer import (
    Easyeda3dModelImporter,
    EasyedaFootprintImporter,
    EasyedaSymbolImporter,
)
from easyeda2kicad.kicad.export_kicad_3d_model import Exporter3dModelKicad
from easyeda2kicad.kicad.export_kicad_footprint import ExporterFootprintKicad
from easyeda2kicad.kicad.export_kicad_symbol import ExporterSymbolKicad
from easyeda2kicad.kicad.parameters_kicad_symbol import KicadVersion

from easy_kicad.core.network import patch_easyeda_requests
from easy_kicad.schemas.part import (
    ConnectionTestResponse,
    InspectResponse,
    Model3DPreview,
    PartMetadata,
)
from easy_kicad.schemas.settings import AppSettings
from easy_kicad.services.import_service import import_part_bundle
from easy_kicad.services.models import PartBundle
from easy_kicad.services.preview_service import render_footprint_svg, render_symbol_svg


class PartLookupError(RuntimeError):
    pass


class PartServiceProtocol(Protocol):
    def inspect_part(self, lcsc_id: str, settings: AppSettings) -> InspectResponse: ...
    def import_part(self, lcsc_id: str, settings: AppSettings): ...
    def get_wrl(self, lcsc_id: str, settings: AppSettings) -> str: ...
    def test_connection(self, settings: AppSettings) -> ConnectionTestResponse: ...


class EasyedaPartService:
    def __init__(self) -> None:
        self._wrl_cache: dict[str, str] = {}

    def _fetch_bundle(
        self,
        lcsc_id: str,
        settings: AppSettings,
        *,
        include_model: bool,
    ) -> PartBundle:
        with patch_easyeda_requests(settings):
            api = EasyedaApi()
            cad_data = api.get_cad_data_of_component(lcsc_id=lcsc_id)
            if not cad_data:
                raise PartLookupError(f"Could not find component {lcsc_id}")

            symbol = EasyedaSymbolImporter(easyeda_cp_cad_data=cad_data).get_symbol()
            footprint = EasyedaFootprintImporter(easyeda_cp_cad_data=cad_data).get_footprint()
            ki_symbol = ExporterSymbolKicad(
                symbol=symbol,
                kicad_version=KicadVersion.v6,
            ).output
            ki_footprint = ExporterFootprintKicad(footprint=footprint).get_ki_footprint()

            model_3d = Easyeda3dModelImporter(
                easyeda_cp_cad_data=cad_data,
                download_raw_3d_model=include_model,
            ).output
            wrl_text: Optional[str] = None
            step_available = False
            if model_3d is not None:
                step_available = bool(model_3d.step)
                model_exporter = Exporter3dModelKicad(model_3d=model_3d)
                if model_exporter.output is not None:
                    wrl_text = model_exporter.output.raw_wrl

        part = PartMetadata(
            lcscId=lcsc_id,
            name=symbol.info.name,
            package=symbol.info.package or "",
            manufacturer=symbol.info.manufacturer or "",
            datasheet=symbol.info.datasheet or "",
        )
        return PartBundle(
            part=part,
            symbol=symbol,
            footprint=footprint,
            ki_symbol=ki_symbol,
            ki_footprint=ki_footprint,
            model_3d=model_3d,
            wrl_text=wrl_text,
            step_available=step_available,
        )

    def inspect_part(self, lcsc_id: str, settings: AppSettings) -> InspectResponse:
        bundle = self._fetch_bundle(lcsc_id, settings, include_model=True)
        if bundle.wrl_text:
            self._wrl_cache[lcsc_id] = bundle.wrl_text
        return InspectResponse(
            part=bundle.part,
            symbolSvg=render_symbol_svg(bundle.ki_symbol),
            footprintSvg=render_footprint_svg(bundle.ki_footprint),
            model3d=Model3DPreview(
                available=bundle.model_3d is not None,
                name=bundle.model_3d.name if bundle.model_3d is not None else None,
                wrlUrl=f"/api/parts/{lcsc_id}/model.wrl" if bundle.wrl_text else None,
                stepAvailable=bundle.step_available,
            ),
        )

    def import_part(self, lcsc_id: str, settings: AppSettings):
        bundle = self._fetch_bundle(lcsc_id, settings, include_model=True)
        if bundle.wrl_text:
            self._wrl_cache[lcsc_id] = bundle.wrl_text
        return import_part_bundle(bundle, settings)

    def get_wrl(self, lcsc_id: str, settings: AppSettings) -> str:
        if lcsc_id not in self._wrl_cache:
            bundle = self._fetch_bundle(lcsc_id, settings, include_model=True)
            if not bundle.wrl_text:
                raise PartLookupError(f"No 3D model available for {lcsc_id}")
            self._wrl_cache[lcsc_id] = bundle.wrl_text
        return self._wrl_cache[lcsc_id]

    def test_connection(self, settings: AppSettings) -> ConnectionTestResponse:
        with patch_easyeda_requests(settings):
            success = bool(EasyedaApi().get_cad_data_of_component(lcsc_id="C2040"))
        return ConnectionTestResponse(
            success=success,
            message="EasyEDA API connection succeeded." if success else "EasyEDA API connection failed.",
        )
