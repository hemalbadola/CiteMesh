# CiteMesh - DBMS Project Documentation

## 🎓 Database Management System Concepts Demonstrated

This project showcases **advanced DBMS concepts** using **RAW SQL queries** (not just ORM):

### 📊 Core DBMS Features

#### 1. **Complex Multi-Table JOINs**
- 6-table JOINs for mentor dashboard
- INNER JOIN, LEFT JOIN, RIGHT JOIN
- Self-referencing JOINs (mentor-student relationships)

```sql
-- Example: Mentor Dashboard with 6-table JOIN
SELECT 
    u.id, u.email, u.full_name,
    COUNT(DISTINCT sp.id) as papers_saved,
    COUNT(DISTINCT c.id) as collections_created,
    COUNT(DISTINCT cl.id) as citations_made
FROM user u
INNER JOIN mentorstudentlink msl ON u.id = msl.student_id
LEFT JOIN savedpaper sp ON u.id = sp.user_id
LEFT JOIN collection c ON u.id = c.user_id
LEFT JOIN citationlink cl ON u.id = cl.user_id
WHERE msl.mentor_id = ?
GROUP BY u.id, u.email, u.full_name;
```

#### 2. **Subqueries (Correlated & Non-Correlated)**
- Scalar subqueries in SELECT
- Correlated subqueries with EXISTS
- Subqueries in WHERE and HAVING clauses

```sql
-- Example: Papers with above-average citations
SELECT paper_id, title,
    (SELECT COUNT(*) FROM citationlink WHERE source_paper_id = sp.paper_id) as citations
FROM savedpaper sp
WHERE (SELECT COUNT(*) FROM citationlink WHERE source_paper_id = sp.paper_id) > 
      (SELECT AVG(cnt) FROM (SELECT COUNT(*) as cnt FROM citationlink GROUP BY source_paper_id));
```

#### 3. **Common Table Expressions (CTEs)**
- Non-recursive CTEs for query readability
- Recursive CTEs for citation chains
- Multiple CTEs in single query

```sql
-- Example: User statistics with multiple CTEs
WITH user_papers AS (
    SELECT user_id, COUNT(*) as paper_count FROM savedpaper GROUP BY user_id
),
user_collections AS (
    SELECT user_id, COUNT(*) as collection_count FROM collection GROUP BY user_id
)
SELECT u.email, up.paper_count, uc.collection_count
FROM user u
LEFT JOIN user_papers up ON u.id = up.user_id
LEFT JOIN user_collections uc ON u.id = uc.user_id;
```

#### 4. **Window Functions**
- ROW_NUMBER(), RANK(), DENSE_RANK()
- PARTITION BY for grouped rankings
- Running totals with SUM() OVER ()
- Moving averages with ROWS BETWEEN

```sql
-- Example: User rankings with window functions
SELECT 
    u.email,
    COUNT(sp.id) as paper_count,
    ROW_NUMBER() OVER (ORDER BY COUNT(sp.id) DESC) as overall_rank,
    ROW_NUMBER() OVER (PARTITION BY u.role ORDER BY COUNT(sp.id) DESC) as rank_in_role
FROM user u
LEFT JOIN savedpaper sp ON u.id = sp.user_id
GROUP BY u.id, u.email, u.role;
```

#### 5. **Advanced Aggregations**
- GROUP BY with HAVING
- Multiple aggregate functions (COUNT, SUM, AVG, MIN, MAX)
- CASE expressions in aggregations
- GROUP_CONCAT for array aggregation

```sql
-- Example: Research topic distribution
SELECT 
    u.email,
    COUNT(DISTINCT sp.id) as total_papers,
    GROUP_CONCAT(DISTINCT sp.tags) as research_topics,
    AVG(CAST(sp.published_year AS REAL)) as avg_publication_year
FROM user u
INNER JOIN savedpaper sp ON u.id = sp.user_id
GROUP BY u.id, u.email
HAVING COUNT(DISTINCT sp.id) >= 3;
```

#### 6. **Set Operations**
- UNION and UNION ALL
- INTERSECT for common results
- EXCEPT for difference queries

```sql
-- Example: Active users from multiple sources
SELECT u.id, u.email, 'Paper Activity' as source FROM user u
INNER JOIN savedpaper sp ON u.id = sp.user_id
WHERE sp.saved_at > datetime('now', '-7 days')
UNION ALL
SELECT u.id, u.email, 'Chat Activity' FROM user u
INNER JOIN researchchatsession rcs ON u.id = rcs.user_id
WHERE rcs.updated_at > datetime('now', '-7 days');
```

#### 7. **Transaction Management**
- BEGIN, COMMIT, ROLLBACK
- ACID properties enforcement
- Multi-step atomic operations

```sql
-- Example: Atomic collection paper move
BEGIN TRANSACTION;
DELETE FROM collectionpaper WHERE collection_id = 1 AND paper_id = 'p123';
INSERT INTO collectionpaper (collection_id, paper_id) VALUES (2, 'p123');
UPDATE collection SET paper_count = paper_count - 1 WHERE id = 1;
UPDATE collection SET paper_count = paper_count + 1 WHERE id = 2;
COMMIT;
```

#### 8. **Indexes & Query Optimization**
- Composite indexes (multi-column)
- Foreign key indexes
- EXPLAIN QUERY PLAN analysis
- Index usage monitoring

```sql
-- Composite index for cache lookups
CREATE INDEX idx_search_cache_lookup ON search_cache(query_hash, expires_at);

-- Check query plan
EXPLAIN QUERY PLAN
SELECT * FROM search_cache WHERE query_hash = ? AND expires_at > datetime('now');
```

#### 9. **Graph Database Concepts**
- Citation network as directed graph
- Node degree calculations (in-degree, out-degree)
- Graph traversal for citation chains
- Centrality metrics

```sql
-- Example: Citation network centrality
WITH out_degrees AS (
    SELECT source_paper_id, COUNT(*) as out_degree FROM citationlink GROUP BY source_paper_id
),
in_degrees AS (
    SELECT target_paper_id, COUNT(*) as in_degree FROM citationlink GROUP BY target_paper_id
)
SELECT sp.title, od.out_degree, id.in_degree
FROM savedpaper sp
LEFT JOIN out_degrees od ON sp.paper_id = od.source_paper_id
LEFT JOIN in_degrees id ON sp.paper_id = id.target_paper_id;
```

#### 10. **Normalized Database Design**
- 3rd Normal Form (3NF)
- M:N relationships via junction tables
- Foreign key constraints
- Referential integrity

**Example: Paper-Topic M:N Relationship**
```
research_topic (id, name, display_name) -- Normalized topic storage
paper_topic (paper_id, topic_id, relevance_score) -- Junction table
savedpaper (id, title, authors) -- Paper table
```

---

## 🗄️ Database Schema

### Tables (20+)

**Core Entities:**
- `user` - Users (students, mentors, researchers)
- `savedpaper` - User's saved research papers
- `collection` - User-created paper collections
- `citationlink` - Citation graph edges

**Research Features:**
- `researchchatsession` - AI chat sessions
- `researchchatmessage` - Chat messages with references
- `researchtimelineevent` - Research timeline tracking

**Mentor-Student:**
- `mentorstudentlink` - Mentor-student relationships (self-referencing FK)
- `studentactivity` - Activity logging
- `readinggroup` - Research reading groups
- `learningpath` - Learning curricula

**DBMS Showcase (NEW):**
- `search_cache` - Query result caching with TTL
- `search_history` - Search pattern analytics
- `paper_topic` - M:N junction table for paper-topics
- `research_topic` - Normalized topic storage
- `paper_reference` - Citation graph data
- `paper_similarity` - Precomputed similarity scores
- `query_performance_log` - Query performance tracking

### Indexes (20+)

```sql
-- Composite indexes
CREATE INDEX idx_search_cache_lookup ON search_cache(query_hash, expires_at);
CREATE INDEX idx_search_history_user_time ON search_history(user_id, created_at);

-- Foreign key indexes
CREATE INDEX idx_paper_topic_paper ON paper_topic(paper_id);
CREATE INDEX idx_paper_topic_topic ON paper_topic(topic_id);

-- Performance indexes
CREATE INDEX idx_savedpaper_user_saved ON savedpaper(user_id, saved_at);
CREATE INDEX idx_citationlink_source ON citationlink(source_paper_id);
```

---

## 🚀 Running SQL Demos

### 1. **Comprehensive SQL Query Showcase**
```bash
cd backend
python demo_sql_queries.py
```

**Demonstrates:**
- 10 categories of SQL queries
- 30+ complex queries
- Real data from production database
- Query plans and optimization

### 2. **DBMS Feature Demo (with Backend API)**
```bash
# Terminal 1: Start backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Run demo
python demo_dbms_showcase.py
```

**Demonstrates:**
- Search caching with TTL
- User behavior analytics
- Paper metadata enrichment
- Real-time API calls

### 3. **Original Demo Queries**
```bash
cd backend
python demo_queries.py
```

**Includes:**
- User activity analysis
- Collection statistics
- Citation network queries
- Mentor dashboard queries

---

## 📊 Sample Queries for Viva

### Q1: "Show me a complex JOIN query"
```sql
-- 6-table JOIN for mentor dashboard
SELECT 
    u.id, u.email, u.full_name,
    COUNT(DISTINCT sp.id) as papers_saved,
    COUNT(DISTINCT c.id) as collections_created,
    COUNT(DISTINCT cl.id) as citations_made,
    COUNT(DISTINCT rcs.id) as chat_sessions,
    MAX(sp.saved_at) as last_paper_activity
FROM user u
INNER JOIN mentorstudentlink msl ON u.id = msl.student_id
LEFT JOIN savedpaper sp ON u.id = sp.user_id
LEFT JOIN collection c ON u.id = c.user_id
LEFT JOIN citationlink cl ON u.id = cl.user_id
LEFT JOIN researchchatsession rcs ON u.id = rcs.user_id
WHERE msl.mentor_id = 1
GROUP BY u.id, u.email, u.full_name
ORDER BY papers_saved DESC;
```

### Q2: "Demonstrate a subquery"
```sql
-- Correlated subquery: Students with recent activity
SELECT 
    u.id, u.email,
    (SELECT COUNT(*) FROM savedpaper sp 
     WHERE sp.user_id = u.id 
     AND sp.saved_at > datetime('now', '-7 days')) as papers_last_week
FROM user u
WHERE EXISTS (
    SELECT 1 FROM savedpaper sp 
    WHERE sp.user_id = u.id 
    AND sp.saved_at > datetime('now', '-7 days')
);
```

### Q3: "Show window functions"
```sql
-- Ranking with window functions
SELECT 
    u.email,
    COUNT(sp.id) as paper_count,
    ROW_NUMBER() OVER (ORDER BY COUNT(sp.id) DESC) as rank,
    ROUND(COUNT(sp.id) * 100.0 / SUM(COUNT(sp.id)) OVER (), 2) as pct_of_total
FROM user u
LEFT JOIN savedpaper sp ON u.id = sp.user_id
GROUP BY u.id, u.email;
```

### Q4: "Explain your indexing strategy"
```sql
-- Show all indexes
SELECT name, tbl_name, sql
FROM sqlite_master
WHERE type = 'index' AND tbl_name = 'search_cache';

-- Composite index for cache lookups
CREATE INDEX idx_search_cache_lookup ON search_cache(query_hash, expires_at);
-- Why? Enables fast lookup by query AND expiration check in single index scan
```

### Q5: "Show a CTE query"
```sql
WITH user_stats AS (
    SELECT 
        user_id,
        COUNT(*) as paper_count,
        MAX(saved_at) as last_activity
    FROM savedpaper
    GROUP BY user_id
)
SELECT 
    u.email,
    us.paper_count,
    us.last_activity,
    CASE 
        WHEN us.last_activity > datetime('now', '-7 days') THEN 'Active'
        ELSE 'Inactive'
    END as status
FROM user u
LEFT JOIN user_stats us ON u.id = us.user_id;
```

---

## 🎯 Key Talking Points for DBMS Viva

1. **"Why did you use raw SQL instead of ORM?"**
   - To demonstrate actual DBMS concepts
   - Better performance for complex queries
   - Shows understanding of query optimization
   - Easier to explain JOIN strategies and indexes

2. **"Explain your normalization"**
   - Research topics stored once (3NF)
   - M:N relationships via junction tables
   - No redundant data storage
   - Example: `paper_topic` junction table

3. **"How do you optimize queries?"**
   - Composite indexes for multi-column lookups
   - EXPLAIN QUERY PLAN analysis
   - Caching frequently accessed data
   - Denormalization where needed (paper_count)

4. **"Show me transaction usage"**
   - Paper metadata enrichment uses transactions
   - Multiple INSERTs must succeed together
   - ROLLBACK on error ensures consistency

5. **"What's your largest JOIN?"**
   - Mentor dashboard: 6 tables
   - Shows LEFT JOINs for optional data
   - Uses GROUP BY for aggregation
   - Demonstrates real-world complexity

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── models.py              # 20+ SQLModel tables
│   ├── models_enhanced.py     # DBMS showcase tables
│   ├── api/
│   │   ├── search.py          # With SQL caching
│   │   ├── mentor.py          # Complex JOINs (NEW)
│   │   ├── papers.py
│   │   ├── collections.py
│   │   ├── citations.py
│   │   └── chat.py
│   ├── services/
│   │   ├── search_cache.py    # Raw SQL caching
│   │   └── paper_enrichment.py # Raw SQL enrichment
│   └── core/
│       └── firebase_auth.py
├── demo_queries.py            # Original demos
├── demo_sql_queries.py        # NEW: 30+ SQL queries
├── demo_dbms_showcase.py      # NEW: API-based demo
├── schema.sql                 # Complete DDL
└── app.db                     # SQLite database

citemesh-ui/                   # React frontend
```

---

## 🎓 DBMS Concepts Coverage

| Concept | Implementation | Demo File |
|---------|---------------|-----------|
| Complex JOINs | Mentor dashboard (6 tables) | `demo_sql_queries.py` |
| Subqueries | Cache statistics, user analytics | `demo_sql_queries.py` |
| CTEs | User stats, citation chains | `demo_sql_queries.py` |
| Window Functions | Rankings, running totals | `demo_sql_queries.py` |
| Aggregations | GROUP BY, HAVING, COUNT, AVG | All demos |
| Set Operations | UNION of activities | `demo_sql_queries.py` |
| Transactions | Paper enrichment | `paper_enrichment.py` |
| Indexes | 20+ indexes, composite | `schema.sql` |
| Normalization | 3NF, junction tables | `models_enhanced.py` |
| Graph Queries | Citation network | `demo_sql_queries.py` |

---

## 🔥 Quick Commands

```bash
# Run SQL demo (no backend needed)
python backend/demo_sql_queries.py

# View database schema
sqlite3 backend/app.db ".schema"

# Count records
sqlite3 backend/app.db "SELECT COUNT(*) FROM savedpaper;"

# Show indexes
sqlite3 backend/app.db "SELECT name, tbl_name FROM sqlite_master WHERE type='index';"

# EXPLAIN query plan
sqlite3 backend/app.db "EXPLAIN QUERY PLAN SELECT * FROM search_cache WHERE query_hash='abc';"
```

---

## ✅ Checklist for DBMS Viva

- [x] Complex multi-table JOINs (6+ tables)
- [x] Subqueries (correlated and non-correlated)
- [x] Common Table Expressions (CTEs)
- [x] Window functions (ROW_NUMBER, RANK, etc.)
- [x] Advanced aggregations (GROUP BY, HAVING)
- [x] Set operations (UNION, INTERSECT)
- [x] Transaction management (BEGIN/COMMIT/ROLLBACK)
- [x] Index optimization (composite indexes)
- [x] Query performance analysis (EXPLAIN QUERY PLAN)
- [x] Graph database concepts (citation network)
- [x] Normalized design (3NF, junction tables)
- [x] Raw SQL queries (not just ORM)

---

**Ready for DBMS viva! 🎓** Run `python backend/demo_sql_queries.py` to see all concepts in action.
