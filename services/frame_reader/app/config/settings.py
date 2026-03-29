"""Frame reader configuration."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.env_paths import resolve_env_file


def _env_file() -> str | Path | None:
    p = resolve_env_file()
    return str(p) if p is not None else None


class FrameReaderSettings(BaseSettings):
    """Video source and encoding."""

    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    camera_id: str = Field(default="default", validation_alias="CAMERA_ID")
    video_source: str = Field(default="0", validation_alias="VIDEO_SOURCE")
    jpeg_quality: int = Field(default=80, ge=1, le=100, validation_alias="JPEG_QUALITY")
    target_fps: float = Field(
        default=0.0,
        ge=0.0,
        validation_alias="FRAME_READER_FPS",
        description="0 = capture as fast as possible",
    )


def get_frame_reader_settings() -> FrameReaderSettings:
    return FrameReaderSettings()
