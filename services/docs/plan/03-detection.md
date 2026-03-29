# Plan: Detection Service

## PDF requirements

- **Subscribe** to the message broker.
- **Object detection** using the **pretrained YOLO** model (Hand, Person, Pizza, Scooper; YOLO 12 medium, 1254 images — per brief).
- **Logic:** if a hand took an ingredient and put it on pizza (e.g. protein) **without a scooper**, log as **violation**; if scooper used → no violation.
- **Persist:** save **frame path** for violation frames + **bounding boxes, labels, timestamp** in a **database**.
- **Publish:** send **bounding boxes, labels, violation status** toward Streaming (via broker or internal contract).
- **ROI:** user defines ROIs for critical zones (e.g. protein); **not all containers** are important.
- **Edge cases:**
  - Hand at ROI but **nothing picked** (e.g. cleaning) → **not** a violation.
  - **Two workers** at the pizza table → handle without merging distinct people/hands.

## Scope

**In scope:** inference, tracking, ROI intersection, temporal violation FSM, DB writes, result messages.  
**Out of scope:** serving HTTP video to browser (Streaming); raw frame capture (Frame Reader).

## Pipeline (ordered)

1. **Consume** frame messages from broker.
2. **Decode** image; align coordinates with **ROI definitions** (from config file or Config service).
3. **Inference:** run YOLO; obtain class names matching `Hand`, `Person`, `Pizza`, `Scooper` (map to model class indices).
4. **Tracking:** assign persistent **track IDs** to detections across frames (ByteTrack, BoT-SORT, or lightweight IoU tracker).
5. **ROI logic:** only **critical** ROIs (e.g. protein) participate in “pick” detection.
6. **Violation FSM (per hand track or per hand–person association):**
   - Hand enters critical ROI → start candidate interaction window.
   - If **scooper** appears in defined spatial/temporal relation to the pick → mark event as **compliant**.
   - If hand trajectory supports **transfer toward pizza** after ROI interaction **without** compliant scooper path → **increment violation**, **snapshot** evidence (save frame path + boxes + labels + timestamp).
   - Hand in ROI only, no transfer event within timeout → **idle** (covers **cleaning**).
7. **Multi-worker:** maintain **separate FSM state per track**; spatial clustering to avoid mixing hands from two people.
8. **Publish** result message each frame or on change: boxes, labels, `violation` / `violation_total`, optional `frame_path` for DB rows.

## Data model (database)

Suggested table `violations` (illustrative):

- `id`, `session_id`, `frame_id`, `timestamp`, `frame_path` (or object storage key)
- `boxes_json`, `labels_json`
- `violation_type` / free-text reason

Use **idempotent** insert keys to avoid duplicate counts on broker redelivery.

## Model assets

- Place weights under `models/` (e.g. from assignment “pretrained model” link).
- Env: `MODEL_PATH`; optional GPU flag for CUDA.

## Dependencies

- Broker (subscribe + publish)
- Database (PostgreSQL per existing `.env.example` pattern)
- ROI/config source (file or Config service)

## Testing

- **Unit:** FSM transitions with synthetic box sequences.
- **Integration:** broker in Docker; sample videos with known violation counts (1, 2, 1 per task filenames).
- **Regression:** cleaning-only ROI contact; two-person synthetic sequences.

## Deliverables checklist

- [ ] YOLO load + batch size 1 realtime path
- [ ] Violation logic matches PDF bullets
- [ ] DB persistence for violation rows
- [ ] Result messages consumed by Streaming
- [ ] Configurable ROIs and thresholds

## Risks

- Class imbalance / occlusion → tune IoU and time windows using provided Roboflow dataset or finetuning.
- Latency → profile inference; consider stride (process every Nth frame) with tracker continuity.
