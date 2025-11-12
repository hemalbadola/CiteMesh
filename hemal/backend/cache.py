"""Simple file-based caching for OpenAlex responses."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any, Optional


class CacheStore:
    """Persist JSON responses keyed by API request signature."""

    def __init__(self, root: str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _key_to_path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.root / f"{digest}.json"

    def get(self, key: str) -> Optional[dict[str, Any]]:
        path = self._key_to_path(key)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError):
            # Corrupt cached file; remove to avoid repeated errors
            path.unlink(missing_ok=True)
            return None

    def set(self, key: str, payload: dict[str, Any]) -> None:
        path = self._key_to_path(key)
        try:
            with path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle)
        except OSError:
            # Ignore write failures; caching is best-effort
            pass
