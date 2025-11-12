# CiteMesh - DBMS Project Presentation Guide

## 🎯 Quick Overview for Teacher Demo

### What is CiteMesh?
A **research paper management platform** with AI-powered features for students and researchers. Think of it as "Spotify for Research Papers" with citation networks, AI chat, and collaboration tools.

---

## 📚 DBMS Concepts Implemented

### ✅ 1. **Entity-Relationship (ER) Modeling**
**Location**: `DATABASE_DESIGN.md` (Lines 50-100)

**Key Entities**:
- `User` (students, mentors, researchers)
- `SavedPaper` (research papers)
- `Collection` (organized paper groups)
- `CitationLink` (paper citations - graph structure)
- `ResearchChatSession` (AI conversations)

**Relationships**:
- User → SavedPaper (1:N) - "A user saves many papers"
- User → Collection (1:N) - "A user creates many collections"
- Collection → CollectionPaper (1:N) - "A collection contains many papers"
- MentorStudentLink (M:N) - "Mentors guide many students, students can have many mentors"
- ResearchChatSession → ResearchChatMessage (1:N) - "A session has many messages"

---

### ✅ 2. **Relational Schema Design**
**Location**: `backend/schema.sql`

**Total Tables**: 20+ tables with proper DDL

**Key Features**:
```sql
-- Primary Keys (AUTO_INCREMENT)
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ...
);

-- Foreign Keys with CASCADE
FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE

-- Unique Constraints
UNIQUE (user_id, paper_id)

-- Check Constraints
CHECK (role IN ('student', 'mentor', 'researcher', 'admin'))
```

**Show Teacher**: Open `backend/schema.sql` and scroll through the complete DDL

---

### ✅ 3. **Normalization**
**Location**: `DATABASE_DESIGN.md` (Section 4)

**Proof of 3NF**:
1. **1NF** ✓ - All attributes atomic (no multi-valued attributes)
2. **2NF** ✓ - No partial dependencies (all non-key attributes depend on full primary key)
3. **3NF** ✓ - No transitive dependencies (no non-key → non-key dependencies)

**Example**:
```
❌ Bad (Denormalized):
user_id | email | paper1_title | paper1_author | paper2_title | paper2_author

✅ Good (3NF):
user (user_id, email)
savedpaper (id, user_id, paper_id, title, authors)
```

---

### ✅ 4. **Complex SQL Queries**
**Location**: `backend/demo_queries.py`

**Run Live Demo**:
```bash
cd backend
python demo_queries.py
```

**Query Types Demonstrated**:

#### A. **Multi-Table JOIN** (Query 1)
```sql
SELECT u.full_name, COUNT(DISTINCT sp.id) as papers, COUNT(DISTINCT c.id) as collections
FROM user u
LEFT JOIN savedpaper sp ON u.id = sp.user_id
LEFT JOIN collection c ON u.id = c.user_id
GROUP BY u.id
```

#### B. **Recursive CTE** (Query 2)
```sql
WITH RECURSIVE citation_chain AS (
    SELECT paper_id, 0 as depth
    UNION ALL
    SELECT cl.target_paper_id, cc.depth + 1
    FROM citation_chain cc
    JOIN citationlink cl ON cc.paper_id = cl.source_paper_id
)
SELECT * FROM citation_chain
```

#### C. **Window Functions** (Query 3)
```sql
SELECT 
    collection_id,
    paper_count,
    RANK() OVER (ORDER BY paper_count DESC) as rank
FROM collection
```

#### D. **Subqueries** (Query 3)
```sql
SELECT c.name, (
    SELECT COUNT(*) 
    FROM citationlink cl 
    WHERE cl.source_paper_id IN (SELECT paper_id FROM collectionpaper WHERE collection_id = c.id)
) as citations
FROM collection c
```

#### E. **Aggregation** (Query 4)
```sql
SELECT 
    published_year,
    COUNT(*) as paper_count,
    AVG(LENGTH(summary)) as avg_summary_length
FROM savedpaper
GROUP BY published_year
HAVING COUNT(*) > 5
```

---

### ✅ 5. **Indexing Strategy**
**Location**: `backend/schema.sql` (After each table definition)

**Indexes Created**:
```sql
-- Foreign key indexes (improve JOIN performance)
CREATE INDEX idx_savedpaper_user_id ON savedpaper(user_id);
CREATE INDEX idx_collection_user_id ON collection(user_id);

-- Search indexes
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_savedpaper_paper_id ON savedpaper(paper_id);

-- Time-based indexes
CREATE INDEX idx_savedpaper_saved_at ON savedpaper(saved_at);

-- Composite indexes (graph queries)
CREATE INDEX idx_citationlink_bidirectional ON citationlink(source_paper_id, target_paper_id);
```

**Performance Impact**:
- WITHOUT index: O(n) table scan
- WITH index: O(log n) B-tree lookup

---

### ✅ 6. **Transaction Management**
**Location**: `backend/demo_queries.py` (Query 9)

**ACID Properties Demonstration**:
```python
def create_collection_with_papers(user_id, collection_data, paper_ids):
    conn.execute("BEGIN TRANSACTION")
    try:
        # Step 1: Create collection
        cursor = conn.execute("INSERT INTO collection ...")
        collection_id = cursor.lastrowid
        
        # Step 2: Add papers
        for paper_id in paper_ids:
            conn.execute("INSERT INTO collectionpaper ...")
        
        # Step 3: Update count
        conn.execute("UPDATE collection SET paper_count = ?", (len(paper_ids),))
        
        conn.commit()  # All or nothing!
    except:
        conn.rollback()  # Undo all changes
```

---

### ✅ 7. **Graph Database Concepts**
**Location**: `backend/app/models.py` (CitationLink), `demo_queries.py` (Query 5)

**Citation Network as Graph**:
- **Nodes**: Research papers (vertices)
- **Edges**: Citations (directed edges)
- **Properties**: Weight, note, timestamp

**Graph Queries**:
```sql
-- Find papers with highest citation count (in-degree)
SELECT target_paper_id, COUNT(*) as in_degree
FROM citationlink
GROUP BY target_paper_id
ORDER BY in_degree DESC

-- Find citation chains (recursive traversal)
WITH RECURSIVE chains AS (...)
```

---

## 🖥️ Live Database Access

### Method 1: SQLite CLI
```bash
cd backend
sqlite3 database.db

# Show all tables
.tables

# Describe table structure
.schema user

# Run query
SELECT * FROM user LIMIT 5;
```

### Method 2: DB Browser for SQLite
1. Download: https://sqlitebrowser.org/
2. Open: `backend/database.db`
3. Browse tables, run queries, view relationships

### Method 3: API Endpoints
**Live Backend**: https://paperverse-kvw2y.ondigitalocean.app/

```bash
# Health check
curl https://paperverse-kvw2y.ondigitalocean.app/health

# Database stats
curl https://paperverse-kvw2y.ondigitalocean.app/api/papers/stats
curl https://paperverse-kvw2y.ondigitalocean.app/api/collections/stats
curl https://paperverse-kvw2y.ondigitalocean.app/api/citations/stats
```

---

## 📊 Demo Script for Teacher

### **5-Minute Presentation**

#### **Slide 1: Overview** (30 seconds)
"CiteMesh is a research paper management platform with a robust relational database backend. We've implemented all major DBMS concepts including ER modeling, normalization, complex queries, and transactions."

#### **Slide 2: ER Diagram** (1 minute)
Open `DATABASE_DESIGN.md` and show the ER diagram (Section 2)
- Point out entities: User, SavedPaper, Collection, CitationLink
- Explain relationships: 1:N, M:N, 1:1
- Highlight foreign keys

#### **Slide 3: Schema** (1 minute)
Open `backend/schema.sql`
- Scroll through table definitions
- Point out: Primary keys, Foreign keys with CASCADE, Indexes, Check constraints
- Show total: 20+ tables

#### **Slide 4: Normalization** (1 minute)
Open `DATABASE_DESIGN.md` (Section 4)
- Explain 1NF, 2NF, 3NF achieved
- Give example of denormalized vs normalized design
- Show no redundant data

#### **Slide 5: Complex Queries** (1.5 minutes)
Run `python backend/demo_queries.py`
- Show multi-table JOINs (Query 1)
- Show recursive CTE for citation chains (Query 2)
- Show window functions and ranking (Query 3)
- Show transaction demonstration (Query 9)

#### **Slide 6: Live Database** (30 seconds)
Open SQLite CLI or DB Browser
```bash
sqlite3 backend/database.db
SELECT * FROM user;
SELECT * FROM savedpaper LIMIT 10;
```

---

## 📋 Checklist for Teacher

### Core DBMS Concepts ✅
- [x] ER Modeling (20+ entities)
- [x] Relational Schema (DDL for all tables)
- [x] Primary Keys (AUTO_INCREMENT)
- [x] Foreign Keys (with CASCADE)
- [x] Unique Constraints
- [x] Check Constraints
- [x] Normalization (1NF, 2NF, 3NF)
- [x] Indexing (20+ indexes)

### Advanced Features ✅
- [x] Multi-table JOINs (3-5 tables)
- [x] Subqueries (correlated & nested)
- [x] Aggregation (COUNT, AVG, SUM, MIN, MAX)
- [x] Window Functions (RANK, SUM OVER, AVG OVER)
- [x] Recursive CTEs (citation chains)
- [x] Transaction Management (BEGIN, COMMIT, ROLLBACK)
- [x] Graph Queries (citation networks)
- [x] Time-series Analysis (trends, moving averages)

### Implementation ✅
- [x] Working database (SQLite)
- [x] ORM integration (SQLModel/SQLAlchemy)
- [x] RESTful APIs (30+ endpoints)
- [x] Frontend integration (React app)
- [x] Deployed application (DigitalOcean + Firebase)

---

## 🎓 Key Points to Emphasize

### 1. **Real-World Application**
"This isn't just a toy database - it's a production-ready system with 20+ tables, proper relationships, and deployed to the cloud."

### 2. **Complex Queries**
"We've implemented 10+ complex queries including recursive CTEs for citation chains, window functions for ranking, and multi-table JOINs across 5+ tables."

### 3. **Normalization**
"The database is fully normalized to 3NF, eliminating redundancy while maintaining data integrity through foreign key constraints."

### 4. **Graph Structure**
"The citation network is essentially a graph database within a relational model, demonstrating how to represent complex relationships."

### 5. **Performance**
"We've optimized queries with 20+ strategic indexes, reducing lookup times from O(n) to O(log n) for frequent operations."

---

## 📁 Files to Show Teacher

### Primary Documents:
1. **DATABASE_DESIGN.md** - Complete documentation (3,500+ lines)
2. **backend/schema.sql** - Production DDL (all tables)
3. **backend/demo_queries.py** - 10 query demonstrations

### Supporting Files:
4. **backend/app/models.py** - SQLModel ORM definitions
5. **API_DOCUMENTATION.md** - API endpoints using database
6. **DEPLOYMENT_STATUS.md** - Live deployment info

---

## 🚀 Quick Commands

### Initialize Database:
```bash
cd backend
python -m app.database
```

### Run Query Demos:
```bash
python demo_queries.py
```

### Start Backend:
```bash
uvicorn app.main:app --reload
```

### Access Database:
```bash
sqlite3 database.db
```

---

## 💡 Bonus Points

### Integration with APIs:
"The database isn't isolated - it powers 30+ RESTful API endpoints that are consumed by a React frontend and deployed to production."

### External Integration:
"We integrate with OpenAlex (269M research papers) and AI models (Gemini, A4F) while maintaining our own structured database for user data."

### Scalability:
"Currently using SQLite for development, but the ORM abstraction (SQLModel) allows seamless migration to PostgreSQL for production scale."

---

## 📞 Questions Teacher Might Ask

**Q: Where are the foreign keys?**
A: Open `backend/schema.sql` - every table with relationships has `FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE`

**Q: How did you normalize the database?**
A: See `DATABASE_DESIGN.md` Section 4 - we eliminated repeating groups (1NF), partial dependencies (2NF), and transitive dependencies (3NF)

**Q: Show me a complex query.**
A: Run `python backend/demo_queries.py` - Query 2 demonstrates recursive CTEs for citation chains, Query 7 shows 5-table JOINs

**Q: What about transactions?**
A: See `demo_queries.py` Query 9 - demonstrates ACID properties with BEGIN/COMMIT/ROLLBACK

**Q: Where's the indexing?**
A: `backend/schema.sql` - 20+ CREATE INDEX statements after table definitions

**Q: Is this actually being used?**
A: Yes! Live at https://paperverse-kvw2y.ondigitalocean.app/ - hit the API endpoints to see real data

---

## ✅ Final Checklist Before Presentation

- [ ] Open `DATABASE_DESIGN.md` in preview mode
- [ ] Have `backend/schema.sql` ready to scroll
- [ ] Terminal ready to run `python demo_queries.py`
- [ ] SQLite CLI or DB Browser installed and tested
- [ ] Backend running locally (optional backup if APIs fail)
- [ ] Browser tabs: Live frontend, API docs, GitHub repo

---

**Good luck with your presentation! 🎉**

This is a comprehensive DBMS project demonstrating mastery of database concepts from theory (ER modeling, normalization) to practice (complex queries, transactions, deployment).
