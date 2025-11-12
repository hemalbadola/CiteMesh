# `hemal`

This folder now owns the AI-assisted backend that orchestrates Gemini translations, OpenAlex queries, and PDF proxying.

## Expected Deliverables
- FastAPI application code for `/search` and supporting services
- Gemini prompt/translation utilities with key rotation and JSON validation
- OpenAlex client with caching, retries, pagination, and response shaping
- PDF caching proxy assets plus documentation for OA retrieval
- Automated tests, CI configurations, and demo scripts for the service layer

## Organization Guidelines
- Keep the FastAPI project rooted under `backend/` with code, tests, and docs grouped by module.
- Store demo queries in `demo-queries/` and usage notes inside `docs/`.
- Use `optimization/` and `queries/` for performance experiments or saved request templates.
- Place archival experiments inside `archive/` to preserve historical context without cluttering the main workspace.
