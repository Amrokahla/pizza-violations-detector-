# Frame reader

Reads **video** (file, index, or RTSP), encodes **JPEG**, publishes `FrameMessage` JSON to **`pizza.frames`**.

## Layout

- `app/config` — `FrameReaderSettings` (Pydantic)
- `app/rabbitmq` — `FramePublisher`
- `app/services` — capture loop

## Run (repo root)

```powershell
$env:PYTHONPATH = "$PWD\services\frame_reader"
poetry run python services/frame_reader/main.py
```

Docker Compose (`--profile app`) runs the same with `PYTHONPATH` set in the image.
