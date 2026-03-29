# Plan: Message Broker

## PDF requirements

- **Facilitate communication** between services.
- Choose **Apache Kafka** or **RabbitMQ**.
- **Buffering** and **stream management**.

## Scope

**In scope:** topology (exchanges/topics, queues), routing keys, durability, consumer groups, operational limits.  
**Out of scope:** business rules (Detection service).

## Choice: RabbitMQ vs Kafka

| Criterion | RabbitMQ | Kafka |
|-----------|----------|--------|
| Throughput | Sufficient for single-store multi-camera at moderate FPS | Higher throughput, replay by offset |
| Ops complexity | Lower for small teams | ZooKeeper/KRaft, topics, retention tuning |
| Replay | Not default | Native log retention |
| Assignment fit | Typical for this coursework / single deployment | Choose if you need audit replay or very high fan-out |

**Recommendation for default implementation:** **RabbitMQ** with a **topic** or **direct** exchange unless the team already runs Kafka.

## Topology (conceptual)

| Stream | Producer | Consumers | Notes |
|--------|-----------|-----------|--------|
| Raw frames | Frame Reader | Detection | High volume; consider max queue length / TTL |
| Detection results | Detection | Streaming (+ optional logger) | JSON with boxes, labels, violation flags |

**Routing examples (RabbitMQ):**

- Exchange `pizza.frames` (topic): routing key `camera.<id>.frame`
- Exchange `pizza.results` (topic): routing key `camera.<id>.result`

**Kafka equivalent:**

- Topics `pizza-frames`, `pizza-results`; partition by `camera_id` if scaled horizontally.

## Buffering and back-pressure

- Set **max queue length** or **message TTL** on frame queues to prevent memory exhaustion if Detection is slow; document **frame drop** behavior.
- Use **dead-letter queues** for poison messages.
- **Prefetch** (`basic_qos`) tuned so one consumer does not hoard unprocessed frames.

## Security

- Broker credentials via env; TLS for remote brokers.

## Testing

- Publish synthetic messages; verify single and multiple consumers.
- Chaos: stop Detection temporarily; confirm broker does not crash and policy (drop vs block) matches design.

## Deliverables checklist

- [ ] Docker Compose service definition (or Helm/Kafka chart if Kafka)
- [ ] Documented exchange/topic names and env vars (`FRAMES_EXCHANGE`, `RESULTS_EXCHANGE`, etc.)
- [ ] Health check usable from dependent services

## Risks

- Mis-sized queues → OOM on broker host; monitor queue depth and consumer lag.
