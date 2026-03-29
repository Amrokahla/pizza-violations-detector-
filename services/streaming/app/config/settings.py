"""Streaming API configuration."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.env_paths import resolve_env_file


def _env_file() -> str | Path | None:
    p = resolve_env_file()
    return str(p) if p is not None else None


class StreamingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    host: str = Field(default="0.0.0.0", validation_alias="STREAMING_HOST")
    port: int = Field(default=8000, validation_alias="STREAMING_PORT")


def get_streaming_settings() -> StreamingSettings:
    return StreamingSettings()
