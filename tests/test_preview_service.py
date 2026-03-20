from __future__ import annotations

import re

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


def test_render_symbol_svg_places_labels_on_body_side_of_pins():
    symbol = KiSymbol(
        info=KiSymbolInfo(
            name="PIN_LAYOUT_TEST",
            prefix="U",
            package="TEST",
            manufacturer="easy_kicad",
            datasheet="https://example.com",
            lcsc_id="C1",
            jlc_id="J1",
        ),
        pins=[
            KiSymbolPin(
                name="LEFT_PIN",
                number="1",
                style=KiPinStyle.line,
                length=5.08,
                type=KiPinType._input,
                orientation=180,
                pos_x=-10.16,
                pos_y=0,
            ),
            KiSymbolPin(
                name="RIGHT_PIN",
                number="2",
                style=KiPinStyle.line,
                length=5.08,
                type=KiPinType.output,
                orientation=0,
                pos_x=10.16,
                pos_y=0,
            ),
            KiSymbolPin(
                name="TOP_PIN",
                number="3",
                style=KiPinStyle.line,
                length=5.08,
                type=KiPinType._input,
                orientation=90,
                pos_x=0,
                pos_y=10.16,
            ),
            KiSymbolPin(
                name="BOTTOM_PIN",
                number="4",
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

    assert re.search(r'x1="-10\.16" y1="-?0\.00" x2="-5\.08" y2="-?0\.00"', svg)
    assert re.search(r'x1="10\.16" y1="-?0\.00" x2="5\.08" y2="-?0\.00"', svg)
    assert re.search(r'x1="0\.00" y1="-10\.16" x2="-?0\.00" y2="-5\.08"', svg)
    assert re.search(r'x1="0\.00" y1="10\.16" x2="-?0\.00" y2="5\.08"', svg)
    assert re.search(r'text x="-3\.28" y="-?0\.00" font-size="2\.1" fill="#006464" text-anchor="start"', svg)
    assert re.search(r'text x="3\.28" y="-?0\.00" font-size="2\.1" fill="#006464" text-anchor="end"', svg)
    assert re.search(r'text x="-?0\.00" y="-3\.28" font-size="2\.1" fill="#006464" text-anchor="middle"', svg)
    assert re.search(r'text x="-?0\.00" y="3\.28" font-size="2\.1" fill="#006464" text-anchor="middle"', svg)
    assert 'stroke="#840000"' in svg
    assert 'fill="#f5f4ef"' in svg
    assert 'dominant-baseline="middle"' in svg
    assert 'rotate(-90' not in svg
