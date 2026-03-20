from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def _default_library_root() -> str:
    return str(Path.home() / "Documents" / "KiCad")


class AppSettings(BaseModel):
    library_root: str = Field(default_factory=_default_library_root)
    library_name: str = "easy_kicad"
    overwrite: bool = False
    project_relative_3d: bool = False
    symbol_format: Literal["v6", "v5"] = "v6"
    proxy_url: str = ""
    ca_bundle_path: str = ""
    ignore_ssl_verification: bool = False
    request_timeout_seconds: int = Field(default=20, ge=1, le=120)

    @field_validator("library_root", "proxy_url", "ca_bundle_path", mode="before")
    @classmethod
    def normalize_strings(cls, value: str) -> str:
        return (value or "").strip()

    @field_validator("library_name")
    @classmethod
    def validate_library_name(cls, value: str) -> str:
        sanitized = (value or "").strip()
        if not sanitized:
            raise ValueError("library_name must not be empty")
        return sanitized

    @property
    def base_library_path(self) -> Path:
        return Path(self.library_root).expanduser() / self.library_name
