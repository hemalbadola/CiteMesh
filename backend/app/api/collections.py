"""Collections API endpoints for organizing papers."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import asc, desc
from sqlmodel import Session, func, select

from ..core.firebase_auth import get_current_user, FirebaseUser
from ..db import get_session
from ..models import Collection, CollectionPaper


router = APIRouter()

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.sql.schema import Table

CollectionTable = cast("Table", getattr(Collection, "__table__"))
CollectionPaperTable = cast("Table", getattr(CollectionPaper, "__table__"))


# Pydantic models for requests/responses
class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#6366f1"
    icon: Optional[str] = "📚"
    is_public: bool = False


class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_public: Optional[bool] = None


class CollectionResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    color: str
    icon: str
    is_public: bool
    paper_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaperAdd(BaseModel):
    paper_id: str
    paper_title: str
    paper_authors: Optional[str] = None
    paper_year: Optional[int] = None
    note: Optional[str] = None


class CollectionPaperResponse(BaseModel):
    id: int
    collection_id: int
    paper_id: str
    paper_title: str
    paper_authors: Optional[str] = None
    paper_year: Optional[int] = None
    note: Optional[str] = None
    order_index: int
    added_at: datetime

    class Config:
        from_attributes = True


class CollectionStats(BaseModel):
    total_collections: int
    total_papers: int
    public_collections: int
    private_collections: int


@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    payload: CollectionCreate,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> CollectionResponse:
    """Create a new collection."""
    if current_user.db_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be saved to database first"
        )
    
    collection = Collection(
        user_id=current_user.db_user.id,
        name=payload.name,
        description=payload.description,
        color=payload.color,
        icon=payload.icon,
        is_public=payload.is_public,
        paper_count=0,
    )
    
    session.add(collection)
    session.commit()
    session.refresh(collection)
    
    return CollectionResponse.model_validate(collection)


@router.get("/", response_model=List[CollectionResponse])
def list_collections(
    *,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
    include_public: bool = False,
) -> List[CollectionResponse]:
    """List all collections for the current user."""
    if current_user.db_user.id is None:
        return []
    
    query = select(Collection).where(Collection.user_id == current_user.db_user.id)
    
    if include_public:
        # Include public collections from other users
        query = select(Collection).where(
            (Collection.user_id == current_user.db_user.id) |
            (Collection.is_public == True)
        )
    
    query = query.order_by(desc(CollectionTable.c.updated_at))
    collections = session.exec(query).all()
    
    return [CollectionResponse.model_validate(collection) for collection in collections]


@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(
    collection_id: int,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> CollectionResponse:
    """Get a specific collection by ID."""
    collection = session.get(Collection, collection_id)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Check access: owner or public collection
    if collection.user_id != current_user.db_user.id and not collection.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return CollectionResponse.model_validate(collection)


@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: int,
    payload: CollectionUpdate,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> CollectionResponse:
    """Update a collection."""
    collection = session.get(Collection, collection_id)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Only owner can update
    if collection.user_id != current_user.db_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update fields
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(collection, key, value)
    
    collection.updated_at = datetime.utcnow()
    
    session.add(collection)
    session.commit()
    session.refresh(collection)
    
    return CollectionResponse.model_validate(collection)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: int,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> None:
    """Delete a collection and all its papers."""
    collection = session.get(Collection, collection_id)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Only owner can delete
    if collection.user_id != current_user.db_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete all papers in the collection
    papers_query = select(CollectionPaper).where(
        CollectionPaper.collection_id == collection_id
    )
    papers = session.exec(papers_query).all()
    for paper in papers:
        session.delete(paper)
    
    # Delete the collection
    session.delete(collection)
    session.commit()


@router.post("/{collection_id}/papers", response_model=CollectionPaperResponse, status_code=status.HTTP_201_CREATED)
def add_paper_to_collection(
    collection_id: int,
    payload: PaperAdd,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> CollectionPaperResponse:
    """Add a paper to a collection."""
    collection = session.get(Collection, collection_id)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Only owner can add papers
    if collection.user_id != current_user.db_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if paper already exists in collection
    existing_query = select(CollectionPaper).where(
        CollectionPaper.collection_id == collection_id,
        CollectionPaper.paper_id == payload.paper_id
    )
    existing = session.exec(existing_query).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Paper already in collection"
        )
    
    # Get current max order_index
    max_order_query = select(func.max(CollectionPaperTable.c.order_index)).where(
        CollectionPaper.collection_id == collection_id
    )
    max_order_row = session.exec(max_order_query).first()
    max_order = max_order_row[0] if max_order_row else 0
    next_order = max_order + 1
    
    # Add paper
    paper = CollectionPaper(
        collection_id=collection_id,
        paper_id=payload.paper_id,
        paper_title=payload.paper_title,
        paper_authors=payload.paper_authors,
        paper_year=payload.paper_year,
        note=payload.note,
        order_index=next_order,
    )
    
    session.add(paper)
    
    # Update collection paper count
    collection.paper_count += 1
    collection.updated_at = datetime.utcnow()
    session.add(collection)
    
    session.commit()
    session.refresh(paper)
    
    return CollectionPaperResponse.model_validate(paper)


@router.get("/{collection_id}/papers", response_model=List[CollectionPaperResponse])
def get_collection_papers(
    collection_id: int,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> List[CollectionPaperResponse]:
    """Get all papers in a collection."""
    collection = session.get(Collection, collection_id)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Check access
    if collection.user_id != current_user.db_user.id and not collection.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    query = select(CollectionPaper).where(
        CollectionPaper.collection_id == collection_id
    ).order_by(asc(CollectionPaperTable.c.order_index))
    
    papers = session.exec(query).all()
    return [CollectionPaperResponse.model_validate(paper) for paper in papers]


@router.delete("/{collection_id}/papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_paper_from_collection(
    collection_id: int,
    paper_id: int,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> None:
    """Remove a paper from a collection."""
    collection = session.get(Collection, collection_id)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    # Only owner can remove papers
    if collection.user_id != current_user.db_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    paper = session.get(CollectionPaper, paper_id)
    
    if not paper or paper.collection_id != collection_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found in this collection"
        )
    
    session.delete(paper)
    
    # Update collection paper count
    collection.paper_count = max(0, collection.paper_count - 1)
    collection.updated_at = datetime.utcnow()
    session.add(collection)
    
    session.commit()


@router.get("/stats/summary", response_model=CollectionStats)
def get_collection_stats(
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> CollectionStats:
    """Get collection statistics for the current user."""
    if current_user.db_user.id is None:
        return CollectionStats(
            total_collections=0,
            total_papers=0,
            public_collections=0,
            private_collections=0,
        )
    
    # Get all user collections
    collections_query = select(Collection).where(
        Collection.user_id == current_user.db_user.id
    )
    collections = session.exec(collections_query).all()
    
    total_collections = len(collections)
    total_papers = sum(c.paper_count for c in collections)
    public_collections = sum(1 for c in collections if c.is_public)
    private_collections = total_collections - public_collections
    
    return CollectionStats(
        total_collections=total_collections,
        total_papers=total_papers,
        public_collections=public_collections,
        private_collections=private_collections,
    )
