# Sample Data Scenario Plan

Outline the scenarios and datasets required to validate the ER model and subsequent schema. Replace the example entries with real planning details.

## Coverage Goals
- Papers with multiple authors (2–6) across diverse institutions and disciplines
- Papers authored by a single researcher, including early career profiles (low h-index)
- Papers without citations (new submissions) and with extensive citations (≥50 references)
- Self-citations and cross-citations across institutions to exercise recursive query logic
- Papers tagged with multiple topics and keywords, including hierarchical topic structures
- Venue diversity: conferences, journals, workshops, preprints, and technical reports

## Dataset Outline
- **Baseline Corpus:** ~100 papers covering the last 5 publication years with balanced topic distribution
- **Citation Stress Set:** Directed citation chains (length 3–5) plus dense citation clusters for graph analytics
- **Author Diversity Set:** Authors with varied affiliation statuses (with/without ORCID, joint appointments)
- **Edge Case Bundle:**
	- Papers missing DOIs but containing alternative identifiers
	- Papers with large author lists (≥12 authors) to validate ordering logic
	- Retractions or status changes to test audit logging and notifications

## Generation & Tooling
- Leverage synthetic data scripts (`../docs/generation_scripts/`) to produce repeatable CSV imports
- Use public datasets (e.g., arXiv metadata, ORCID samples) as seed values where licensing permits
- Maintain random seed control for reproducibility during testing and demos

## Validation Checklist
- [ ] Each paper links to at least one author and one publication venue
- [ ] Citation graph includes acyclic chains and cycles for traversal tests
- [ ] Topic and keyword distributions align with analytics scenarios (trending topics, recommendation)
- [ ] Sample data flagged for demo use stored under `/ayush/demo-queries/`
- [ ] Archive previous dataset revisions in `/maaz/archive/` with version notes

## Maintenance Notes
- Document dataset versions and generation scripts in `/maaz/docs/`
- Coordinate with Hemal before schema changes to align foreign key requirements
- Refresh datasets ahead of integration milestones and demo rehearsals
