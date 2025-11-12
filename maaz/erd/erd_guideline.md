# ERD Guideline & Gallery Placeholder

Use this document to capture ER diagram exports, version history, and tooling notes. Keep all ERD source files in this folder and update the gallery below when new exports are generated.

## Tooling Instructions
- **Preferred Tools:** draw.io (browser or desktop), ERDPlus, or Lucidchart (team choice, maintain consistent notation)
- **Notation:** Crow's Foot at the logical model level; show cardinalities on both ends of each relationship
- **Export Formats:** Always save native source (`.drawio` or equivalent) and shareable image (`.png`); generate `.pdf` when stakeholder review required
- **Versioning:** Append `v#` to filenames (e.g., `research_repo_erd_v1.drawio`) and mirror the numbering in the gallery table
- **Storage:** Keep all source and exports within this `/maaz/erd/` directory to simplify handoffs to Hemal

## Update Checklist
- [x] Validate entities and relationships against the latest requirements document.
- [ ] Confirm referential integrity annotations for all foreign keys.
- [ ] Review attribute naming conventions before export.

## Export Gallery
| Version | File | Date | Notes |
|---------|------|------|-------|
| v1 | `research_repo_erd_v1.png` | 2025-10-12 | Initial draft including core entities |

## Change Log Example
- **2025-10-12:** Added `Institution` entity to capture affiliations; linked to `Paper` with optional relationship.

## Modeling Guidance
- Display all entity attributes, flagging primary keys (PK) and foreign keys (FK) explicitly; include composite keys for junction tables
- Represent junction entities (`PaperAuthor`, `PaperTopic`, etc.) with their own boxes to capture attributes like order or relevance
- Annotate optional relationships (e.g., Paper–Institution) with appropriate notation to avoid ambiguity during schema translation
- Document unresolved issues (e.g., cascading rules, polymorphic audit logging) in the change log until finalized

## Instructions
- Update the gallery table after each export, including a short note describing changes and major decisions
- Record significant modeling decisions and open questions in the change log with timestamps for traceability
- Store supporting rationale documents in `../docs/` with cross-references where needed, especially for edge cases or complex constraints
