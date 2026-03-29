"""Resolve repository root and `.env` for all services."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Parent of the `shared` package directory."""
    return Path(__file__).resolve().parents[1]


def resolve_env_file() -> Path | None:
    """Prefer repo-root `.env`, then cwd `.env`."""
    candidates = [repo_root() / ".env", Path.cwd() / ".env"]
    for p in candidates:
        if p.is_file():
            return p
    return None
