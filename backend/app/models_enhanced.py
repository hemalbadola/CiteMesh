"""
Enhanced SQLModel models for DBMS showcase features
These models demonstrate advanced database concepts:
- Search caching and optimization
- Search history analytics
- Paper metadata enrichment
- Performance monitoring
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON
from sqlalchemy import Text, Index


# ============================================
# SEARCH CACHE & HISTORY TABLES
# ============================================

class SearchCache(SQLModel, table=True):
    """
    Cache OpenAlex search results to reduce API calls and improve performance
    
    DBMS Concepts Demonstrated:
    - Query result caching
    - Composite indexes for cache lookup
    - TTL (Time-To-Live) management
    - Cache hit/miss tracking
    """
    __tablename__ = "search_cache"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    query_hash: str = Field(index=True, max_length=64, description="MD5 hash of query+filters")
    query_text: str = Field(max_length=500, description="Original search query")
    filters_json: Optional[str] = Field(default=None, sa_column=Column(Text), description="Search filters as JSON")
    
    # Cache metadata
    results_json: str = Field(sa_column=Column(Text), description="Cached search results")
    total_results: int = Field(default=0, description="Total result count from OpenAlex")
    page: int = Field(default=1)
    per_page: int = Field(default=25)
    
    # Cache management
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    expires_at: datetime = Field(index=True, description="Cache expiration timestamp")
    hit_count: int = Field(default=0, description="Number of times this cache was used")
    last_accessed_at: Optional[datetime] = Field(default=None, description="Last cache hit timestamp")
    
    # Performance tracking
    api_response_time_ms: Optional[int] = Field(default=None, description="Original API response time")
    
    __table_args__ = (
        Index('idx_search_cache_lookup', 'query_hash', 'expires_at'),  # Composite index for cache lookup
        Index('idx_search_cache_expiration', 'expires_at'),  # For cleanup queries
    )


class SearchHistory(SQLModel, table=True):
    """
    Track all user searches for analytics and personalization
    
    DBMS Concepts Demonstrated:
    - Time-series data tracking
    - User behavior analytics
    - Aggregation queries (trending searches, popular filters)
    - Window functions for search patterns
    """
    __tablename__ = "search_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, description="User who performed search")
    
    # Search details
    query_text: str = Field(max_length=500, description="Search query")
    filters_json: Optional[str] = Field(default=None, sa_column=Column(Text), description="Applied filters")
    use_ai_enhancement: bool = Field(default=False, description="Whether AI query enhancement was used")
    enhanced_query: Optional[str] = Field(default=None, max_length=1000, description="AI-enhanced query")
    
    # Results
    results_count: int = Field(default=0, description="Number of results returned")
    page: int = Field(default=1)
    
    # Timing
    search_time_ms: Optional[int] = Field(default=None, description="Search execution time")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # User interaction
    papers_viewed: int = Field(default=0, description="Papers clicked from results")
    papers_saved: int = Field(default=0, description="Papers saved from results")
    
    # Cache hit
    cache_hit: bool = Field(default=False, description="Whether result was served from cache")
    
    __table_args__ = (
        Index('idx_search_history_user_time', 'user_id', 'created_at'),  # For user search timeline
        Index('idx_search_history_time', 'created_at'),  # For trending searches
    )


# ============================================
# PAPER METADATA ENRICHMENT
# ============================================

class PaperTopic(SQLModel, table=True):
    """
    Store research topics/concepts for each paper from OpenAlex
    
    DBMS Concepts Demonstrated:
    - M:N relationship via junction table
    - Normalized topic storage (no redundancy)
    - Composite primary key
    """
    __tablename__ = "paper_topic"
    
    paper_id: int = Field(foreign_key="savedpaper.id", primary_key=True, description="Paper FK")
    topic_id: int = Field(foreign_key="research_topic.id", primary_key=True, description="Topic FK")
    
    # Relevance score from OpenAlex
    relevance_score: float = Field(ge=0.0, le=1.0, description="Topic relevance (0-1)")
    
    # Timestamps
    added_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_paper_topic_paper', 'paper_id'),
        Index('idx_paper_topic_topic', 'topic_id'),
        Index('idx_paper_topic_score', 'relevance_score'),  # For "most relevant topics" queries
    )


class ResearchTopic(SQLModel, table=True):
    """
    Normalized table of research topics/concepts from OpenAlex
    
    DBMS Concepts Demonstrated:
    - Normalization (separate topic entity)
    - Unique constraints
    - Hierarchical data (parent topics)
    """
    __tablename__ = "research_topic"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    openalex_id: str = Field(unique=True, index=True, max_length=255, description="OpenAlex concept ID")
    name: str = Field(max_length=255, description="Topic name")
    display_name: str = Field(max_length=255, description="Display name")
    
    # Hierarchy
    parent_topic_id: Optional[int] = Field(default=None, foreign_key="research_topic.id", description="Parent topic (self-referencing)")
    level: int = Field(default=0, description="Hierarchy level (0=root)")
    
    # Metadata
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    works_count: int = Field(default=0, description="Number of works tagged with this topic")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_topic_parent', 'parent_topic_id'),
        Index('idx_topic_level', 'level'),
    )


class PaperReference(SQLModel, table=True):
    """
    Store references (cited papers) for each saved paper
    
    DBMS Concepts Demonstrated:
    - Citation graph edges (directed)
    - Self-referencing relationships
    - Graph database concepts
    """
    __tablename__ = "paper_reference"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    source_paper_id: int = Field(foreign_key="savedpaper.id", index=True, description="Paper that cites")
    
    # Referenced paper (may not be in our database)
    referenced_paper_openalex_id: str = Field(max_length=255, description="OpenAlex ID of cited paper")
    referenced_paper_title: Optional[str] = Field(default=None, max_length=1000)
    referenced_paper_year: Optional[int] = Field(default=None)
    referenced_paper_doi: Optional[str] = Field(default=None, max_length=255)
    
    # Reference details
    reference_order: Optional[int] = Field(default=None, description="Order in reference list")
    
    # Timestamps
    added_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_paper_ref_source', 'source_paper_id'),
        Index('idx_paper_ref_target', 'referenced_paper_openalex_id'),
        Index('idx_paper_ref_graph', 'source_paper_id', 'referenced_paper_openalex_id'),  # For graph queries
    )


# ============================================
# CHAT CONTEXT ENHANCEMENT
# ============================================

class ChatPaperContext(SQLModel, table=True):
    """
    Link chat messages to specific papers for context-aware responses
    
    DBMS Concepts Demonstrated:
    - M:N relationship tracking
    - Context management
    - JOIN optimization
    """
    __tablename__ = "chat_paper_context"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="researchchatmessage.id", index=True)
    paper_id: int = Field(foreign_key="savedpaper.id", index=True)
    
    # Relevance
    relevance_score: Optional[float] = Field(default=None, description="How relevant this paper is to the message")
    was_referenced: bool = Field(default=False, description="Was explicitly mentioned by user")
    
    # Timestamps
    added_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_chat_context_message', 'message_id'),
        Index('idx_chat_context_paper', 'paper_id'),
    )


# ============================================
# PERFORMANCE MONITORING
# ============================================

class QueryPerformanceLog(SQLModel, table=True):
    """
    Track query execution times and patterns for optimization
    
    DBMS Concepts Demonstrated:
    - Query performance analysis
    - EXPLAIN QUERY PLAN usage
    - Index effectiveness tracking
    """
    __tablename__ = "query_performance_log"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Query details
    query_type: str = Field(max_length=100, index=True, description="Type: search, paper_list, citation_graph, etc.")
    query_sql: Optional[str] = Field(default=None, sa_column=Column(Text), description="SQL query executed")
    query_params_json: Optional[str] = Field(default=None, sa_column=Column(Text), description="Query parameters")
    
    # Performance metrics
    execution_time_ms: int = Field(description="Query execution time in milliseconds")
    rows_returned: int = Field(default=0)
    rows_scanned: Optional[int] = Field(default=None, description="Rows scanned (from EXPLAIN)")
    
    # Index usage
    indexes_used: Optional[str] = Field(default=None, sa_column=Column(Text), description="Indexes used by query")
    table_scans: int = Field(default=0, description="Number of full table scans")
    
    # Context
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    endpoint: Optional[str] = Field(default=None, max_length=255, description="API endpoint")
    
    # Timestamps
    executed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Performance flags
    is_slow_query: bool = Field(default=False, index=True, description="Execution time > threshold")
    needs_optimization: bool = Field(default=False, description="Query should be optimized")
    
    __table_args__ = (
        Index('idx_perf_type_time', 'query_type', 'execution_time_ms'),
        Index('idx_perf_slow', 'is_slow_query', 'executed_at'),
    )


# ============================================
# PAPER RECOMMENDATIONS
# ============================================

class PaperSimilarity(SQLModel, table=True):
    """
    Precomputed paper similarity scores for recommendations
    
    DBMS Concepts Demonstrated:
    - Materialized similarity computation
    - Graph algorithms (similarity)
    - Batch processing results
    """
    __tablename__ = "paper_similarity"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    paper_id_1: int = Field(foreign_key="savedpaper.id", index=True)
    paper_id_2: int = Field(foreign_key="savedpaper.id", index=True)
    
    # Similarity metrics
    citation_similarity: float = Field(default=0.0, ge=0.0, le=1.0, description="Based on shared citations")
    topic_similarity: float = Field(default=0.0, ge=0.0, le=1.0, description="Based on shared topics")
    author_similarity: float = Field(default=0.0, ge=0.0, le=1.0, description="Based on shared authors")
    
    # Combined score
    overall_similarity: float = Field(ge=0.0, le=1.0, description="Weighted combination")
    
    # Computation metadata
    computed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    computation_method: str = Field(max_length=50, description="Algorithm used")
    
    __table_args__ = (
        Index('idx_similarity_paper1', 'paper_id_1', 'overall_similarity'),
        Index('idx_similarity_paper2', 'paper_id_2', 'overall_similarity'),
        Index('idx_similarity_score', 'overall_similarity'),
    )


# ============================================
# ANALYTICS TABLES
# ============================================

class TrendingTopic(SQLModel, table=True):
    """
    Aggregated trending topics based on user activity
    
    DBMS Concepts Demonstrated:
    - Aggregation tables
    - Time-series aggregation
    - Windowing functions
    """
    __tablename__ = "trending_topic"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="research_topic.id", index=True)
    
    # Time window
    window_start: datetime = Field(index=True, description="Start of aggregation window")
    window_end: datetime = Field(index=True, description="End of aggregation window")
    window_type: str = Field(max_length=20, description="hour, day, week, month")
    
    # Metrics
    search_count: int = Field(default=0, description="Searches mentioning this topic")
    paper_save_count: int = Field(default=0, description="Papers saved with this topic")
    view_count: int = Field(default=0, description="Paper views with this topic")
    
    # Ranking
    trend_score: float = Field(default=0.0, description="Calculated trend score")
    rank_in_window: int = Field(default=0, description="Rank among all topics in window")
    
    # Timestamps
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_trending_window', 'window_type', 'window_start', 'rank_in_window'),
        Index('idx_trending_score', 'trend_score'),
    )
