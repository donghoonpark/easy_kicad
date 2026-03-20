from __future__ import annotations

from easyeda2kicad.kicad.parameters_kicad_symbol import (
    KiPinStyle,
    KiPinType,
    KiSymbol,
    KiSymbolInfo,
    KiSymbolPin,
    KiSymbolRectangle,
)

from easy_kicad.services.preview_service import render_footprint_svg, render_symbol_svg
from tests.helpers import make_bundle


def test_render_symbol_svg_contains_shape_markup():
    bundle = make_bundle()
    svg = render_symbol_svg(bundle.ki_symbol)
    assert svg.startswith("<svg")
    assert "polyline" in svg or "rect" in svg or "line" in svg
    assert 'transform="translate(' in svg


def test_render_footprint_svg_contains_pad_markup():
    bundle = make_bundle()
    svg = render_footprint_svg(bundle.ki_footprint)
    assert svg.startswith("<svg")
    assert "rect" in svg or "circle" in svg
    assert 'transform="translate(' in svg


def test_render_symbol_svg_rotates_vertical_pin_labels():
    symbol = KiSymbol(
        info=KiSymbolInfo(
            name="VERTICAL_TEST",
            prefix="U",
            package="TEST",
            manufacturer="easy_kicad",
            datasheet="https://example.com",
            lcsc_id="C1",
            jlc_id="J1",
        ),
        pins=[
            KiSymbolPin(
                name="TOP_PIN",
                number="1",
                style=KiPinStyle.line,
                length=5.08,
                type=KiPinType._input,
                orientation=90,
                pos_x=0,
                pos_y=10.16,
            ),
            KiSymbolPin(
                name="BOTTOM_PIN",
                number="2",
                style=KiPinStyle.line,
                length=5.08,
                type=KiPinType.output,
                orientation=270,
                pos_x=0,
                pos_y=-10.16,
            ),
        ],
        rectangles=[KiSymbolRectangle(pos_x0=-5.08, pos_y0=5.08, pos_x1=5.08, pos_y1=-5.08)],
    )

    svg = render_symbol_svg(symbol)

    assert 'transform="rotate(-90' in svg
    assert 'dominant-baseline="middle"' in svg
