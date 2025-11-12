from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import requests
from datetime import datetime
from app.core.api_key_rotator import get_gemini_key
import json

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
async def search_papers(request: SearchRequest):
    """
    Search for academic papers using OpenAlex API with optional AI query enhancement
    
    Features:
    - Full-text and title search
    - AI-powered query enhancement
    - Advanced filtering (year, citations, authors, institutions)
    - Open access filtering
    - Relevance and citation-based sorting
    """
    start_time = datetime.now()
    
    # Enhance query with AI if requested
    enhanced_query = None
    search_query = request.query
    
    if request.use_ai_enhancement:
        enhanced_query = enhance_query_with_ai(request.query)
        if enhanced_query:
            search_query = enhanced_query
    
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
        total_pages = (total_results + request.per_page - 1) // request.per_page
        
        # Calculate search time
        search_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
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
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Search request timed out")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"OpenAlex API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


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
async def get_search_stats():
    """
    Get OpenAlex database statistics
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
