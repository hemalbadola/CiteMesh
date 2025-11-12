# API Notes

## Overview
- **Endpoint:** `POST /search`
- **Payload:** `{ "query": "Find top cited AI papers since 2021" }`
- **Success Response:**
  ```json
  {
    "results": {"results": [...]},
    "source": "https://api.openalex.org/works"
  }
  ```
- **Error Codes:**
  - `400` missing payload field `query`
  - `422` AI translator failed to interpret the request
  - `502` OpenAlex returned an upstream error (timeout, 429, invalid JSON)

## Configuration
Set environment variables (or add to a `.env` loaded by your process manager):

```
AI_PROVIDER=gemini
AI_MODEL=gemini-2.0-flash-lite
AI_BASE_URL=https://generativelanguage.googleapis.com/v1/models
AI_API_KEYS=KEY1,KEY2,KEY3
OPENALEX_BASE_URL=https://api.openalex.org
REQUEST_TIMEOUT_SECONDS=15
ENABLE_CACHE=true
CACHE_DIR=cache
PDF_CACHE_DIR=pdf_cache
PDF_MAX_DOWNLOAD_MB=20
PDF_DOWNLOAD_TIMEOUT_SECONDS=20
```

- Keys rotate automatically; provide a comma-separated list in `AI_API_KEYS`.
- Never commit actual keys into source control—use deployment secrets or `.env` ignored by git.

## Running Locally
```bash
cd hemal/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## Pagination
- Optional request fields: `page` (default 1) and `per_page` (default 25)
- The backend appends these parameters to the translated OpenAlex request.
- Response includes a `pagination` block with `next_page` and `prev_page` hints calculated from OpenAlex metadata.

## Caching
- File-based cache stored under `CACHE_DIR` (default `cache/`).
- Enabled when `ENABLE_CACHE=true`.
- Cache key is a hash of the full OpenAlex URL and parameters.
- Subsequent identical queries return cached responses instantly.

## Rate Limits & Retries
- `openalex_client.OpenAlexClient` retries requests up to three times.
- Handles 429 responses by honoring `Retry-After` headers with exponential backoff.
- Surfaces clear errors if retries fail or JSON is malformed.

## Testing
- Unit tests mock external services:
  ```bash
  pytest
  ```
- Add additional tests that simulate rate limits and malformed responses as needed.

## Implementation Notes
1. `ai_query.query_to_openalex` calls the Gemini API with strict JSON response instructions.
2. `openalex_client.OpenAlexClient.fetch` wraps HTTP errors, rate limits, and invalid responses with retry/backoff.
3. Caching is transparent to callers and controlled via environment variables.
4. CI via GitHub Actions (`.github/workflows/ci.yml`) runs tests, linting, formatting, and type checks on each push/PR.
