# Plan: Streaming Service

## PDF requirements

- Expose **REST API** for **metadata**, especially **number of violations** for the frontend.
- Provide **real-time video** with detections drawn, via **WebRTC**, **WebSocket**, or **MJPEG**.
- Suggested frameworks: **Flask** or **FastAPI** (or similar).

## Scope

**In scope:** HTTP API, WebSocket and/or MJPEG (or WebRTC if chosen), consumption of detection results from broker or internal queue, optional server-side drawing of boxes/ROIs.  
**Out of scope:** training models; long-term storage of raw video (unless explicitly added).

## REST API (minimum)

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Orchestration / load balancers |
| `GET /violations/count` | Total violations for current session or selected run (PDF requirement) |
| Optional `GET /violations` | Paginated violation records (frame path, timestamp) for dashboards |

Extend with `session_id` or `video_id` query params when multiple runs exist.

## Real-time video

Pick **one primary** transport for MVP; add a second if needed.

| Transport | Pros | Cons |
|-----------|------|------|
| **MJPEG** | Simple `<img>` tag; easy to proxy | Higher bandwidth; less efficient |
| **WebSocket** | Flexible: JSON + binary JPEG frames | Client must decode/draw |
| **WebRTC** | Low latency | More moving parts (STUN/TURN if remote) |

**Patterns:**

- **Server-drawn:** compose frame + boxes + ROI overlay in backend; stream MJPEG or WebRTC.
- **Client-drawn:** stream raw or lightly compressed frames + JSON side channel over WebSocket; frontend draws on canvas.

PDF requires **bounding boxes**, **ROI areas**, and **violation** emphasis — ensure the chosen pattern exposes all three visually.

## Data flow

1. **Broker consumer** (async task) subscribes to `results` and pushes latest state into an in-memory structure or small cache (per session).
2. **REST** reads aggregates from DB and/or in-memory counter mirrored from Detection.
3. **WebSocket/MJPEG** loop pushes frames or metadata to connected clients.

If Detection already sends annotated images, Streaming can forward them with minimal processing.

## Dependencies

- Broker (results) and/or direct read from DB for counts
- CORS configuration if frontend is on another origin; or same-origin reverse proxy

## Testing

- Contract tests for REST JSON schema.
- Load test with one or more WebSocket clients; verify no unbounded memory growth.

## Deliverables checklist

- [ ] Violation count endpoint wired to DB or event stream
- [ ] At least one live video path (MJPEG or WebSocket)
- [ ] FastAPI app with Uvicorn in Docker
- [ ] Documented ports and env vars

## Risks

- Desync between displayed frame and overlay → include shared `frame_id` in payloads.
