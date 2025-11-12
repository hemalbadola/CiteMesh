# `ayush`

This workspace now houses the relational design, normalization, and documentation workstreams.

## Expected Deliverables
- Normalization walkthroughs (1NF, 2NF, 3NF) with supporting evidence
- PostgreSQL DDL scripts for tables, constraints, indexes, and sequences
- Data dictionaries detailing column semantics, datatypes, and relationships
- Sample load scripts, integrity checks, and migration rehearsal notes
- Schema diagrams and accompanying documentation for viva preparation

## Organization Guidelines
- Keep DDL and migration scripts in the `ddl/` subfolder, ordered by execution sequence.
- Place documentation artifacts under `docs/`, with diagrams or exports in `assets/`.
- Store data dictionary material in `data-dictionary/` and normalization proofs in `normalization/`.
- Retain previous iterations inside `archive/` rather than deleting them, so design rationale stays traceable.
