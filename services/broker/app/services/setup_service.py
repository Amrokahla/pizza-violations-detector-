"""Orchestrates RabbitMQ topology setup with retries."""

from __future__ import annotations

import logging
import sys
import time

import pika
from pika.exceptions import AMQPConnectionError

from app.config.settings import get_rabbitmq_settings
from app.models.topology import BrokerTopology
from app.rabbitmq.connection import build_connection_parameters
from app.rabbitmq.declaration import declare_topology

logger = logging.getLogger(__name__)

MAX_RETRIES = 30
RETRY_DELAY_SEC = 2.0


def run_setup() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    topo = BrokerTopology()
    mq = get_rabbitmq_settings()
    params = build_connection_parameters(mq)

    last_err: Exception | None = None
    connection: pika.BlockingConnection | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            connection = pika.BlockingConnection(params)
            break
        except AMQPConnectionError as e:
            last_err = e
            logger.warning(
                "Cannot connect to RabbitMQ (%s), retry %s/%s",
                e,
                attempt,
                MAX_RETRIES,
            )
            time.sleep(RETRY_DELAY_SEC)
    else:
        logger.error("Giving up connecting to RabbitMQ: %s", last_err)
        raise SystemExit(1) from last_err

    assert connection is not None
    try:
        ch = connection.channel()
        declare_topology(ch, topo)
        logger.info(
            "Topology ready: exchanges [%s, %s], queues [%s, %s]",
            topo.frames_exchange,
            topo.results_exchange,
            topo.frames_queue,
            topo.results_queue,
        )
    finally:
        connection.close()


def main() -> None:
    run_setup()


if __name__ == "__main__":
    main()
