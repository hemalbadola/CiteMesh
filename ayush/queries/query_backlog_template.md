# Query Backlog Template

Track SQL query requirements mapped to user stories. Update the table as new requests surface or priorities shift.

## Backlog Grid
| Query ID | User Story / Requirement | Type (CRUD/Analytics/CTE) | Priority | Owner | Status | Notes |
|----------|--------------------------|---------------------------|----------|-------|--------|-------|
| QRY-001 | As a researcher, I want to search papers by topic | Analytics | High | Ayush | Draft | Requires join on `paper_topic` |
| QRY-002 | As an admin, I want to add a new author | CRUD | Medium | Ayush | To Do | Implement as parameterized insert |

## Instructions
- Use one row per query requirement and keep descriptions concise.
- Align query priorities with sprint goals; adjust as stakeholders reprioritize.
- Include references to related files (e.g., `queries/analytics/topic_trends.sql`) in the Notes column for quick navigation.
