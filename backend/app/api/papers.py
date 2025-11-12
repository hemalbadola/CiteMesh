"""Saved papers (library) API endpoints."""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import asc, desc
from sqlmodel import Session, func, select

from ..core.firebase_auth import FirebaseUser, get_current_user
from ..db import get_session
from ..models import SavedPaper

router = APIRouter()

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.sql.schema import Table

SavedPaperTable = cast("Table", getattr(SavedPaper, "__table__"))


class SavedPaperCreate(BaseModel):
    """Schema for saving a new paper."""

    paper_id: str
    title: str
    authors: Optional[str] = None
    summary: Optional[str] = None
    published_year: Optional[int] = None
    tags: Optional[str] = None


class SavedPaperUpdate(BaseModel):
    """Schema for updating a saved paper."""

    tags: Optional[str] = None


class SavedPaperResponse(BaseModel):
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


class PaperStats(BaseModel):
    """Statistics about saved papers."""

    total_papers: int
    papers_this_month: int
    most_common_tags: List[str]


@router.post("/", response_model=SavedPaperResponse, status_code=status.HTTP_201_CREATED)
async def save_paper(
    paper: SavedPaperCreate,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Save a paper to user's library."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be saved to database first",
        )
    # Check if paper already saved
    statement = select(SavedPaper).where(
        SavedPaper.user_id == current_user.id,
        SavedPaper.paper_id == paper.paper_id,
    )
    existing = session.exec(statement).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Paper already saved",
        )

    saved_paper = SavedPaper(
        user_id=current_user.id,
        paper_id=paper.paper_id,
        title=paper.title,
        authors=paper.authors,
        summary=paper.summary,
        published_year=paper.published_year,
        tags=paper.tags,
    )

    session.add(saved_paper)
    session.commit()
    session.refresh(saved_paper)

    return SavedPaperResponse.model_validate(saved_paper)


@router.get("/", response_model=List[SavedPaperResponse])
async def get_saved_papers(
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    year: Optional[int] = Query(None, description="Filter by publication year"),
):
    """Get user's saved papers with optional filters."""
    if current_user.id is None:
        return []

    statement = select(SavedPaper).where(SavedPaper.user_id == current_user.id)

    if tags:
        # Filter by tags - simple contains check
        for tag in tags.split(","):
            statement = statement.where(SavedPaperTable.c.tags.contains(tag.strip()))

    if year:
        statement = statement.where(SavedPaperTable.c.published_year == year)

    statement = statement.order_by(desc(SavedPaperTable.c.saved_at)).offset(skip).limit(limit)

    papers = session.exec(statement).all()
    return [SavedPaperResponse.model_validate(paper) for paper in papers]


@router.get("/stats", response_model=PaperStats)
async def get_paper_stats(
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get statistics about user's saved papers."""
    if current_user.id is None:
        return PaperStats(total_papers=0, papers_this_month=0, most_common_tags=[])
    # Total papers
    total_statement = select(func.count(SavedPaperTable.c.id)).where(
        SavedPaperTable.c.user_id == current_user.id
    )
    total_result = session.exec(total_statement).first()
    if isinstance(total_result, tuple):
        total_papers = int(total_result[0] or 0)
    elif isinstance(total_result, (int, float)):
        total_papers = int(total_result)
    else:
        total_papers = 0

    # Papers this month
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    month_statement = select(func.count(SavedPaperTable.c.id)).where(
        SavedPaperTable.c.user_id == current_user.id,
        SavedPaperTable.c.saved_at >= month_start,
    )
    month_result = session.exec(month_statement).first()
    if isinstance(month_result, tuple):
        papers_this_month = int(month_result[0] or 0)
    elif isinstance(month_result, (int, float)):
        papers_this_month = int(month_result)
    else:
        papers_this_month = 0

    # Most common tags (simplified)
    tags_statement = select(SavedPaperTable.c.tags).where(
        SavedPaperTable.c.user_id == current_user.id,
        SavedPaperTable.c.tags.is_not(None),
    )
    all_tags = session.exec(tags_statement).all()

    # Count tag occurrences
    tag_counts = {}
    for raw_tag in all_tags:
        tag_string = raw_tag[0] if isinstance(raw_tag, tuple) else raw_tag
        if tag_string:
            for tag in tag_string.split(","):
                tag = tag.strip()
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Get top 5 tags
    most_common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    most_common_tags = [tag for tag, _ in most_common_tags]

    return PaperStats(
        total_papers=total_papers,
        papers_this_month=papers_this_month,
        most_common_tags=most_common_tags,
    )


@router.get("/{paper_id}", response_model=SavedPaperResponse)
async def get_saved_paper(
    paper_id: int,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific saved paper by ID."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be saved to database first",
        )
    statement = select(SavedPaper).where(
        SavedPaper.id == paper_id, SavedPaper.user_id == current_user.id
    )
    paper = session.exec(statement).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )

    return SavedPaperResponse.model_validate(paper)


@router.put("/{paper_id}", response_model=SavedPaperResponse)
async def update_saved_paper(
    paper_id: int,
    paper_update: SavedPaperUpdate,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update a saved paper (e.g., add tags)."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be saved to database first",
        )
    statement = select(SavedPaper).where(
        SavedPaper.id == paper_id, SavedPaper.user_id == current_user.id
    )
    paper = session.exec(statement).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )

    if paper_update.tags is not None:
        paper.tags = paper_update.tags

    session.add(paper)
    session.commit()
    session.refresh(paper)

    return SavedPaperResponse.model_validate(paper)


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_paper(
    paper_id: int,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Remove a paper from user's library."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be saved to database first",
        )
    statement = select(SavedPaper).where(
        SavedPaper.id == paper_id, SavedPaper.user_id == current_user.id
    )
    paper = session.exec(statement).first()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )

    session.delete(paper)
    session.commit()
