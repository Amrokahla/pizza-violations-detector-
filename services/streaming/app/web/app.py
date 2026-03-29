"""FastAPI: REST metadata + WebSocket live detection JSON."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_streaming_settings
from app.rabbitmq.results_consumer import ResultsConsumerThread
from app.state.hub import hub


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    consumer = ResultsConsumerThread(loop, hub.set_latest)
    consumer.start()
    app.state.results_consumer = consumer
    yield
    consumer.stop()


app = FastAPI(title="Pizza Violations Streaming", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/violations/count")
async def violations_count() -> dict[str, int]:
    return {"count": hub.violation_count}


@app.get("/results/latest")
async def results_latest() -> dict:
    snap = hub.snapshot()
    return snap if snap is not None else {}


@app.websocket("/ws")
async def websocket_results(ws: WebSocket) -> None:
    await ws.accept()
    await hub.register(ws)
    try:
        snap = hub.snapshot()
        if snap is not None:
            await ws.send_json(snap)
        while True:
            await ws.receive()
    except WebSocketDisconnect:
        pass
    finally:
        await hub.unregister(ws)


def main() -> None:
    import uvicorn

    s = get_streaming_settings()
    uvicorn.run(
        "app.web.app:app",
        host=s.host,
        port=s.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
