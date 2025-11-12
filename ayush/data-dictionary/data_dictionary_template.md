# Data Dictionary Template

Use this template to document each table, column, and constraint in the schema. Replace the example sections with actual definitions as the schema evolves.

## Table: paper
- **Description:** Stores research paper metadata.
- **Primary Key:** `paper_id`
- **Indexes:** `idx_paper_publication_year`

| Column | Data Type | Nullable | Default | Description |
|--------|-----------|----------|---------|-------------|
| paper_id | UUID | No | `gen_random_uuid()` | Unique identifier for each paper |
| title | VARCHAR(255) | No | — | Full paper title |
| publication_year | SMALLINT | No | — | Year the paper was published |
| created_at | TIMESTAMPTZ | No | `NOW()` | Record creation timestamp |

### Constraints & Notes
- CHECK `publication_year` between 1900 and 2100 to ensure data validity.
- Add comment: `COMMENT ON TABLE paper IS 'Stores core metadata for research papers.'`

## Table: paper_author
- **Description:** Junction table mapping papers to authors.
- **Primary Key:** `(paper_id, author_id)`
- **Foreign Keys:** `paper_author.paper_id → paper.paper_id`

| Column | Data Type | Nullable | Default | Description |
|--------|-----------|----------|---------|-------------|
| paper_id | UUID | No | — | Linked paper identifier |
| author_id | UUID | No | — | Linked author identifier |
| author_role | VARCHAR(50) | No | `'Primary'` | Role of the author for the paper |

### Constraints & Notes
- Enforce role values via CHECK (`author_role IN ('Primary','Co-Author','Editor')`).
- Cascade delete on `paper_id` to maintain referential integrity.

## Instructions
- Repeat the section layout for every table in the schema.
- Include index descriptions and usage notes to help Ayush optimize queries.
- Cross-reference related tables and note any non-obvious relationships.
