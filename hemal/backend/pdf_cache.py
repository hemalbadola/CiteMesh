"""Utilities for caching and proxying Open Access PDFs."""
from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import urlparse

import httpx


class PDFCacheError(RuntimeError):
    """Raised when fetching or serving an Open Access PDF fails."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class PDFCache:
    """Download and cache Open Access PDFs for local serving."""

    def __init__(
        self,
        root: str,
        timeout_seconds: float,
        max_bytes: int,
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max(0, int(max_bytes))

    def get_or_fetch(self, url: str) -> Path:
        """Return a local file path for the given PDF URL, downloading if needed."""
        if not url:
            raise PDFCacheError("Missing PDF URL", status_code=400)

        path = self._path_for_url(url)
        if path.exists():
            return path

        self._download(url, path)
        return path

    def _path_for_url(self, url: str) -> Path:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.root / f"{digest}.pdf"

    def _download(self, url: str, destination: Path) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise PDFCacheError("PDF URL must use http or https", status_code=400)

        tmp_path = destination.with_suffix(".tmp")
        tmp_path.unlink(missing_ok=True)

        try:
            with httpx.Client(timeout=self.timeout_seconds, follow_redirects=True) as client:
                with client.stream("GET", url) as response:
                    if response.status_code == 404:
                        raise PDFCacheError("PDF not found at source", status_code=404)
                    if response.status_code >= 400:
                        raise PDFCacheError(
                            f"Upstream PDF request failed with {response.status_code}", status_code=502
                        )

                    total = 0
                    first_chunk: bytes | None = None
                    try:
                        with tmp_path.open("wb") as handle:
                            for chunk in response.iter_bytes(65536):
                                if not chunk:
                                    continue
                                if first_chunk is None:
                                    first_chunk = chunk[:8]
                                total += len(chunk)
                                if self.max_bytes and total > self.max_bytes:
                                    raise PDFCacheError(
                                        "PDF exceeds configured size limit",
                                        status_code=413,
                                    )
                                handle.write(chunk)
                    except Exception:
                        tmp_path.unlink(missing_ok=True)
                        raise

            if not tmp_path.exists():
                raise PDFCacheError("PDF download failed", status_code=502)

            if first_chunk is None or b"%PDF" not in first_chunk:
                tmp_path.unlink(missing_ok=True)
                raise PDFCacheError("Fetched content does not appear to be a PDF", status_code=415)

            tmp_path.replace(destination)
        except httpx.TimeoutException as exc:
            tmp_path.unlink(missing_ok=True)
            raise PDFCacheError("Timed out while downloading PDF", status_code=504) from exc
        except httpx.HTTPError as exc:
            tmp_path.unlink(missing_ok=True)
            raise PDFCacheError(f"Failed to download PDF: {exc}") from exc

        if destination.stat().st_size == 0:
            destination.unlink(missing_ok=True)
            raise PDFCacheError("Downloaded PDF was empty", status_code=502)