"""Tests for the FastAPI application services with mocked dependencies."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

import app as app_module
from ai_query import OpenAlexAPIRequest, QueryTranslationError
from openalex_client import OpenAlexError
from pdf_cache import PDFCacheError


def test_search_missing_query_field() -> None:
    client = TestClient(app_module.app)
    response = client.post("/search", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing 'query' in request body"


def test_search_invalid_page() -> None:
    client = TestClient(app_module.app)
    response = client.post("/search", json={"query": "artificial intelligence", "page": 0})
    assert response.status_code == 400
    assert response.json()["detail"] == "'page' must be a positive integer"


def test_search_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(app_module.app)

    async def fake_translate(query: str, settings: Any) -> OpenAlexAPIRequest:  # noqa: ANN401
        return OpenAlexAPIRequest(
            url="https://api.openalex.org/works",
            params={"search": "ai"},
        )

    monkeypatch.setattr(app_module, "query_to_openalex", fake_translate)
    monkeypatch.setattr(
        app_module.client,
        "fetch",
        lambda request: {
            "meta": {"count": 100, "page": 1, "per-page": 25},
            "results": [1, 2, 3],
        },
    )

    response = client.post("/search", json={"query": "show me ai", "page": 2, "per_page": 10})
    assert response.status_code == 200
    body = response.json()
    assert body["results"]["results"] == [1, 2, 3]
    assert body["pagination"]["page"] == 2
    assert body["pagination"]["per_page"] == 10
    assert body["pagination"]["prev_page"] == 1
    assert body["pagination"]["next_page"] == 3


def test_search_translation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(app_module.app)

    async def fake_translate(query: str, settings: Any) -> OpenAlexAPIRequest:  # noqa: ANN401
        raise QueryTranslationError("could not translate")

    monkeypatch.setattr(app_module, "query_to_openalex", fake_translate)

    response = client.post("/search", json={"query": "bad query"})
    assert response.status_code == 422
    assert response.json()["detail"] == "could not translate"


def test_search_openalex_error(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(app_module.app)

    async def fake_translate(query: str, settings: Any) -> OpenAlexAPIRequest:  # noqa: ANN401
        return OpenAlexAPIRequest(url="", params={})

    monkeypatch.setattr(app_module, "query_to_openalex", fake_translate)

    def fake_fetch(_: OpenAlexAPIRequest) -> dict[str, Any]:  # noqa: ANN401
        raise OpenAlexError("boom")

    monkeypatch.setattr(app_module.client, "fetch", fake_fetch)

    response = client.post("/search", json={"query": "test query"})
    assert response.status_code == 502
    assert response.json()["detail"] == "boom"


def test_pdf_proxy_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    client = TestClient(app_module.app)

    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test")

    class StubCache:
        def get_or_fetch(self, url: str) -> Path:  # noqa: ANN401
            assert url == "https://example.com/test.pdf"
            return pdf_path

    monkeypatch.setattr(app_module, "pdf_cache", StubCache())

    response = client.get("/pdf", params={"url": "https://example.com/test.pdf"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.content.startswith(b"%PDF")


def test_pdf_proxy_error(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(app_module.app)

    class StubCache:
        def get_or_fetch(self, url: str) -> Path:  # noqa: ANN401
            raise PDFCacheError("bad url", status_code=400)

    monkeypatch.setattr(app_module, "pdf_cache", StubCache())

    response = client.get("/pdf", params={"url": "notaurl"})
    assert response.status_code == 400
    assert response.json()["detail"] == "bad url"
