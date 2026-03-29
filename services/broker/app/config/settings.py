"""Environment and connection settings."""

from __future__ import annotations

from shared.rabbitmq import RabbitMQSettings


def get_rabbitmq_settings() -> RabbitMQSettings:
    return RabbitMQSettings()
