"""Lightweight OpenAlex client utilities."""
from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Mapping
from urllib.parse import urlencode

import httpx

from ai_query import OpenAlexAPIRequest
from cache import CacheStore


class OpenAlexError(RuntimeError):
    """Raised when OpenAlex API requests fail."""


@dataclass
class OpenAlexClient:
    """Encapsulates HTTP calls to OpenAlex."""

    base_url: str
    timeout_seconds: float = 10.0
    session: httpx.Client | None = None
    cache: CacheStore | None = None
    max_retries: int = 3
    backoff_initial: float = 2.0

    def fetch(self, request: OpenAlexAPIRequest) -> Mapping[str, Any]:
        """Execute the OpenAlex API call and return JSON payload."""
        url = request.url or f"{self.base_url}/works"
        params = request.params or {}
        cache_key = self._cache_key(url, params)

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        client = self.session or httpx.Client(timeout=self.timeout_seconds)

        try:
            response_json = self._perform_request(client, url, params)
        finally:
            if self.session is None:
                client.close()

        if self.cache:
            self.cache.set(cache_key, response_json)

        return response_json

    def _perform_request(
        self, client: httpx.Client, url: str, params: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        backoff = self.backoff_initial

        for attempt in range(1, self.max_retries + 1):
            try:
                response = client.get(url, params=params)
            except httpx.TimeoutException as exc:
                if attempt == self.max_retries:
                    raise OpenAlexError("OpenAlex request timed out") from exc
                time.sleep(backoff)
                backoff *= 2
                continue
            except httpx.HTTPError as exc:  # network failure
                if attempt == self.max_retries:
                    raise OpenAlexError(f"OpenAlex request failed: {exc}") from exc
                time.sleep(backoff)
                backoff *= 2
                continue

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait_seconds = float(retry_after) if retry_after else backoff
                if attempt == self.max_retries:
                    raise OpenAlexError("OpenAlex rate limit exceeded (HTTP 429)")
                time.sleep(wait_seconds)
                backoff *= 2
                continue

            if response.status_code >= 400:
                raise OpenAlexError(
                    f"OpenAlex returned {response.status_code}: {response.text[:200]}"
                )

            try:
                return response.json()
            except ValueError as exc:
                raise OpenAlexError("OpenAlex returned invalid JSON") from exc

        raise OpenAlexError("Unable to complete OpenAlex request after retries")

    @staticmethod
    def _cache_key(url: str, params: Mapping[str, Any]) -> str:
        serialized_params = urlencode(sorted(params.items()), doseq=True)
        return f"{url}?{serialized_params}"
