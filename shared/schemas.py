"""Broker message shapes (Pydantic) for frame and detection payloads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FrameMessage(BaseModel):
    """Published by frame_reader (JSON body on `pizza.frames`)."""

    model_config = ConfigDict(extra="allow")

    frame_id: int
    timestamp_ms: int
    camera_id: str
    image_b64: str = Field(description="JPEG bytes as base64")


class DetectionResult(BaseModel):
    """Published by detection → `pizza.results`."""

    model_config = ConfigDict(extra="allow")

    frame_id: int
    timestamp_ms: int
    camera_id: str
    boxes: list[dict[str, Any]] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    violation: bool = False
    violation_count_total: int = 0
