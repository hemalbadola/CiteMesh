# Academic Research Repository — Presentation & Viva Brief

## 1. Project Snapshot
- **Goal:** Provide a campus-friendly portal that curates research papers in real time, highlights citation impact, and consolidates access to full-text resources.
- **Primary Data Source:** OpenAlex Works API (live queries, no static dumps).
- **AI Layer:** Gemini (Google Generative Language API) translates natural-language questions into structured OpenAlex requests.
- **Core Deliverables:** Normalized PostgreSQL schema, AI-assisted backend service, caching strategy, CI-tested codebase, and demo-ready scripts.

## 2. Problem Context
- Research discovery is fragmented across publisher portals and search engines.
- Citation awareness demands multiple tools; open-access links are inconsistent.
- Universities need a centralized discovery experience that respects licensing while keeping data fresh.

## 3. Functional Objectives
1. Translate natural-language research questions into precise API filters.
2. Surface high-impact works with citation counts, years, and venues.
3. Expose open-access links (or cached PDFs) directly inside our UI.
4. Maintain a structured database for analytics and historical snapshots.
5. Automate quality checks (tests, linting, type safety) in CI.

## 4. Team Allocation
| Member | Primary Scope (after reassignment) |
| --- | --- |
| **Hemal** | AI-driven backend: FastAPI service, Gemini integration, OpenAlex client, PDF proxy, caching, CI automation. |
| **Ayush** | Data architecture: normalization proofs, PostgreSQL DDL, data dictionary, sample loads, schema documentation. |
| **Maaz** | Query optimization, benchmarking scripts, demo datasets (see `maaz/`). |
| **Naincy** | Documentation templates, contributor onboarding assets (see `naincy/`). |

## 5. Solution Architecture
1. **Client Layer (future):** Will consume `/search` and render results with embedded PDFs.
2. **API Layer (`hemal/backend`):**
   - `/search`: Accepts `{query, page, per_page}`.
   - `ai_query.py`: Rotates Gemini keys, enforces JSON schema, appends safe defaults (select fields).
   - `openalex_client.py`: Applies retries, rate-limit handling, caching, and JSON validation.
   - `pdf_cache.py`: Downloads OA PDFs (with signature + size checks) and serves them via `/pdf`.
3. **Data Layer (`ayush/ddl` + dictionary):**
   - Tables: `institutions`, `authors`, `works`, `concepts`, bridge tables for many-to-many links.
   - Constraints and indexes tuned for citation queries and timeline analytics.
   - Sample scripts for loading incremental snapshots.
4. **Automation:** GitHub Actions CI runs tests, flake8, black, mypy with environment stubs.

## 6. Detailed Backend Flow
1. User posts natural-language query to `/search`.
2. Gemini translates into `{base_url, params}` (e.g., filters, sort, per-page) with enforced JSON.
3. Service augments params with `select=` fields (to retrieve OA metadata) and optional pagination.
4. `OpenAlexClient` fetches results, writing/reading file-based cache when enabled.
5. Response returns:
   - `results`: Raw OpenAlex payload (with `open_access` block).
   - `pagination`: Derived metadata (page, per_page, next/prev hints, total count).
   - `source`: Original OpenAlex endpoint for transparency.
6. When the UI needs full text, it requests `/pdf?url=<oa_url>`:
   - `PDFCache` validates scheme, size (< configured MB), and PDF signature before returning `application/pdf` stream.

## 7. Database Highlights
- **Design:** Fully normalized to 3NF with surrogate UUIDs.
- **Key Tables:**
  - `works` (core papers, citations, OA flags).
  - `authors`, `concepts`, `institutions`, `venues` with linking tables (`author_works`, `work_concepts`, etc.).
  - Audit columns for ingestion timestamps.
- **Indexes:** Composite indexes on `(publication_year, cited_by_count)` to support trending queries.
- **Sample Data Scripts:** Located in `ayush/test-load/` for quick schema validation.

## 8. Feature Matrix
| Feature | Status | Notes |
| --- | --- | --- |
| Natural language to OpenAlex translation | ✅ | Gemini 2.0 Flash-Lite via rotating API keys. |
| Pagination & caching | ✅ | File cache gateable via `ENABLE_CACHE`. |
| OA PDF proxy | ✅ | Streams PDFs through `/pdf`, enforces size + signature checks. |
| Schema & data dictionary | ✅ | `ayush/ddl/schema.sql`, `data-dictionary/` docs. |
| Front-end UI | ⏳ | Pending; follow-up sprint once backend stabilizes. |
| Analytics dashboards | ⏳ | Needs materialized views + visualization layer. |

## 9. Testing & Quality Gates
- **Unit Tests:** `hemal/backend/tests/test_app.py` mocks Gemini/OpenAlex/PDF cache paths.
- **CI:** `.github/workflows/ci.yml` runs pytest, flake8, black, mypy in GitHub Actions (working dir now `hemal/backend`).
- **Manual QA:** Demo scripts in `hemal/demo-queries/` show real queries (RL papers, OA ratios, etc.).

## 10. Demo Script (for PPT Walkthrough)
1. **Slide:** Problem statement & objectives.
2. **Slide:** Architecture diagram (client → backend → OpenAlex/Gemini → DB).
3. **Live Step:** Run `pytest` to show green suite.
4. **Live Step:** Execute sample query:
   ```bash
   cd hemal/backend
   source .venv/bin/activate
   uvicorn app:app --reload
   # In another terminal
   curl -X POST http://127.0.0.1:8000/search \
     -H 'Content-Type: application/json' \
     -d '{"query": "Find the most cited reinforcement learning papers since 2021"}'
   ```
5. **Highlight:** Show response snippet with `open_access` block and derived `/pdf?url=...` link.
6. **Live Step:** Hit `/pdf?url=<OA link>` and display cached PDF via browser (or mention HTML fallback if blocked).
7. **Slide:** Database schema overview (ER diagram + key tables).
8. **Slide:** Future roadmap (UI, analytics, user accounts, recommendation engine).

## 11. Viva Talking Points & Potential Questions
- **Why OpenAlex?**
  - Free, comprehensive, offers citation metadata and OA indicators; stable rate limits.
- **How do you ensure Gemini responses are safe?**
  - Forced JSON output, strict schema validation, fallback on search term, and filter sanitization (we drop unsupported keys).
- **How do you respect copyright?**
  - Only proxy PDFs flagged as Open Access; PDF cache enforces format + size checks and honors upstream errors.
- **What happens if Gemini fails?**
  - `QueryTranslationError` surfaces `422`; UI should prompt manual filters.
- **Scalability concerns?**
  - Cache + retries reduce load; can migrate to Redis/S3 later.
- **Extending to UI?**
  - Plan to embed PDF.js pointing to `/pdf`, with search facets powered by the same backend.
- **DB usefulness when we rely on live APIs?**
  - Stores snapshots, citation analytics, and institutional trend archives; supports offline reporting.

## 12. Next Steps & Future Enhancements
- Build React or Next.js frontend with search facets, result cards, and inline PDF viewer.
- Add background worker to prefetch PDFs and warm caches for popular queries.
- Implement user accounts with saved searches and alerting.
- Integrate additional OA sources (CORE, Semantic Scholar) for fallback PDFs.
- Schedule nightly OpenAlex ingests into PostgreSQL for longitudinal analytics.

## 13. Appendix — Key Paths After Reassignment
- **Backend & AI assets:** `hemal/backend/`
- **Schema & documentation:** `ayush/ddl/`, `ayush/data-dictionary/`
- **CI Workflow:** `.github/workflows/ci.yml`
- **Environment samples:** `hemal/backend/.env.example`
- **Presentation brief (this file):** `docs/viva_presentation_brief.md`

> Use this document as the script for the PPT narration and viva prep. Each section maps directly to one or more slides, ensuring technical depth plus clear demo steps.
