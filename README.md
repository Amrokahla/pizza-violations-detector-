# Pizza Store — Scooper Violation Detection

Microservices system for monitoring hygiene compliance: detecting when ingredients are taken from defined ROIs without a scooper, with real-time visualization.

## Architecture

| Component | Role |
|-----------|------|
| **Frame Reader** | Ingests video (file or RTSP), publishes frames to the broker |
| **RabbitMQ** | Message broker for frames and detection results |
| **Detection** | YOLO inference, ROI/violation logic, persists violations |
| **Streaming** | REST + WebSocket/MJPEG for metadata and annotated video |
| **Frontend** | Live stream, bounding boxes, ROI overlay, violation count |

## Repository layout

```
├── pyproject.toml           # Poetry — dependencies & shared package
├── poetry.lock
├── poetry.toml              # in-project .venv
├── services/README.md       # Standard microservice layout
├── services/broker/         # Declare exchanges/queues (run `broker_setup` once)
├── services/frame_reader/   # Video → JPEG JSON → `pizza.frames`
├── services/detection/      # Consume frames → YOLO → `pizza.results`
├── services/streaming/      # FastAPI + `/ws` + consume results queue
├── frontend/
├── infra/rabbitmq/
├── shared/                  # Shared Pydantic models (installed as a package)
├── models/
├── data/videos/
├── docker-compose.yml
└── .env                     # Copy from .env.example
```

## Prerequisites

- **Poetry** (`pip install poetry` or [official installer](https://python-poetry.org/docs/#installation))
- **Python 3.11+** (3.12 recommended for local dev; use **Docker** for the full stack if your OS only has 3.14 and wheels fail)
- **Node 20+** for the frontend
- Docker and Docker Compose (recommended for RabbitMQ, Postgres, and GPU/torch-friendly Linux images)

## Python environment (Poetry)

From the repository root:

```bash
poetry install              # main deps + dev tools + shared package
poetry install --only main  # runtime only (no ruff/pytest)
```

Optional dependency groups (see `pyproject.toml`):

| Group | Purpose |
|-------|---------|
| `database` | SQLAlchemy + asyncpg (detection / DB-backed services) |
| `detection` | Ultralytics (YOLO / torch stack) |

```bash
poetry install --with database,detection   # e.g. local detection work on Python 3.11/3.12
```

**Broker (example):** set `PYTHONPATH` to the service directory, then run `main.py`:

```bash
# Windows PowerShell (repo root)
$env:PYTHONPATH = "$PWD\services\broker"
poetry run python services/broker/main.py
```

## Quick start (when services are implemented)

1. Copy `.env.example` to `.env` and adjust paths and broker settings.
2. `poetry install` at the repo root (see above).
3. Place pretrained YOLO weights under `models/` as referenced by `MODEL_PATH`.
4. Start infrastructure: `docker compose up -d rabbitmq postgres`
5. Declare broker topology: `docker compose run --rm broker_setup` (requires Docker and `.env`).
6. Full app: `docker compose --profile app up --build`

**Frontend:** `cd frontend && npm install && npm run dev` — Vite proxies `/api` to `http://localhost:8000`.

## Deliverables (task)

Functional pipeline, documented code, this README, UI with stream + detections + violation count, optional recorded demo, Docker Compose (included).
