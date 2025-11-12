-- DDL Template (PostgreSQL)
-- Purpose: Provide a starting structure for defining tables, constraints, and indexes.
-- Instructions: Replace sample objects with project-specific names and definitions.

BEGIN;

-- Example table definition
CREATE TABLE IF NOT EXISTS paper (
    paper_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    publication_year SMALLINT NOT NULL CHECK (publication_year BETWEEN 1900 AND 2100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Example junction table with composite primary key
CREATE TABLE IF NOT EXISTS paper_author (
    paper_id UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    author_id UUID NOT NULL,
    author_role VARCHAR(50) NOT NULL DEFAULT 'Primary',
    PRIMARY KEY (paper_id, author_id)
);

-- Example index to support query optimization
CREATE INDEX IF NOT EXISTS idx_paper_publication_year ON paper (publication_year);

-- Constraint checklist (mark items completed as you implement real tables)
-- [ ] Define surrogate vs. natural keys per entity
-- [ ] Enforce NOT NULL and CHECK constraints for business rules
-- [ ] Add FOREIGN KEY constraints with appropriate cascading actions
-- [ ] Create indexes for high-frequency query fields
-- [ ] Include comments on tables and columns for documentation

COMMIT;
