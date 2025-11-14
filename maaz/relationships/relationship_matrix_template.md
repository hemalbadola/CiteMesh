

| Relationship Name | Entities Involved | Cardinality | Junction Table Required | Notes |
|-------------------|-------------------|-------------|-------------------------|-------|
| Paper–Author Assignment | Paper ↔ Author | M:N | Yes (`PaperAuthor`) | Tracks author order and contribution role; enforce unique (paper_id, author_id) |
| Paper–Topic Tagging | Paper ↔ Topic | M:N | Yes (`PaperTopic`) | Supports hierarchical topics; relevance score captured in junction |
| Paper–Keyword Tagging | Paper ↔ Keyword | M:N | Yes (`PaperKeyword`) | Optional feature for lightweight tagging; consider merge with topics if simplified |
| Paper–Institution Affiliation | Paper ↔ Institution | M:1 | No | Paper optionally references primary institution; cascade updates disabled to protect history |
| Paper–Publication Venue | Paper ↔ PublicationVenue | M:1 | No | Paper links to venue of publication; venue info maintained independently |
| Paper–Version History | Paper ↔ PaperVersion | 1:M | No | Paper owns multiple versions; enforce unique version numbers per paper |
| Paper–Attachment Link | Paper ↔ Attachment | 1:M | No | Attachments reference a single paper; include file metadata |
| Paper–Citation Graph | Paper ↔ Paper | M:N | Yes (`Citation`) | Self-referencing via junction; includes citation type/context |
| Paper–Review Feedback | Paper ↔ Review | 1:M | No | Multiple reviews per paper and round; reviewer reference stored in Review |
| Reviewer–Institution | Reviewer ↔ Institution | M:1 | No | Reviewer optional affiliation; share institution reference with authors |
| Review–Reviewer Assignment | Review ↔ Reviewer | M:1 | No | Review references reviewer; reviewer may be external |
| UserAccount–Task Ownership | UserAccount ↔ Task | 1:M | No | Tasks assigned to users handling project workflows |
| Reviewer–Topic Expertise | Reviewer ↔ Topic | M:N | Yes (`ReviewerTopic`) | Supports reviewer matching; table includes expertise level |
| Author–Institution | Author ↔ Institution | M:1 | No | Author belongs to a primary institution; consider history table for moves |
| UserAccount–Notification | UserAccount ↔ Notification | 1:M | No | Notifications targeted to users; track read receipts |
| TagSuggestion–Paper | TagSuggestion ↔ Paper | M:1 | No | Suggestions originate from ML pipelines or users; include metadata |
| AuditLog–Entity Reference | AuditLog ↔ (Any Entity) | 1:M via polymorphic | No | Audit captures entity references; store entity name and ID without FK constraints |

## Notes
- Many-to-many relationships employ junction tables with composite primary keys and optional surrogate keys if analytics require.
- Ensure cascading delete rules align with data retention policies, especially for `Paper`, `Citation`, and `Review`.
- Polymorphic relationships (e.g., `AuditLog`) rely on application-level enforcement; document accepted entity types.
