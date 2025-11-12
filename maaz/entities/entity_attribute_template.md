# Entity & Attribute Inventory Template

Document each entity with its attributes, data types, and business rules. Use one table per entity, updating the example entry with real values.

## Entity: Paper
| Attribute | Data Type | Nullable | Description | Notes |
|-----------|-----------|----------|-------------|-------|
| paper_id | UUID | No | Unique identifier for a paper | Generated via UUIDv4 |
| title | VARCHAR(255) | No | Full title of the research paper | Enforce unique constraint per year |
| publication_year | SMALLINT | No | Year the paper was published | Range check 1900-2100 |

## Entity: Author
| Attribute | Data Type | Nullable | Description | Notes |
|-----------|-----------|----------|-------------|-------|
| author_id | UUID | No | Unique identifier for an author | Surrogate key |
| full_name | VARCHAR(150) | No | Author's full name | Consider additional name components |
| orcid | VARCHAR(19) | Yes | ORCID identifier | Format ####-####-####-#### |

## Instructions
- Duplicate the table structure for each new entity in the system.
- Include derived or calculated attributes with clear notes when applicable.
- Flag candidate keys or unique constraint requirements in the Notes column.
