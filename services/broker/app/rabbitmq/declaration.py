"""Declare exchanges, queues, and bindings (idempotent)."""

from __future__ import annotations

import pika

from shared.rabbitmq import TopologySettings

_DLX_KEY_FRAMES = "frames"
_DLX_KEY_RESULTS = "results"


def declare_topology(channel: pika.channel.Channel, topo: TopologySettings) -> None:
    """Declare DLX, topic exchanges, durable queues, and bindings."""
    channel.exchange_declare(
        exchange=topo.dlx_exchange,
        exchange_type="direct",
        durable=True,
    )

    channel.queue_declare(queue=topo.frames_dlq, durable=True)
    channel.queue_declare(queue=topo.results_dlq, durable=True)
    channel.queue_bind(
        exchange=topo.dlx_exchange,
        queue=topo.frames_dlq,
        routing_key=_DLX_KEY_FRAMES,
    )
    channel.queue_bind(
        exchange=topo.dlx_exchange,
        queue=topo.results_dlq,
        routing_key=_DLX_KEY_RESULTS,
    )

    channel.exchange_declare(
        exchange=topo.frames_exchange,
        exchange_type="topic",
        durable=True,
    )
    channel.exchange_declare(
        exchange=topo.results_exchange,
        exchange_type="topic",
        durable=True,
    )

    channel.queue_declare(
        queue=topo.frames_queue,
        durable=True,
        arguments={
            "x-dead-letter-exchange": topo.dlx_exchange,
            "x-dead-letter-routing-key": _DLX_KEY_FRAMES,
        },
    )
    channel.queue_declare(
        queue=topo.results_queue,
        durable=True,
        arguments={
            "x-dead-letter-exchange": topo.dlx_exchange,
            "x-dead-letter-routing-key": _DLX_KEY_RESULTS,
        },
    )

    channel.queue_bind(
        exchange=topo.frames_exchange,
        queue=topo.frames_queue,
        routing_key="camera.*.frame",
    )
    channel.queue_bind(
        exchange=topo.results_exchange,
        queue=topo.results_queue,
        routing_key="camera.*.result",
    )
