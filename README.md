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
├── services/frame_reader/   # Video ingest → broker
├── services/detection/      # Inference + violation logic + DB
├── services/streaming/      # API + real-time stream
├── frontend/                # Web UI
├── shared/                  # Shared types/schemas (optional)
├── models/                  # Place pretrained YOLO weights here (gitignored)
├── data/videos/             # Sample videos (gitignored)
├── docker-compose.yml
└── .env                     # Copy from .env.example
```

## Prerequisites

- Docker and Docker Compose (recommended), or Python 3.11+ and Node 20+ for local runs
- Pretrained model path set in `.env` (`MODEL_PATH`)

## Quick start (when services are implemented)

1. Copy `.env.example` to `.env` and adjust paths and broker settings.
2. Place the pretrained YOLO weights under `models/` as referenced by `MODEL_PATH`.
3. Start infrastructure only: `docker compose up -d rabbitmq postgres`
4. Start the full application stack: `docker compose --profile app up --build`

**Frontend (local dev):** `cd frontend && npm install && npm run dev` — Vite proxies `/api` to `http://localhost:8000`.

Development without Docker: run each service from its folder after installing dependencies (`requirements.txt` / `npm install`).

## Deliverables (task)

Functional pipeline, documented code, this README, UI with stream + detections + violation count, optional recorded demo, Docker Compose (included).
