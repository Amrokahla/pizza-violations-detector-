# Streaming

**FastAPI** service: consumes **`q.results.streaming`**, keeps the latest payload in memory, exposes **REST** (`/violations/count`, `/results/latest`) and **`/ws`** for live JSON updates.

## Run

```powershell
$env:PYTHONPATH = "$PWD\services\streaming"
poetry run python services/streaming/main.py
```

Uvicorn binds using `STREAMING_HOST` / `STREAMING_PORT` from `.env`.
