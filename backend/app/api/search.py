from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import requests
from datetime import datetime
from sqlmodel import Session, select
from app.core.api_key_rotator import get_gemini_key
from app.core.firebase_auth import FirebaseUser, get_current_user
from app.db import get_session
from app.models import SavedPaper
from app.services.search_cache import SearchCacheService, SearchHistoryService
from app.services.paper_enrichment import PaperEnrichmentService
import json
import time

router = APIRouter()

# OpenAlex API Configuration
# Using Walden rewrite (launched Nov 2025) - 190M+ new works including datasets, software
# data-version=2: Activates Walden backend with better metadata, references, and OA detection
# include_xpac=true: Includes expanded content pack from DataCite and repositories
OPENALEX_BASE_URL = "https://api.openalex.org"
OPENALEX_EMAIL = "your-email@example.com"  # Add to .env for polite pool

# Pydantic Models
class SearchFilters(BaseModel):
    """Search filter options"""
    year_from: Optional[int] = Field(None, ge=1900, le=2024, description="Start year")
    year_to: Optional[int] = Field(None, ge=1900, le=2024, description="End year")
    min_citations: Optional[int] = Field(None, ge=0, description="Minimum citation count")
    max_citations: Optional[int] = Field(None, ge=0, description="Maximum citation count")
    authors: Optional[List[str]] = Field(None, description="Filter by author names")
    institutions: Optional[List[str]] = Field(None, description="Filter by institution names")
    open_access: Optional[bool] = Field(None, description="Only open access papers")
    has_fulltext: Optional[bool] = Field(None, description="Only papers with full text")
    sort_by: Optional[str] = Field("relevance", description="Sort by: relevance, cited_by_count, publication_date")

class SearchRequest(BaseModel):
    """Search request with query and filters"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    filters: Optional[SearchFilters] = None
    page: int = Field(1, ge=1, le=200, description="Page number")
    per_page: int = Field(25, ge=1, le=100, description="Results per page")
    use_ai_enhancement: bool = Field(True, description="Use AI to enhance query")

class PaperAuthor(BaseModel):
    """Author information"""
    id: Optional[str] = None
    name: str
    institution: Optional[str] = None

class PaperConcept(BaseModel):
    """Research concept/topic"""
    id: str
    name: str
    score: float

class SearchResult(BaseModel):
    """Single paper search result"""
    id: str
    title: str
    authors: List[PaperAuthor]
    publication_date: Optional[str] = None
    publication_year: Optional[int] = None
    venue: Optional[str] = None
    cited_by_count: int
    doi: Optional[str] = None
    pdf_url: Optional[str] = None
    abstract: Optional[str] = None
    concepts: List[PaperConcept] = []
    open_access: bool = False
    relevance_score: Optional[float] = None

class SearchResponse(BaseModel):
    """Search response with results and metadata"""
    query: str
    enhanced_query: Optional[str] = None
    results: List[SearchResult]
    total_results: int
    page: int
    per_page: int
    total_pages: int
    search_time_ms: int

class SuggestResponse(BaseModel):
    """Query suggestion response"""
    original_query: str
    suggestions: List[str]
    enhanced_query: str


def enhance_query_with_ai(query: str) -> Optional[str]:
    """
    Use Gemini AI to enhance the search query with academic keywords
    """
    try:
        api_key = get_gemini_key()
        if not api_key:
            return None
            
        prompt = f"""You are an academic search assistant. Enhance this research query with relevant academic keywords and concepts.
        
Original query: "{query}"

Provide an enhanced search query that:
1. Adds relevant academic terminology
2. Includes synonyms and related concepts
3. Uses proper academic language
4. Keeps it concise (max 100 words)

Return ONLY the enhanced query text, no explanation or formatting."""

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 200
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                enhanced = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                return enhanced
                
        return None
        
    except Exception as e:
        print(f"AI enhancement error: {e}")
        return None


def build_openalex_filter(filters: Optional[SearchFilters]) -> str:
    """
    Build OpenAlex filter string from SearchFilters
    """
    if not filters:
        return ""
    
    filter_parts = []
    
    # Year range
    if filters.year_from or filters.year_to:
        year_from = filters.year_from or 1900
        year_to = filters.year_to or 2024
        filter_parts.append(f"publication_year:{year_from}-{year_to}")
    
    # Citation count
    if filters.min_citations is not None:
        filter_parts.append(f"cited_by_count:>{filters.min_citations}")
    if filters.max_citations is not None:
        filter_parts.append(f"cited_by_count:<{filters.max_citations}")
    
    # Open access
    if filters.open_access:
        filter_parts.append("is_oa:true")
    
    # Has fulltext
    if filters.has_fulltext:
        filter_parts.append("has_fulltext:true")
    
    # Authors (use display_name search)
    if filters.authors:
        author_filters = [f'authorships.author.display_name:"{author}"' for author in filters.authors]
        filter_parts.append(f"({','.join(author_filters)})")
    
    # Institutions
    if filters.institutions:
        inst_filters = [f'authorships.institutions.display_name:"{inst}"' for inst in filters.institutions]
        filter_parts.append(f"({','.join(inst_filters)})")
    
    return ",".join(filter_parts)


def parse_openalex_work(work: Dict[str, Any]) -> SearchResult:
    """
    Parse OpenAlex work JSON into SearchResult model
    """
    # Extract authors
    authors = []
    for authorship in work.get("authorships", [])[:10]:  # Limit to 10 authors
        author_data = authorship.get("author", {})
        institutions = authorship.get("institutions", [])
        institution_name = institutions[0].get("display_name") if institutions else None
        
        authors.append(PaperAuthor(
            id=author_data.get("id"),
            name=author_data.get("display_name", "Unknown Author"),
            institution=institution_name
        ))
    
    # Extract concepts
    concepts = []
    for concept in work.get("concepts", [])[:5]:  # Top 5 concepts
        concepts.append(PaperConcept(
            id=concept.get("id", ""),
            name=concept.get("display_name", ""),
            score=concept.get("score", 0.0)
        ))
    
    # Extract publication venue
    venue = None
    if work.get("primary_location"):
        source = work["primary_location"].get("source")
        if source:
            venue = source.get("display_name")
    
    # Extract PDF URL
    pdf_url = None
    if work.get("open_access"):
        pdf_url = work["open_access"].get("oa_url")
    
    # Extract abstract
    abstract = None
    if work.get("abstract_inverted_index"):
        # Reconstruct abstract from inverted index
        inverted = work["abstract_inverted_index"]
        words = [""] * (max(max(positions) for positions in inverted.values()) + 1)
        for word, positions in inverted.items():
            for pos in positions:
                words[pos] = word
        abstract = " ".join(words)
    
    return SearchResult(
        id=work.get("id", ""),
        title=work.get("title", "Untitled"),
        authors=authors,
        publication_date=work.get("publication_date"),
        publication_year=work.get("publication_year"),
        venue=venue,
        cited_by_count=work.get("cited_by_count", 0),
        doi=work.get("doi"),
        pdf_url=pdf_url,
        abstract=abstract,
        concepts=concepts,
        open_access=work.get("open_access", {}).get("is_oa", False)
    )


@router.post("/search", response_model=SearchResponse)
async def search_papers(
    request: SearchRequest,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Search for academic papers using OpenAlex API with optional AI query enhancement
    
    DBMS SHOWCASE FEATURES:
    - Search result caching with TTL (reduces API calls)
    - Search history tracking (user behavior analytics)
    - Cache hit/miss tracking (performance metrics)
    - Composite indexes for fast cache lookups
    
    Features:
    - Full-text and title search
    - AI-powered query enhancement
    - Advanced filtering (year, citations, authors, institutions)
    - Open access filtering
    - Relevance and citation-based sorting
    
    Requires authentication.
    """
    start_time = time.time()
    
    # Enhance query with AI if requested
    enhanced_query = None
    search_query = request.query
    
    if request.use_ai_enhancement:
        enhanced_query = enhance_query_with_ai(request.query)
        if enhanced_query:
            search_query = enhanced_query
    
    # Prepare filters dict for cache key
    filters_dict = request.filters.dict() if request.filters else None
    
    # ===============================================
    # DBMS FEATURE: Search Result Caching
    # Check cache first before hitting OpenAlex API
    # ===============================================
    cached_results = SearchCacheService.get_cached_results(
        session=session,
        query=search_query,
        filters=filters_dict,
        page=request.page,
        per_page=request.per_page
    )
    
    cache_hit = cached_results is not None
    
    if cached_results:
        # Parse cached results
        results = [SearchResult(**paper) for paper in cached_results.get("results", [])]
        total_results = cached_results.get("total_results", 0)
        data = cached_results  # Use cached data structure
    else:
        # Cache miss - query OpenAlex API
        api_start_time = time.time()
        
        # Build OpenAlex query parameters with Walden API
        params = {
            "search": search_query,
            "page": request.page,
            "per_page": request.per_page,
            "mailto": OPENALEX_EMAIL,
            "data-version": "2",  # Use new Walden rewrite (190M+ new works)
            "include_xpac": "true"  # Include expanded content from DataCite
        }
        
        # Add filters
        if request.filters:
            filter_str = build_openalex_filter(request.filters)
            if filter_str:
                params["filter"] = filter_str
            
            # Add sorting
            if request.filters.sort_by == "cited_by_count":
                params["sort"] = "cited_by_count:desc"
            elif request.filters.sort_by == "publication_date":
                params["sort"] = "publication_date:desc"
        
        # Make request to OpenAlex
        try:
            response = requests.get(
                f"{OPENALEX_BASE_URL}/works",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            api_time_ms = int((time.time() - api_start_time) * 1000)
            
            # Parse results
            results = []
            for work in data.get("results", []):
                try:
                    result = parse_openalex_work(work)
                    results.append(result)
                except Exception as e:
                    print(f"Error parsing work: {e}")
                    continue
            
            # Calculate pagination
            total_results = data.get("meta", {}).get("count", 0)
            
            # ===============================================
            # DBMS FEATURE: Save to Cache
            # Store results in database for future queries
            # ===============================================
            cache_data = {
                "results": [r.dict() for r in results],
                "total_results": total_results,
                "meta": data.get("meta", {})
            }
            
            SearchCacheService.save_to_cache(
                session=session,
                query=search_query,
                filters=filters_dict,
                results=cache_data,
                page=request.page,
                per_page=request.per_page,
                api_response_time_ms=api_time_ms
            )
        
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Search request timed out")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=502, detail=f"OpenAlex API error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
    
    # Calculate pagination
    total_results = len(results) if cache_hit else data.get("meta", {}).get("count", 0)
    total_pages = (total_results + request.per_page - 1) // request.per_page
    
    # Calculate total search time
    search_time_ms = int((time.time() - start_time) * 1000)
    
    # ===============================================
    # DBMS FEATURE: Log Search History
    # Track user search patterns for analytics
    # ===============================================
    SearchHistoryService.log_search(
        session=session,
        user_id=current_user.db_user.id,
        query=request.query,
        filters=filters_dict,
        results_count=len(results),
        page=request.page,
        search_time_ms=search_time_ms,
        use_ai_enhancement=request.use_ai_enhancement,
        enhanced_query=enhanced_query,
        cache_hit=cache_hit
    )
    
    return SearchResponse(
        query=request.query,
        enhanced_query=enhanced_query,
        results=results,
        total_results=total_results,
        page=request.page,
        per_page=request.per_page,
        total_pages=total_pages,
        search_time_ms=search_time_ms
    )


@router.get("/suggest")
async def suggest_queries(
    query: str = Query(..., min_length=1, max_length=200, description="Base query for suggestions")
):
    """
    Get AI-powered query suggestions and enhancements
    """
    try:
        api_key = get_gemini_key()
        if not api_key:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        
        prompt = f"""You are an academic research assistant. For this query: "{query}"

Provide:
1. An enhanced version with academic terminology
2. 3 related search suggestions

Return as JSON:
{{
    "enhanced": "enhanced query here",
    "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"]
}}"""

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": 300
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Extract JSON from response
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                
                try:
                    data = json.loads(text)
                    return SuggestResponse(
                        original_query=query,
                        suggestions=data.get("suggestions", []),
                        enhanced_query=data.get("enhanced", query)
                    )
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    pass
        
        # Fallback response
        return SuggestResponse(
            original_query=query,
            suggestions=[
                f"{query} recent advances",
                f"{query} systematic review",
                f"{query} applications"
            ],
            enhanced_query=query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion error: {str(e)}")


@router.get("/trending")
async def get_trending_topics(
    period: str = Query("week", description="Time period: day, week, month"),
    limit: int = Query(10, ge=1, le=50, description="Number of topics")
):
    """
    Get trending research topics from OpenAlex
    """
    try:
        # Map period to OpenAlex date range
        from_date_map = {
            "day": "2024-01-01",  # Adjust based on actual date
            "week": "2024-01-01",
            "month": "2023-12-01"
        }
        
        params = {
            "group_by": "concepts.id",
            "per_page": limit,
            "filter": f"publication_date:>{from_date_map.get(period, '2024-01-01')}",
            "mailto": OPENALEX_EMAIL,
            "data-version": "2",
            "include_xpac": "true"
        }
        
        response = requests.get(
            f"{OPENALEX_BASE_URL}/works",
            params=params,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        
        topics = []
        for group in data.get("group_by", []):
            topics.append({
                "id": group.get("key"),
                "name": group.get("key_display_name"),
                "count": group.get("count", 0)
            })
        
        return {
            "period": period,
            "topics": topics,
            "total": len(topics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trending topics error: {str(e)}")


@router.get("/stats")
async def get_search_stats(
    current_user: FirebaseUser = Depends(get_current_user),
):
    """
    Get OpenAlex database statistics
    
    Requires authentication.
    """
    try:
        response = requests.get(
            f"{OPENALEX_BASE_URL}/works",
            params={"per_page": 1, "mailto": OPENALEX_EMAIL, "data-version": "2", "include_xpac": "true"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        total_papers = data.get("meta", {}).get("count", 0)
        
        return {
            "total_papers": total_papers,
            "database": "OpenAlex",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


class SaveFromSearchRequest(BaseModel):
    """Request to save a paper from search results"""
    paper_id: str = Field(..., description="OpenAlex paper ID")
    title: str = Field(..., min_length=1, max_length=1000)
    authors: Optional[str] = Field(None, description="Comma-separated author names")
    summary: Optional[str] = Field(None, description="Paper abstract")
    published_year: Optional[int] = Field(None, ge=1900, le=2030)
    venue: Optional[str] = Field(None, description="Publication venue")
    doi: Optional[str] = None
    pdf_url: Optional[str] = None
    cited_by_count: Optional[int] = Field(None, ge=0)
    tags: Optional[str] = Field(None, description="User tags (comma-separated)")


class SavedPaperResponse(BaseModel):
    """Response after saving a paper"""
    id: int
    user_id: int
    paper_id: str
    title: str
    authors: Optional[str] = None
    summary: Optional[str] = None
    published_year: Optional[int] = None
    tags: Optional[str] = None
    saved_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/save-paper", response_model=SavedPaperResponse, status_code=status.HTTP_201_CREATED)
async def save_paper_from_search(
    request: SaveFromSearchRequest,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Save a paper from search results to user's library
    
    This endpoint allows users to directly save papers they find in search results.
    Includes all relevant metadata from OpenAlex.
    """
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be saved to database first"
        )
    
    # Check if paper already saved
    statement = select(SavedPaper).where(
        SavedPaper.user_id == current_user.id,
        SavedPaper.paper_id == request.paper_id,
    )
    existing = session.exec(statement).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Paper already saved to your library"
        )
    
    # Create saved paper record
    saved_paper = SavedPaper(
        user_id=current_user.id,
        paper_id=request.paper_id,
        title=request.title,
        authors=request.authors,
        summary=request.summary,
        published_year=request.published_year,
        tags=request.tags,
    )
    
    session.add(saved_paper)
    session.commit()
    session.refresh(saved_paper)
    
    return SavedPaperResponse.model_validate(saved_paper)


@router.get("/check-saved/{paper_id}")
async def check_if_paper_saved(
    paper_id: str,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Check if a paper is already saved in user's library
    
    Returns:
        - saved: boolean
        - saved_paper_id: database ID if saved, null otherwise
    """
    if current_user.id is None:
        return {"saved": False, "saved_paper_id": None}
    
    statement = select(SavedPaper).where(
        SavedPaper.user_id == current_user.id,
        SavedPaper.paper_id == paper_id,
    )
    existing = session.exec(statement).first()
    
    return {
        "saved": existing is not None,
        "saved_paper_id": existing.id if existing else None
    }


# =========================================================================
# DBMS SHOWCASE: ANALYTICS ENDPOINTS
# These endpoints demonstrate advanced database queries and aggregations
# =========================================================================

@router.get("/analytics/cache-stats")
async def get_cache_statistics(
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get search cache performance statistics
    
    DBMS Concepts Demonstrated:
    - Aggregate functions (COUNT, SUM, AVG)
    - Multiple aggregations in single query
    - Performance metrics calculation
    """
    stats = SearchCacheService.get_cache_statistics(session)
    return stats


@router.get("/analytics/trending-searches")
async def get_trending_searches(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get trending search queries across all users
    
    DBMS Concepts Demonstrated:
    - GROUP BY with aggregation
    - Time-based filtering
    - ORDER BY aggregate results
    - HAVING clause for group filtering
    """
    trending = SearchHistoryService.get_trending_searches(
        session=session,
        hours=hours,
        limit=limit
    )
    return {"trending_searches": trending}


@router.get("/analytics/my-search-history")
async def get_my_search_history(
    limit: int = Query(50, ge=1, le=200, description="Number of results"),
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get user's recent search history
    
    DBMS Concepts Demonstrated:
    - SELECT with WHERE clause
    - ORDER BY timestamp
    - LIMIT for pagination
    - Index usage (idx_search_history_user_time)
    """
    history = SearchHistoryService.get_user_search_history(
        session=session,
        user_id=current_user.db_user.id,
        limit=limit
    )
    
    return {
        "history": [
            {
                "query": h.query_text,
                "enhanced_query": h.enhanced_query,
                "results_count": h.results_count,
                "search_time_ms": h.search_time_ms,
                "use_ai_enhancement": h.use_ai_enhancement,
                "cache_hit": h.cache_hit,
                "created_at": h.created_at.isoformat()
            }
            for h in history
        ]
    }


@router.get("/analytics/my-search-stats")
async def get_my_search_statistics(
    days: int = Query(30, ge=1, le=365, description="Time window in days"),
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get personalized search analytics for current user
    
    DBMS Concepts Demonstrated:
    - Complex WHERE conditions with AND
    - Multiple COUNT queries with different filters
    - AVG aggregate function
    - Percentage calculations
    """
    stats = SearchHistoryService.get_user_search_statistics(
        session=session,
        user_id=current_user.db_user.id,
        days=days
    )
    return stats


@router.post("/admin/cleanup-cache")
async def cleanup_expired_cache(
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Remove expired cache entries (admin operation)
    
    DBMS Concepts Demonstrated:
    - DELETE with WHERE condition
    - Bulk delete operations
    - Index usage for efficient deletion
    """
    # In production, this would be restricted to admin users
    removed_count = SearchCacheService.cleanup_expired_cache(session)
    
    return {
        "removed_entries": removed_count,
        "message": f"Cleaned up {removed_count} expired cache entries"
    }


# =========================================================================
# DBMS SHOWCASE: PAPER ENRICHMENT ENDPOINTS
# Demonstrate normalized data storage and complex relationships
# =========================================================================

@router.post("/enrich/{saved_paper_id}")
async def enrich_saved_paper(
    saved_paper_id: int,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Enrich a saved paper with topics and references from OpenAlex
    
    DBMS Concepts Demonstrated:
    - Transaction management (all-or-nothing)
    - M:N relationships (paper-topics)
    - Foreign key constraints
    - Normalized data storage
    """
    # Verify paper belongs to user
    paper_stmt = select(SavedPaper).where(
        SavedPaper.id == saved_paper_id,
        SavedPaper.user_id == current_user.db_user.id
    )
    paper = session.exec(paper_stmt).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found or not owned by user"
        )
    
    # Enrich the paper
    enrichment_stats = PaperEnrichmentService.enrich_paper(
        session=session,
        paper_id=saved_paper_id,
        openalex_id=paper.paper_id
    )
    
    return enrichment_stats


@router.get("/paper/{saved_paper_id}/topics")
async def get_paper_topics(
    saved_paper_id: int,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get research topics for a paper
    
    DBMS Concepts Demonstrated:
    - JOIN operation (PaperTopic → ResearchTopic)
    - SELECT with ORDER BY
    - Composite indexes for fast lookups
    """
    topics = PaperEnrichmentService.get_paper_topics(
        session=session,
        paper_id=saved_paper_id
    )
    
    return {"topics": topics}


@router.get("/paper/{saved_paper_id}/references")
async def get_paper_references(
    saved_paper_id: int,
    limit: int = Query(50, ge=1, le=200),
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get papers cited by this paper
    
    DBMS Concepts Demonstrated:
    - Citation graph edges
    - Directed relationships
    - Pagination with LIMIT
    """
    references = PaperEnrichmentService.get_paper_references(
        session=session,
        paper_id=saved_paper_id,
        limit=limit
    )
    
    return {"references": references}


@router.get("/analytics/topic-statistics")
async def get_topic_statistics(
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get statistics about research topics in the database
    
    DBMS Concepts Demonstrated:
    - Aggregate functions (COUNT, AVG)
    - GROUP BY for aggregation
    - Multiple aggregation queries
    """
    stats = PaperEnrichmentService.get_topic_statistics(session)
    return stats
