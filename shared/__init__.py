"""Shared models and schemas (installed as the `shared` package via Poetry)."""

from shared.rabbitmq import RabbitMQSettings, TopologySettings
from shared.schemas import DetectionResult, FrameMessage

__all__ = [
    "DetectionResult",
    "FrameMessage",
    "RabbitMQSettings",
    "TopologySettings",
]
