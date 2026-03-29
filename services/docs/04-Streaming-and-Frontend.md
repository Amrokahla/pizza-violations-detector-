# 04 — Streaming Service and Frontend

## 1. Streaming service responsibilities

The **Streaming** service is the **edge** between the backend pipeline and browsers:

1. **REST API** — metadata for the frontend, especially **total violation count** and optional pagination of past violations.
2. **Real-time channel** — at least one of:
   - **WebSocket** (JSON + binary frames for JPEG), or
   - **MJPEG** over HTTP (simple integration), or
   - **WebRTC** (lower latency; more setup).

Suggested stack: **FastAPI** with Uvicorn; async handlers for WebSocket and background tasks that pull from the broker or an internal queue fed by the broker consumer.

## 2. REST (illustrative endpoints)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness for orchestration |
| GET | `/violations/count` | Current session or global violation count |
| GET | `/violations` | Optional list with timestamps and frame references |

Versioning (`/v1/...`) can be added if the API is public.

## 3. Real-time video contract

Two common patterns:

**A. Server-side compositing** — Detection or Streaming draws boxes and ROIs on frames; client displays a single video stream (MJPEG or WebRTC).

**B. Client-side overlay** — Streaming sends **compressed video** or **still frames** plus **JSON** with boxes and ROI coordinates; frontend draws on `<canvas>` or overlays on `<video>`.

The assignment requires **bounding boxes**, **ROI areas**, and **violation highlights** (e.g. red alert). Either pattern is valid if all three are visible.

## 4. Frontend responsibilities

- **Video area** — bind to MJPEG `<img>`, WebRTC video element, or frame loop via WebSocket.
- **Overlays** — render detection boxes and ROI polygons from API/stream metadata.
- **Violation UX** — prominent count; optional flash or red border on event frames.
- **Configuration** — if ROIs are user-editable, provide a simple editor that POSTs to Config API or updates a shared config file (depends on deployment).

Framework: React or Vue (per brief); avoid Streamlit/Gradio as primary UI if flexibility is required.

## 5. Configuration and CORS

- Browser calls Streaming API: enable **CORS** for dev origins or serve frontend **behind same origin** via reverse proxy (see `frontend/nginx.conf` pattern).
- WebSocket URL must match how the user opens the app (localhost vs host name).

## 6. Related documents

- [01-Architecture.md](./01-Architecture.md) — overall system.
- [02-Data-Flow-and-Broker.md](./02-Data-Flow-and-Broker.md) — result messages from Detection.
