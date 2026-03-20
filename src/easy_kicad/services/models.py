from __future__ import annotations

from dataclasses import dataclass

from typing import Optional

from easy_kicad.schemas.part import PartMetadata


@dataclass
class PartBundle:
    part: PartMetadata
    symbol: object
    footprint: object
    ki_symbol: object
    ki_footprint: object
    model_3d: Optional[object]
    wrl_text: Optional[str]
    step_available: bool
