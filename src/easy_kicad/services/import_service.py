from __future__ import annotations

from pathlib import Path

from easyeda2kicad.helpers import (
    add_component_in_symbol_lib_file,
    id_already_in_symbol_lib,
    update_component_in_symbol_lib_file,
)
from easyeda2kicad.kicad.export_kicad_3d_model import Exporter3dModelKicad
from easyeda2kicad.kicad.export_kicad_footprint import ExporterFootprintKicad
from easyeda2kicad.kicad.export_kicad_symbol import ExporterSymbolKicad
from easyeda2kicad.kicad.parameters_kicad_symbol import KicadVersion

from easy_kicad.schemas.part import ImportResponse
from easy_kicad.schemas.settings import AppSettings
from easy_kicad.services.models import PartBundle

V6_SYMBOL_HEADER = """(kicad_symbol_lib
  (version 20211014)
  (generator https://github.com/uPesy/easyeda2kicad.py)
)"""
V5_SYMBOL_HEADER = "EESchema-LIBRARY Version 2.4\n#encoding utf-8\n"


def _symbol_version(settings: AppSettings) -> KicadVersion:
    return KicadVersion.v5 if settings.symbol_format == "v5" else KicadVersion.v6


def ensure_library_paths(settings: AppSettings) -> tuple[Path, Path, Path]:
    library_root = Path(settings.library_root).expanduser()
    library_root.mkdir(parents=True, exist_ok=True)

    base_path = library_root / settings.library_name
    symbol_extension = "lib" if settings.symbol_format == "v5" else "kicad_sym"
    symbol_path = library_root / f"{settings.library_name}.{symbol_extension}"
    footprint_dir = library_root / f"{settings.library_name}.pretty"
    model_dir = library_root / f"{settings.library_name}.3dshapes"

    footprint_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    if not symbol_path.exists():
        header = V5_SYMBOL_HEADER if settings.symbol_format == "v5" else V6_SYMBOL_HEADER
        symbol_path.write_text(header, encoding="utf-8")

    return base_path, symbol_path, footprint_dir


def import_part_bundle(bundle: PartBundle, settings: AppSettings) -> ImportResponse:
    version = _symbol_version(settings)
    base_path, symbol_path, footprint_dir = ensure_library_paths(settings)

    symbol_exporter = ExporterSymbolKicad(symbol=bundle.symbol, kicad_version=version)
    symbol_content = symbol_exporter.export(footprint_lib_name=settings.library_name)
    symbol_exists = id_already_in_symbol_lib(
        lib_path=str(symbol_path),
        component_name=bundle.symbol.info.name,
        kicad_version=version,
    )
    if symbol_exists and not settings.overwrite:
        raise FileExistsError("Symbol already exists. Enable overwrite to replace it.")
    if symbol_exists:
        update_component_in_symbol_lib_file(
            lib_path=str(symbol_path),
            component_name=bundle.symbol.info.name,
            component_content=symbol_content,
            kicad_version=version,
        )
    else:
        add_component_in_symbol_lib_file(
            lib_path=str(symbol_path),
            component_content=symbol_content,
            kicad_version=version,
        )

    footprint_exporter = ExporterFootprintKicad(footprint=bundle.footprint)
    footprint_path = footprint_dir / f"{bundle.footprint.info.name}.kicad_mod"
    if footprint_path.exists() and not settings.overwrite:
        raise FileExistsError("Footprint already exists. Enable overwrite to replace it.")

    model_path_ref = base_path.with_suffix(".3dshapes").as_posix()
    if settings.project_relative_3d:
        model_path_ref = f"${{KIPRJMOD}}/{settings.library_name}.3dshapes"

    footprint_exporter.export(
        footprint_full_path=str(footprint_path),
        model_3d_path=model_path_ref,
    )

    model_dir = base_path.with_suffix(".3dshapes")
    if bundle.model_3d is not None:
        model_exporter = Exporter3dModelKicad(model_3d=bundle.model_3d)
        model_exporter.export(lib_path=str(base_path))
        model_name = bundle.model_3d.name
    else:
        model_name = None

    return ImportResponse(
        success=True,
        symbolLibrary=str(symbol_path),
        footprintFile=str(footprint_path),
        modelDirectory=str(model_dir),
        importedSymbolName=bundle.symbol.info.name,
        importedFootprintName=bundle.footprint.info.name,
        modelName=model_name,
    )
