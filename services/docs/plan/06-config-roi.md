# Plan: Config / ROI Service (recommended extra)

## PDF basis

- “**User defines ROIs** for each critical zone (e.g. protein cargo).”
- Only **some** areas are important — not all containers.

The brief allows **extra microservices** if needed; centralizing ROI definitions avoids hardcoding in Detection and keeps the **Frontend** aligned when drawing ROI overlays.

## Scope

**In scope:** CRUD or read-only API for ROI polygons per `camera_id` / `session_id`; validation (closed polygons, within frame bounds).  
**Out of scope:** running YOLO (Detection).

## API (illustrative)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/rois?camera_id=` | List ROI definitions |
| PUT | `/rois` | Replace ROI set for a camera (admin UI or startup script) |

**Payload example:**

```json
{
  "camera_id": "main",
  "rois": [
    { "id": "protein", "critical": true, "polygon": [[x,y], ...] },
    { "id": "salt", "critical": false, "polygon": [[x,y], ...] }
  ]
}
```

## Storage

- **JSON file** on shared volume for minimal deployments.
- **PostgreSQL** table `rois` for multi-tenant or editable UIs.

## Consumers

- **Detection:** load ROIs at startup; optional watch/reload on change.
- **Frontend:** fetch same definitions to render overlay (or receive simplified list from Streaming proxy).

## Testing

- Validation rejects self-intersecting polygons; coordinate systems documented relative to **model input size** (after letterbox, use inverse transform).

## Deliverables checklist

- [ ] Single source of truth for critical vs non-critical ROIs
- [ ] Documented coordinate space vs Frame Reader resolution
- [ ] Optional: simple admin page or CLI seed script

## When to skip

- Short deadline: use **static `rois.json`** mounted in Detection and duplicated read-only in Frontend until this service is introduced.
