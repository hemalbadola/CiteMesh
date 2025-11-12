"""
PDF API endpoints for on-demand paper PDF downloads
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

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
