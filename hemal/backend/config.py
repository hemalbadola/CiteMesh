"""Configuration management for the OpenAlex backend service."""
from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Tuple


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    try:
        return default if raw is None else float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    try:
        return default if raw is None else int(raw)
    except ValueError:
        return default


def _env_keys(name: str) -> Tuple[str, ...]:
    raw = os.getenv(name, "")
    keys = [item.strip() for item in raw.split(",") if item.strip()]
    return tuple(keys)


@dataclass(frozen=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    openalex_base_url: str = os.getenv("OPENALEX_BASE_URL", "https://api.openalex.org")
    ai_provider: str = os.getenv("AI_PROVIDER", "gemini")
    ai_model: str = os.getenv("AI_MODEL", "gemini-1.5-flash-latest")
    ai_base_url: str = os.getenv(
        "AI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/models"
    )
    ai_api_keys: Tuple[str, ...] = _env_keys("AI_API_KEYS")
    request_timeout_seconds: float = _env_float("REQUEST_TIMEOUT_SECONDS", 10.0)
    enable_cache: bool = _env_bool("ENABLE_CACHE", False)
    cache_dir: str = os.getenv("CACHE_DIR", "cache")
    pdf_cache_dir: str = os.getenv("PDF_CACHE_DIR", "pdf_cache")
    pdf_download_timeout_seconds: float = _env_float(
        "PDF_DOWNLOAD_TIMEOUT_SECONDS", 20.0
    )
    pdf_max_download_mb: float = _env_float("PDF_MAX_DOWNLOAD_MB", 20.0)


settings = Settings()
