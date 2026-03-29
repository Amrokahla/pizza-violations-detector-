"""Shared pika connection parameters."""

from __future__ import annotations

import pika

from shared.rabbitmq import RabbitMQSettings


def build_connection_parameters(settings: RabbitMQSettings) -> pika.ConnectionParameters:
    credentials = pika.PlainCredentials(settings.user, settings.password)
    return pika.ConnectionParameters(
        host=settings.host,
        port=settings.port,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=300,
        connection_attempts=3,
        retry_delay=2,
    )
