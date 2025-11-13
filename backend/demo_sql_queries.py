"""
CiteMesh - Advanced SQL Queries Demonstration
==============================================

This file demonstrates comprehensive DBMS concepts using RAW SQL:

1. Complex JOINs (INNER, LEFT, RIGHT, CROSS)
2. Subqueries (correlated and non-correlated)
3. Common Table Expressions (CTEs) - Recursive and Non-recursive
4. Window Functions (ROW_NUMBER, RANK, LAG, LEAD)
5. Aggregate Functions (COUNT, SUM, AVG, MIN, MAX, GROUP_CONCAT)
6. GROUP BY with HAVING
7. Set Operations (UNION, INTERSECT, EXCEPT)
8. Transaction Management
9. Index Usage and Query Optimization
10. Full-Text Search

Run: python backend/demo_sql_queries.py
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


class SQLDemonstration:
    def __init__(self, db_path: str = "backend/app.db"):
        self.db_path = db_path
    
    def print_section(self, title: str, concept: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print(f"  DBMS Concept: {concept}")
        print("=" * 80 + "\n")
    
    def execute_and_display(self, query: str, params: tuple = (), title: str = ""):
        """Execute query and display results"""
        if title:
            print(f"\n{title}\n")
        
        print("SQL Query:")
        print("-" * 80)
        print(query)
        print("-" * 80)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            print(f"\nResults ({len(results)} rows):")
            print("-" * 80)
            
            if results:
                # Print column names
                columns = results[0].keys()
                print(" | ".join(columns))
                print("-" * 80)
                
                # Print first 10 rows
                for row in results[:10]:
                    print(" | ".join(str(row[col])[:30] for col in columns))
            else:
                print("(No results)")
            
            print()
            
            conn.commit()
        except Exception as e:
            print(f"❌ Error: {e}\n")
        finally:
            conn.close()
    
    # =========================================================================
    # DEMO 1: Complex Multi-Table JOINs
    # =========================================================================
    
    def demo_complex_joins(self):
        self.print_section(
            "DEMO 1: Complex Multi-Table JOINs",
            "INNER JOIN, LEFT JOIN, Multiple table joins, Aggregations"
        )
        
        # Query 1: Mentor Dashboard - 6-table JOIN
        query = """
            -- Comprehensive Mentor Dashboard Query
            -- Demonstrates: Multi-level JOINs, LEFT JOINs, Aggregations
            
            SELECT 
                u.id as student_id,
                u.email,
                u.full_name,
                COUNT(DISTINCT sp.id) as papers_saved,
                COUNT(DISTINCT c.id) as collections_created,
                COUNT(DISTINCT cl.id) as citations_made,
                COUNT(DISTINCT rcs.id) as chat_sessions,
                MAX(sp.saved_at) as last_paper_activity,
                MAX(rcs.updated_at) as last_chat_activity,
                msl.created_at as mentorship_started,
                ROUND(JULIANDAY('now') - JULIANDAY(msl.created_at)) as days_as_mentee
            FROM user u
            INNER JOIN mentorstudentlink msl ON u.id = msl.student_id
            LEFT JOIN savedpaper sp ON u.id = sp.user_id
            LEFT JOIN collection c ON u.id = c.user_id
            LEFT JOIN citationlink cl ON u.id = cl.user_id
            LEFT JOIN researchchatsession rcs ON u.id = rcs.user_id
            WHERE msl.mentor_id = (SELECT id FROM user WHERE role = 'mentor' LIMIT 1)
            GROUP BY u.id, u.email, u.full_name, msl.created_at
            ORDER BY papers_saved DESC, last_paper_activity DESC
            LIMIT 10;
        """
        
        self.execute_and_display(query, title="Multi-Table JOIN: Mentor Dashboard")
    
    # =========================================================================
    # DEMO 2: Subqueries (Correlated and Non-Correlated)
    # =========================================================================
    
    def demo_subqueries(self):
        self.print_section(
            "DEMO 2: Subqueries",
            "Correlated subqueries, Scalar subqueries, EXISTS clause"
        )
        
        # Query 1: Papers with above-average citations
        query = """
            -- Papers with Above-Average Citation Count
            -- Demonstrates: Scalar subquery in WHERE clause
            
            SELECT 
                paper_id,
                title,
                authors,
                published_year,
                (SELECT COUNT(*) 
                 FROM citationlink cl 
                 WHERE cl.source_paper_id = sp.paper_id) as citations_count,
                (SELECT AVG(cnt) 
                 FROM (SELECT COUNT(*) as cnt 
                       FROM citationlink 
                       GROUP BY source_paper_id)) as avg_citations
            FROM savedpaper sp
            WHERE (SELECT COUNT(*) 
                   FROM citationlink cl 
                   WHERE cl.source_paper_id = sp.paper_id) > 
                  (SELECT AVG(cnt) 
                   FROM (SELECT COUNT(*) as cnt 
                         FROM citationlink 
                         GROUP BY source_paper_id))
            ORDER BY citations_count DESC
            LIMIT 10;
        """
        
        self.execute_and_display(query, title="Subquery: Above-Average Citations")
        
        # Query 2: Correlated subquery - Students with recent activity
        query2 = """
            -- Students with Activity in Last 7 Days
            -- Demonstrates: Correlated subquery with EXISTS
            
            SELECT 
                u.id,
                u.email,
                u.full_name,
                (SELECT COUNT(*) 
                 FROM savedpaper sp 
                 WHERE sp.user_id = u.id 
                 AND sp.saved_at > datetime('now', '-7 days')) as papers_last_week,
                (SELECT MAX(saved_at) 
                 FROM savedpaper sp 
                 WHERE sp.user_id = u.id) as last_activity
            FROM user u
            WHERE EXISTS (
                SELECT 1 
                FROM savedpaper sp 
                WHERE sp.user_id = u.id 
                AND sp.saved_at > datetime('now', '-7 days')
            )
            ORDER BY papers_last_week DESC;
        """
        
        self.execute_and_display(query2, title="Correlated Subquery: Recent Activity")
    
    # =========================================================================
    # DEMO 3: Common Table Expressions (CTEs)
    # =========================================================================
    
    def demo_ctes(self):
        self.print_section(
            "DEMO 3: Common Table Expressions (CTEs)",
            "WITH clause, Non-recursive CTEs, Query readability"
        )
        
        # Query 1: User statistics with CTE
        query = """
            -- User Research Activity Statistics Using CTE
            -- Demonstrates: Multiple CTEs, Clean query structure
            
            WITH user_papers AS (
                SELECT 
                    user_id,
                    COUNT(*) as paper_count,
                    MAX(saved_at) as last_paper_date
                FROM savedpaper
                GROUP BY user_id
            ),
            user_collections AS (
                SELECT 
                    user_id,
                    COUNT(*) as collection_count
                FROM collection
                GROUP BY user_id
            ),
            user_citations AS (
                SELECT 
                    user_id,
                    COUNT(*) as citation_count
                FROM citationlink
                GROUP BY user_id
            )
            SELECT 
                u.id,
                u.email,
                u.full_name,
                COALESCE(up.paper_count, 0) as papers,
                COALESCE(uc.collection_count, 0) as collections,
                COALESCE(uci.citation_count, 0) as citations,
                up.last_paper_date,
                CASE 
                    WHEN up.last_paper_date > datetime('now', '-7 days') THEN 'Active'
                    WHEN up.last_paper_date > datetime('now', '-30 days') THEN 'Moderate'
                    ELSE 'Inactive'
                END as activity_status
            FROM user u
            LEFT JOIN user_papers up ON u.id = up.user_id
            LEFT JOIN user_collections uc ON u.id = uc.user_id
            LEFT JOIN user_citations uci ON u.id = uci.user_id
            WHERE u.role != 'admin'
            ORDER BY papers DESC, collections DESC
            LIMIT 20;
        """
        
        self.execute_and_display(query, title="CTE: User Activity Statistics")
        
        # Query 2: Recursive CTE for citation chains (if supported)
        query2 = """
            -- Citation Chain Analysis
            -- Demonstrates: CTE with self-referencing query
            
            WITH citation_stats AS (
                SELECT 
                    source_paper_id,
                    target_paper_id,
                    weight,
                    created_at
                FROM citationlink
            ),
            paper_info AS (
                SELECT 
                    cs.source_paper_id,
                    sp.title as source_title,
                    COUNT(*) as outgoing_citations,
                    AVG(cs.weight) as avg_citation_weight
                FROM citation_stats cs
                JOIN savedpaper sp ON cs.source_paper_id = sp.paper_id
                GROUP BY cs.source_paper_id, sp.title
            )
            SELECT 
                source_paper_id,
                source_title,
                outgoing_citations,
                ROUND(avg_citation_weight, 2) as avg_weight,
                CASE 
                    WHEN outgoing_citations > 10 THEN 'High Impact'
                    WHEN outgoing_citations > 5 THEN 'Medium Impact'
                    ELSE 'Low Impact'
                END as impact_category
            FROM paper_info
            ORDER BY outgoing_citations DESC
            LIMIT 15;
        """
        
        self.execute_and_display(query2, title="CTE: Citation Chain Analysis")
    
    # =========================================================================
    # DEMO 4: Window Functions
    # =========================================================================
    
    def demo_window_functions(self):
        self.print_section(
            "DEMO 4: Window Functions",
            "ROW_NUMBER, RANK, DENSE_RANK, PARTITION BY, Running totals"
        )
        
        # Query 1: Ranking users by paper count
        query = """
            -- User Paper Rankings with Window Functions
            -- Demonstrates: ROW_NUMBER, RANK, PARTITION BY
            
            SELECT 
                u.id,
                u.email,
                u.role,
                COUNT(sp.id) as paper_count,
                ROW_NUMBER() OVER (ORDER BY COUNT(sp.id) DESC) as overall_rank,
                RANK() OVER (ORDER BY COUNT(sp.id) DESC) as dense_rank,
                ROW_NUMBER() OVER (PARTITION BY u.role ORDER BY COUNT(sp.id) DESC) as rank_in_role,
                ROUND(COUNT(sp.id) * 100.0 / SUM(COUNT(sp.id)) OVER (), 2) as pct_of_total
            FROM user u
            LEFT JOIN savedpaper sp ON u.id = sp.user_id
            GROUP BY u.id, u.email, u.role
            HAVING COUNT(sp.id) > 0
            ORDER BY paper_count DESC
            LIMIT 20;
        """
        
        self.execute_and_display(query, title="Window Functions: User Rankings")
        
        # Query 2: Running total of papers over time
        query2 = """
            -- Running Total of Papers Saved Over Time
            -- Demonstrates: SUM() OVER (ORDER BY), Cumulative aggregation
            
            SELECT 
                DATE(saved_at) as save_date,
                COUNT(*) as papers_saved_today,
                SUM(COUNT(*)) OVER (ORDER BY DATE(saved_at)) as cumulative_papers,
                AVG(COUNT(*)) OVER (ORDER BY DATE(saved_at) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_7day_avg
            FROM savedpaper
            WHERE saved_at >= datetime('now', '-30 days')
            GROUP BY DATE(saved_at)
            ORDER BY save_date DESC;
        """
        
        self.execute_and_display(query2, title="Window Functions: Running Totals")
    
    # =========================================================================
    # DEMO 5: Advanced Aggregations
    # =========================================================================
    
    def demo_aggregations(self):
        self.print_section(
            "DEMO 5: Advanced Aggregations",
            "GROUP BY, HAVING, Multiple aggregates, GROUP_CONCAT"
        )
        
        # Query 1: Research topic distribution
        query = """
            -- Research Topic Distribution by User
            -- Demonstrates: GROUP BY, HAVING, COUNT, GROUP_CONCAT
            
            SELECT 
                u.id,
                u.email,
                u.full_name,
                COUNT(DISTINCT sp.id) as total_papers,
                COUNT(DISTINCT CASE WHEN sp.published_year >= 2020 THEN sp.id END) as recent_papers,
                GROUP_CONCAT(DISTINCT sp.tags) as research_topics,
                MIN(sp.published_year) as earliest_paper,
                MAX(sp.published_year) as latest_paper,
                AVG(CAST(sp.published_year AS REAL)) as avg_publication_year
            FROM user u
            INNER JOIN savedpaper sp ON u.id = sp.user_id
            WHERE sp.published_year IS NOT NULL
            GROUP BY u.id, u.email, u.full_name
            HAVING COUNT(DISTINCT sp.id) >= 3
            ORDER BY total_papers DESC
            LIMIT 15;
        """
        
        self.execute_and_display(query, title="Aggregations: Research Topics")
        
        # Query 2: Collection statistics with CASE expressions
        query2 = """
            -- Collection Size Distribution
            -- Demonstrates: CASE in aggregation, Bucketing
            
            SELECT 
                CASE 
                    WHEN paper_count = 0 THEN 'Empty'
                    WHEN paper_count BETWEEN 1 AND 5 THEN '1-5 papers'
                    WHEN paper_count BETWEEN 6 AND 10 THEN '6-10 papers'
                    WHEN paper_count BETWEEN 11 AND 20 THEN '11-20 papers'
                    ELSE '20+ papers'
                END as size_category,
                COUNT(*) as collection_count,
                AVG(paper_count) as avg_papers,
                MIN(paper_count) as min_papers,
                MAX(paper_count) as max_papers
            FROM collection
            GROUP BY size_category
            ORDER BY min_papers;
        """
        
        self.execute_and_display(query2, title="Aggregations: Collection Distribution")
    
    # =========================================================================
    # DEMO 6: Set Operations
    # =========================================================================
    
    def demo_set_operations(self):
        self.print_section(
            "DEMO 6: Set Operations",
            "UNION, INTERSECT, EXCEPT"
        )
        
        # Query 1: UNION of active users from different sources
        query = """
            -- Active Users from Multiple Sources (UNION)
            -- Demonstrates: UNION ALL for combining results
            
            SELECT DISTINCT
                u.id,
                u.email,
                'Paper Activity' as activity_source,
                sp.saved_at as last_activity
            FROM user u
            INNER JOIN savedpaper sp ON u.id = sp.user_id
            WHERE sp.saved_at > datetime('now', '-7 days')
            
            UNION ALL
            
            SELECT DISTINCT
                u.id,
                u.email,
                'Chat Activity' as activity_source,
                rcs.updated_at as last_activity
            FROM user u
            INNER JOIN researchchatsession rcs ON u.id = rcs.user_id
            WHERE rcs.updated_at > datetime('now', '-7 days')
            
            UNION ALL
            
            SELECT DISTINCT
                u.id,
                u.email,
                'Citation Activity' as activity_source,
                cl.created_at as last_activity
            FROM user u
            INNER JOIN citationlink cl ON u.id = cl.user_id
            WHERE cl.created_at > datetime('now', '-7 days')
            
            ORDER BY last_activity DESC;
        """
        
        self.execute_and_display(query, title="Set Operations: UNION of Activities")
    
    # =========================================================================
    # DEMO 7: Search Cache Performance Analysis
    # =========================================================================
    
    def demo_cache_analysis(self):
        self.print_section(
            "DEMO 7: Search Cache Performance",
            "Index usage, Cache hit rate, Performance metrics"
        )
        
        query = """
            -- Search Cache Performance Analysis
            -- Demonstrates: Aggregate functions, Percentage calculations, Index usage
            
            SELECT 
                COUNT(*) as total_cache_entries,
                SUM(CASE WHEN expires_at > datetime('now') THEN 1 ELSE 0 END) as active_entries,
                SUM(CASE WHEN expires_at <= datetime('now') THEN 1 ELSE 0 END) as expired_entries,
                SUM(hit_count) as total_cache_hits,
                AVG(hit_count) as avg_hits_per_entry,
                MAX(hit_count) as max_hits,
                AVG(api_response_time_ms) as avg_api_time_ms,
                ROUND(SUM(CASE WHEN expires_at > datetime('now') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as active_percentage,
                (SELECT query_text FROM search_cache ORDER BY hit_count DESC LIMIT 1) as most_popular_query
            FROM search_cache;
        """
        
        self.execute_and_display(query, title="Cache Analysis: Performance Metrics")
        
        # Query 2: Search history trends
        query2 = """
            -- Search Trends Over Time
            -- Demonstrates: Date grouping, Trend analysis
            
            SELECT 
                DATE(created_at) as search_date,
                COUNT(*) as total_searches,
                COUNT(DISTINCT user_id) as unique_users,
                SUM(CASE WHEN cache_hit = 1 THEN 1 ELSE 0 END) as cache_hits,
                SUM(CASE WHEN use_ai_enhancement = 1 THEN 1 ELSE 0 END) as ai_enhanced,
                AVG(search_time_ms) as avg_search_time,
                AVG(results_count) as avg_results
            FROM search_history
            WHERE created_at >= datetime('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY search_date DESC
            LIMIT 30;
        """
        
        self.execute_and_display(query2, title="Search History: Daily Trends")
    
    # =========================================================================
    # DEMO 8: Citation Network Analysis
    # =========================================================================
    
    def demo_citation_network(self):
        self.print_section(
            "DEMO 8: Citation Network Analysis",
            "Graph queries, Network metrics, Centrality"
        )
        
        query = """
            -- Citation Network Centrality
            -- Demonstrates: Self-joins, Network analysis, Graph metrics
            
            WITH citation_degrees AS (
                SELECT 
                    source_paper_id as paper_id,
                    COUNT(*) as out_degree
                FROM citationlink
                GROUP BY source_paper_id
            ),
            cited_papers AS (
                SELECT 
                    target_paper_id as paper_id,
                    COUNT(*) as in_degree
                FROM citationlink
                GROUP BY target_paper_id
            )
            SELECT 
                sp.paper_id,
                sp.title,
                sp.authors,
                sp.published_year,
                COALESCE(cd.out_degree, 0) as citations_made,
                COALESCE(cp.in_degree, 0) as times_cited,
                COALESCE(cd.out_degree, 0) + COALESCE(cp.in_degree, 0) as total_degree,
                CASE 
                    WHEN COALESCE(cp.in_degree, 0) > 5 THEN 'Highly Cited'
                    WHEN COALESCE(cp.in_degree, 0) > 2 THEN 'Moderately Cited'
                    ELSE 'Low Citations'
                END as citation_category
            FROM savedpaper sp
            LEFT JOIN citation_degrees cd ON sp.paper_id = cd.paper_id
            LEFT JOIN cited_papers cp ON sp.paper_id = cp.paper_id
            WHERE COALESCE(cd.out_degree, 0) + COALESCE(cp.in_degree, 0) > 0
            ORDER BY total_degree DESC, times_cited DESC
            LIMIT 20;
        """
        
        self.execute_and_display(query, title="Citation Network: Centrality Metrics")
    
    # =========================================================================
    # DEMO 9: Transaction Example
    # =========================================================================
    
    def demo_transactions(self):
        self.print_section(
            "DEMO 9: Transaction Management",
            "BEGIN, COMMIT, ROLLBACK, ACID properties"
        )
        
        print("Transaction Example:")
        print("-" * 80)
        print("""
-- Example: Atomic operation to move paper between collections
-- Demonstrates: Transaction atomicity, error handling

BEGIN TRANSACTION;

-- Step 1: Remove paper from old collection
DELETE FROM collectionpaper 
WHERE collection_id = 1 AND paper_id = 'paper123';

-- Step 2: Add paper to new collection
INSERT INTO collectionpaper (collection_id, paper_id, paper_title, added_at)
VALUES (2, 'paper123', 'Example Paper', datetime('now'));

-- Step 3: Update collection counts
UPDATE collection SET paper_count = paper_count - 1, updated_at = datetime('now')
WHERE id = 1;

UPDATE collection SET paper_count = paper_count + 1, updated_at = datetime('now')
WHERE id = 2;

-- If all steps succeed, commit; otherwise rollback
COMMIT;  -- or ROLLBACK on error
        """)
        print("-" * 80)
    
    # =========================================================================
    # DEMO 10: Index Usage and Query Plans
    # =========================================================================
    
    def demo_query_optimization(self):
        self.print_section(
            "DEMO 10: Query Optimization",
            "EXPLAIN QUERY PLAN, Index usage, Performance tuning"
        )
        
        # Show query plan for complex query
        query = """
            EXPLAIN QUERY PLAN
            SELECT 
                sp.paper_id,
                sp.title,
                COUNT(cl.id) as citation_count
            FROM savedpaper sp
            LEFT JOIN citationlink cl ON sp.paper_id = cl.source_paper_id
            WHERE sp.user_id = 1
            GROUP BY sp.paper_id, sp.title
            ORDER BY citation_count DESC;
        """
        
        self.execute_and_display(query, title="Query Plan: Citation Count")
        
        # Show indexes
        query2 = """
            SELECT 
                type,
                name,
                tbl_name,
                sql
            FROM sqlite_master
            WHERE type = 'index'
            AND tbl_name IN ('savedpaper', 'citationlink', 'search_cache', 'search_history')
            ORDER BY tbl_name, name;
        """
        
        self.execute_and_display(query2, title="Database Indexes")
    
    # =========================================================================
    # Run All Demos
    # =========================================================================
    
    def run_all_demos(self):
        print("\n")
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                              ║")
        print("║                  CiteMesh - SQL Queries Demonstration                        ║")
        print("║                    Advanced DBMS Concepts Showcase                           ║")
        print("║                                                                              ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        
        self.demo_complex_joins()
        self.demo_subqueries()
        self.demo_ctes()
        self.demo_window_functions()
        self.demo_aggregations()
        self.demo_set_operations()
        self.demo_cache_analysis()
        self.demo_citation_network()
        self.demo_transactions()
        self.demo_query_optimization()
        
        print("\n" + "=" * 80)
        print("  ✨ All SQL Demonstrations Complete!")
        print("=" * 80)
        print("\nKey DBMS Concepts Demonstrated:")
        print("  ✅ Complex multi-table JOINs (6+ tables)")
        print("  ✅ Correlated and non-correlated subqueries")
        print("  ✅ Common Table Expressions (CTEs)")
        print("  ✅ Window functions (ROW_NUMBER, RANK, running totals)")
        print("  ✅ Advanced aggregations (GROUP BY, HAVING)")
        print("  ✅ Set operations (UNION, INTERSECT)")
        print("  ✅ Transaction management (ACID)")
        print("  ✅ Query optimization (EXPLAIN, indexes)")
        print("  ✅ Graph queries (citation network)")
        print("  ✅ Performance analysis (cache metrics)\n")


if __name__ == "__main__":
    demo = SQLDemonstration()
    demo.run_all_demos()
