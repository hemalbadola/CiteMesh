-- CiteMesh Database Schema - Complete DDL
-- Database Management System Project
-- SQLite/PostgreSQL Compatible

-- ============================================
-- CORE TABLES
-- ============================================

-- User Table: Central entity for all users
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    display_name VARCHAR(255),
    photo_url TEXT,
    role VARCHAR(50) DEFAULT 'student' CHECK (role IN ('student', 'mentor', 'researcher', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE INDEX idx_user_firebase_uid ON user(firebase_uid);
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_user_role ON user(role);

-- Profile Table: Extended user information (1:1 with User)
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    bio TEXT,
    affiliation VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_profile_user_id ON profile(user_id);

-- ============================================
-- PAPER MANAGEMENT
-- ============================================

-- SavedPaper Table: User's saved research papers
CREATE TABLE IF NOT EXISTS savedpaper (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    paper_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    authors TEXT,
    summary TEXT,
    published_year INTEGER,
    tags TEXT,
    saved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE (user_id, paper_id)
);

CREATE INDEX idx_savedpaper_user_id ON savedpaper(user_id);
CREATE INDEX idx_savedpaper_paper_id ON savedpaper(paper_id);
CREATE INDEX idx_savedpaper_saved_at ON savedpaper(saved_at);
CREATE INDEX idx_savedpaper_year ON savedpaper(published_year);

-- ============================================
-- COLLECTIONS (Paper Organization)
-- ============================================

-- Collection Table: User-created paper collections
CREATE TABLE IF NOT EXISTS collection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    color VARCHAR(20) DEFAULT '#6366f1',
    icon VARCHAR(10) DEFAULT '📚',
    is_public BOOLEAN DEFAULT FALSE,
    paper_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_collection_user_id ON collection(user_id);
CREATE INDEX idx_collection_name ON collection(name);
CREATE INDEX idx_collection_public ON collection(is_public);

-- CollectionPaper Table: Many-to-Many junction between Collection and Papers
CREATE TABLE IF NOT EXISTS collectionpaper (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    paper_id VARCHAR(255) NOT NULL,
    paper_title VARCHAR(500) NOT NULL,
    paper_authors TEXT,
    paper_year INTEGER,
    note TEXT,
    order_index INTEGER DEFAULT 0,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (collection_id) REFERENCES collection(id) ON DELETE CASCADE,
    UNIQUE (collection_id, paper_id)
);

CREATE INDEX idx_collectionpaper_collection_id ON collectionpaper(collection_id);
CREATE INDEX idx_collectionpaper_paper_id ON collectionpaper(paper_id);
CREATE INDEX idx_collectionpaper_order ON collectionpaper(order_index);

-- ============================================
-- CITATION NETWORK (Graph Structure)
-- ============================================

-- CitationLink Table: Directed graph of paper citations
CREATE TABLE IF NOT EXISTS citationlink (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    source_paper_id VARCHAR(255) NOT NULL,
    target_paper_id VARCHAR(255) NOT NULL,
    weight REAL DEFAULT 1.0,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE (user_id, source_paper_id, target_paper_id)
);

CREATE INDEX idx_citationlink_user_id ON citationlink(user_id);
CREATE INDEX idx_citationlink_source ON citationlink(source_paper_id);
CREATE INDEX idx_citationlink_target ON citationlink(target_paper_id);
CREATE INDEX idx_citationlink_bidirectional ON citationlink(source_paper_id, target_paper_id);

-- ============================================
-- AI CHAT SYSTEM
-- ============================================

-- ResearchChatSession Table: AI chat sessions
CREATE TABLE IF NOT EXISTS researchchatsession (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    system_prompt TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_researchchatsession_user_id ON researchchatsession(user_id);
CREATE INDEX idx_researchchatsession_updated ON researchchatsession(updated_at);

-- ResearchChatMessage Table: Individual messages in chat sessions
CREATE TABLE IF NOT EXISTS researchchatmessage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    sender VARCHAR(20) NOT NULL CHECK (sender IN ('user', 'assistant')),
    content TEXT NOT NULL,
    references TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES researchchatsession(id) ON DELETE CASCADE
);

CREATE INDEX idx_researchchatmessage_session_id ON researchchatmessage(session_id);
CREATE INDEX idx_researchchatmessage_created_at ON researchchatmessage(created_at);

-- ============================================
-- COLLABORATION (Mentor-Student)
-- ============================================

-- MentorStudentLink Table: Many-to-Many relationship for mentorship
CREATE TABLE IF NOT EXISTS mentorstudentlink (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mentor_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (mentor_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE (mentor_id, student_id),
    CHECK (mentor_id != student_id)
);

CREATE INDEX idx_mentorstudentlink_mentor ON mentorstudentlink(mentor_id);
CREATE INDEX idx_mentorstudentlink_student ON mentorstudentlink(student_id);

-- ============================================
-- ADVANCED FEATURES
-- ============================================

-- StudentActivity Table: Track student activities for mentors
CREATE TABLE IF NOT EXISTS studentactivity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mentor_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    detail TEXT,
    metric_value REAL,
    occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (mentor_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_studentactivity_mentor ON studentactivity(mentor_id);
CREATE INDEX idx_studentactivity_student ON studentactivity(student_id);
CREATE INDEX idx_studentactivity_occurred ON studentactivity(occurred_at);

-- ResearchTimelineEvent Table: Track research milestones
CREATE TABLE IF NOT EXISTS researchtimelineevent (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    concept VARCHAR(255) NOT NULL,
    description TEXT,
    year INTEGER,
    source_paper_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_researchtimelineevent_user ON researchtimelineevent(user_id);
CREATE INDEX idx_researchtimelineevent_year ON researchtimelineevent(year);

-- PaperCluster Table: ML-based paper clustering
CREATE TABLE IF NOT EXISTS papercluster (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    label VARCHAR(255) NOT NULL,
    description TEXT,
    method VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_papercluster_user ON papercluster(user_id);

-- PaperClusterMembership Table: Papers in clusters
CREATE TABLE IF NOT EXISTS paperclustermembership (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_id INTEGER NOT NULL,
    paper_id VARCHAR(255) NOT NULL,
    paper_title VARCHAR(500),
    note TEXT,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cluster_id) REFERENCES papercluster(id) ON DELETE CASCADE
);

CREATE INDEX idx_paperclustermembership_cluster ON paperclustermembership(cluster_id);
CREATE INDEX idx_paperclustermembership_paper ON paperclustermembership(paper_id);

-- LiteratureReview Table: Generated literature reviews
CREATE TABLE IF NOT EXISTS literaturereview (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic VARCHAR(255) NOT NULL,
    prompt TEXT,
    content TEXT,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'in_progress', 'completed', 'archived')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_literaturereview_user ON literaturereview(user_id);
CREATE INDEX idx_literaturereview_status ON literaturereview(status);

-- PaperComparison Table: Side-by-side paper comparisons
CREATE TABLE IF NOT EXISTS papercomparison (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    paper_a_id VARCHAR(255) NOT NULL,
    paper_b_id VARCHAR(255) NOT NULL,
    focus TEXT,
    summary TEXT,
    strengths_a TEXT,
    strengths_b TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_papercomparison_user ON papercomparison(user_id);

-- ReadingGroup Table: Collaborative reading groups
CREATE TABLE IF NOT EXISTS readinggroup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mentor_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    focus_area VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (mentor_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_readinggroup_mentor ON readinggroup(mentor_id);

-- ReadingGroupMembership Table: Group members
CREATE TABLE IF NOT EXISTS readinggroupmembership (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role VARCHAR(50) DEFAULT 'student' CHECK (role IN ('student', 'mentor', 'guest')),
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (group_id) REFERENCES readinggroup(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE (group_id, user_id)
);

CREATE INDEX idx_readinggroupmembership_group ON readinggroupmembership(group_id);
CREATE INDEX idx_readinggroupmembership_user ON readinggroupmembership(user_id);

-- ReadingGroupPost Table: Group discussions
CREATE TABLE IF NOT EXISTS readinggrouppost (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    paper_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (group_id) REFERENCES readinggroup(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_readinggrouppost_group ON readinggrouppost(group_id);
CREATE INDEX idx_readinggrouppost_created ON readinggrouppost(created_at);

-- ContradictionFlag Table: Flag conflicting papers
CREATE TABLE IF NOT EXISTS contradictionflag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    paper_id VARCHAR(255) NOT NULL,
    conflicting_paper_id VARCHAR(255) NOT NULL,
    summary TEXT,
    severity VARCHAR(50) CHECK (severity IN ('low', 'medium', 'high')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_contradictionflag_user ON contradictionflag(user_id);
CREATE INDEX idx_contradictionflag_paper ON contradictionflag(paper_id);

-- LearningPath Table: Structured learning paths
CREATE TABLE IF NOT EXISTS learningpath (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mentor_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    skill_focus VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (mentor_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX idx_learningpath_mentor ON learningpath(mentor_id);

-- LearningPathStep Table: Steps in learning paths
CREATE TABLE IF NOT EXISTS learningpathstep (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    resource_url TEXT,
    estimated_minutes INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (path_id) REFERENCES learningpath(id) ON DELETE CASCADE
);

CREATE INDEX idx_learningpathstep_path ON learningpathstep(path_id);
CREATE INDEX idx_learningpathstep_order ON learningpathstep(step_order);

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: User Statistics
CREATE VIEW IF NOT EXISTS user_statistics AS
SELECT 
    u.id,
    u.full_name,
    u.email,
    u.role,
    COUNT(DISTINCT sp.id) as saved_papers_count,
    COUNT(DISTINCT c.id) as collections_count,
    COUNT(DISTINCT cl.id) as citations_count,
    COUNT(DISTINCT rcs.id) as chat_sessions_count,
    MAX(sp.saved_at) as last_paper_saved
FROM user u
LEFT JOIN savedpaper sp ON u.id = sp.user_id
LEFT JOIN collection c ON u.id = c.user_id
LEFT JOIN citationlink cl ON u.id = cl.user_id
LEFT JOIN researchchatsession rcs ON u.id = rcs.user_id
GROUP BY u.id, u.full_name, u.email, u.role;

-- View: Citation Network Summary
CREATE VIEW IF NOT EXISTS citation_network_summary AS
SELECT 
    cl.target_paper_id as paper_id,
    COUNT(*) as times_cited,
    COUNT(DISTINCT cl.user_id) as cited_by_users,
    AVG(cl.weight) as avg_citation_weight,
    MAX(cl.created_at) as most_recent_citation
FROM citationlink cl
GROUP BY cl.target_paper_id
HAVING COUNT(*) > 0
ORDER BY times_cited DESC;

-- View: Collection Overview
CREATE VIEW IF NOT EXISTS collection_overview AS
SELECT 
    c.id,
    c.user_id,
    c.name,
    c.description,
    c.is_public,
    c.paper_count,
    COUNT(DISTINCT cp.id) as actual_paper_count,
    MIN(cp.paper_year) as oldest_paper_year,
    MAX(cp.paper_year) as newest_paper_year,
    c.created_at,
    c.updated_at
FROM collection c
LEFT JOIN collectionpaper cp ON c.id = cp.collection_id
GROUP BY c.id, c.user_id, c.name, c.description, c.is_public, c.paper_count, c.created_at, c.updated_at;

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Insert sample user (for testing only)
INSERT OR IGNORE INTO user (id, firebase_uid, email, full_name, role) 
VALUES (1, 'test_uid_123', 'test@citemesh.edu', 'Test User', 'student');

-- Insert sample profile
INSERT OR IGNORE INTO profile (user_id, affiliation, bio) 
VALUES (1, 'Test University', 'PhD student in Computer Science');

-- ============================================
-- DATABASE STATISTICS QUERY
-- ============================================

-- Query to show table counts
CREATE VIEW IF NOT EXISTS database_stats AS
SELECT 
    'users' as table_name,
    COUNT(*) as record_count
FROM user
UNION ALL
SELECT 'saved_papers', COUNT(*) FROM savedpaper
UNION ALL
SELECT 'collections', COUNT(*) FROM collection
UNION ALL
SELECT 'collection_papers', COUNT(*) FROM collectionpaper
UNION ALL
SELECT 'citation_links', COUNT(*) FROM citationlink
UNION ALL
SELECT 'chat_sessions', COUNT(*) FROM researchchatsession
UNION ALL
SELECT 'chat_messages', COUNT(*) FROM researchchatmessage
UNION ALL
SELECT 'mentor_student_links', COUNT(*) FROM mentorstudentlink;

-- ============================================
-- END OF SCHEMA
-- ============================================

-- To use this schema:
-- 1. SQLite: sqlite3 database.db < schema.sql
-- 2. PostgreSQL: psql -d database_name -f schema.sql
-- 3. MySQL: mysql -u username -p database_name < schema.sql
