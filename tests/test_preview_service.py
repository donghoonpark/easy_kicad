from __future__ import annotations

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
