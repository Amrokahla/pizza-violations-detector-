"""Publish detection JSON to the results topic exchange."""

from __future__ import annotations

import json
import logging

import pika
from pika.adapters.blocking_connection import BlockingChannel

from shared.rabbitmq import RabbitMQSettings, TopologySettings

logger = logging.getLogger(__name__)


class ResultPublisher:
    def __init__(
        self,
        *,
        mq: RabbitMQSettings,
        topo: TopologySettings,
    ) -> None:
        self._mq = mq
        self._topo = topo
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def connect(self) -> None:
        from shared.pika_connection import build_connection_parameters

        params = build_connection_parameters(self._mq)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._channel.confirm_delivery()

    def close(self) -> None:
        if self._connection and self._connection.is_open:
            self._connection.close()
        self._connection = None
        self._channel = None

    def publish_json(self, body: dict, camera_id: str) -> None:
        if self._channel is None:
            raise RuntimeError("Publisher not connected")
        rk = self._topo.routing_key_result(camera_id)
        payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
        self._channel.basic_publish(
            exchange=self._topo.results_exchange,
            routing_key=rk,
            body=payload,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
            ),
            mandatory=True,
        )
