"""YOLO inference wrapper (optional ultralytics)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class YoloEngine:
    """Loads Ultralytics YOLO when weights exist; otherwise no-op."""

    def __init__(self, model_path: str) -> None:
        self._model: Any = None
        self._names: dict[int, str] = {}
        path = Path(model_path)
        if not path.is_file():
            logger.warning("Model file not found at %s — running without inference", model_path)
            return
        try:
            from ultralytics import YOLO  # type: ignore[import-untyped]

            self._model = YOLO(str(path))
            self._names = dict(self._model.names or {})
            logger.info("Loaded YOLO model from %s", model_path)
        except Exception as e:
            logger.warning("Could not load YOLO (%s) — running without inference", e)

    @property
    def is_ready(self) -> bool:
        return self._model is not None

    def predict(self, frame: Any) -> tuple[list[dict[str, Any]], list[str]]:
        if self._model is None:
            return [], []
        results = self._model(frame, verbose=False)
        boxes: list[dict[str, Any]] = []
        labels: list[str] = []
        for r in results:
            if r.boxes is None:
                continue
            for b in r.boxes:
                xyxy = b.xyxy[0].tolist()
                conf = float(b.conf[0]) if b.conf is not None else 0.0
                cls_id = int(b.cls[0])
                name = self._names.get(cls_id, str(cls_id))
                boxes.append(
                    {
                        "xyxy": xyxy,
                        "conf": conf,
                        "cls": cls_id,
                        "label": name,
                    }
                )
                labels.append(name)
        return boxes, labels
