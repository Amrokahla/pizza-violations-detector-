"""In-memory latest detection snapshot + WebSocket fan-out."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ResultHub:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._latest: dict[str, Any] | None = None
        self._violation_count: int = 0
        self._websockets: list[WebSocket] = []

    @property
    def violation_count(self) -> int:
        return self._violation_count

    async def set_latest(self, payload: dict[str, Any]) -> None:
        async with self._lock:
            self._latest = payload
            self._violation_count = int(payload.get("violation_count_total", 0))
            targets = list(self._websockets)

        dead: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_json(payload)
            except Exception as e:
                logger.debug("WebSocket send failed: %s", e)
                dead.append(ws)
        for ws in dead:
            await self.unregister(ws)

    def snapshot(self) -> dict[str, Any] | None:
        return self._latest

    async def register(self, ws: WebSocket) -> None:
        async with self._lock:
            self._websockets.append(ws)

    async def unregister(self, ws: WebSocket) -> None:
        async with self._lock:
            if ws in self._websockets:
                self._websockets.remove(ws)


hub = ResultHub()
