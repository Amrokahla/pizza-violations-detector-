"""Detection service configuration."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.env_paths import resolve_env_file


def _env_file() -> str | Path | None:
    p = resolve_env_file()
    return str(p) if p is not None else None


class DetectionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    model_path: str = Field(default="/models/yolo12m.pt", validation_alias="MODEL_PATH")


def get_detection_settings() -> DetectionSettings:
    return DetectionSettings()
