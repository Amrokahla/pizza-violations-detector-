# 03 — Detection and Violation Logic

## 1. Model

- **Pretrained YOLO** (e.g. YOLO12 medium) with classes relevant to the task: **Hand**, **Person**, **Pizza**, **Scooper** (per assignment brief).
- Runs inside the **Detection** service only; other services do not load the weights.

## 2. ROI configuration

- **User-defined ROIs** identify **critical** zones (e.g. protein container). Only these regions participate in violation logic.
- ROI data: polygons or axis-aligned rectangles in **image coordinates** (same space as model boxes after any letterboxing is inverted).
- Source: static JSON/YAML, environment path, or a small **Config API** (optional microservice).

Non-critical containers or background must **not** trigger protein-specific rules unless explicitly added to ROI config.

## 3. Per-frame pipeline (inside Detection)

1. **Infer** — run YOLO; obtain boxes and class labels.
2. **Track** — assign stable **track ids** to hands / persons across frames (IoU tracker, ByteTrack, or similar) to support multi-worker scenes.
3. **ROI test** — intersect hand (and optionally scooper) boxes with critical ROI geometry.
4. **FSM update** — advance per-track state machines (see below).
5. **Persist** — on violation, write DB row: frame path or snapshot id, boxes, labels, timestamp.
6. **Publish** — emit result message to broker for Streaming.

## 4. Violation finite-state machine (conceptual)

Rules follow the assignment: violation when a hand interacts with a critical ROI and subsequently contributes ingredient to pizza **without** using a scooper; **cleaning** (hand in ROI, no transfer) is **not** a violation.

Suggested states per **hand track** (or per hand–person pair):

| State | Meaning |
|-------|--------|
| `idle` | Hand not relevant to critical ROI |
| `roi_contact` | Hand overlaps critical ROI — possible interaction |
| `scooper_assisted` | Scooper present and used in picking path — **clears** violation for this pick |
| `transfer_to_pizza` | Hand approaches pizza with plausible cargo (from ROI interaction) |
| `violation_committed` | Transition to pizza **without** scooper-assisted path — increment count, save evidence |

**Cleaning:** `roi_contact` without transition to `transfer_to_pizza` within a timeout returns to `idle` with **no** violation.

**Scooper:** If scooper is detected in spatial/temporal proximity to the hand during the pick window, classify as compliant for that event.

Exact thresholds (IoU, time windows, distance hand–pizza) are **tuning parameters** and should be centralized for experiments on the provided sample videos.

## 5. Two workers at the pizza table

- **Separate tracks** for each person/hand; do not merge boxes across distant clusters.
- Associate **hand** events to the nearest **person** blob if helpful for debugging.
- Violation FSM runs **per track** so simultaneous workers do not share one state machine.

## 6. Outputs

- **Broker**: streaming-friendly JSON per frame or per violation event.
- **Database**: durable log of violations for REST aggregates and audit.

## 7. Related documents

- [02-Data-Flow-and-Broker.md](./02-Data-Flow-and-Broker.md) — where messages go.
- [04-Streaming-and-Frontend.md](./04-Streaming-and-Frontend.md) — how the UI consumes results.
