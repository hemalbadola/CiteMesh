-- Test Load Script Template
-- Purpose: Seed sample data and validate schema integrity after DDL execution.
-- Instructions: Replace sample inserts with project-specific data; extend validation queries as needed.

-- Step 1: Seed lookup tables
INSERT INTO topic (topic_id, name)
VALUES
    (gen_random_uuid(), 'Artificial Intelligence'),
    (gen_random_uuid(), 'Data Mining')
ON CONFLICT DO NOTHING;

-- Step 2: Seed core entities
WITH new_paper AS (
    INSERT INTO paper (paper_id, title, publication_year)
    VALUES (gen_random_uuid(), 'AI in Education 2025', 2025)
    RETURNING paper_id
)
INSERT INTO paper_author (paper_id, author_id, author_role)
SELECT np.paper_id, gen_random_uuid(), 'Primary'
FROM new_paper np;

-- Step 3: Integrity validation queries (replace with actual CHECKS)
-- Example: Verify row counts
SELECT 'paper_count' AS metric, COUNT(*) AS value FROM paper;
SELECT 'paper_author_count' AS metric, COUNT(*) AS value FROM paper_author;

-- Example: Ensure foreign key relationships hold
SELECT pa.paper_id
FROM paper_author pa
LEFT JOIN paper p ON p.paper_id = pa.paper_id
WHERE p.paper_id IS NULL;
-- Expect zero rows; any result signals referential integrity issues.

-- Step 4: Cleanup commands for repeated test runs (comment out if not needed)
-- DELETE FROM paper_author;
-- DELETE FROM paper;
