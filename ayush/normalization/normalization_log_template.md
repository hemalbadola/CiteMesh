# Normalization Log Template

Document the progression of schema refinement from unnormalized structures to 3NF (or higher as needed). Replace the example entries with actual tables and decisions.

## Table Under Analysis: PaperSubmission

### Unnormalized Form (UNF)
- **Attributes:** paper_id, title, authors (array), topics (array), institution_name, institution_country
- **Issues Identified:** Repeating groups in authors and topics; mixed institution data

### First Normal Form (1NF)
- **Action Taken:** Split authors into `paper_author` junction table; topics into `paper_topic`
- **Resulting Tables:** paper, paper_author, paper_topic
- **Open Questions:** Should `institution` be its own table?

### Second Normal Form (2NF)
- **Composite Keys Evaluated:** `paper_author(paper_id, author_id)`
- **Dependencies Removed:** author_role depends only on author, migrated to author table
- **New Tables:** author

### Third Normal Form (3NF)
- **Transitive Dependencies:** `institution_country` depends on `institution_name`
- **Resolution:** Created `institution` table with country attribute
- **Constraints Added:** Foreign key from paper to institution

### Validation & Notes
- Verified functional dependencies with ER diagram v1
- Pending review with Maaz for alignment on institution modeling

## Instructions
- Create a new section for each table or dataset undergoing normalization.
- Capture decisions, dependencies, and resulting structures at each normal form stage.
- Record outstanding questions or cross-team follow-ups in the notes.
