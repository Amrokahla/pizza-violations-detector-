"""Capture video and publish frames to RabbitMQ."""

from __future__ import annotations

import base64
import logging
import sys
import time
import cv2

from app.config.settings import get_frame_reader_settings
from app.rabbitmq.publisher import FramePublisher
from shared.rabbitmq import RabbitMQSettings, TopologySettings
from shared.schemas import FrameMessage

logger = logging.getLogger(__name__)


def _open_capture(video_source: str) -> cv2.VideoCapture:
    if video_source.isdigit():
        return cv2.VideoCapture(int(video_source))
    return cv2.VideoCapture(video_source)


def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    cfg = get_frame_reader_settings()
    mq = RabbitMQSettings()
    topo = TopologySettings()

    cap = _open_capture(cfg.video_source)
    if not cap.isOpened():
        logger.error("Could not open video source: %s", cfg.video_source)
        raise SystemExit(1)

    publisher = FramePublisher(mq=mq, topo=topo, camera_id=cfg.camera_id)
    publisher.connect()
    logger.info(
        "Publishing frames camera=%s exchange=%s source=%s",
        cfg.camera_id,
        topo.frames_exchange,
        cfg.video_source,
    )

    frame_id = 0
    period = 1.0 / cfg.target_fps if cfg.target_fps and cfg.target_fps > 0 else 0.0
    try:
        while True:
            t0 = time.perf_counter()
            ok, frame = cap.read()
            if not ok:
                logger.info("End of stream or read failure; exiting loop")
                break
            frame_id += 1
            ts = int(time.time() * 1000)
            ok_jpg, buf = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), cfg.jpeg_quality],
            )
            if not ok_jpg:
                logger.warning("JPEG encode failed for frame %s", frame_id)
                continue
            b64 = base64.b64encode(buf.tobytes()).decode("ascii")
            msg = FrameMessage(
                frame_id=frame_id,
                timestamp_ms=ts,
                camera_id=cfg.camera_id,
                image_b64=b64,
            )
            publisher.publish_json(msg.model_dump())
            if frame_id == 1 or frame_id % 30 == 0:
                logger.info("Published frame %s", frame_id)

            if period > 0:
                elapsed = time.perf_counter() - t0
                sleep_s = period - elapsed
                if sleep_s > 0:
                    time.sleep(sleep_s)
    finally:
        publisher.close()
        cap.release()


if __name__ == "__main__":
    run()
