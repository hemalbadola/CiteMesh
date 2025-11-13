"""
Search Cache Service - DBMS Showcase Feature
============================================

Demonstrates:
- Query result caching with TTL
- Composite indexes for fast lookups
- Cache hit/miss tracking
- Performance optimization
- Aggregate queries for cache statistics
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from sqlmodel import Session, select, func, and_, or_
from ..models_enhanced import SearchCache, SearchHistory
from ..models import User


class SearchCacheService:
    """
    Service for managing OpenAlex search result caching
    
    Benefits:
    - Reduces API calls to OpenAlex
    - Improves response time for repeated searches
    - Tracks search patterns for analytics
    """
    
    # Cache TTL (Time To Live)
    DEFAULT_CACHE_TTL_HOURS = 24
    
    # Slow query threshold for performance tracking
    SLOW_QUERY_THRESHOLD_MS = 1000
    
    @staticmethod
    def generate_cache_key(query: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate MD5 hash for query + filters combination
        
        DBMS Concept: Composite key generation for fast lookups
        """
        cache_data = {
            "query": query.strip().lower(),
            "filters": filters or {}
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    @classmethod
    def get_cached_results(
        cls, 
        session: Session,
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 25
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached search results if available and not expired
        
        DBMS Concepts Demonstrated:
        - Composite index usage (query_hash + expires_at)
        - WHERE clause with multiple conditions
        - UPDATE statement for hit tracking
        - Raw SQL for direct database interaction
        """
        query_hash = cls.generate_cache_key(query, filters)
        now = datetime.utcnow()
        
        # RAW SQL: Query with composite index: idx_search_cache_lookup (query_hash, expires_at)
        sql_query = """
            SELECT id, query_text, results_json, total_results, 
                   hit_count, last_accessed_at, created_at, expires_at
            FROM search_cache
            WHERE query_hash = :query_hash
              AND page = :page
              AND per_page = :per_page
              AND expires_at > :now
            LIMIT 1
        """
        
        result = session.execute(
            sql_query,
            {
                "query_hash": query_hash,
                "page": page,
                "per_page": per_page,
                "now": now
            }
        ).fetchone()
        
        if result:
            cache_id, query_text, results_json, total_results, hit_count, last_accessed, created, expires = result
            
            # RAW SQL: Update hit count and last accessed time (cache hit tracking)
            update_sql = """
                UPDATE search_cache
                SET hit_count = hit_count + 1,
                    last_accessed_at = :now
                WHERE id = :cache_id
            """
            session.execute(update_sql, {"cache_id": cache_id, "now": now})
            session.commit()
            
            # Parse cached results
            return json.loads(results_json)
        
        return None
    
    @classmethod
    def save_to_cache(
        cls,
        session: Session,
        query: str,
        filters: Optional[Dict[str, Any]],
        results: Dict[str, Any],
        page: int = 1,
        per_page: int = 25,
        api_response_time_ms: Optional[int] = None,
        ttl_hours: Optional[int] = None
    ) -> SearchCache:
        """
        Save search results to cache with expiration
        
        DBMS Concepts Demonstrated:
        - INSERT with multiple columns
        - Timestamp management
        - JSON storage for complex data
        """
        query_hash = cls.generate_cache_key(query, filters)
        now = datetime.utcnow()
        ttl = ttl_hours or cls.DEFAULT_CACHE_TTL_HOURS
        expires_at = now + timedelta(hours=ttl)
        
        cache_entry = SearchCache(
            query_hash=query_hash,
            query_text=query[:500],  # Truncate if too long
            filters_json=json.dumps(filters) if filters else None,
            results_json=json.dumps(results),
            total_results=results.get('meta', {}).get('count', 0),
            page=page,
            per_page=per_page,
            created_at=now,
            expires_at=expires_at,
            hit_count=0,
            api_response_time_ms=api_response_time_ms
        )
        
        session.add(cache_entry)
        session.commit()
        session.refresh(cache_entry)
        
        return cache_entry
    
    @classmethod
    def cleanup_expired_cache(cls, session: Session) -> int:
        """
        Remove expired cache entries
        
        DBMS Concepts Demonstrated:
        - DELETE with WHERE condition
        - Bulk delete operation
        - Index usage for efficient deletion (idx_search_cache_expiration)
        """
        now = datetime.utcnow()
        
        # Uses index: idx_search_cache_expiration (expires_at)
        statement = select(SearchCache).where(SearchCache.expires_at <= now)
        expired_entries = session.exec(statement).all()
        
        count = len(expired_entries)
        for entry in expired_entries:
            session.delete(entry)
        
        session.commit()
        return count
    
    @classmethod
    def get_cache_statistics(cls, session: Session) -> Dict[str, Any]:
        """
        Calculate cache performance metrics
        
        DBMS Concepts Demonstrated:
        - Aggregate functions (COUNT, SUM, AVG, MAX)
        - Multiple aggregations in single query
        - CASE statements for conditional aggregation
        """
        now = datetime.utcnow()
        
        # Total cache entries
        total_statement = select(func.count(SearchCache.id))
        total_entries = session.exec(total_statement).first()
        
        # Active (non-expired) entries
        active_statement = select(func.count(SearchCache.id)).where(
            SearchCache.expires_at > now
        )
        active_entries = session.exec(active_statement).first()
        
        # Total cache hits
        hits_statement = select(func.sum(SearchCache.hit_count))
        total_hits = session.exec(hits_statement).first() or 0
        
        # Average API response time
        avg_response_statement = select(func.avg(SearchCache.api_response_time_ms)).where(
            SearchCache.api_response_time_ms.isnot(None)
        )
        avg_response_time = session.exec(avg_response_statement).first()
        
        # Most popular cached query
        popular_statement = (
            select(
                SearchCache.query_text,
                SearchCache.hit_count
            )
            .where(SearchCache.expires_at > now)
            .order_by(SearchCache.hit_count.desc())
            .limit(1)
        )
        popular_result = session.exec(popular_statement).first()
        
        return {
            "total_cache_entries": total_entries or 0,
            "active_cache_entries": active_entries or 0,
            "expired_entries": (total_entries or 0) - (active_entries or 0),
            "total_cache_hits": int(total_hits),
            "average_api_response_time_ms": round(avg_response_time, 2) if avg_response_time else None,
            "most_popular_query": popular_result[0] if popular_result else None,
            "most_popular_query_hits": popular_result[1] if popular_result else 0,
        }


class SearchHistoryService:
    """
    Service for tracking and analyzing user search patterns
    
    Demonstrates:
    - Time-series data tracking
    - User behavior analytics
    - Window functions for trending analysis
    """
    
    @classmethod
    def log_search(
        cls,
        session: Session,
        user_id: int,
        query: str,
        filters: Optional[Dict[str, Any]],
        results_count: int,
        page: int,
        search_time_ms: int,
        use_ai_enhancement: bool = False,
        enhanced_query: Optional[str] = None,
        cache_hit: bool = False
    ) -> SearchHistory:
        """
        Log a search query for analytics
        
        DBMS Concepts Demonstrated:
        - INSERT operation
        - Foreign key relationship (user_id)
        - Timestamp tracking
        """
        history_entry = SearchHistory(
            user_id=user_id,
            query_text=query[:500],
            filters_json=json.dumps(filters) if filters else None,
            use_ai_enhancement=use_ai_enhancement,
            enhanced_query=enhanced_query[:1000] if enhanced_query else None,
            results_count=results_count,
            page=page,
            search_time_ms=search_time_ms,
            cache_hit=cache_hit,
            created_at=datetime.utcnow()
        )
        
        session.add(history_entry)
        session.commit()
        session.refresh(history_entry)
        
        return history_entry
    
    @classmethod
    def get_user_search_history(
        cls,
        session: Session,
        user_id: int,
        limit: int = 50
    ) -> List[SearchHistory]:
        """
        Get recent search history for a user
        
        DBMS Concepts Demonstrated:
        - SELECT with WHERE and ORDER BY
        - LIMIT clause for pagination
        - Index usage (idx_search_history_user_time)
        """
        # Uses composite index: idx_search_history_user_time (user_id, created_at)
        statement = (
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        )
        
        return list(session.exec(statement).all())
    
    @classmethod
    def get_trending_searches(
        cls,
        session: Session,
        hours: int = 24,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most popular searches in recent timeframe
        
        DBMS Concepts Demonstrated:
        - GROUP BY with COUNT aggregate
        - HAVING clause for filtering groups
        - Time-based filtering
        - ORDER BY aggregate results
        - Multiple aggregate functions in single query
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # RAW SQL: Uses index: idx_search_history_time (created_at)
        sql_query = """
            SELECT 
                query_text,
                COUNT(id) as search_count,
                AVG(results_count) as avg_results,
                SUM(CASE WHEN cache_hit = 1 THEN 1 ELSE 0 END) as cache_hits,
                ROUND(SUM(CASE WHEN cache_hit = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(id), 1) as cache_hit_rate
            FROM search_history
            WHERE created_at >= :cutoff_time
            GROUP BY query_text
            HAVING COUNT(id) > 0
            ORDER BY search_count DESC
            LIMIT :limit
        """
        
        results = session.execute(
            sql_query,
            {"cutoff_time": cutoff_time, "limit": limit}
        ).fetchall()
        
        return [
            {
                "query": row[0],
                "search_count": row[1],
                "avg_results": round(row[2], 1) if row[2] else 0,
                "cache_hits": int(row[3]) if row[3] else 0,
                "cache_hit_rate": round(row[4], 1) if row[4] else 0
            }
            for row in results
        ]
    
    @classmethod
    def get_user_search_statistics(
        cls,
        session: Session,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get search analytics for a specific user
        
        DBMS Concepts Demonstrated:
        - Complex WHERE conditions
        - Multiple aggregate functions
        - Conditional aggregation
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Total searches
        total_statement = select(func.count(SearchHistory.id)).where(
            and_(
                SearchHistory.user_id == user_id,
                SearchHistory.created_at >= cutoff_time
            )
        )
        total_searches = session.exec(total_statement).first() or 0
        
        # AI enhancement usage
        ai_statement = select(func.count(SearchHistory.id)).where(
            and_(
                SearchHistory.user_id == user_id,
                SearchHistory.created_at >= cutoff_time,
                SearchHistory.use_ai_enhancement == True
            )
        )
        ai_searches = session.exec(ai_statement).first() or 0
        
        # Cache hit rate
        cache_statement = select(func.count(SearchHistory.id)).where(
            and_(
                SearchHistory.user_id == user_id,
                SearchHistory.created_at >= cutoff_time,
                SearchHistory.cache_hit == True
            )
        )
        cache_hits = session.exec(cache_statement).first() or 0
        
        # Average search time
        avg_time_statement = select(func.avg(SearchHistory.search_time_ms)).where(
            and_(
                SearchHistory.user_id == user_id,
                SearchHistory.created_at >= cutoff_time
            )
        )
        avg_search_time = session.exec(avg_time_statement).first()
        
        return {
            "total_searches": int(total_searches),
            "ai_enhanced_searches": int(ai_searches),
            "ai_usage_rate": round((ai_searches / total_searches * 100), 1) if total_searches > 0 else 0,
            "cache_hits": int(cache_hits),
            "cache_hit_rate": round((cache_hits / total_searches * 100), 1) if total_searches > 0 else 0,
            "average_search_time_ms": round(avg_search_time, 2) if avg_search_time else None,
            "period_days": days
        }
