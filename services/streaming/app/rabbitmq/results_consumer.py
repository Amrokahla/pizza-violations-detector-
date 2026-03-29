"""Background thread: consume detection results and push to the async hub."""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from typing import Any, Awaitable, Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel

from shared.rabbitmq import RabbitMQSettings, TopologySettings

logger = logging.getLogger(__name__)


class ResultsConsumerThread:
    """Runs a blocking RabbitMQ consumer in a daemon thread."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        on_result: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> None:
        self._loop = loop
        self._on_result = on_result
        self._thread: threading.Thread | None = None
        self._conn: pika.BlockingConnection | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="results-consumer", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._conn and self._conn.is_open:
            try:
                self._conn.close()
            except Exception as e:
                logger.debug("Consumer connection close: %s", e)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)

    def _run(self) -> None:
        mq = RabbitMQSettings()
        topo = TopologySettings()
        from shared.pika_connection import build_connection_parameters

        self._conn = pika.BlockingConnection(build_connection_parameters(mq))
        ch: BlockingChannel = self._conn.channel()
        ch.basic_qos(prefetch_count=16)

        def on_message(
            _ch: BlockingChannel,
            method: Any,
            _props: Any,
            body: bytes,
        ) -> None:
            try:
                data = json.loads(body.decode("utf-8"))
                fut = asyncio.run_coroutine_threadsafe(self._on_result(data), self._loop)
                fut.result(timeout=10.0)
            except Exception:
                logger.exception("Failed to handle result message")
            finally:
                _ch.basic_ack(delivery_tag=method.delivery_tag)

        ch.basic_consume(
            queue=topo.results_queue,
            on_message_callback=on_message,
            auto_ack=False,
        )
        logger.info("Streaming consuming queue=%s", topo.results_queue)
        try:
            ch.start_consuming()
        except Exception as e:
            if self._conn and self._conn.is_open:
                logger.debug("Consumer ended: %s", e)
