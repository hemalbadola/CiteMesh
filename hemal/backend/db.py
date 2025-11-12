"""Placeholder for optional local database helpers."""
from __future__ import annotations

import contextlib
from typing import Iterator

import psycopg


@contextlib.contextmanager
def get_connection(dsn: str | None = None) -> Iterator[psycopg.Connection]:
    """Yield a PostgreSQL connection when local persistence is required."""
    conn = psycopg.connect(dsn or "postgresql://localhost/research_repo")
    try:
        yield conn
    finally:
        conn.close()
