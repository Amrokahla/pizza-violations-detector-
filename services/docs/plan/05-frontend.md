# Plan: Frontend UI

## PDF requirements

- **Receive** detection results and **visualize** them.
- **Highlight:**
  - Bounding boxes of detected objects
  - **ROI** areas
  - **Violation** events (red box or alert)
- Show **video stream** with detections in **real time**.
- Display **total violation count**.
- Suggested: HTML/CSS/JS or **React** / **Vue**; Streamlit/Gradio **not recommended** when flexibility is required.

## Scope

**In scope:** video surface, overlays, violation counter, connection to Streaming REST + real-time channel.  
**Out of scope:** model training; broker administration.

## Layout (suggested)

- **Header:** session title, connection status (live / reconnecting).
- **Main:** video (`<video>` for WebRTC, `<img>` for MJPEG, or canvas for WebSocket frames).
- **Overlay layer:** SVG or canvas aligned to video intrinsic size; scale on resize.
- **Sidebar or banner:** **Violation count** (large, persistent).
- **Violation toast:** short alert on new violation event (optional but matches “red box or alert”).

## Data binding

| Source | Data |
|--------|------|
| REST (`/violations/count`) | Integer; poll every N seconds or after WebSocket events |
| WebSocket / MJPEG | Frames and/or JSON with `boxes[]`, `rois[]`, `violation` flag per frame |

Normalize coordinates to **0–1** or provide image width/height for consistent scaling.

## ROI drawing

- Fetch ROI polygon list from Streaming (static per session) or embed from build-time config for demo.
- Draw semi-transparent fill + border distinct from detection boxes.

## Styling

- Violation state: red border around frame or pulsing badge; ensure **WCAG**-visible contrast.

## Tech stack

- **React + Vite + TypeScript** (already scaffolded in repo) with hooks for WebSocket and fetch.
- State: React Query or simple `useState`/`useEffect` for count polling.

## Testing

- Component tests for overlay math (bbox scaling).
- E2E: mock Streaming API; assert count increments when mock sends violation event.

## Deliverables checklist

- [ ] Live stream visible in UI
- [ ] Boxes + ROIs + violation styling
- [ ] Violation count visible and updated
- [ ] Works behind dev proxy (`/api` → backend)

## Risks

- Aspect ratio mismatch → letterbox video and overlay using same transform matrix.
