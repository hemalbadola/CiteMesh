# Demo Query Shortlist Template

Curate the queries highlighted during the demo, including purpose, setup, and results snapshots. Update the example entries with the actual demo selections.

## Hero Query Overview
| Query Name | Purpose | Dataset Prerequisites | Demo Flow Placement |
|------------|---------|-----------------------|---------------------|
| Trending Topics | Showcase analytics capability to surface emerging themes | Requires refreshed `topic_trends_mv` | After schema walkthrough |
| Citation Depth CTE | Demonstrate recursive traversal of citation graph | Seed dataset with multi-level citations | Final showcase segment |

## Execution Steps (Example: Trending Topics)
1. Ensure materialized view `topic_trends_mv` refreshed within last 24 hours.
2. Run `sql/demo/trending_topics.sql` in psql or application dashboard.
3. Highlight top 5 topics and compare year-over-year growth.
4. Display pre-generated chart stored at `demo-queries/assets/trending_topics.png`.

## Expected Output Snapshot
```
 topic_name        | paper_count | growth_rate
------------------+-------------+-------------
 Artificial Intelligence | 45 | 18%
 Data Governance         | 32 | 12%
```

## Risk & Backup Plan
- **Risk:** Materialized view not refreshed → outdated results
- **Mitigation:** Keep CSV export `demo-queries/backups/trending_topics_latest.csv` ready for visualization

## Follow-Up Actions
- [ ] Capture screenshot of latest output for slide deck
- [ ] Confirm dataset alignment with Maaz's sample data plan before rehearsal

## Instructions
- Add new hero queries as additional sections with execution steps and expected outputs.
- Reference exact SQL files and datasets so the demo team can replicate results quickly.
- Update risk mitigations as system behavior evolves.
