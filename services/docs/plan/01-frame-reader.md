# Plan: Frame Reader Service

## PDF requirements

- Read video frames from a **video file** or **RTSP camera** feed.
- **Publish frames** to the message broker.
- Suggested tools: OpenCV, GStreamer, DeepStream, FFmpeg, or equivalent.

## Scope

**In scope:** decoding, optional resize, timestamps, publishing serialized frames (or references).  
**Out of scope:** object detection, violation logic, HTTP APIs (those belong to Detection and Streaming).

## Inputs

| Source | Configuration |
|--------|----------------|
| Local file | Path from env or CLI (`VIDEO_SOURCE` or `VIDEO_PATH`) |
| RTSP / IP camera | URL, credentials via env/secrets |
| Webcam | Device index (dev/demo only) |

## Behavior

1. **Open** capture; on failure, retry with backoff and log.
2. **Loop:** read frame → assign monotonic `frame_id` → attach `timestamp_ms` (wall or stream time) and `session_id` / `source_id`.
3. **Optional:** cap FPS or resolution to match downstream inference budget.
4. **Serialize** payload (JPEG recommended for cross-process transport) and **publish** to broker exchange/queue configured for frames.
5. **Shutdown:** release capture cleanly on SIGTERM.

## Outputs (to broker)

- Minimum fields: `frame_id`, `timestamp_ms`, `source_id`, `image` (bytes or base64) or `blob_ref` if using shared volume.

## Dependencies

- Message broker reachable before sustained publish.
- Network stability for RTSP (long-running connections).

## Tooling choice

| Option | When to use |
|--------|-------------|
| **OpenCV** `VideoCapture` | Fastest to implement for files and many RTSP streams |
| **FFmpeg** subprocess / PyAV | Finer control over codecs and reconnect |
| **GStreamer / DeepStream** | GPU pipelines, multiple cameras, production NVR integration |

## Testing

- Unit: mock broker, assert message shape and frame_id monotonicity.
- Integration: short sample clip from task resources; verify consumer receives expected count of messages.

## Deliverables checklist

- [ ] Configurable file vs RTSP via environment variables
- [ ] Stable frame metadata for sync with detection
- [ ] Docker image with minimal deps (`opencv-python-headless` or chosen stack)
- [ ] Documentation in service README for env vars and limits

## Risks

- RTSP latency and dropped frames → document expected behavior and broker overflow policy.
