# Optimization Notes Template

Use this document to capture query tuning experiments, EXPLAIN plan observations, and follow-up actions. Replace the sample entry with real findings.

## Session Summary
- **Date:** 2025-10-12
- **Query:** `analytics/topic_trends.sql`
- **Environment:** PostgreSQL 16.2 (staging cluster)

## Baseline Metrics
| Metric | Value | Notes |
|--------|-------|-------|
| Execution Time | 320 ms | Average of 5 runs |
| Rows Returned | 25 | Trending topics last 12 months |
| Plan Hash | 0x9fa2 | Captured via `EXPLAIN (ANALYZE, BUFFERS)` |

## EXPLAIN Snapshot
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT topic_name, COUNT(*)
FROM topic_trends
GROUP BY topic_name
ORDER BY COUNT(*) DESC;
```

- **Observation:** Sequential scan on `topic_trends`
- **Buffers:** shared hit=240, read=12

## Tuning Actions
1. Created index `idx_topic_trends_topic_name`
2. Added materialized view refresh schedule for heavy aggregation period

## Post-Tuning Metrics
| Metric | Value | Notes |
|--------|-------|-------|
| Execution Time | 110 ms | 66% improvement |
| Rows Returned | 25 | Unchanged |
| Plan Hash | 0x7bd3 | Indicates index usage |

## Follow-Up
- [ ] Monitor performance during peak load window
- [ ] Coordinate with Hemal to adjust index strategy if write latency increases

## Instructions
- Log one session per optimization effort; include detailed EXPLAIN excerpts when useful.
- Capture before/after metrics to quantify the impact of tuning.
- Add next steps or questions for the team in the Follow-Up list.
