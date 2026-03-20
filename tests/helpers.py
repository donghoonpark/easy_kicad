from __future__ import annotations

from pathlib import Path

from easyeda2kicad.easyeda.parameters_easyeda import (
    Ee3dModel,
    Ee3dModelBase,
    EeFootprintBbox,
    EeFootprintInfo,
    EeFootprintPad,
    EeSymbol,
    EeSymbolBbox,
    EeSymbolInfo,
    EeSymbolRectangle,
    ee_footprint,
)
from easyeda2kicad.kicad.parameters_kicad_footprint import (
    Ki3dModel,
    Ki3dModelBase,
    KiFootprint,
    KiFootprintInfo,
    KiFootprintPad,
)
from easyeda2kicad.kicad.parameters_kicad_symbol import (
    KiPinStyle,
    KiPinType,
    KiSymbol,
    KiSymbolInfo,
    KiSymbolPin,
    KiSymbolRectangle,
)

from easy_kicad.schemas.part import (
    ConnectionTestResponse,
    ImportResponse,
    InspectResponse,
    Model3DPreview,
    PartMetadata,
)
from easy_kicad.schemas.settings import AppSettings
from easy_kicad.services.models import PartBundle
from easy_kicad.services.preview_service import render_footprint_svg, render_symbol_svg


def sample_raw_obj() -> str:
    return """newmtl matte
Ka 0.2 0.2 0.2
Kd 0.8 0.3 0.1
Ks 0.1 0.1 0.1
d 1
endmtl
v 0 0 0
v 2.54 0 0
v 0 2.54 0
usemtl matte
f 1 2 3
"""


def make_bundle() -> PartBundle:
    symbol = EeSymbol(
        info=EeSymbolInfo(
            name="EASY_TEST_PART",
            prefix="U",
            package="TEST_0603",
            manufacturer="easy_kicad",
            datasheet="https://example.com/datasheet",
            lcsc_id="C2040",
            jlc_id="JLC123",
        ),
        bbox=EeSymbolBbox(x=0, y=0),
        rectangles=[
            EeSymbolRectangle(
                pos_x="0",
                pos_y="0",
                rx="",
                ry="",
                width="12",
                height="8",
                stroke_color="#000000",
                stroke_width="1",
                stroke_style="solid",
                fill_color="none",
                id="rect-1",
                is_locked="0",
            )
        ],
    )
    footprint = ee_footprint(
        info=EeFootprintInfo(
            name="TEST_0603",
            fp_type="smd",
            model_3d_name="TEST_0603",
        ),
        bbox=EeFootprintBbox(x=0, y=0),
        model_3d=Ee3dModel(
            name="TEST_0603",
            uuid="uuid-1",
            translation=Ee3dModelBase(x=0, y=0, z=0),
            rotation=Ee3dModelBase(x=0, y=0, z=0),
            raw_obj=sample_raw_obj(),
            step=b"STEP-DATA",
        ),
        pads=[
            EeFootprintPad(
                shape="RECT",
                center_x=10,
                center_y=10,
                width=6,
                height=3,
                layer_id=1,
                net="",
                number="1",
                hole_radius=0,
                points="",
                rotation=0,
                id="pad-1",
                hole_length=0,
                hole_point="",
                is_plated=False,
                is_locked=False,
            )
        ],
    )
    ki_symbol = KiSymbol(
        info=KiSymbolInfo(
            name="EASY_TEST_PART",
            prefix="U",
            package="TEST_0603",
            manufacturer="easy_kicad",
            datasheet="https://example.com/datasheet",
            lcsc_id="C2040",
            jlc_id="JLC123",
        ),
        pins=[
            KiSymbolPin(
                name="IN",
                number="1",
                style=KiPinStyle.line,
                length=5.08,
                type=KiPinType._input,
                orientation=0,
                pos_x=0,
                pos_y=0,
            )
        ],
        rectangles=[KiSymbolRectangle(pos_x0=0, pos_y0=2.54, pos_x1=10.16, pos_y1=-2.54)],
    )
    ki_footprint = KiFootprint(
        info=KiFootprintInfo(name="TEST_0603", fp_type="smd"),
        model_3d=Ki3dModel(
            name="TEST_0603",
            translation=Ki3dModelBase(x=0, y=0, z=0),
            rotation=Ki3dModelBase(x=0, y=0, z=0),
            raw_wrl="#VRML V2.0 utf8",
        ),
        pads=[
            KiFootprintPad(
                type="smd",
                shape="rect",
                pos_x=1.27,
                pos_y=0,
                width=1.5,
                height=0.9,
                layers="F.Cu F.Paste F.Mask",
                number="1",
                drill=0.0,
                orientation=0.0,
                polygon="",
            )
        ],
    )
    part = PartMetadata(
        lcscId="C2040",
        name="EASY_TEST_PART",
        package="TEST_0603",
        manufacturer="easy_kicad",
        datasheet="https://example.com/datasheet",
    )
    return PartBundle(
        part=part,
        symbol=symbol,
        footprint=footprint,
        ki_symbol=ki_symbol,
        ki_footprint=ki_footprint,
        model_3d=footprint.model_3d,
        wrl_text="#VRML V2.0 utf8",
        step_available=True,
    )


class FakePartService:
    def __init__(self) -> None:
        self.bundle = make_bundle()

    def inspect_part(self, lcsc_id: str, settings: AppSettings) -> InspectResponse:
        return InspectResponse(
            part=self.bundle.part,
            symbolSvg=render_symbol_svg(self.bundle.ki_symbol),
            footprintSvg=render_footprint_svg(self.bundle.ki_footprint),
            model3d=Model3DPreview(
                available=True,
                name="TEST_0603",
                wrlUrl=f"/api/parts/{lcsc_id}/model.wrl",
                stepAvailable=True,
            ),
        )

    def import_part(self, lcsc_id: str, settings: AppSettings) -> ImportResponse:
        return ImportResponse(
            success=True,
            symbolLibrary=str(Path(settings.library_root) / f"{settings.library_name}.kicad_sym"),
            footprintFile=str(Path(settings.library_root) / f"{settings.library_name}.pretty" / "TEST_0603.kicad_mod"),
            modelDirectory=str(Path(settings.library_root) / f"{settings.library_name}.3dshapes"),
            importedSymbolName="EASY_TEST_PART",
            importedFootprintName="TEST_0603",
            modelName="TEST_0603",
        )

    def get_wrl(self, lcsc_id: str, settings: AppSettings) -> str:
        return self.bundle.wrl_text or ""

    def test_connection(self, settings: AppSettings) -> ConnectionTestResponse:
        return ConnectionTestResponse(success=True, message="Connection OK")
