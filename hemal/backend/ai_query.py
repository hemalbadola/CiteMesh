"""Translate natural language queries into OpenAlex API requests."""
from __future__ import annotations

from dataclasses import dataclass
import json
from itertools import cycle
from typing import Any, Optional

import httpx

from config import Settings


class QueryTranslationError(RuntimeError):
    """Raised when the AI service cannot translate the user query."""


@dataclass
class OpenAlexAPIRequest:
    """Container for the translated API request."""

    url: str
    params: dict[str, Any]


_KEY_CYCLE: Optional[cycle[str]] = None
_KEY_SNAPSHOT: tuple[str, ...] = ()

SYSTEM_PROMPT = (
    "You translate natural language research questions into OpenAlex API calls. "
    "Always respond with JSON containing base_url (string) and params (object). "
    "IMPORTANT: Valid OpenAlex parameters are ONLY: search, filter, sort, per_page, page, select, cursor. "
    "Use 'search' for keywords/topics. Use 'filter' for constraints (must be comma-separated string). "
    "Filter syntax examples: 'publication_year:2024', 'publication_year:2020-2023', 'cited_by_count:>50'. "
    "Combine filters with commas: 'publication_year:2024,cited_by_count:>100'. "
    "DO NOT use publication_year as a separate parameter - it must be inside the filter string. "
    "Sort format: 'cited_by_count:desc' or 'publication_date:desc'. "
    "Always include a 'search' parameter for the main topic."
)


def _next_api_key(settings: Settings) -> str:
    """Return the next API key in a rotation."""
    global _KEY_CYCLE, _KEY_SNAPSHOT

    if not settings.ai_api_keys:
        raise QueryTranslationError("AI_API_KEYS environment variable is not configured")

    if settings.ai_api_keys != _KEY_SNAPSHOT or _KEY_CYCLE is None:
        _KEY_SNAPSHOT = settings.ai_api_keys
        _KEY_CYCLE = cycle(_KEY_SNAPSHOT)

    return next(_KEY_CYCLE)


async def _call_gemini(prompt: str, settings: Settings, retry_count: int = 0) -> str:
    """Call Gemini API with retry logic and multiple fallback strategies."""
    max_retries = min(3, len(settings.ai_api_keys))
    
    api_key = _next_api_key(settings)
    url = f"{settings.ai_base_url}/{settings.ai_model}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            SYSTEM_PROMPT
                            + "\n\nTranslate the following request and return a JSON object with keys "
                            "base_url (string) and params (object). Ensure params keys align with "
                            "OpenAlex filtering syntax.\n\n"
                            + prompt
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
            "topP": 0.9,
            "maxOutputTokens": 512,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(url, json=payload)

        if response.status_code >= 400:
            error_msg = f"AI API error: {response.status_code} {response.text[:200]}"
            
            # Retry with next API key if we have retries left
            if retry_count < max_retries:
                return await _call_gemini(prompt, settings, retry_count + 1)
            
            raise QueryTranslationError(error_msg)

        data = response.json()
        try:
            content_text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            # Retry if response format is unexpected
            if retry_count < max_retries:
                return await _call_gemini(prompt, settings, retry_count + 1)
            raise QueryTranslationError("Unexpected AI response format") from exc

        return content_text
        
    except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as exc:
        # Network errors - retry with next API key
        if retry_count < max_retries:
            return await _call_gemini(prompt, settings, retry_count + 1)
        raise QueryTranslationError(f"Network error calling AI API: {str(exc)}") from exc
    except Exception as exc:
        # Unexpected errors - retry once
        if retry_count < max_retries:
            return await _call_gemini(prompt, settings, retry_count + 1)
        raise QueryTranslationError(f"Unexpected error calling AI API: {str(exc)}") from exc


async def _call_llm(prompt: str, settings: Settings) -> str:
    if settings.ai_provider.lower() == "gemini":
        return await _call_gemini(prompt, settings)

    raise QueryTranslationError(f"Unsupported AI provider: {settings.ai_provider}")


def _validate_translation(translation: dict[str, Any]) -> OpenAlexAPIRequest:
    """Ensure translation contains expected keys and build request container."""
    base_url = translation.get("base_url") or "https://api.openalex.org/works"
    params = translation.get("params")

    if not isinstance(params, dict):
        raise QueryTranslationError("Translation missing 'params' object")

    # Whitelist of valid OpenAlex parameters
    VALID_PARAMS = {"search", "filter", "sort", "per_page", "page", "select", "cursor", "group_by"}
    
    # Remove any invalid parameters the AI might have added
    invalid_params = set(params.keys()) - VALID_PARAMS
    for invalid_param in invalid_params:
        print(f"⚠️  Removing invalid parameter: {invalid_param}")
        del params[invalid_param]

    # Ensure filter is properly formatted
    raw_filter = params.get("filter")
    if isinstance(raw_filter, dict):
        parts = []
        for key, value in raw_filter.items():
            if value is None:
                continue
            if key == "concepts.display_name":
                # Rely on the broader search term rather than an unsupported concept filter.
                continue
            parts.append(f"{key}:{value}")
        params["filter"] = ",".join(parts) if parts else None
    elif isinstance(raw_filter, str):
        parts = []
        for segment in raw_filter.split(","):
            piece = segment.strip()
            if piece.startswith("concepts.display_name:"):
                continue
            if piece:  # Only add non-empty segments
                parts.append(piece)
        params["filter"] = ",".join(parts) if parts else None
    
    # Remove filter if it's empty
    if not params.get("filter"):
        params.pop("filter", None)
    
    # Validate per_page is reasonable (max 200 for OpenAlex)
    if "per_page" in params:
        try:
            per_page = int(params["per_page"])
            params["per_page"] = min(max(1, per_page), 200)
        except (ValueError, TypeError):
            params["per_page"] = 10  # Default

    return OpenAlexAPIRequest(url=base_url, params=params)


def _extract_json_text(raw_text: str) -> str:
    """Strip Markdown fences or prefixes before parsing JSON."""
    stripped = raw_text.strip()
    if not stripped.startswith("```"):
        return stripped

    lines = stripped.splitlines()
    # Drop opening fence
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    # Drop closing fence
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    # Remove optional language hint on first line
    if lines and lines[0].lower().startswith("json"):
        lines = lines[1:]

    return "\n".join(lines).strip()


def _create_fallback_request(user_query: str) -> OpenAlexAPIRequest:
    """Create a basic fallback request when AI translation fails."""
    import re
    
    # Extract potential year mentions
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, user_query)
    
    # Build basic filter
    filters = []
    if years:
        latest_year = max(years)
        filters.append(f"publication_year:{latest_year}")
    
    # Check for common keywords that indicate constraints
    if any(word in user_query.lower() for word in ['open access', 'oa', 'free']):
        filters.append("is_oa:true")
    
    if any(word in user_query.lower() for word in ['highly cited', 'popular', 'influential']):
        filters.append("cited_by_count:>50")
    
    # Build params
    params = {
        "search": user_query,
        "select": "id,title,display_name,publication_year,cited_by_count,primary_location,open_access,doi",
        "per_page": 10,
    }
    
    if filters:
        params["filter"] = ",".join(filters)
    
    # Sort by relevance by default
    params["sort"] = "cited_by_count:desc"
    
    return OpenAlexAPIRequest(
        url="https://api.openalex.org/works",
        params=params
    )


async def query_to_openalex(user_query: str, settings: Settings) -> OpenAlexAPIRequest:
    """Translate a user query into an OpenAlex request asynchronously with fallback."""
    prompt = (
        "Turn the following request into an OpenAlex works API call. "
        "Return JSON {\"base_url\": \"https://api.openalex.org/works\", \"params\": {...}}. "
        "CRITICAL: params must only use these keys: search, filter, sort, per_page, page. "
        "The 'filter' value must be a STRING with comma-separated filters like 'publication_year:2024,cited_by_count:>50'. "
        "Example: {\"base_url\": \"https://api.openalex.org/works\", \"params\": {\"search\": \"quantum computing\", \"filter\": \"publication_year:2024\", \"sort\": \"cited_by_count:desc\"}}. "
        f"Request: {user_query}"
    )

    try:
        # Try AI translation first
        response_content = await _call_llm(prompt, settings)
        
        try:
            json_payload = _extract_json_text(response_content)
            translation = json.loads(json_payload)
        except json.JSONDecodeError as exc:
            # JSON parsing failed - try fallback
            print(f"⚠️  AI response not valid JSON, using fallback for: {user_query}")
            return _create_fallback_request(user_query)

        request = _validate_translation(translation)
        request.params.setdefault("search", user_query)
        request.params.setdefault(
            "select",
            "id,title,display_name,publication_year,cited_by_count,primary_location,open_access,doi",
        )
        return request
        
    except QueryTranslationError as exc:
        # AI translation completely failed - use fallback
        print(f"⚠️  AI translation failed ({str(exc)}), using fallback for: {user_query}")
        return _create_fallback_request(user_query)
    except Exception as exc:
        # Unexpected error - use fallback as last resort
        print(f"⚠️  Unexpected error ({str(exc)}), using fallback for: {user_query}")
        return _create_fallback_request(user_query)
