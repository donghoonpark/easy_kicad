from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class LcscRequest(BaseModel):
    lcsc_id: str = Field(..., alias="lcscId")

    @field_validator("lcsc_id")
    @classmethod
    def normalize_lcsc_id(cls, value: str) -> str:
        normalized = (value or "").strip().upper()
        if not normalized.startswith("C"):
            raise ValueError("LCSC id must start with C")
        return normalized

    model_config = {"populate_by_name": True}


class PartMetadata(BaseModel):
    lcsc_id: str = Field(..., alias="lcscId")
    name: str
    package: str = ""
    manufacturer: str = ""
    datasheet: str = ""

    model_config = {"populate_by_name": True}


class Model3DPreview(BaseModel):
    available: bool
    name: Optional[str] = None
    wrl_url: Optional[str] = Field(default=None, alias="wrlUrl")
    step_available: bool = Field(default=False, alias="stepAvailable")

    model_config = {"populate_by_name": True}


class InspectResponse(BaseModel):
    part: PartMetadata
    symbol_svg: str = Field(..., alias="symbolSvg")
    footprint_svg: str = Field(..., alias="footprintSvg")
    model_3d: Model3DPreview = Field(..., alias="model3d")

    model_config = {"populate_by_name": True}


class ImportResponse(BaseModel):
    success: bool
    symbol_library: str = Field(..., alias="symbolLibrary")
    footprint_file: str = Field(..., alias="footprintFile")
    model_directory: str = Field(..., alias="modelDirectory")
    imported_symbol_name: str = Field(..., alias="importedSymbolName")
    imported_footprint_name: str = Field(..., alias="importedFootprintName")
    model_name: Optional[str] = Field(default=None, alias="modelName")

    model_config = {"populate_by_name": True}


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
