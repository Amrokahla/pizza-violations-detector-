# Broker microservice

Declares RabbitMQ **exchanges**, **queues**, **dead-letter queues**, and **bindings** idempotently. Configuration uses **Pydantic Settings** (`app/config`, `app/models`).

Dependencies are managed by **Poetry** at the **repository root** — not per-service `requirements.txt`.

## Layout

```
broker/
├── main.py
├── app/
│   ├── config/          # env_paths, RabbitMQSettings (pydantic-settings)
│   ├── models/          # BrokerTopology (pydantic-settings)
│   ├── rabbitmq/        # connection + declaration
│   └── services/        # setup_service
├── clients/             # (reserved)
├── database/            # N/A — see README there
├── migrations/          # N/A
├── repositories/        # N/A
└── scripts/
```

## Run (from repo root)

```powershell
$env:PYTHONPATH = "$PWD\services\broker"
poetry run python services/broker/main.py
```

Docker: `docker compose run --rm broker_setup` (build context is the repo root).

## Environment

See root `.env.example`: `RABBITMQ_*`, `FRAMES_EXCHANGE`, `RESULTS_EXCHANGE`, queue names.
