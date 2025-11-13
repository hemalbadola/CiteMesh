"""
Paper Metadata Enrichment Service - DBMS Showcase Feature
==========================================================

Demonstrates:
- Normalized data storage (Topics, References)
- M:N relationships via junction tables
- Foreign key constraints
- Batch INSERT operations
- Transaction management
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import requests

from sqlmodel import Session, select, func, and_
from ..models_enhanced import (
    PaperTopic,
    ResearchTopic,
    PaperReference,
)
from ..models import SavedPaper


class PaperEnrichmentService:
    """
    Service for enriching saved papers with additional metadata from OpenAlex
    """
    
    OPENALEX_BASE_URL = "https://api.openalex.org"
    
    @classmethod
    def enrich_paper(
        cls,
        session: Session,
        paper_id: int,
        openalex_id: str
    ) -> Dict[str, Any]:
        """
        Enrich a saved paper with references, topics, and citations from OpenAlex
        
        DBMS Concepts Demonstrated:
        - Transaction management (all-or-nothing)
        - Multiple INSERT operations
        - Foreign key relationships
        - Normalized data storage
        """
        # Fetch paper details from OpenAlex
        try:
            response = requests.get(
                f"{cls.OPENALEX_BASE_URL}/works/{openalex_id}",
                params={"data-version": "2"},
                timeout=10
            )
            response.raise_for_status()
            work = response.json()
        except Exception as e:
            return {"error": f"Failed to fetch OpenAlex data: {e}"}
        
        enrichment_stats = {
            "topics_added": 0,
            "references_added": 0,
            "errors": []
        }
        
        # Start transaction - all operations succeed or all fail
        try:
            # 1. Extract and store topics/concepts
            topics_added = cls._store_topics(session, paper_id, work.get("concepts", []))
            enrichment_stats["topics_added"] = topics_added
            
            # 2. Extract and store references (papers cited by this paper)
            refs_added = cls._store_references(session, paper_id, work.get("referenced_works", []))
            enrichment_stats["references_added"] = refs_added
            
            # Commit transaction
            session.commit()
            
        except Exception as e:
            session.rollback()
            enrichment_stats["errors"].append(f"Transaction failed: {e}")
        
        return enrichment_stats
    
    @classmethod
    def _store_topics(
        cls,
        session: Session,
        paper_id: int,
        concepts: List[Dict[str, Any]]
    ) -> int:
        """
        Store research topics with normalized Topic table
        
        DBMS Concepts Demonstrated:
        - Normalization (separate Topic entity to avoid redundancy)
        - M:N relationship via PaperTopic junction table
        - INSERT OR UPDATE pattern (upsert)
        - Composite primary key in junction table
        """
        count = 0
        
        for concept in concepts:
            try:
                openalex_id = concept.get("id", "")
                if not openalex_id:
                    continue
                
                # Check if topic already exists
                topic_statement = select(ResearchTopic).where(
                    ResearchTopic.openalex_id == openalex_id
                )
                topic = session.exec(topic_statement).first()
                
                if not topic:
                    # Create new topic (normalization - store topic only once)
                    topic = ResearchTopic(
                        openalex_id=openalex_id,
                        name=concept.get("display_name", "Unknown"),
                        display_name=concept.get("display_name", "Unknown"),
                        level=concept.get("level", 0),
                        works_count=concept.get("works_count", 0),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(topic)
                    session.flush()  # Get topic.id before linking
                
                # Check if paper-topic link already exists
                link_statement = select(PaperTopic).where(
                    and_(
                        PaperTopic.paper_id == paper_id,
                        PaperTopic.topic_id == topic.id
                    )
                )
                existing_link = session.exec(link_statement).first()
                
                if not existing_link:
                    # Create paper-topic link (junction table)
                    paper_topic = PaperTopic(
                        paper_id=paper_id,
                        topic_id=topic.id,
                        relevance_score=concept.get("score", 0.0),
                        added_at=datetime.utcnow()
                    )
                    session.add(paper_topic)
                    count += 1
                
            except Exception as e:
                print(f"Error storing topic: {e}")
                continue
        
        return count
    
    @classmethod
    def _store_references(
        cls,
        session: Session,
        paper_id: int,
        referenced_works: List[str]
    ) -> int:
        """
        Store paper references (citation graph edges)
        
        DBMS Concepts Demonstrated:
        - Directed graph representation
        - Self-referencing relationships
        - Bulk INSERT for performance
        """
        count = 0
        
        for order_idx, ref_openalex_id in enumerate(referenced_works[:100]):  # Limit to 100 refs
            try:
                # Check if reference already stored
                ref_statement = select(PaperReference).where(
                    and_(
                        PaperReference.source_paper_id == paper_id,
                        PaperReference.referenced_paper_openalex_id == ref_openalex_id
                    )
                )
                existing = session.exec(ref_statement).first()
                
                if not existing:
                    # Fetch reference metadata from OpenAlex (could be batched)
                    ref_metadata = cls._fetch_reference_metadata(ref_openalex_id)
                    
                    reference = PaperReference(
                        source_paper_id=paper_id,
                        referenced_paper_openalex_id=ref_openalex_id,
                        referenced_paper_title=ref_metadata.get("title"),
                        referenced_paper_year=ref_metadata.get("year"),
                        referenced_paper_doi=ref_metadata.get("doi"),
                        reference_order=order_idx + 1,
                        added_at=datetime.utcnow()
                    )
                    session.add(reference)
                    count += 1
                
            except Exception as e:
                print(f"Error storing reference: {e}")
                continue
        
        return count
    
    @classmethod
    def _fetch_reference_metadata(cls, openalex_id: str) -> Dict[str, Any]:
        """
        Fetch minimal metadata for a referenced paper
        """
        try:
            response = requests.get(
                f"{cls.OPENALEX_BASE_URL}/works/{openalex_id}",
                params={"select": "id,title,publication_year,doi"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "title": data.get("title", "Unknown"),
                    "year": data.get("publication_year"),
                    "doi": data.get("doi")
                }
        except:
            pass
        
        return {"title": None, "year": None, "doi": None}
    
    @classmethod
    def get_paper_topics(
        cls,
        session: Session,
        paper_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all topics for a paper with relevance scores
        
        DBMS Concepts Demonstrated:
        - INNER JOIN operation (PaperTopic → ResearchTopic)
        - M:N relationship query via junction table
        - SELECT with multiple table columns
        - ORDER BY on joined columns
        - Composite index usage (idx_paper_topic_paper)
        """
        # RAW SQL: Join through junction table to demonstrate M:N relationship
        sql_query = """
            SELECT 
                rt.id as topic_id,
                rt.openalex_id,
                rt.display_name as name,
                rt.level,
                pt.relevance_score,
                rt.works_count
            FROM paper_topic pt
            INNER JOIN research_topic rt ON pt.topic_id = rt.id
            WHERE pt.paper_id = :paper_id
            ORDER BY pt.relevance_score DESC
        """
        
        results = session.execute(sql_query, {"paper_id": paper_id}).fetchall()
        
        return [
            {
                "topic_id": row[0],
                "openalex_id": row[1],
                "name": row[2],
                "level": row[3],
                "relevance_score": row[4],
                "works_count": row[5]
            }
            for row in results
        ]
    
    @classmethod
    def get_paper_references(
        cls,
        session: Session,
        paper_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get papers cited by this paper
        
        DBMS Concepts Demonstrated:
        - SELECT with WHERE filter
        - ORDER BY for ordering
        - LIMIT for pagination
        """
        statement = (
            select(PaperReference)
            .where(PaperReference.source_paper_id == paper_id)
            .order_by(PaperReference.reference_order)
            .limit(limit)
        )
        
        references = session.exec(statement).all()
        
        return [
            {
                "openalex_id": ref.referenced_paper_openalex_id,
                "title": ref.referenced_paper_title,
                "year": ref.referenced_paper_year,
                "doi": ref.referenced_paper_doi,
                "order": ref.reference_order
            }
            for ref in references
        ]
    
    @classmethod
    def get_papers_by_topic(
        cls,
        session: Session,
        topic_id: int,
        min_relevance: float = 0.3,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find all papers tagged with a specific topic
        
        DBMS Concepts Demonstrated:
        - JOIN across three tables (PaperTopic → SavedPaper)
        - WHERE with threshold filtering
        - Aggregate COUNT for related papers
        """
        statement = (
            select(SavedPaper, PaperTopic.relevance_score)
            .join(PaperTopic, PaperTopic.paper_id == SavedPaper.id)
            .where(
                and_(
                    PaperTopic.topic_id == topic_id,
                    PaperTopic.relevance_score >= min_relevance
                )
            )
            .order_by(PaperTopic.relevance_score.desc())
            .limit(limit)
        )
        
        results = session.exec(statement).all()
        
        return [
            {
                "paper_id": paper.id,
                "paper_openalex_id": paper.paper_id,
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.published_year,
                "relevance_score": score
            }
            for paper, score in results
        ]
    
    @classmethod
    def get_topic_statistics(
        cls,
        session: Session
    ) -> Dict[str, Any]:
        """
        Get statistics about stored topics
        
        DBMS Concepts Demonstrated:
        - Aggregate functions (COUNT, AVG)
        - GROUP BY for grouping
        - Subqueries for complex aggregations
        - Multiple SELECT statements
        """
        # RAW SQL: Multiple aggregate queries to demonstrate different DBMS concepts
        
        # Total topics and links with subquery
        totals_sql = """
            SELECT 
                (SELECT COUNT(*) FROM research_topic) as total_topics,
                (SELECT COUNT(*) FROM paper_topic) as total_links,
                (SELECT COUNT(DISTINCT paper_id) FROM paper_topic) as papers_with_topics
        """
        totals = session.execute(totals_sql).fetchone()
        total_topics = totals[0] or 0
        total_links = totals[1] or 0
        papers_with_topics = totals[2] or 0
        
        # Average topics per paper
        avg_topics_per_paper = total_links / papers_with_topics if papers_with_topics > 0 else 0
        
        # RAW SQL: Most popular topics with GROUP BY and JOIN
        popular_topics_sql = """
            SELECT 
                rt.display_name,
                COUNT(pt.paper_id) as paper_count,
                AVG(pt.relevance_score) as avg_relevance
            FROM research_topic rt
            INNER JOIN paper_topic pt ON rt.id = pt.topic_id
            GROUP BY rt.id, rt.display_name
            HAVING COUNT(pt.paper_id) > 0
            ORDER BY paper_count DESC, avg_relevance DESC
            LIMIT 10
        """
        popular_topics = session.execute(popular_topics_sql).fetchall()
        
        return {
            "total_topics": int(total_topics),
            "total_links": int(total_links),
            "papers_with_topics": int(papers_with_topics),
            "avg_topics_per_paper": round(avg_topics_per_paper, 2),
            "popular_topics": [
                {
                    "name": row[0],
                    "paper_count": row[1],
                    "avg_relevance": round(row[2], 3) if row[2] else 0
                }
                for row in popular_topics
            ]
        }
