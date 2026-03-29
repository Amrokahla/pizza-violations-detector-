"""RabbitMQ connection and topology settings (shared across services)."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.env_paths import resolve_env_file


def _env_file() -> str | Path | None:
    p = resolve_env_file()
    return str(p) if p is not None else None


class RabbitMQSettings(BaseSettings):
    """Broker connection (`RABBITMQ_*`)."""

    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    host: str = Field(default="localhost", validation_alias="RABBITMQ_HOST")
    port: int = Field(default=5672, validation_alias="RABBITMQ_PORT")
    user: str = Field(default="guest", validation_alias="RABBITMQ_USER")
    password: str = Field(default="guest", validation_alias="RABBITMQ_PASS")


class TopologySettings(BaseSettings):
    """Exchanges, queues, routing (`FRAMES_*`, `RESULTS_*`, `DLX_*`)."""

    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    frames_exchange: str = Field(default="pizza.frames", validation_alias="FRAMES_EXCHANGE")
    results_exchange: str = Field(default="pizza.results", validation_alias="RESULTS_EXCHANGE")
    frames_queue: str = Field(default="q.frames.detection", validation_alias="FRAMES_QUEUE")
    results_queue: str = Field(default="q.results.streaming", validation_alias="RESULTS_QUEUE")
    dlx_exchange: str = Field(default="pizza.dlx", validation_alias="DLX_EXCHANGE")
    frames_dlq: str = Field(default="q.frames.detection.dlq", validation_alias="FRAMES_DLQ")
    results_dlq: str = Field(default="q.results.streaming.dlq", validation_alias="RESULTS_DLQ")
    routing_frame_suffix: str = "frame"
    routing_result_suffix: str = "result"

    def routing_key_frame(self, camera_id: str) -> str:
        safe = camera_id.replace(".", "_")
        return f"camera.{safe}.{self.routing_frame_suffix}"

    def routing_key_result(self, camera_id: str) -> str:
        safe = camera_id.replace(".", "_")
        return f"camera.{safe}.{self.routing_result_suffix}"
