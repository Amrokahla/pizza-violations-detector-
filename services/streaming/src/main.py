"""FastAPI app: violation counts REST + real-time stream endpoints (to be implemented)."""

from fastapi import FastAPI

app = FastAPI(title="Pizza Violations Streaming API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/violations/count")
def violations_count() -> dict[str, int]:
    return {"count": 0}
