"""Consume frames, run inference, publish detection results."""

from __future__ import annotations

import base64
import json
import logging
import sys
from typing import Any

import cv2
import numpy as np
import pika
from pika.adapters.blocking_connection import BlockingChannel

from app.config.settings import get_detection_settings
from app.inference.yolo_engine import YoloEngine
from app.rabbitmq.publisher import ResultPublisher
from app.services.violation_rules import infer_violation_from_labels
from shared.rabbitmq import RabbitMQSettings, TopologySettings
from shared.schemas import DetectionResult, FrameMessage

logger = logging.getLogger(__name__)


class _State:
    violation_count_total: int = 0


_state = _State()


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    cfg = get_detection_settings()
    mq = RabbitMQSettings()
    topo = TopologySettings()
    engine = YoloEngine(cfg.model_path)

    publisher = ResultPublisher(mq=mq, topo=topo)
    publisher.connect()

    from shared.pika_connection import build_connection_parameters

    consumer_conn = pika.BlockingConnection(build_connection_parameters(mq))
    ch: BlockingChannel = consumer_conn.channel()
    ch.basic_qos(prefetch_count=1)

    def on_message(
        _ch: BlockingChannel,
        method: Any,
        _props: Any,
        body: bytes,
    ) -> None:
        try:
            data = json.loads(body.decode("utf-8"))
            frame_msg = FrameMessage.model_validate(data)
            raw = base64.b64decode(frame_msg.image_b64)
            arr = np.frombuffer(raw, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is None:
                logger.warning("Failed to decode frame %s", frame_msg.frame_id)
                _ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            boxes, labels = engine.predict(frame)
            violation = infer_violation_from_labels(labels)
            if violation:
                _state.violation_count_total += 1

            out = DetectionResult(
                frame_id=frame_msg.frame_id,
                timestamp_ms=frame_msg.timestamp_ms,
                camera_id=frame_msg.camera_id,
                boxes=boxes,
                labels=labels,
                violation=violation,
                violation_count_total=_state.violation_count_total,
            )
            publisher.publish_json(out.model_dump(), frame_msg.camera_id)
            if frame_msg.frame_id == 1 or frame_msg.frame_id % 60 == 0:
                logger.info(
                    "Frame %s labels=%s violation_total=%s",
                    frame_msg.frame_id,
                    labels[:5],
                    _state.violation_count_total,
                )
        except Exception:
            logger.exception("Frame processing error")
        finally:
            _ch.basic_ack(delivery_tag=method.delivery_tag)

    logger.info(
        "Consuming queue=%s publishing exchange=%s",
        topo.frames_queue,
        topo.results_exchange,
    )
    ch.basic_consume(
        queue=topo.frames_queue,
        on_message_callback=on_message,
        auto_ack=False,
    )
    try:
        ch.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping detection service")
    finally:
        ch.stop_consuming()
        consumer_conn.close()
        publisher.close()
