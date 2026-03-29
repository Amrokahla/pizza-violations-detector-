# Detection

Consumes **`q.frames.detection`**, runs **Ultralytics YOLO** when `MODEL_PATH` exists, applies a **placeholder violation rule** on labels, publishes **`DetectionResult`** JSON to **`pizza.results`**.

## Layout

- `app/config` — `DetectionSettings`
- `app/inference` — `YoloEngine`
- `app/rabbitmq` — `ResultPublisher`
- `app/services` — consumer loop + `violation_rules`

## Run

Requires Poetry **with** the detection extras (YOLO/torch) for real inference:

```powershell
poetry install --with database,detection
$env:PYTHONPATH = "$PWD\services\detection"
poetry run python services/detection/main.py
```

Docker Compose builds the detection image with `--with database,detection`.
