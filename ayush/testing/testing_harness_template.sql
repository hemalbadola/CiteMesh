-- Testing Harness Template
-- Purpose: Provide a repeatable way to execute and validate SQL queries.
-- Instructions: Replace sample queries with project-specific statements and assertions.

-- Step 1: Define parameters (if using psql variables or DO blocks)
\set paper_title 'AI in Education 2025'

-- Step 2: Execute target query
WITH target_query AS (
    SELECT p.paper_id, p.title, COUNT(c.citation_id) AS citation_count
    FROM paper p
    LEFT JOIN citation c ON c.cited_paper_id = p.paper_id
    WHERE p.title = :'paper_title'
    GROUP BY p.paper_id, p.title
)
SELECT * FROM target_query;

-- Step 3: Assertion checks (simple form using expected counts)
SELECT CASE
    WHEN EXISTS (SELECT 1 FROM target_query WHERE citation_count >= 0)
        THEN 'PASS: Citation count non-negative'
    ELSE 'FAIL: Citation count negative'
END AS assertion_result;

-- Step 4: Log results (insert into a test results table or export via psql \g)
-- Example logging table creation (run once):
-- CREATE TABLE IF NOT EXISTS query_test_results (
--     test_id SERIAL PRIMARY KEY,
--     executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
--     query_name TEXT NOT NULL,
--     status TEXT NOT NULL,
--     notes TEXT
-- );

-- INSERT INTO query_test_results (query_name, status, notes)
-- VALUES ('topic_trends', 'PASS', 'Baseline validation on staging dataset');

-- Step 5: Cleanup or rollback as needed for deterministic tests
-- ROLLBACK;  -- Uncomment when running in transaction for reversible tests
