"""FastAPI entry point for the OpenAlex-powered research query service."""
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from ai_query import QueryTranslationError, query_to_openalex
from cache import CacheStore
from config import settings
from openalex_client import OpenAlexClient, OpenAlexError
from pdf_cache import PDFCache, PDFCacheError

app = FastAPI(title="Research Query Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache_store = CacheStore(settings.cache_dir) if settings.enable_cache else None

client = OpenAlexClient(
    base_url=settings.openalex_base_url,
    timeout_seconds=settings.request_timeout_seconds,
    session=None,
    cache=cache_store,
)

pdf_cache = PDFCache(
    root=settings.pdf_cache_dir,
    timeout_seconds=settings.pdf_download_timeout_seconds,
    max_bytes=int(settings.pdf_max_download_mb * 1024 * 1024),
)


@app.post("/search")
async def search(request: Request) -> dict:
    """Translate a natural language query and return OpenAlex results."""
    payload = await request.json()
    user_query = payload.get("query")
    page = payload.get("page")
    per_page = payload.get("per_page")

    # Validate and sanitize query
    if not user_query:
        raise HTTPException(status_code=400, detail="Missing 'query' in request body")
    
    if not isinstance(user_query, str):
        raise HTTPException(status_code=400, detail="'query' must be a string")
    
    # Sanitize query - remove excessive whitespace and limit length
    user_query = " ".join(user_query.strip().split())
    if len(user_query) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters long")
    
    if len(user_query) > 500:
        raise HTTPException(status_code=400, detail="Query is too long (max 500 characters)")

    if page is not None:
        try:
            page = int(page)
            if page < 1:
                raise ValueError
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="'page' must be a positive integer")

    if per_page is not None:
        try:
            per_page = int(per_page)
            if per_page < 1 or per_page > 200:
                raise ValueError
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="'per_page' must be between 1 and 200")

    try:
        api_request = await query_to_openalex(user_query, settings=settings)
    except QueryTranslationError as exc:
        # This should rarely happen now with fallback mechanism
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        # Catch any unexpected errors and provide user-friendly message
        print(f"❌ Unexpected error in search endpoint: {str(exc)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred processing your query. Please try again."
        ) from exc

    if page is not None:
        api_request.params["page"] = page
    if per_page is not None:
        api_request.params["per_page"] = per_page

    try:
        results = client.fetch(api_request)
    except OpenAlexError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    meta = results.get("meta", {}) if isinstance(results, dict) else {}
    current_page = int(page or meta.get("page", 1))
    current_per_page = int(per_page or meta.get("per_page", meta.get("per-page", 25)))
    total_count = meta.get("count")

    next_page = None
    prev_page = None
    if isinstance(total_count, int) and total_count >= 0:
        total_pages = (total_count + current_per_page - 1) // current_per_page
        if current_page < total_pages:
            next_page = current_page + 1
    if current_page > 1:
        prev_page = current_page - 1

    return {
        "results": results,
        "source": api_request.url,
        "pagination": {
            "page": current_page,
            "per_page": current_per_page,
            "next_page": next_page,
            "prev_page": prev_page,
            "total_count": total_count,
        },
    }


@app.get("/pdf")
def proxy_pdf(url: str = Query(..., description="Open Access PDF URL")) -> FileResponse:
    """Download (if needed) and stream an Open Access PDF through the service."""
    try:
        pdf_path = pdf_cache.get_or_fetch(url)
    except PDFCacheError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )
