# CiteMesh DBMS Project - Team Contributions Guide

## 📋 Project Overview

**Project Name:** CiteMesh - Research Paper Management & Citation Network Platform  
**Course:** Database Management Systems (DBMS)  
**Team Size:** 4 Members  
**Timeline:** 2024-2025  
**Status:** ✅ **COMPLETE & DEPLOYED**

**Live Deployments:**
- 🌐 Frontend: https://citemesh.web.app/ (Firebase Hosting)
- 🔧 Backend API: https://paperverse-kvw2y.ondigitalocean.app/ (DigitalOcean)
- 📚 API Documentation: https://paperverse-kvw2y.ondigitalocean.app/docs

---

## 👥 Team Members & Role Distribution

### 1. **Hemal Badola** - Backend Architecture & AI Integration Lead
### 2. **Naincy** - Integration, QA & Demo Coordination Lead
### 3. **Maaz** - Database Design & ER Modeling Lead
### 4. **Ayush** - Schema Design & Normalization Lead

---

## 🏗️ Project Architecture Overview

```
CiteMesh/
├── backend/                    # Main FastAPI Backend (Production)
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── models.py          # 20+ SQLModel database models
│   │   ├── db.py              # Database connection & session management
│   │   ├── api/               # REST API endpoints (8 routers)
│   │   ├── core/              # Firebase auth, API key rotation
│   │   └── services/          # Business logic (PDF processing, etc.)
│   ├── schema.sql             # Complete DDL with indexes
│   └── demo_queries.py        # 10 complex query demonstrations
│
├── citemesh-ui/               # React + TypeScript Frontend
│   ├── src/
│   │   ├── pages/            # 8 main routes (Dashboard, Library, Search, etc.)
│   │   ├── components/       # Reusable UI components
│   │   ├── services/         # API client (api.ts)
│   │   └── contexts/         # Auth state management
│   └── public/
│
├── hemal/                     # Hemal's Backend Experiments & AI Services
│   ├── backend/              # Standalone AI search backend
│   ├── demo-queries/         # SQL query examples
│   ├── optimization/         # Performance tuning notes
│   └── queries/              # Saved query templates
│
├── naincy/                    # Naincy's Integration & QA Assets
│   ├── integration/          # Integration test scripts
│   ├── qa/                   # QA plans and validation reports
│   ├── demo/                 # Demo preparation materials
│   └── management/           # Project coordination docs
│
├── maaz/                      # Maaz's Database Design Work
│   ├── erd/                  # ER diagram source files
│   ├── entities/             # Entity definitions & attributes
│   ├── relationships/        # Relationship matrices & cardinality
│   └── sample-data/          # Sample data planning
│
├── ayush/                     # Ayush's Schema & Normalization Work
│   ├── ddl/                  # PostgreSQL DDL scripts
│   ├── normalization/        # 1NF, 2NF, 3NF proofs
│   ├── data-dictionary/      # Column semantics & datatypes
│   └── testing/              # Schema integrity tests
│
└── docs/                      # Shared documentation
    └── viva_presentation_brief.md

```

---

## 🎯 Component Breakdown & Ownership

### **A. Backend (Production API)** - Shared Ownership

#### Core Components:
1. **FastAPI Application** (`backend/app/main.py`)
   - CORS configuration
   - Router registration
   - Database initialization
   - Health check endpoint

2. **Database Models** (`backend/app/models.py`)
   - 20+ SQLModel classes
   - User, SavedPaper, Collection, CitationLink, etc.
   - ORM relationships and constraints

3. **Database Layer** (`backend/app/db.py`)
   - SQLite/PostgreSQL connection
   - Session management
   - Engine configuration

4. **API Routers** (`backend/app/api/`)
   - `users.py` - User management
   - `papers.py` - Paper CRUD operations
   - `collections.py` - Collection management
   - `citations.py` - Citation network operations
   - `search.py` - OpenAlex search integration
   - `chat.py` - AI chat assistant
   - `pdf.py` - PDF proxy endpoint
   - `activity.py` - Activity logging

5. **Core Services** (`backend/app/core/`)
   - `firebase_auth.py` - Firebase authentication middleware
   - `api_key_rotator.py` - Gemini API key rotation (15 keys)

6. **Business Logic** (`backend/app/services/`)
   - PDF processing utilities
   - Paper metadata extraction

---

### **B. Frontend (React UI)** - Shared Ownership

#### Pages (`citemesh-ui/src/pages/`):
1. **Dashboard.tsx** - Main overview with statistics
2. **Library.tsx** - Saved papers grid/list view
3. **Search.tsx** - OpenAlex search interface (PaperVerseConsole)
4. **Chat.tsx** - AI research assistant
5. **Network.tsx** - Citation network visualization
6. **Login.tsx** - Firebase passwordless authentication
7. **PaperDetail.tsx** - Individual paper view
8. **ScholarSearch.tsx** - Advanced search filters

#### Components (`citemesh-ui/src/components/`):
- SearchBar, Sidebar, PaperCard, CollectionCard, etc.
- PaperVerseConsole - Main search interface with AI query translation

#### Services (`citemesh-ui/src/services/`):
- **api.ts** - Complete API client for backend (30+ methods)
  - Papers, Collections, Citations, Search, Chat APIs
  - Authentication token management

#### Configuration:
- Firebase client setup (`firebase.ts`)
- Auth context provider (`contexts/AuthContext.tsx`)
- Vite build configuration

---

## 📊 Individual Contributions

### 🔵 **1. Hemal Badola** - Backend Architecture & AI Integration

#### Primary Responsibilities:
- Backend architecture design and implementation
- AI/ML integration (Gemini, OpenAlex)
- API development and optimization
- Search system design

#### Major Contributions:

**A. AI-Powered Search System** (`hemal/backend/`)
```
hemal/backend/
├── main.py                 # Standalone FastAPI search service
├── search_service.py       # OpenAlex API client with caching
├── gemini_translator.py    # AI query enhancement
├── pdf_proxy.py           # Open access PDF retrieval
└── cache/                 # Response caching layer
```

**Key Features Implemented:**
- 🤖 **Gemini AI Query Translation**: Converts natural language to academic search queries
- 🔍 **OpenAlex Integration**: 269M+ research papers via Walden API (data-version=2)
- 📄 **PDF Proxy System**: CORS-safe PDF streaming from arxiv.org, europepmc.org, etc.
- 🔄 **API Key Rotation**: 15 Gemini keys with automatic rotation
- 💾 **Response Caching**: Redis-style caching for query optimization
- 🎯 **Smart Query Enhancement**: Adds academic terminology and synonyms

**B. Backend API Endpoints** (`backend/app/api/`)
- `search.py` - OpenAlex search with AI enhancement
  - `/api/search/search` - POST endpoint with filters
  - `/api/search/save-paper` - Save from search results
  - `/api/search/check-saved/{paper_id}` - Check if paper saved
  - `/api/search/suggest` - Query suggestions
  - `/api/search/stats` - Database statistics

- `pdf.py` - PDF proxy endpoint
  - `/api/pdf?url=` - Proxy Open Access PDFs
  - Domain whitelisting for security
  - Streaming response with httpx

- `chat.py` - AI research assistant
  - `/api/chat/sessions` - Create/list chat sessions
  - `/api/chat/sessions/{id}/messages` - Send/receive messages
  - Context-aware responses using paper library

**C. Core Infrastructure**
- `api_key_rotator.py` - Intelligent key management
  - 15 Gemini API keys
  - Automatic rotation on rate limits
  - Key health monitoring

**D. Database Optimization Work** (`hemal/optimization/`)
- Index strategy documentation
- Query performance analysis
- Caching layer design

**E. Demo Queries** (`hemal/demo-queries/`)
- Complex SQL query examples
- Performance benchmarks
- Use case demonstrations

**Technologies Used:**
- FastAPI, SQLModel, Firebase Admin SDK
- httpx (async HTTP), requests
- Gemini Pro API, OpenAlex Walden API
- SQLite, PostgreSQL

**Files Owned/Modified:**
- `backend/app/api/search.py` (~500 lines)
- `backend/app/api/pdf.py` (~150 lines)
- `backend/app/api/chat.py` (~400 lines)
- `backend/app/core/api_key_rotator.py` (~200 lines)
- `hemal/backend/` (entire folder, ~1000+ lines)

---

### 🟢 **2. Naincy** - Integration, QA & Demo Coordination

#### Primary Responsibilities:
- System integration testing
- Quality assurance and validation
- Demo preparation and coordination
- Project management and documentation

#### Major Contributions:

**A. Integration Testing** (`naincy/integration/`)
```
naincy/integration/
├── api_integration_tests.py       # Backend API endpoint tests
├── frontend_backend_tests.py      # Full-stack integration tests
├── auth_flow_tests.py             # Firebase auth validation
├── search_flow_tests.py           # Search → Save → Library flow
└── test_reports/                  # Test execution reports
```

**Test Coverage:**
- ✅ User authentication flow (Firebase → Backend)
- ✅ Paper CRUD operations
- ✅ Collection management
- ✅ Citation network creation
- ✅ Search integration (OpenAlex → Backend → Frontend)
- ✅ PDF proxy functionality
- ✅ Chat assistant responses
- ✅ Cross-browser compatibility
- ✅ Mobile responsiveness

**B. QA Documentation** (`naincy/qa/`)
```
naincy/qa/
├── test_plan.md                   # Comprehensive test strategy
├── test_cases.xlsx                # 100+ test cases with status
├── bug_reports/                   # Issue tracking and resolution
├── validation_checklist.md        # Feature validation checklist
└── regression_tests.md            # Regression test suite
```

**Quality Metrics Tracked:**
- API response times (< 500ms target)
- Database query performance
- Frontend load times
- Error rates and handling
- User experience flows

**C. Demo Preparation** (`naincy/demo/`)
```
naincy/demo/
├── viva_presentation.pptx         # PowerPoint slides
├── demo_script.md                 # Step-by-step demo walkthrough
├── sample_queries.txt             # Example search queries
├── feature_showcase.md            # Feature highlights
└── screenshots/                   # UI screenshots for documentation
```

**Demo Materials Created:**
- 🎬 **Live Demo Script**: 5-minute presentation flow
- 📊 **Feature Showcase**: Key functionality highlights
- 🖼️ **Visual Assets**: Screenshots and diagrams
- 📝 **FAQ Document**: Anticipated teacher questions
- 🎯 **Quick Reference**: Cheat sheet for demo day

**D. Project Coordination** (`naincy/management/`)
```
naincy/management/
├── sprint_planning.md             # Sprint breakdown and timeline
├── task_tracking.xlsx             # Task assignments and status
├── meeting_notes/                 # Weekly sync meeting notes
├── deployment_checklist.md        # Pre-deployment validation
└── documentation_index.md         # All docs cross-reference
```

**Coordination Activities:**
- Weekly team syncs and status updates
- Task assignment and progress tracking
- Documentation organization
- Deployment coordination
- Teacher presentation preparation

**E. Documentation Contributions**
- `INTEGRATION_TEST_REPORT.md` - Complete test results
- `INTEGRATION_COMPLETE.md` - Integration status
- `FINAL_DELIVERABLES.md` - Submission checklist
- `TEACHER_DEMO_GUIDE.md` - Presentation guide
- `docs/viva_presentation_brief.md` - Viva prep

**Tools Used:**
- pytest (Python testing)
- Postman (API testing)
- Selenium (Frontend automation)
- Excel/Google Sheets (Test tracking)
- PowerPoint (Presentations)

**Files Owned/Modified:**
- `naincy/` (entire folder)
- `INTEGRATION_TEST_REPORT.md`
- `TEACHER_DEMO_GUIDE.md`
- `docs/viva_presentation_brief.md`

---

### 🟣 **3. Maaz** - Database Design & ER Modeling

#### Primary Responsibilities:
- Entity-Relationship (ER) diagram design
- Entity definitions and attribute specifications
- Relationship mapping and cardinality
- Database conceptual design

#### Major Contributions:

**A. ER Diagram Design** (`maaz/erd/`)
```
maaz/erd/
├── citemesh_er_diagram.drawio     # Main ER diagram source
├── citemesh_er_diagram.png        # Exported PNG
├── citemesh_er_diagram_v1.pdf     # Version 1 (archived)
├── citemesh_er_diagram_v2.pdf     # Version 2 (current)
└── entity_notation_guide.md       # Diagram notation reference
```

**ER Diagram Features:**
- **20+ Entities**: User, Paper, Collection, Citation, Chat, Profile, etc.
- **Cardinality Specifications**: 1:1, 1:N, M:N relationships
- **Attribute Details**: Primary keys, foreign keys, data types
- **Relationship Types**: Identifying vs non-identifying relationships
- **Inheritance Hierarchies**: User roles (Student, Mentor, Researcher)

**Key Relationships Designed:**
1. **User ↔ SavedPaper** (1:N)
   - One user can save many papers
   - Each saved paper belongs to one user

2. **Collection ↔ SavedPaper** (M:N via CollectionPaper)
   - Many papers can be in many collections
   - Junction table with order_index and note

3. **User ↔ User** (M:N via MentorStudentLink)
   - Mentors can guide multiple students
   - Students can have multiple mentors

4. **SavedPaper ↔ SavedPaper** (M:N via CitationLink)
   - Papers cite other papers (directed graph)
   - Self-referencing relationship with weight

5. **User ↔ ResearchChatSession** (1:N)
   - One user can have many chat sessions
   - Each session belongs to one user

6. **ResearchChatSession ↔ ResearchChatMessage** (1:N)
   - One session contains many messages
   - Messages belong to one session

**B. Entity Specifications** (`maaz/entities/`)
```
maaz/entities/
├── user_entity.md                 # User attributes & constraints
├── savedpaper_entity.md           # Paper entity details
├── collection_entity.md           # Collection specifications
├── citationlink_entity.md         # Citation graph design
├── profile_entity.md              # User profile (1:1)
└── all_entities_summary.md        # Complete entity catalog
```

**Entity Documentation Includes:**
- Attribute names and data types
- Constraint specifications (NOT NULL, UNIQUE, CHECK)
- Business rules and validation logic
- Functional dependencies
- Sample data examples

**C. Relationship Matrices** (`maaz/relationships/`)
```
maaz/relationships/
├── relationship_matrix.xlsx       # All relationships in table form
├── cardinality_notes.md          # Cardinality justifications
├── participation_constraints.md   # Total vs partial participation
└── referential_integrity.md       # CASCADE, SET NULL, etc.
```

**Relationship Documentation:**
| Relationship | Entities | Cardinality | Participation | Notes |
|--------------|----------|-------------|---------------|-------|
| Saves | User - SavedPaper | 1:N | Partial - Total | User can save 0+ papers |
| Contains | Collection - Paper | M:N | Partial - Partial | Via CollectionPaper |
| Cites | Paper - Paper | M:N | Partial - Partial | Via CitationLink |
| Guides | Mentor - Student | M:N | Partial - Partial | Via MentorStudentLink |
| Owns | User - Collection | 1:N | Partial - Total | User can create 0+ collections |

**D. Sample Data Planning** (`maaz/sample-data/`)
```
maaz/sample-data/
├── sample_users.csv               # 50 sample users
├── sample_papers.csv              # 100 sample papers
├── sample_collections.csv         # 30 sample collections
├── sample_citations.csv           # 200 citation links
└── data_generation_script.py      # Script to generate test data
```

**E. Design Rationale Documents**
- Entity choice justifications
- Attribute granularity decisions
- Relationship type selections
- Normalization strategy
- Extensibility considerations

**F. Major Contributions to Shared Docs:**
- `DATABASE_DESIGN.md` (Section 2: ER Diagram)
- `ER_DIAGRAM_VISUAL.txt` (ASCII art version)
- Visual diagrams in `PROJECT_SUMMARY.md`

**G. Production Database Deployment** (`maaz/deployment/`)
```
maaz/deployment/
├── digitalocean_setup.md          # DigitalOcean database configuration
├── postgresql_migration.md        # SQLite to PostgreSQL migration guide
├── database_backup_strategy.md    # Backup and recovery procedures
├── connection_pooling_config.md   # Connection pool optimization
└── monitoring_setup.md            # Database performance monitoring
```

**Deployment Contributions:**
- **DigitalOcean Managed PostgreSQL Setup**
  - Configured managed PostgreSQL database cluster
  - Set up connection strings and environment variables
  - SSL/TLS certificate configuration for secure connections
  - Firewall rules and trusted sources configuration

- **Database Migration Strategy**
  - SQLite to PostgreSQL migration planning
  - Data type compatibility mapping (INTEGER → SERIAL, etc.)
  - Foreign key constraint verification
  - Index recreation and optimization

- **Backup & Recovery**
  - Daily automated backups configuration
  - Point-in-time recovery (PITR) setup
  - Backup retention policies (7 days rolling)
  - Disaster recovery documentation

**H. Database Performance Monitoring**
```
maaz/monitoring/
├── query_performance_metrics.md   # Query execution time tracking
├── slow_query_analysis.md         # Identifying bottlenecks
├── connection_pool_stats.md       # Connection usage patterns
└── database_health_dashboard.md   # Monitoring dashboard design
```

**Monitoring Tools Configured:**
- DigitalOcean Database Insights
- Query performance tracking
- Connection pool monitoring
- Disk usage alerts
- CPU/Memory utilization tracking

**Performance Metrics Established:**
- Query execution time targets (< 100ms for simple, < 500ms for complex)
- Connection pool size optimization (min: 5, max: 20)
- Index hit ratio targets (> 95%)
- Cache hit ratio monitoring

**I. Database Security Implementation**
- **Access Control**: Role-based database users (read-only, read-write, admin)
- **Connection Security**: SSL-only connections enforced
- **IP Whitelisting**: Restricted access to backend servers only
- **Credential Management**: Environment variable-based secrets
- **Audit Logging**: Database query logging for security analysis

**J. Database Scaling Strategy**
```
maaz/scaling/
├── vertical_scaling_plan.md       # CPU/RAM upgrade paths
├── horizontal_scaling_design.md   # Read replicas configuration
├── sharding_strategy.md           # Future sharding approach for papers
└── connection_pooling.md          # Pool size optimization
```

**Scaling Considerations Documented:**
- Vertical scaling: CPU/RAM upgrade thresholds
- Read replicas for search-heavy workloads
- Connection pooling to handle 100+ concurrent users
- Query optimization for large datasets (1M+ papers)
- Partitioning strategy for citation_link table (future)

**K. Data Integrity & Constraints**
- **Referential Integrity**: All foreign keys with CASCADE rules
- **Check Constraints**: Email validation, role validation, year ranges
- **Unique Constraints**: Prevent duplicate users, papers, citations
- **Not Null Constraints**: Critical fields always populated
- **Default Values**: Timestamps, boolean flags, role defaults

**L. Technical Documentation Contributions**
- Database architecture diagrams
- Connection flow diagrams (Frontend → API → Database)
- Data flow diagrams for search pipeline
- Security architecture documentation
- Deployment runbooks for database operations

**Technical Achievements:**
- ✅ Designed citation network as directed graph (source → target)
- ✅ Implemented M:N relationships with junction tables
- ✅ Self-referencing relationships (User ↔ User via MentorStudentLink)
- ✅ Cascade delete rules for data consistency
- ✅ Composite keys for junction tables
- ✅ Timestamp tracking (created_at, updated_at) across all tables
- ✅ Database normalization verification (no redundancy)
- ✅ Index coverage for all foreign keys
- ✅ Production-ready deployment configuration

**Tools Used:**
- draw.io (ER diagram creation)
- Microsoft Visio
- Lucidchart
- Excel (Relationship matrices)
- DigitalOcean (Database hosting)
- PostgreSQL (Production database)
- pgAdmin (Database management)
- DBeaver (Query development)

**Files Owned/Modified:**
- `maaz/` (entire folder)
- `DATABASE_DESIGN.md` (Section 2)
- `ER_DIAGRAM_VISUAL.txt`
- `DEPLOYMENT_STATUS.md` (Database section)
- `DIGITALOCEAN_FIX.md` (Database configuration)

---

### 🟡 **4. Ayush** - Schema Design & Normalization

#### Primary Responsibilities:
- Relational schema design
- Normalization (1NF, 2NF, 3NF)
- DDL script creation
- Data dictionary documentation

#### Major Contributions:

**A. DDL Scripts** (`ayush/ddl/`)
```
ayush/ddl/
├── 01_create_user_table.sql       # User and Profile tables
├── 02_create_paper_tables.sql     # SavedPaper, Collection, CollectionPaper
├── 03_create_citation_table.sql   # CitationLink (graph)
├── 04_create_chat_tables.sql      # ResearchChatSession, Message
├── 05_create_indexes.sql          # All 20+ indexes
├── 06_create_views.sql            # Reusable views
├── 07_create_triggers.sql         # Triggers for constraints
└── master_schema.sql              # Complete schema (production)
```

**Schema Features Implemented:**
- ✅ **20+ Tables** with proper constraints
- ✅ **Primary Keys** (AUTO_INCREMENT)
- ✅ **Foreign Keys** with CASCADE rules
- ✅ **Unique Constraints** (email, firebase_uid)
- ✅ **Check Constraints** (role validation, email format)
- ✅ **Default Values** (timestamps, booleans)
- ✅ **Indexes** (20+ strategic indexes)
- ✅ **Views** (user_statistics, citation_network_summary)
- ✅ **Comments** (column-level documentation)

**Example DDL (User Table):**
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    display_name VARCHAR(255),
    photo_url TEXT,
    role VARCHAR(50) DEFAULT 'student' CHECK(role IN ('student', 'mentor', 'researcher', 'admin')),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    
    INDEX idx_firebase_uid (firebase_uid),
    INDEX idx_email (email),
    INDEX idx_role (role)
);
```

**B. Normalization Documentation** (`ayush/normalization/`)
```
ayush/normalization/
├── 1nf_proof.md                   # First Normal Form proof
├── 2nf_proof.md                   # Second Normal Form proof
├── 3nf_proof.md                   # Third Normal Form proof
├── functional_dependencies.md     # FD analysis
├── candidate_keys.md              # Key identification
└── normalization_summary.md       # All forms explained
```

**Normalization Process Documented:**

**1NF (First Normal Form) Proof:**
- ✅ All attributes are atomic (no multi-valued fields)
- ✅ No repeating groups
- ✅ Each row is unique (primary key defined)
- Example: `authors` stored as TEXT (comma-separated) acceptable for display, or normalized to separate AuthorPaper table if needed

**2NF (Second Normal Form) Proof:**
- ✅ Already in 1NF
- ✅ No partial dependencies (all non-key attributes depend on entire primary key)
- Example: In CollectionPaper (collection_id, paper_id), both `order_index` and `note` depend on the full composite key

**3NF (Third Normal Form) Proof:**
- ✅ Already in 2NF
- ✅ No transitive dependencies (no non-key → non-key dependencies)
- Example: User's `full_name` doesn't determine `email`, both depend only on `id`

**Functional Dependencies Mapped:**
```
User:
- id → firebase_uid, email, full_name, role, ...
- firebase_uid → id (candidate key)
- email → id (candidate key)

SavedPaper:
- id → user_id, paper_id, title, authors, ...
- (user_id, paper_id) → id (composite candidate key)

CitationLink:
- id → user_id, source_paper_id, target_paper_id, weight
- (user_id, source_paper_id, target_paper_id) → id (composite candidate key)
```

**C. Data Dictionary** (`ayush/data-dictionary/`)
```
ayush/data-dictionary/
├── user_table_dictionary.md       # User table column details
├── paper_table_dictionary.md      # Paper-related tables
├── citation_table_dictionary.md   # Citation network tables
├── chat_table_dictionary.md       # Chat-related tables
├── complete_data_dictionary.xlsx  # Excel with all columns
└── data_types_reference.md        # SQLite/PostgreSQL type mapping
```

**Data Dictionary Format:**
| Table | Column | Data Type | Constraints | Description | Example |
|-------|--------|-----------|-------------|-------------|---------|
| user | id | INTEGER | PK, AUTOINCREMENT | Unique user identifier | 1 |
| user | firebase_uid | VARCHAR(128) | UNIQUE, NOT NULL | Firebase Auth UID | "abc123..." |
| user | email | VARCHAR(255) | UNIQUE | User email address | "user@example.com" |
| savedpaper | paper_id | VARCHAR(255) | NOT NULL | OpenAlex paper ID | "W2964141474" |
| citationlink | weight | INTEGER | DEFAULT 1 | Citation importance | 1-10 |

**D. Schema Optimization** (`ayush/optimization/`)
```
ayush/optimization/
├── index_strategy.md              # Index selection rationale
├── query_performance.md           # EXPLAIN QUERY PLAN analysis
├── foreign_key_indexes.md         # FK indexing for JOINs
└── composite_indexes.md           # Multi-column indexes
```

**Index Strategy:**
- Foreign key columns (for JOINs): `user_id`, `collection_id`, `session_id`, etc.
- Search columns: `email`, `firebase_uid`, `paper_id`
- Filter columns: `role`, `is_active`, `is_public`
- Sort columns: `created_at`, `saved_at`, `cited_by_count`
- Composite indexes: `(user_id, created_at)`, `(collection_id, paper_id)`

**E. Test Load Scripts** (`ayush/test-load/`)
```
ayush/test-load/
├── load_sample_users.sql          # Insert 100 users
├── load_sample_papers.sql         # Insert 500 papers
├── load_sample_collections.sql    # Insert 50 collections
├── load_citation_network.sql      # Create citation graph
└── performance_test_data.sql      # Large dataset for testing
```

**F. Schema Testing** (`ayush/testing/`)
```
ayush/testing/
├── constraint_tests.sql           # Test all constraints
├── referential_integrity_tests.sql # FK cascade tests
├── index_verification.sql         # Verify indexes exist
├── data_validation_tests.sql      # Check data quality
└── migration_tests.sql            # Schema version migration
```

**G. Major Contributions to Production Schema:**
- `backend/schema.sql` (600+ lines, production DDL)
- `backend/app/models.py` (SQLModel ORM definitions)
- All table structures, constraints, and indexes

**H. Migration Strategy:**
- SQLite (development) → PostgreSQL (production)
- Type compatibility mapping
- Data migration scripts
- Rollback procedures

**Tools Used:**
- PostgreSQL, SQLite
- DB Browser for SQLite
- pgAdmin
- DBeaver
- Excel (Data dictionary)

**Files Owned/Modified:**
- `ayush/` (entire folder)
- `backend/schema.sql` (primary author)
- `DATABASE_DESIGN.md` (Section 3: Relational Schema)
- `DATABASE_DESIGN.md` (Section 4: Normalization)

---

## 🔗 Shared/Collaborative Work

### **Documentation** (All Members)
1. **PROJECT_SUMMARY.md** (All) - Comprehensive project overview
2. **DATABASE_DESIGN.md** (Maaz + Ayush) - Complete DBMS documentation
3. **TEACHER_DEMO_GUIDE.md** (Naincy + All) - Viva presentation guide
4. **DEPLOYMENT_STATUS.md** (Hemal + Naincy) - Deployment info
5. **README.md** (All) - Project introduction

### **Backend Development** (Hemal + Ayush)
- **SQLModel Models** (`backend/app/models.py`) - ORM definitions
- **Database Layer** (`backend/app/db.py`) - Connection management
- **API Endpoints** (`backend/app/api/`) - REST API implementation
- **Demo Queries** (`backend/demo_queries.py`) - Complex SQL examples

### **Frontend Development** (Hemal + Naincy)
- **React Pages** (`citemesh-ui/src/pages/`) - All 8 pages
- **API Client** (`citemesh-ui/src/services/api.ts`) - Backend integration
- **Authentication** (`citemesh-ui/src/firebase.ts`) - Firebase setup
- **UI Components** (`citemesh-ui/src/components/`) - Reusable components

### **Testing** (Naincy + All)
- API endpoint testing
- Integration testing
- UI/UX validation
- Performance testing

### **Deployment** (Hemal + Naincy)
- Backend deployment to DigitalOcean
- Frontend deployment to Firebase
- Environment configuration
- CI/CD setup

---

## 📁 File Count & LOC Statistics

### By Team Member:

**Hemal:**
- Files: 50+
- Lines of Code: ~3,000
- Key Files: `hemal/backend/`, `backend/app/api/search.py`, `backend/app/api/pdf.py`, `backend/app/api/chat.py`

**Naincy:**
- Files: 40+
- Lines: ~1,500 (code) + extensive Excel/docs
- Key Files: `naincy/integration/`, `naincy/qa/`, `INTEGRATION_TEST_REPORT.md`

**Maaz:**
- Files: 30+
- Lines: ~2,000 (including diagrams, docs, data)
- Key Files: `maaz/erd/`, `maaz/entities/`, `DATABASE_DESIGN.md` (Section 2)

**Ayush:**
- Files: 45+
- Lines of SQL: ~2,500
- Key Files: `ayush/ddl/`, `backend/schema.sql`, `DATABASE_DESIGN.md` (Sections 3 & 4)

### Overall Project:
- **Total Files**: 300+
- **Total Lines of Code**: ~15,000+
- **SQL DDL**: 600+ lines
- **Python Backend**: 5,000+ lines
- **TypeScript Frontend**: 4,000+ lines
- **Documentation**: 10,000+ lines

---

## 🎓 DBMS Concepts Implemented

### ✅ **Foundational Concepts**
- [x] Entity-Relationship (ER) Modeling (Maaz)
- [x] Relational Schema Design (Ayush)
- [x] Primary Keys & Auto-increment (Ayush)
- [x] Foreign Keys with CASCADE (Ayush)
- [x] Unique Constraints (Ayush)
- [x] Check Constraints (Ayush)
- [x] Normalization 1NF, 2NF, 3NF (Ayush)
- [x] Data Integrity (Ayush)

### ✅ **Advanced SQL**
- [x] Multi-table JOINs (3-5 tables) (Hemal + Ayush)
- [x] Subqueries (correlated & nested) (Hemal)
- [x] Aggregation (COUNT, AVG, SUM, MIN, MAX) (Hemal)
- [x] Window Functions (RANK, LAG, SUM OVER) (Hemal)
- [x] Recursive CTEs (citation chains) (Hemal)
- [x] Transaction Management (BEGIN, COMMIT, ROLLBACK) (Hemal)
- [x] Query Optimization (EXPLAIN QUERY PLAN) (Hemal + Ayush)

### ✅ **Performance**
- [x] Strategic Indexing (20+ indexes) (Ayush)
- [x] Foreign Key Indexes (Ayush)
- [x] Composite Indexes (Ayush)
- [x] Query Performance Analysis (Hemal)

### ✅ **Graph Database Concepts**
- [x] Nodes (Papers) (Maaz)
- [x] Edges (Citations) (Maaz)
- [x] Directed Graph (Maaz + Ayush)
- [x] Graph Traversal (Hemal)
- [x] Degree Analysis (Hemal)

### ✅ **Integration & Testing**
- [x] API Testing (Naincy)
- [x] Integration Testing (Naincy)
- [x] Data Validation (Naincy)
- [x] Performance Testing (Naincy)

---

## 🚀 Technologies Used

### **Backend:**
- **Language:** Python 3.9+
- **Framework:** FastAPI 0.115.2
- **ORM:** SQLModel (SQLAlchemy + Pydantic)
- **Database:** SQLite (dev), PostgreSQL (prod)
- **Authentication:** Firebase Admin SDK
- **API Clients:** httpx, requests
- **AI Integration:** Gemini Pro API

### **Frontend:**
- **Language:** TypeScript
- **Framework:** React 18
- **Build Tool:** Vite
- **UI Library:** Custom CSS + React components
- **Auth:** Firebase Client SDK
- **State Management:** React Context

### **External APIs:**
- **OpenAlex:** 269M+ research papers
- **Gemini Pro:** AI query enhancement
- **Firebase:** Authentication & hosting

### **Deployment:**
- **Backend:** DigitalOcean App Platform
- **Frontend:** Firebase Hosting
- **Database:** Managed PostgreSQL (DigitalOcean)

### **Development Tools:**
- **Version Control:** Git, GitHub
- **API Testing:** Postman, curl
- **Database Tools:** DB Browser for SQLite, pgAdmin, DBeaver
- **Diagramming:** draw.io, Lucidchart
- **Documentation:** Markdown, Excel

---

## 📊 Project Statistics

### Database:
- **Tables:** 20+
- **Indexes:** 20+
- **Foreign Keys:** 15+
- **Views:** 3
- **Constraints:** 30+

### API:
- **Endpoints:** 30+
- **Routers:** 8
- **Request Models:** 25+
- **Response Models:** 25+

### Frontend:
- **Pages:** 8
- **Components:** 20+
- **API Methods:** 30+
- **Routes:** 8

### External Data:
- **OpenAlex Papers:** 269,800,019
- **API Keys:** 15 (Gemini)
- **Cached Queries:** 100+ (Redis-style)

---

## 🎯 Key Features Implemented

### **1. User Management**
- Firebase passwordless authentication
- User profiles with roles (Student, Mentor, Researcher, Admin)
- Mentor-student linking (M:N relationship)

### **2. Paper Management**
- Save papers from OpenAlex
- Add custom notes and tags
- Organize into collections
- Track publication details

### **3. Collection System**
- Create named collections
- Add papers to multiple collections
- Custom colors and icons
- Public/private visibility
- Order management (order_index)

### **4. Citation Network**
- Build citation graphs
- Visualize paper relationships
- Citation chain analysis (recursive CTEs)
- In-degree/out-degree metrics
- Weight-based importance

### **5. AI-Powered Search**
- Natural language queries
- Gemini AI query enhancement
- 269M+ papers from OpenAlex
- Advanced filters (year, citations, authors, OA)
- Walden API integration (data-version=2)

### **6. PDF Access**
- Open Access PDF proxy
- CORS-safe streaming
- Whitelisted domains (arxiv, europepmc, biorxiv)
- Direct download links

### **7. Research Assistant**
- AI chat about papers
- Context-aware responses
- Paper reference support
- Session management
- Gemini Pro integration

### **8. Activity Tracking**
- User action logging
- Research timeline events
- Activity feed
- Analytics dashboard

---

## 🏆 Project Achievements

### **Technical Excellence:**
- ✅ Production-ready deployment
- ✅ 269M+ papers integrated
- ✅ Sub-500ms API response times
- ✅ Comprehensive DBMS implementation
- ✅ Type-safe codebase (TypeScript + Pydantic)
- ✅ Authenticated API (Firebase)
- ✅ Scalable architecture

### **DBMS Mastery:**
- ✅ Complete ER modeling
- ✅ Normalized to 3NF
- ✅ 20+ strategically indexed tables
- ✅ Complex multi-table queries
- ✅ Recursive CTEs for graph traversal
- ✅ Transaction management
- ✅ Query optimization

### **Documentation Quality:**
- ✅ 10,000+ lines of documentation
- ✅ Complete API documentation (Swagger)
- ✅ ER diagrams with notation
- ✅ Normalization proofs
- ✅ Query examples
- ✅ Teacher demo guide

### **Real-World Application:**
- ✅ Solves actual research problem
- ✅ Scalable to millions of papers
- ✅ Modern tech stack
- ✅ Cloud deployment
- ✅ Mobile-responsive UI

---

## 📝 Key Deliverables for Viva/Demo

### **1. Documentation to Show:**
- `TEAM_CONTRIBUTIONS_GUIDE.md` (this file)
- `PROJECT_SUMMARY.md`
- `DATABASE_DESIGN.md`
- `TEACHER_DEMO_GUIDE.md`
- `backend/schema.sql`

### **2. ER Diagram to Present:**
- `maaz/erd/citemesh_er_diagram.png`
- ASCII art version in `ER_DIAGRAM_VISUAL.txt`

### **3. Code to Demonstrate:**
- `backend/demo_queries.py` (run live)
- `backend/app/models.py` (show ORM)
- `backend/schema.sql` (show DDL)

### **4. Live URLs to Access:**
- Frontend: https://citemesh.web.app/
- Backend API: https://paperverse-kvw2y.ondigitalocean.app/docs
- Health Check: https://paperverse-kvw2y.ondigitalocean.app/health

### **5. Features to Demo:**
1. Login with Firebase
2. Search for papers (AI-enhanced)
3. Save paper to library
4. Create collection
5. Build citation network
6. Chat with AI assistant
7. View statistics dashboard

---

## 🎤 Presentation Tips for Each Member

### **Hemal** - Should Talk About:
- Backend architecture and API design
- AI integration (Gemini + OpenAlex)
- Search system implementation
- PDF proxy and caching
- Performance optimization
- API endpoint demonstrations

### **Naincy** - Should Talk About:
- Integration testing strategy
- QA process and test coverage
- Demo preparation and coordination
- System validation
- Cross-component integration
- Project management

### **Maaz** - Should Talk About:
- ER diagram walkthrough
- Entity design rationale
- Relationship types and cardinality
- Graph database concepts (citation network)
- Design decisions and trade-offs

### **Ayush** - Should Talk About:
- Relational schema design
- Normalization process (1NF, 2NF, 3NF)
- DDL scripts and constraints
- Indexing strategy
- Query optimization
- Data dictionary

---

## 🔄 Workflow & Collaboration

### **Development Process:**
1. **Design Phase** (Maaz + Ayush)
   - ER modeling
   - Schema design
   - Normalization

2. **Implementation Phase** (Hemal + Ayush)
   - Backend API development
   - Database schema creation
   - Frontend integration

3. **Testing Phase** (Naincy + All)
   - Unit testing
   - Integration testing
   - QA validation

4. **Deployment Phase** (Hemal + Naincy)
   - Environment setup
   - Backend deployment
   - Frontend deployment

5. **Documentation Phase** (All)
   - Code documentation
   - User guides
   - Viva preparation

### **Communication:**
- Weekly team meetings
- GitHub for version control
- Shared Google Drive for docs
- WhatsApp for quick coordination

---

## 🎓 Learning Outcomes

### **DBMS Concepts Mastered:**
- Entity-Relationship modeling
- Relational database design
- Normalization theory
- SQL query optimization
- Transaction management
- Index strategy
- Graph database concepts

### **Software Engineering Skills:**
- RESTful API design
- ORM usage (SQLModel)
- Authentication & authorization
- Frontend-backend integration
- Cloud deployment
- Version control (Git)
- Testing & QA

### **Modern Technologies:**
- FastAPI (Python)
- React (TypeScript)
- Firebase
- PostgreSQL/SQLite
- DigitalOcean
- OpenAlex API
- Gemini AI

---

## 🎯 Grading Criteria Satisfaction

### **DBMS Theory (40%)** ✅
- ✅ ER Diagrams - Comprehensive (Maaz)
- ✅ Relational Schema - Complete DDL (Ayush)
- ✅ Normalization - 1NF, 2NF, 3NF proven (Ayush)
- ✅ Functional Dependencies - Documented (Ayush)
- ✅ Keys - Primary, Foreign, Candidate keys (Ayush)

### **SQL Implementation (40%)** ✅
- ✅ DDL - 20+ tables, indexes, views (Ayush)
- ✅ DML - INSERT, UPDATE, DELETE (Hemal)
- ✅ Queries - JOINs, subqueries, aggregation (Hemal)
- ✅ Complex Queries - Recursive, window functions (Hemal)
- ✅ Transactions - ACID properties (Hemal)
- ✅ Optimization - Indexes, EXPLAIN (Hemal + Ayush)

### **Project Quality (20%)** ✅
- ✅ Real-world application (All)
- ✅ Complete implementation (All)
- ✅ Documentation (All - 10,000+ lines)
- ✅ Deployment (Hemal + Naincy)
- ✅ Testing (Naincy)
- ✅ Code quality (All)

---

## 📞 Quick Reference Commands

### **View Database:**
```bash
cd backend
sqlite3 app.db
.tables
.schema user
```

### **Run Demo Queries:**
```bash
cd backend
python demo_queries.py
```

### **Start Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### **Start Frontend:**
```bash
cd citemesh-ui
npm install
npm run dev
```

### **Test API:**
```bash
# Health check
curl https://paperverse-kvw2y.ondigitalocean.app/health

# Search
curl -X POST https://paperverse-kvw2y.ondigitalocean.app/api/search/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "per_page": 5}'
```

---

## ✅ Final Status

**Project Completion:** 100% ✅

**All Team Members:** Contributed significantly ✅

**DBMS Requirements:** All satisfied ✅

**Deployment:** Live and accessible ✅

**Documentation:** Comprehensive and complete ✅

**Ready for Viva:** YES ✅

---

## 🎉 Conclusion

CiteMesh is a **production-grade research paper management platform** demonstrating:

1. **Collaborative Teamwork**: 4 members with clear role distribution
2. **DBMS Mastery**: Complete implementation of all DBMS concepts
3. **Real-world Application**: Solving actual research management problems
4. **Modern Technology**: Using industry-standard tools and frameworks
5. **Quality Documentation**: Extensive guides and references

Each team member made **substantial, measurable contributions** to the project's success, combining their strengths to deliver a comprehensive database management system.

---

**Project Team:**
- 🔵 Hemal Badola - Backend Architecture & AI Integration Lead
- 🟢 Naincy - Integration, QA & Demo Coordination Lead
- 🟣 Maaz - Database Design & ER Modeling Lead
- 🟡 Ayush - Schema Design & Normalization Lead

**Course:** Database Management Systems (DBMS)  
**Date:** 2024-2025  
**Status:** ✅ **COMPLETE & DEPLOYED**

---

*This guide serves as a comprehensive reference for understanding each team member's contributions to the CiteMesh DBMS project.*
