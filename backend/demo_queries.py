"""
CiteMesh - Database Query Demonstrations
DBMS Project - Complex Query Examples

This script demonstrates advanced SQL queries and database operations
including joins, aggregations, subqueries, recursive queries, and transactions.
"""

import sqlite3
from datetime import datetime, timedelta
import json

# Database connection
DB_PATH = "database.db"

def get_db_connection():
    """Create database connection with proper settings"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn

# ============================================
# QUERY 1: Complex JOIN - User Activity Analysis
# ============================================

def query_user_activity_analysis(user_id: int):
    """
    Demonstrates: Multi-table JOIN, Aggregation, GROUP BY
    
    Finds comprehensive user activity across papers, collections, citations, and chat
    """
    query = """
    SELECT 
        u.id as user_id,
        u.full_name,
        u.email,
        u.role,
        COUNT(DISTINCT sp.id) as total_papers_saved,
        COUNT(DISTINCT c.id) as total_collections,
        COUNT(DISTINCT cl.id) as total_citations,
        COUNT(DISTINCT rcs.id) as total_chat_sessions,
        COUNT(DISTINCT rcm.id) as total_chat_messages,
        MAX(sp.saved_at) as last_paper_saved,
        MAX(rcs.updated_at) as last_chat_activity,
        CAST(julianday('now') - julianday(u.created_at) AS INTEGER) as account_age_days
    FROM user u
    LEFT JOIN savedpaper sp ON u.id = sp.user_id
    LEFT JOIN collection c ON u.id = c.user_id
    LEFT JOIN citationlink cl ON u.id = cl.user_id
    LEFT JOIN researchchatsession rcs ON u.id = rcs.user_id
    LEFT JOIN researchchatmessage rcm ON rcs.id = rcm.session_id
    WHERE u.id = ?
    GROUP BY u.id, u.full_name, u.email, u.role, u.created_at
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, (user_id,)).fetchone()
        return dict(result) if result else None

# ============================================
# QUERY 2: Recursive CTE - Citation Chain
# ============================================

def query_citation_chain(paper_id: str, max_depth: int = 5):
    """
    Demonstrates: Recursive Common Table Expression (CTE)
    
    Finds all papers in the citation chain starting from a given paper
    """
    query = """
    WITH RECURSIVE citation_chain(paper_id, depth, path) AS (
        -- Base case: Start with the initial paper
        SELECT 
            ? as paper_id,
            0 as depth,
            ? as path
        
        UNION ALL
        
        -- Recursive case: Find papers cited by papers in the chain
        SELECT 
            cl.target_paper_id as paper_id,
            cc.depth + 1 as depth,
            cc.path || ' -> ' || cl.target_paper_id as path
        FROM citation_chain cc
        JOIN citationlink cl ON cc.paper_id = cl.source_paper_id
        WHERE cc.depth < ?
    )
    SELECT 
        paper_id,
        depth,
        path,
        COUNT(*) OVER (PARTITION BY depth) as papers_at_depth
    FROM citation_chain
    ORDER BY depth, paper_id
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        results = cursor.execute(query, (paper_id, paper_id, max_depth)).fetchall()
        return [dict(row) for row in results]

# ============================================
# QUERY 3: Subquery - Top Collections by Activity
# ============================================

def query_top_collections_by_activity(limit: int = 10):
    """
    Demonstrates: Correlated subquery, Window functions
    
    Finds most active collections based on paper count and citation involvement
    """
    query = """
    SELECT 
        c.id,
        c.name,
        c.user_id,
        u.full_name as owner_name,
        c.paper_count,
        c.is_public,
        (
            SELECT COUNT(*)
            FROM citationlink cl
            WHERE cl.source_paper_id IN (
                SELECT paper_id
                FROM collectionpaper cp
                WHERE cp.collection_id = c.id
            )
        ) as citations_from_collection,
        (
            SELECT COUNT(DISTINCT cp.paper_year)
            FROM collectionpaper cp
            WHERE cp.collection_id = c.id
        ) as unique_years_covered,
        c.created_at,
        c.updated_at,
        RANK() OVER (ORDER BY c.paper_count DESC) as rank_by_papers
    FROM collection c
    JOIN user u ON c.user_id = u.id
    WHERE c.paper_count > 0
    ORDER BY c.paper_count DESC, citations_from_collection DESC
    LIMIT ?
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        results = cursor.execute(query, (limit,)).fetchall()
        return [dict(row) for row in results]

# ============================================
# QUERY 4: Aggregation - Paper Statistics
# ============================================

def query_paper_statistics():
    """
    Demonstrates: Complex aggregation, GROUP BY, HAVING
    
    Analyzes paper trends across the entire database
    """
    query = """
    SELECT 
        sp.published_year,
        COUNT(DISTINCT sp.id) as papers_saved,
        COUNT(DISTINCT sp.user_id) as unique_users,
        COUNT(DISTINCT sp.paper_id) as unique_papers,
        AVG(LENGTH(sp.summary)) as avg_summary_length,
        (
            SELECT COUNT(*)
            FROM citationlink cl
            WHERE cl.target_paper_id IN (
                SELECT paper_id
                FROM savedpaper sp2
                WHERE sp2.published_year = sp.published_year
            )
        ) as citations_for_year
    FROM savedpaper sp
    WHERE sp.published_year IS NOT NULL
    GROUP BY sp.published_year
    HAVING COUNT(*) > 0
    ORDER BY sp.published_year DESC
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        results = cursor.execute(query).fetchall()
        return [dict(row) for row in results]

# ============================================
# QUERY 5: Graph Analysis - Citation Network
# ============================================

def query_citation_network_analysis(user_id: int):
    """
    Demonstrates: Self-join, Graph metrics, Complex aggregation
    
    Analyzes citation network structure for a user
    """
    query = """
    WITH paper_citations AS (
        SELECT 
            cl.source_paper_id,
            cl.target_paper_id,
            cl.weight,
            COUNT(*) OVER (PARTITION BY cl.source_paper_id) as out_degree,
            COUNT(*) OVER (PARTITION BY cl.target_paper_id) as in_degree
        FROM citationlink cl
        WHERE cl.user_id = ?
    ),
    citation_stats AS (
        SELECT 
            source_paper_id as paper_id,
            SUM(weight) as total_out_weight,
            out_degree
        FROM paper_citations
        GROUP BY source_paper_id, out_degree
        
        UNION ALL
        
        SELECT 
            target_paper_id as paper_id,
            0 as total_out_weight,
            in_degree as out_degree
        FROM paper_citations
        GROUP BY target_paper_id, in_degree
    )
    SELECT 
        cs.paper_id,
        SUM(cs.total_out_weight) as total_citation_weight,
        MAX(cs.out_degree) as max_out_degree,
        COUNT(DISTINCT CASE WHEN cs.total_out_weight > 0 THEN cs.paper_id END) as papers_citing_others,
        COUNT(DISTINCT CASE WHEN cs.out_degree > 0 AND cs.total_out_weight = 0 THEN cs.paper_id END) as papers_cited,
        AVG(cs.out_degree) as avg_degree
    FROM citation_stats cs
    GROUP BY cs.paper_id
    ORDER BY total_citation_weight DESC, max_out_degree DESC
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        results = cursor.execute(query, (user_id,)).fetchall()
        return [dict(row) for row in results]

# ============================================
# QUERY 6: Time-series Analysis - User Growth
# ============================================

def query_user_growth_over_time():
    """
    Demonstrates: Date functions, Window functions, Running totals
    
    Analyzes user registration trends over time
    """
    query = """
    WITH daily_signups AS (
        SELECT 
            DATE(created_at) as signup_date,
            COUNT(*) as new_users,
            role
        FROM user
        WHERE created_at IS NOT NULL
        GROUP BY DATE(created_at), role
    )
    SELECT 
        signup_date,
        role,
        new_users,
        SUM(new_users) OVER (
            PARTITION BY role 
            ORDER BY signup_date 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) as cumulative_users,
        AVG(new_users) OVER (
            PARTITION BY role 
            ORDER BY signup_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as moving_avg_7_days
    FROM daily_signups
    ORDER BY signup_date DESC, role
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        results = cursor.execute(query).fetchall()
        return [dict(row) for row in results]

# ============================================
# QUERY 7: Complex Join - Mentor Dashboard
# ============================================

def query_mentor_dashboard(mentor_id: int):
    """
    Demonstrates: Multi-level JOIN, Aggregation across relationships
    
    Provides comprehensive view of all students for a mentor
    """
    query = """
    SELECT 
        s.id as student_id,
        s.full_name as student_name,
        s.email as student_email,
        COUNT(DISTINCT sp.id) as papers_saved,
        COUNT(DISTINCT c.id) as collections_created,
        COUNT(DISTINCT cl.id) as citations_made,
        COUNT(DISTINCT rcs.id) as chat_sessions,
        MAX(sp.saved_at) as last_paper_activity,
        MAX(rcs.updated_at) as last_chat_activity,
        (
            SELECT COUNT(*)
            FROM studentactivity sa
            WHERE sa.student_id = s.id 
            AND sa.mentor_id = ?
            AND sa.occurred_at > datetime('now', '-7 days')
        ) as activities_last_week,
        msl.created_at as mentorship_started
    FROM user s
    JOIN mentorstudentlink msl ON s.id = msl.student_id
    LEFT JOIN savedpaper sp ON s.id = sp.user_id
    LEFT JOIN collection c ON s.id = c.user_id
    LEFT JOIN citationlink cl ON s.id = cl.user_id
    LEFT JOIN researchchatsession rcs ON s.id = rcs.user_id
    WHERE msl.mentor_id = ?
    GROUP BY s.id, s.full_name, s.email, msl.created_at
    ORDER BY activities_last_week DESC, last_paper_activity DESC
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        results = cursor.execute(query, (mentor_id, mentor_id)).fetchall()
        return [dict(row) for row in results]

# ============================================
# QUERY 8: Optimization Example - Index Usage
# ============================================

def query_most_cited_papers_optimized(limit: int = 10):
    """
    Demonstrates: Query optimization using indexes
    
    This query uses indexes on citationlink(target_paper_id) and savedpaper(paper_id)
    for efficient lookups
    """
    query = """
    EXPLAIN QUERY PLAN
    SELECT 
        cl.target_paper_id,
        sp.title,
        sp.authors,
        sp.published_year,
        COUNT(*) as citation_count,
        COUNT(DISTINCT cl.user_id) as cited_by_users,
        AVG(cl.weight) as avg_citation_weight,
        MIN(cl.created_at) as first_cited,
        MAX(cl.created_at) as last_cited
    FROM citationlink cl
    LEFT JOIN savedpaper sp ON cl.target_paper_id = sp.paper_id
    GROUP BY cl.target_paper_id, sp.title, sp.authors, sp.published_year
    ORDER BY citation_count DESC, cited_by_users DESC
    LIMIT ?
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # First show the query plan
        print("\n=== QUERY PLAN (showing index usage) ===")
        plan = cursor.execute(query, (limit,)).fetchall()
        for row in plan:
            print(dict(row))
        
        # Then execute the actual query
        actual_query = query.replace("EXPLAIN QUERY PLAN\n", "")
        results = cursor.execute(actual_query, (limit,)).fetchall()
        return [dict(row) for row in results]

# ============================================
# QUERY 9: Transaction Example - Collection Management
# ============================================

def transaction_create_collection_with_papers(user_id: int, collection_data: dict, paper_ids: list):
    """
    Demonstrates: ACID transactions, Rollback on error
    
    Creates a collection and adds papers atomically
    """
    conn = get_db_connection()
    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Insert collection
        cursor = conn.execute("""
            INSERT INTO collection (user_id, name, description, color, icon, is_public)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            collection_data['name'],
            collection_data.get('description'),
            collection_data.get('color', '#6366f1'),
            collection_data.get('icon', '📚'),
            collection_data.get('is_public', False)
        ))
        
        collection_id = cursor.lastrowid
        
        # Add papers to collection
        for idx, paper_id in enumerate(paper_ids):
            conn.execute("""
                INSERT INTO collectionpaper (collection_id, paper_id, paper_title, order_index)
                VALUES (?, ?, ?, ?)
            """, (collection_id, paper_id, f"Paper {paper_id}", idx))
        
        # Update paper count
        conn.execute("""
            UPDATE collection 
            SET paper_count = ?
            WHERE id = ?
        """, (len(paper_ids), collection_id))
        
        # Commit transaction
        conn.commit()
        print(f"✅ Transaction successful: Collection {collection_id} created with {len(paper_ids)} papers")
        return collection_id
        
    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f"❌ Transaction failed: {e}")
        raise
    finally:
        conn.close()

# ============================================
# QUERY 10: Advanced Analytics - Research Trends
# ============================================

def query_research_trends_by_year(start_year: int = 2000):
    """
    Demonstrates: Complex aggregation, Trend analysis
    
    Analyzes research trends based on papers, citations, and collections
    """
    query = """
    WITH yearly_stats AS (
        SELECT 
            sp.published_year as year,
            COUNT(DISTINCT sp.paper_id) as unique_papers,
            COUNT(DISTINCT sp.user_id) as users_interested,
            COUNT(*) as total_saves
        FROM savedpaper sp
        WHERE sp.published_year >= ?
        GROUP BY sp.published_year
    ),
    yearly_citations AS (
        SELECT 
            sp.published_year as year,
            COUNT(DISTINCT cl.id) as citations_made
        FROM citationlink cl
        JOIN savedpaper sp ON cl.target_paper_id = sp.paper_id
        WHERE sp.published_year >= ?
        GROUP BY sp.published_year
    )
    SELECT 
        ys.year,
        ys.unique_papers,
        ys.users_interested,
        ys.total_saves,
        COALESCE(yc.citations_made, 0) as citations_made,
        CAST(COALESCE(yc.citations_made, 0) AS FLOAT) / ys.unique_papers as citations_per_paper,
        CAST(ys.total_saves AS FLOAT) / ys.users_interested as avg_saves_per_user,
        ys.total_saves - LAG(ys.total_saves) OVER (ORDER BY ys.year) as saves_growth_yoy
    FROM yearly_stats ys
    LEFT JOIN yearly_citations yc ON ys.year = yc.year
    ORDER BY ys.year DESC
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        results = cursor.execute(query, (start_year, start_year)).fetchall()
        return [dict(row) for row in results]

# ============================================
# UTILITY FUNCTIONS
# ============================================

def print_results(results, title):
    """Pretty print query results"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")
    
    if not results:
        print("No results found.")
        return
    
    if isinstance(results, list):
        for i, row in enumerate(results, 1):
            print(f"Result {i}:")
            for key, value in row.items():
                print(f"  {key}: {value}")
            print()
    elif isinstance(results, dict):
        for key, value in results.items():
            print(f"  {key}: {value}")
    
    print(f"Total results: {len(results) if isinstance(results, list) else 1}\n")

# ============================================
# DEMO SCRIPT
# ============================================

def run_all_demonstrations():
    """
    Run all query demonstrations
    """
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║          CiteMesh - Database Query Demonstrations                  ║
    ║                 DBMS Project - SQL Examples                         ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Demo 1: User Activity Analysis
    print("\n📊 DEMO 1: Multi-table JOIN - User Activity Analysis")
    result = query_user_activity_analysis(1)
    print_results(result, "User Activity Comprehensive Report")
    
    # Demo 2: Citation Chain (Recursive)
    print("\n🔗 DEMO 2: Recursive CTE - Citation Chain")
    result = query_citation_chain("example_paper_id", max_depth=3)
    print_results(result, "Citation Chain (Recursive Traversal)")
    
    # Demo 3: Top Collections
    print("\n⭐ DEMO 3: Subquery - Top Collections by Activity")
    result = query_top_collections_by_activity(5)
    print_results(result, "Top 5 Most Active Collections")
    
    # Demo 4: Paper Statistics
    print("\n📈 DEMO 4: Aggregation - Paper Statistics by Year")
    result = query_paper_statistics()
    print_results(result, "Paper Trends Over Years")
    
    # Demo 5: Citation Network
    print("\n🌐 DEMO 5: Graph Analysis - Citation Network Metrics")
    result = query_citation_network_analysis(1)
    print_results(result, "Citation Network Analysis for User")
    
    # Demo 6: User Growth
    print("\n📅 DEMO 6: Time-series - User Growth Trends")
    result = query_user_growth_over_time()
    print_results(result, "User Registration Trends (with Moving Average)")
    
    # Demo 7: Mentor Dashboard
    print("\n👨‍🏫 DEMO 7: Complex JOIN - Mentor Dashboard")
    result = query_mentor_dashboard(1)
    print_results(result, "Mentor View of All Students")
    
    # Demo 8: Query Optimization
    print("\n⚡ DEMO 8: Query Optimization - Index Usage")
    result = query_most_cited_papers_optimized(5)
    print_results(result, "Most Cited Papers (Optimized Query)")
    
    # Demo 9: Transaction Example
    print("\n💾 DEMO 9: ACID Transaction - Collection Creation")
    try:
        collection_id = transaction_create_collection_with_papers(
            user_id=1,
            collection_data={'name': 'ML Papers', 'description': 'Machine Learning Collection'},
            paper_ids=['paper1', 'paper2', 'paper3']
        )
        print(f"Collection {collection_id} created successfully!")
    except Exception as e:
        print(f"Transaction demonstration completed (may fail if data exists)")
    
    # Demo 10: Research Trends
    print("\n📊 DEMO 10: Advanced Analytics - Research Trends")
    result = query_research_trends_by_year(2015)
    print_results(result, "Research Trends Analysis (2015-Present)")
    
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                 All Demonstrations Completed!                       ║
    ║                                                                     ║
    ║  This script demonstrated:                                          ║
    ║  ✓ Multi-table JOINs (3-5 tables)                                  ║
    ║  ✓ Recursive CTEs (citation chains)                                ║
    ║  ✓ Subqueries and correlated subqueries                            ║
    ║  ✓ Window functions (RANK, SUM OVER, AVG OVER)                     ║
    ║  ✓ Aggregation (COUNT, AVG, SUM, MIN, MAX)                         ║
    ║  ✓ Graph analysis (citation networks)                              ║
    ║  ✓ Time-series analysis (trends, moving averages)                  ║
    ║  ✓ Query optimization (EXPLAIN QUERY PLAN)                         ║
    ║  ✓ ACID transactions (BEGIN, COMMIT, ROLLBACK)                     ║
    ║  ✓ Complex analytics (YoY growth, ratios)                          ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    run_all_demonstrations()
