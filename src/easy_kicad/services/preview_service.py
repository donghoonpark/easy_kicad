from __future__ import annotations

from dataclasses import dataclass
import html
import math
import re
from typing import Iterable, Optional, Sequence

from easyeda2kicad.kicad.parameters_kicad_footprint import KiFootprint
from easyeda2kicad.kicad.parameters_kicad_symbol import (
    KiSymbol,
    KiSymbolBezier,
    KiSymbolPin,
)

PIN_LABEL_FONT_SIZE = 2.1
VERTICAL_PIN_LABEL_FONT_SIZE = 1.8
PIN_LABEL_OFFSET = 1.8
PIN_LABEL_VERTICAL_X_OFFSET = 0.7
PIN_LABEL_VERTICAL_Y_OFFSET = 1.2
PIN_LABEL_CHAR_WIDTH = 0.62
PIN_LABEL_LINE_HEIGHT = 1.0


@dataclass(frozen=True)
class PinLabelLayout:
    text: str
    x: float
    y: float
    anchor: str
    font_size: float
    is_vertical: bool
    transform: Optional[str] = None


def _svg_bounds(points: Iterable[tuple[float, float]], padding: float = 4.0) -> str:
    point_list = list(points) or [(0.0, 0.0), (10.0, 10.0)]
    x_values = [point[0] for point in point_list]
    y_values = [point[1] for point in point_list]
    min_x = min(x_values) - padding
    min_y = min(y_values) - padding
    width = max(max(x_values) - min(x_values) + padding, 10.0)
    height = max(max(y_values) - min(y_values) + padding, 10.0)
    return f"{min_x:.2f} {min_y:.2f} {width:.2f} {height:.2f}"


def _normalized_viewport(
    points: Iterable[tuple[float, float]],
    padding: float,
) -> tuple[str, float, float, float, float]:
    point_list = list(points) or [(0.0, 0.0), (10.0, 10.0)]
    x_values = [point[0] for point in point_list]
    y_values = [point[1] for point in point_list]
    min_x = min(x_values)
    max_x = max(x_values)
    min_y = min(y_values)
    max_y = max(y_values)

    width = max(max_x - min_x, 10.0)
    height = max(max_y - min_y, 10.0)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    view_min_x = -(width / 2) - padding
    view_min_y = -(height / 2) - padding
    view_width = width + (padding * 2)
    view_height = height + (padding * 2)
    view_box = f"{view_min_x:.2f} {view_min_y:.2f} {view_width:.2f} {view_height:.2f}"
    return view_box, center_x, center_y, view_width, view_height


def _background_rect(
    view_width: float,
    view_height: float,
    pattern_id: str,
) -> str:
    x = -(view_width / 2)
    y = -(view_height / 2)
    return (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{view_width:.2f}" height="{view_height:.2f}" '
        f'fill="url(#{pattern_id})" rx="8" />'
    )


def _screen_y(value: float) -> float:
    return -value


def _pin_end(pin: KiSymbolPin) -> tuple[float, float]:
    radians = math.radians(pin.orientation)
    end_x = pin.pos_x + math.cos(radians) * pin.length
    end_y = pin.pos_y + math.sin(radians) * pin.length
    return end_x, end_y


def _pin_orientation(pin: KiSymbolPin) -> int:
    return int(round(pin.orientation)) % 360


def _pin_label_layout(pin: KiSymbolPin, end_x: float, end_y: float) -> PinLabelLayout:
    orientation = _pin_orientation(pin)
    label_text = pin.name or pin.number
    screen_end_y = _screen_y(end_y)

    if orientation == 180:
        return PinLabelLayout(
            text=label_text,
            x=end_x - PIN_LABEL_OFFSET,
            y=screen_end_y,
            anchor="end",
            font_size=PIN_LABEL_FONT_SIZE,
            is_vertical=False,
        )

    if orientation == 90:
        label_x = end_x + PIN_LABEL_VERTICAL_X_OFFSET
        label_y = screen_end_y - PIN_LABEL_VERTICAL_Y_OFFSET
        return PinLabelLayout(
            text=label_text,
            x=label_x,
            y=label_y,
            anchor="end",
            font_size=VERTICAL_PIN_LABEL_FONT_SIZE,
            is_vertical=True,
            transform=f"rotate(-90 {label_x:.2f} {label_y:.2f})",
        )

    if orientation == 270:
        label_x = end_x - PIN_LABEL_VERTICAL_X_OFFSET
        label_y = screen_end_y + PIN_LABEL_VERTICAL_Y_OFFSET
        return PinLabelLayout(
            text=label_text,
            x=label_x,
            y=label_y,
            anchor="start",
            font_size=VERTICAL_PIN_LABEL_FONT_SIZE,
            is_vertical=True,
            transform=f"rotate(-90 {label_x:.2f} {label_y:.2f})",
        )

    return PinLabelLayout(
        text=label_text,
        x=end_x + PIN_LABEL_OFFSET,
        y=screen_end_y,
        anchor="start",
        font_size=PIN_LABEL_FONT_SIZE,
        is_vertical=False,
    )


def _pin_label_bounds(layout: PinLabelLayout) -> tuple[tuple[float, float], tuple[float, float]]:
    text_width = max(len(layout.text), 1) * layout.font_size * PIN_LABEL_CHAR_WIDTH
    text_height = layout.font_size * PIN_LABEL_LINE_HEIGHT

    if not layout.is_vertical:
        if layout.anchor == "end":
            min_x = layout.x - text_width
            max_x = layout.x
        elif layout.anchor == "middle":
            min_x = layout.x - (text_width / 2)
            max_x = layout.x + (text_width / 2)
        else:
            min_x = layout.x
            max_x = layout.x + text_width
        min_y = layout.y - (text_height / 2)
        max_y = layout.y + (text_height / 2)
        return (min_x, min_y), (max_x, max_y)

    min_x = layout.x - (text_height / 2)
    max_x = layout.x + (text_height / 2)
    if layout.anchor == "end":
        min_y = layout.y - text_width
        max_y = layout.y
    else:
        min_y = layout.y
        max_y = layout.y + text_width
    return (min_x, min_y), (max_x, max_y)


def _symbol_bounds(symbol: KiSymbol) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for pin in symbol.pins:
        end_x, end_y = _pin_end(pin)
        label_layout = _pin_label_layout(pin, end_x, end_y)
        label_min, label_max = _pin_label_bounds(label_layout)
        points.extend(
            [
                (pin.pos_x, _screen_y(pin.pos_y)),
                (end_x, _screen_y(end_y)),
                label_min,
                label_max,
            ]
        )
    for rectangle in symbol.rectangles:
        points.extend(
            [
                (rectangle.pos_x0, _screen_y(rectangle.pos_y0)),
                (rectangle.pos_x1, _screen_y(rectangle.pos_y1)),
            ]
        )
    for circle in symbol.circles:
        points.extend(
            [
                (circle.pos_x - circle.radius, _screen_y(circle.pos_y - circle.radius)),
                (circle.pos_x + circle.radius, _screen_y(circle.pos_y + circle.radius)),
            ]
        )
    for polygon in symbol.polygons:
        points.extend((point[0], _screen_y(point[1])) for point in polygon.points)
    for bezier in symbol.beziers:
        points.extend((point[0], _screen_y(point[1])) for point in bezier.points)
    for arc in symbol.arcs:
        points.extend(
            [
                (arc.start_x, _screen_y(arc.start_y)),
                (arc.middle_x, _screen_y(arc.middle_y)),
                (arc.end_x, _screen_y(arc.end_y)),
            ]
        )
    return points


def _render_bezier(bezier: KiSymbolBezier) -> str:
    if len(bezier.points) < 4:
        points = " ".join(f"{point[0]:.2f},{_screen_y(point[1]):.2f}" for point in bezier.points)
        return (
            f'<polyline points="{points}" fill="none" '
            'stroke="currentColor" stroke-width="0.3" />'
        )

    first = bezier.points[0]
    path_parts = [f"M {first[0]:.2f} {_screen_y(first[1]):.2f}"]
    for index in range(1, len(bezier.points), 3):
        chunk = bezier.points[index : index + 3]
        if len(chunk) == 3:
            control_1, control_2, end = chunk
            path_parts.append(
                "C "
                f"{control_1[0]:.2f} {_screen_y(control_1[1]):.2f}, "
                f"{control_2[0]:.2f} {_screen_y(control_2[1]):.2f}, "
                f"{end[0]:.2f} {_screen_y(end[1]):.2f}"
            )
    return (
        f'<path d="{" ".join(path_parts)}" fill="none" '
        'stroke="currentColor" stroke-width="0.3" />'
    )


def render_symbol_svg(symbol: KiSymbol) -> str:
    elements: list[str] = []
    bounds = _symbol_bounds(symbol)
    pattern_id = (
        f"symbol-grid-{re.sub(r'[^a-zA-Z0-9]+', '-', symbol.info.name).strip('-').lower() or 'part'}"
    )

    for rectangle in symbol.rectangles:
        x = min(rectangle.pos_x0, rectangle.pos_x1)
        y = min(_screen_y(rectangle.pos_y0), _screen_y(rectangle.pos_y1))
        width = abs(rectangle.pos_x1 - rectangle.pos_x0)
        height = abs(rectangle.pos_y1 - rectangle.pos_y0)
        elements.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="{height:.2f}" '
            'fill="rgba(15, 23, 42, 0.06)" stroke="currentColor" stroke-width="0.3" />'
        )

    for circle in symbol.circles:
        elements.append(
            f'<circle cx="{circle.pos_x:.2f}" cy="{_screen_y(circle.pos_y):.2f}" '
            f'r="{circle.radius:.2f}" fill="{"rgba(15, 23, 42, 0.06)" if circle.background_filling else "none"}" '
            'stroke="currentColor" stroke-width="0.3" />'
        )

    for polygon in symbol.polygons:
        points = " ".join(f"{point[0]:.2f},{_screen_y(point[1]):.2f}" for point in polygon.points)
        tag = "polygon" if polygon.is_closed else "polyline"
        fill = 'fill="rgba(15, 23, 42, 0.06)"' if polygon.is_closed else 'fill="none"'
        elements.append(
            f'<{tag} points="{points}" {fill} stroke="currentColor" stroke-width="0.3" />'
        )

    for bezier in symbol.beziers:
        elements.append(_render_bezier(bezier))

    for arc in symbol.arcs:
        elements.append(
            f'<path d="M {arc.start_x:.2f} {_screen_y(arc.start_y):.2f} '
            f'Q {arc.middle_x:.2f} {_screen_y(arc.middle_y):.2f} '
            f'{arc.end_x:.2f} {_screen_y(arc.end_y):.2f}" '
            'fill="none" stroke="currentColor" stroke-width="0.3" />'
        )

    for pin in symbol.pins:
        end_x, end_y = _pin_end(pin)
        label_layout = _pin_label_layout(pin, end_x, end_y)
        elements.append(
            f'<line x1="{pin.pos_x:.2f}" y1="{_screen_y(pin.pos_y):.2f}" '
            f'x2="{end_x:.2f}" y2="{_screen_y(end_y):.2f}" '
            'stroke="#0f172a" stroke-width="0.4" />'
        )
        transform_attr = f' transform="{label_layout.transform}"' if label_layout.transform else ""
        elements.append(
            f'<text x="{label_layout.x:.2f}" y="{label_layout.y:.2f}" '
            f'font-size="{label_layout.font_size:.1f}" fill="#334155" '
            f'text-anchor="{label_layout.anchor}" dominant-baseline="middle"{transform_attr}>'
            f"{html.escape(label_layout.text)}"
            "</text>"
        )

    view_box, center_x, center_y, view_width, view_height = _normalized_viewport(
        bounds,
        padding=5.0,
    )

    return (
        f'<svg viewBox="{view_box}" class="preview-svg" '
        'xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">'
        '<defs>'
        f'<pattern id="{pattern_id}" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<path d="M 4 0 L 0 0 0 4" fill="none" stroke="rgba(148,163,184,0.18)" stroke-width="0.12" />'
        "</pattern>"
        "</defs>"
        + _background_rect(view_width, view_height, pattern_id)
        + '<g style="color:#0f172a" transform="translate({:.2f} {:.2f})">'.format(
            -center_x,
            -center_y,
        )
        + "".join(elements)
        + "</g></svg>"
    )


def _track_points(track: Sequence[float], invert_y: bool = True) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for index in range(0, len(track), 2):
        if index + 1 >= len(track):
            break
        y_value = -track[index + 1] if invert_y else track[index + 1]
        points.append((track[index], y_value))
    return points


def _parse_custom_polygon(
    raw_polygon: str,
    center_x: float,
    center_y: float,
) -> Optional[str]:
    matches = re.findall(r"\(xy ([^ ]+) ([^)]+)\)", raw_polygon)
    if not matches:
        return None
    points = []
    for x_str, y_str in matches:
        x_value = center_x + float(x_str)
        y_value = -(center_y + float(y_str))
        points.append(f"{x_value:.2f},{y_value:.2f}")
    return " ".join(points)


def render_footprint_svg(footprint: KiFootprint) -> str:
    elements: list[str] = []
    bounds: list[tuple[float, float]] = []
    pattern_id = (
        f"footprint-grid-{re.sub(r'[^a-zA-Z0-9]+', '-', footprint.info.name).strip('-').lower() or 'part'}"
    )

    for track in footprint.tracks + footprint.rectangles:
        for start_x, start_y, end_x, end_y in zip(
            track.points_start_x,
            track.points_start_y,
            track.points_end_x,
            track.points_end_y,
        ):
            bounds.extend([(start_x, -start_y), (end_x, -end_y)])
            elements.append(
                f'<line x1="{start_x:.2f}" y1="{-start_y:.2f}" '
                f'x2="{end_x:.2f}" y2="{-end_y:.2f}" '
                f'stroke="#334155" stroke-width="{max(track.stroke_width, 0.18):.2f}" />'
            )

    for pad in footprint.pads:
        bounds.extend(
            [
                (pad.pos_x - pad.width / 2, -(pad.pos_y - pad.height / 2)),
                (pad.pos_x + pad.width / 2, -(pad.pos_y + pad.height / 2)),
            ]
        )
        if pad.shape == "circle":
            elements.append(
                f'<circle cx="{pad.pos_x:.2f}" cy="{-pad.pos_y:.2f}" '
                f'r="{min(pad.width, pad.height) / 2:.2f}" fill="#f97316" opacity="0.82" />'
            )
        elif pad.shape == "custom" and pad.polygon:
            points = _parse_custom_polygon(pad.polygon, pad.pos_x, pad.pos_y)
            if points:
                elements.append(
                    f'<polygon points="{points}" fill="#f97316" opacity="0.82" stroke="#7c2d12" stroke-width="0.12" />'
                )
        else:
            radius = min(pad.width, pad.height) / 2 if pad.shape == "oval" else 0.18
            x = pad.pos_x - pad.width / 2
            y = -pad.pos_y - pad.height / 2
            transform = (
                f' transform="rotate({-pad.orientation:.2f} {pad.pos_x:.2f} {-pad.pos_y:.2f})"'
                if pad.orientation
                else ""
            )
            elements.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{pad.width:.2f}" height="{pad.height:.2f}" '
                f'rx="{radius:.2f}" ry="{radius:.2f}" fill="#f97316" opacity="0.82"{transform} />'
            )

        if pad.drill:
            drill_radius = pad.drill / 2 if isinstance(pad.drill, float) else 0
            if drill_radius:
                elements.append(
                    f'<circle cx="{pad.pos_x:.2f}" cy="{-pad.pos_y:.2f}" r="{drill_radius:.2f}" fill="#f8fafc" />'
                )

    for circle in footprint.circles:
        radius = abs(circle.end_x - circle.cx)
        bounds.extend(
            [
                (circle.cx - radius, -(circle.cy - radius)),
                (circle.cx + radius, -(circle.cy + radius)),
            ]
        )
        elements.append(
            f'<circle cx="{circle.cx:.2f}" cy="{-circle.cy:.2f}" r="{radius:.2f}" '
            f'fill="none" stroke="#0f172a" stroke-width="{max(circle.stroke_width, 0.15):.2f}" />'
        )

    for hole in footprint.holes:
        bounds.extend(
            [
                (hole.pos_x - hole.size / 2, -(hole.pos_y - hole.size / 2)),
                (hole.pos_x + hole.size / 2, -(hole.pos_y + hole.size / 2)),
            ]
        )
        elements.append(
            f'<circle cx="{hole.pos_x:.2f}" cy="{-hole.pos_y:.2f}" r="{hole.size / 2:.2f}" '
            'fill="#f8fafc" stroke="#475569" stroke-width="0.12" />'
        )

    for via in footprint.vias:
        bounds.extend(
            [
                (via.pos_x - via.diameter / 2, -(via.pos_y - via.diameter / 2)),
                (via.pos_x + via.diameter / 2, -(via.pos_y + via.diameter / 2)),
            ]
        )
        elements.append(
            f'<circle cx="{via.pos_x:.2f}" cy="{-via.pos_y:.2f}" r="{via.diameter / 2:.2f}" '
            'fill="#fde68a" opacity="0.7" />'
        )
        elements.append(
            f'<circle cx="{via.pos_x:.2f}" cy="{-via.pos_y:.2f}" r="{via.size / 2:.2f}" '
            'fill="#f8fafc" />'
        )

    for text in footprint.texts:
        bounds.append((text.pos_x, -text.pos_y))
        elements.append(
            f'<text x="{text.pos_x:.2f}" y="{-text.pos_y:.2f}" font-size="{max(text.font_size, 0.8):.2f}" '
            'fill="#1e293b">'
            f"{html.escape(text.text)}"
            "</text>"
        )

    view_box, center_x, center_y, view_width, view_height = _normalized_viewport(
        bounds,
        padding=3.5,
    )

    return (
        f'<svg viewBox="{view_box}" class="preview-svg" '
        'xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">'
        '<defs>'
        f'<pattern id="{pattern_id}" width="1" height="1" patternUnits="userSpaceOnUse">'
        '<path d="M 1 0 L 0 0 0 1" fill="none" stroke="rgba(148,163,184,0.12)" stroke-width="0.04" />'
        "</pattern>"
        "</defs>"
        + _background_rect(view_width, view_height, pattern_id)
        + '<g transform="translate({:.2f} {:.2f})">'.format(-center_x, -center_y)
        + "".join(elements)
        + "</g></svg>"
    )
