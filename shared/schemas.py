"""Shared message shapes for broker payloads (extend as you implement services)."""

from typing import Any, TypedDict


class FrameMessage(TypedDict, total=False):
    """Published by frame_reader."""

    frame_id: int
    timestamp_ms: int
    payload: Any  # e.g. JPEG bytes base64 or reference id


class DetectionResult(TypedDict, total=False):
    """Published by detection → streaming."""

    frame_id: int
    timestamp_ms: int
    boxes: list[dict[str, Any]]
    violation: bool
