"""
PDF API endpoints for on-demand paper PDF downloads and proxying
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional
import httpx

from ..services.pdf_service import get_pdf_url

router = APIRouter()


class PDFResponse(BaseModel):
    """Response for PDF URL request"""
    pdf_url: Optional[str]
    source: str  # cache, arxiv, openalex, none
    arxiv_id: Optional[str]
    error: Optional[str]


@router.get("/get-pdf", response_model=PDFResponse)
async def get_paper_pdf(
    work_id: str = Query(..., description="OpenAlex work ID (e.g., W2741809807 or full URL)"),
    doi: Optional[str] = Query(None, description="Paper DOI if available"),
    existing_pdf_url: Optional[str] = Query(None, description="Existing PDF URL from OpenAlex")
):
    """
    Get PDF URL for a paper, downloading and caching if necessary
    
    Process:
    1. If OpenAlex already has PDF URL, return it
    2. Check if paper is from arXiv
    3. Check DigitalOcean Spaces cache
    4. Download from arXiv and cache
    5. Return PDF URL or error
    
    Example:
        GET /api/pdf/get-pdf?work_id=W2741809807&doi=10.48550/arXiv.2301.12345
    """
    try:
        result = get_pdf_url(work_id, doi, existing_pdf_url)
        return PDFResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get PDF: {str(e)}"
        )


@router.get("/check-pdf")
async def check_pdf_availability(
    work_id: str = Query(..., description="OpenAlex work ID"),
    doi: Optional[str] = Query(None, description="Paper DOI if available")
):
    """
    Quick check if PDF is available (doesn't trigger download)
    
    Returns:
        {
            "available": true/false,
            "source": "cache|openalex|arxiv|none",
            "cached": true/false
        }
    """
    try:
        from ..services.pdf_service import extract_arxiv_id, check_spaces_cache
        
        # Check if it's an arXiv paper
        arxiv_id = extract_arxiv_id(work_id, doi)
        if not arxiv_id:
            return {
                "available": False,
                "source": "none",
                "cached": False,
                "reason": "Not an arXiv paper"
            }
        
        # Check cache
        cached_url = check_spaces_cache(arxiv_id)
        if cached_url:
            return {
                "available": True,
                "source": "cache",
                "cached": True,
                "pdf_url": cached_url
            }
        
        # arXiv papers are generally available
        return {
            "available": True,
            "source": "arxiv",
            "cached": False,
            "arxiv_id": arxiv_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check PDF: {str(e)}"
        )


@router.get("")
async def proxy_pdf(
    url: str = Query(..., description="Open Access PDF URL to proxy")
):
    """
    Proxy and stream a PDF from OpenAlex or other open access sources
    
    This endpoint allows viewing PDFs without CORS issues and provides
    proper content-type headers for browser PDF viewers.
    
    Example:
        GET /api/pdf?url=https://arxiv.org/pdf/2301.12345.pdf
    """
    try:
        # Validate URL (basic security check)
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF URL - must start with http:// or https://"
            )
        
        # Check if it's a known safe domain
        safe_domains = [
            'arxiv.org',
            'europepmc.org', 
            'ncbi.nlm.nih.gov',
            'biorxiv.org',
            'medrxiv.org',
            'digitaloceanspaces.com',
            'openalex.org',
            's3.amazonaws.com'
        ]
        
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Check if domain matches any safe domain
        is_safe = any(safe_domain in domain for safe_domain in safe_domains)
        
        if not is_safe:
            # For unknown domains, just redirect to let browser handle it
            return RedirectResponse(url=url, status_code=302)
        
        # Stream the PDF through our server
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={
                    'User-Agent': 'CiteMesh/1.0 (Academic Research Tool; mailto:support@citemesh.app)'
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch PDF: HTTP {response.status_code}"
                )
            
            # Check if it's actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and 'octet-stream' not in content_type:
                # Not a PDF, redirect to original URL
                return RedirectResponse(url=url, status_code=302)
            
            # Stream the PDF with proper headers
            return StreamingResponse(
                iter([response.content]),
                media_type='application/pdf',
                headers={
                    'Content-Disposition': 'inline',
                    'Cache-Control': 'public, max-age=86400',  # Cache for 1 day
                    'Accept-Ranges': 'bytes'
                }
            )
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="PDF download timed out - try opening the PDF directly"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch PDF: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error proxying PDF: {str(e)}"
        )
