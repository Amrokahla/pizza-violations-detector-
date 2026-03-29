# Microservices

Python services use **Poetry** at the **repository root** (`pyproject.toml`), **Pydantic** / **pydantic-settings** for config and shared DTOs, and a **layered folder layout** similar to typical Go services (config, models, messaging, services, persistence when needed).

## Root Poetry project

- Install once from repo root: `poetry install`
- The `shared/` package is installable as `shared` (schemas, Pydantic models).
- Services are **not** separate Poetry projects; run them with `PYTHONPATH` pointing at `services/<name>` (see root `README.md`).
- Heavy stacks are **optional groups**: `database` (SQLAlchemy + asyncpg), `detection` (Ultralytics / torch).

## Standard layout (per service)

| Path | Role |
|------|------|
| `main.py` | Entry point |
| `app/config/` | Settings (`pydantic-settings`) |
| `app/models/` | Pydantic models / topology |
| `app/rabbitmq/` (or `app/messaging/`) | Broker client, declarations, publishers |
| `app/services/` | Use cases |
| `clients/` | Outbound HTTP/gRPC clients |
| `database/` | DB helpers (when used) |
| `migrations/` | SQL migrations (when used) |
| `repositories/` | Data access (when used) |
| `scripts/` | Helper scripts |

## Services

| Directory | Role |
|-----------|------|
| `broker/` | RabbitMQ topology setup |
| `frame_reader/` | Video ingest |
| `detection/` | Inference + DB (use `--with database,detection` in Poetry when developing locally) |
| `streaming/` | API + streaming |
