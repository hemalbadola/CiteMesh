"""Citation Network API endpoints for paper relationships and graph visualization."""

from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy import desc

from ..core.firebase_auth import FirebaseUser, get_current_user
from ..db import get_session
from ..models import CitationLink

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.sql.schema import Table

CitationTable = cast("Table", getattr(CitationLink, "__table__"))


router = APIRouter()


# Pydantic models for requests/responses
class CitationCreate(BaseModel):
    source_paper_id: str
    target_paper_id: str
    weight: float = 1.0
    note: Optional[str] = None


class CitationResponse(BaseModel):
    id: int
    user_id: int
    source_paper_id: str
    target_paper_id: str
    weight: float
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Node(BaseModel):
    """Graph node representing a paper."""
    id: str
    label: str
    size: float = 10.0
    color: str = "#6366f1"
    citations: int = 0


class Edge(BaseModel):
    """Graph edge representing a citation link."""
    source: str
    target: str
    weight: float = 1.0
    label: Optional[str] = None


class NetworkGraph(BaseModel):
    """Complete graph data for visualization."""
    nodes: List[Node]
    edges: List[Edge]
    total_nodes: int
    total_edges: int


class CitationStats(BaseModel):
    total_citations: int
    total_papers: int
    avg_citations_per_paper: float
    most_cited_paper: Optional[str] = None
    most_cited_count: int = 0


@router.post("/", response_model=CitationResponse, status_code=status.HTTP_201_CREATED)
def add_citation_link(
    payload: CitationCreate,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> CitationResponse:
    """Add a new citation link between two papers."""
    if current_user.db_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be saved to database first"
        )
    
    # Check if link already exists
    existing_query = select(CitationLink).where(
        CitationLink.user_id == current_user.db_user.id,
        CitationLink.source_paper_id == payload.source_paper_id,
        CitationLink.target_paper_id == payload.target_paper_id,
    )
    existing = session.exec(existing_query).first()
    
    if existing:
        # Update existing link
        existing.weight = payload.weight
        if payload.note:
            existing.note = payload.note
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return CitationResponse.model_validate(existing)
    
    # Create new link
    citation = CitationLink(
        user_id=current_user.db_user.id,
        source_paper_id=payload.source_paper_id,
        target_paper_id=payload.target_paper_id,
        weight=payload.weight,
        note=payload.note,
    )
    
    session.add(citation)
    session.commit()
    session.refresh(citation)
    
    return CitationResponse.model_validate(citation)


@router.get("/network", response_model=NetworkGraph)
def get_citation_network(
    *,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
    max_nodes: int = 100,
) -> NetworkGraph:
    """Get the complete citation network as a graph."""
    if current_user.db_user.id is None:
        return NetworkGraph(nodes=[], edges=[], total_nodes=0, total_edges=0)
    
    # Get all citation links for the user
    query = select(CitationLink).where(
        CitationLink.user_id == current_user.db_user.id
    )
    citations = session.exec(query).all()
    
    if not citations:
        return NetworkGraph(nodes=[], edges=[], total_nodes=0, total_edges=0)
    
    # Build graph structure
    nodes_dict: Dict[str, Node] = {}
    edges: List[Edge] = []
    
    # Count citations for each paper
    citation_counts: Dict[str, int] = {}
    
    for citation in citations:
        # Count citations (papers that are cited)
        target_id = citation.target_paper_id
        citation_counts[target_id] = citation_counts.get(target_id, 0) + 1
        
        # Add nodes
        if citation.source_paper_id not in nodes_dict:
            nodes_dict[citation.source_paper_id] = Node(
                id=citation.source_paper_id,
                label=citation.source_paper_id,
                citations=0,
            )
        
        if citation.target_paper_id not in nodes_dict:
            nodes_dict[citation.target_paper_id] = Node(
                id=citation.target_paper_id,
                label=citation.target_paper_id,
                citations=0,
            )
        
        # Add edge
        edges.append(Edge(
            source=citation.source_paper_id,
            target=citation.target_paper_id,
            weight=citation.weight,
            label=citation.note,
        ))
    
    # Update citation counts and node sizes
    for paper_id, count in citation_counts.items():
        if paper_id in nodes_dict:
            nodes_dict[paper_id].citations = count
            # Scale node size based on citations (10-50 range)
            nodes_dict[paper_id].size = min(50, 10 + count * 5)
            # Color highly cited papers differently
            if count >= 3:
                nodes_dict[paper_id].color = "#ef4444"  # Red for highly cited
            elif count >= 2:
                nodes_dict[paper_id].color = "#f59e0b"  # Orange for moderately cited
    
    nodes = list(nodes_dict.values())
    
    # Limit nodes if requested
    if len(nodes) > max_nodes:
        # Keep most cited papers
        nodes = sorted(nodes, key=lambda n: n.citations, reverse=True)[:max_nodes]
        node_ids = {n.id for n in nodes}
        edges = [e for e in edges if e.source in node_ids and e.target in node_ids]
    
    return NetworkGraph(
        nodes=nodes,
        edges=edges,
        total_nodes=len(nodes),
        total_edges=len(edges),
    )


@router.get("/", response_model=List[CitationResponse])
def list_citations(
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> List[CitationResponse]:
    """List all citation links for the current user."""
    if current_user.db_user.id is None:
        return []
    
    query = select(CitationLink).where(
        CitationLink.user_id == current_user.db_user.id
    ).order_by(desc(CitationTable.c.created_at))
    
    citations = session.exec(query).all()
    return [CitationResponse.model_validate(citation) for citation in citations]


@router.delete("/{citation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_citation(
    citation_id: int,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> None:
    """Delete a citation link."""
    citation = session.get(CitationLink, citation_id)
    
    if not citation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citation not found"
        )
    
    # Only owner can delete
    if citation.user_id != current_user.db_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    session.delete(citation)
    session.commit()


@router.get("/stats", response_model=CitationStats)
def get_citation_stats(
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
) -> CitationStats:
    """Get citation network statistics."""
    if current_user.db_user.id is None:
        return CitationStats(
            total_citations=0,
            total_papers=0,
            avg_citations_per_paper=0.0,
            most_cited_paper=None,
            most_cited_count=0,
        )
    
    # Get all citations
    query = select(CitationLink).where(
        CitationLink.user_id == current_user.db_user.id
    )
    citations = session.exec(query).all()
    
    if not citations:
        return CitationStats(
            total_citations=0,
            total_papers=0,
            avg_citations_per_paper=0.0,
            most_cited_paper=None,
            most_cited_count=0,
        )
    
    # Count citations per paper
    citation_counts: Dict[str, int] = {}
    all_papers = set()
    
    for citation in citations:
        all_papers.add(citation.source_paper_id)
        all_papers.add(citation.target_paper_id)
        
        target = citation.target_paper_id
        citation_counts[target] = citation_counts.get(target, 0) + 1
    
    # Find most cited paper
    most_cited_paper = None
    most_cited_count = 0
    
    if citation_counts:
        top_paper, top_count = max(citation_counts.items(), key=lambda item: item[1])
        most_cited_paper = top_paper
        most_cited_count = top_count
    
    total_citations = len(citations)
    total_papers = len(all_papers)
    avg_citations = total_citations / total_papers if total_papers > 0 else 0.0
    
    return CitationStats(
        total_citations=total_citations,
        total_papers=total_papers,
        avg_citations_per_paper=round(avg_citations, 2),
        most_cited_paper=most_cited_paper,
        most_cited_count=most_cited_count,
    )


@router.get("/paper/{paper_id}/related", response_model=List[str])
def get_related_papers(
    paper_id: str,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
    max_results: int = 10,
) -> List[str]:
    """Get papers related to a given paper through citations."""
    if current_user.db_user.id is None:
        return []
    
    # Get papers that cite this paper
    citing_query = select(CitationLink.source_paper_id).where(
        CitationLink.user_id == current_user.db_user.id,
        CitationLink.target_paper_id == paper_id,
    )
    
    # Get papers that this paper cites
    cited_query = select(CitationLink.target_paper_id).where(
        CitationLink.user_id == current_user.db_user.id,
        CitationLink.source_paper_id == paper_id,
    )
    
    citing_papers = session.exec(citing_query).all()
    cited_papers = session.exec(cited_query).all()
    
    # Combine and deduplicate
    related = list(set(list(citing_papers) + list(cited_papers)))
    
    return related[:max_results]
