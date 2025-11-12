# QA Test Report Template

Document the outcome of a QA cycle using this structure. Replace sample text with actual findings while keeping the sections intact for consistency across cycles.

## Test Campaign Overview
- **Campaign Name:** Release Candidate RC-1 Regression
- **Execution Window:** 2025-10-10 → 2025-10-12
- **QA Lead:** Naincy Sharma
- **Build Under Test:** `v1.0.0-rc1`

## Test Environment
| Component | Version | Notes |
|-----------|---------|-------|
| PostgreSQL | 16.2 | Hosted on staging cluster |
| Application | commit `abc1234` | Deployed on Kubernetes namespace `staging` |
| Test Data Set | `staging_seed_v3` | Includes 50k papers, 120k citations |

## Test Scope
- Regression tests for user management, search, and citation workflows
- Verification of new indexing strategy implemented by Hemal
- Smoke tests for newly integrated reporting module

## Test Case Execution
| Test Case ID | Description | Result | Defect Ref | Notes |
|--------------|-------------|--------|------------|-------|
| REG-101 | Verify author profile editing | ✅ Pass | — | Works as expected |
| REG-214 | Citation graph traversal depth check | ❌ Fail | BUG-342 | Null pointer when paper lacks topic |

## Defect Summary
- **Total Defects:** 4 (Severity: 1 Critical, 2 Major, 1 Minor)
- **Status:** 1 Open, 2 In Progress, 1 Resolved pending retest
- **Critical Issue:** BUG-341 (Search results stale after index rebuild)

## Recommendations
- Block release until BUG-341 resolved and regression retested
- Coordinate with Ayush to add query latency measurement to automated suite

## Sign-Off
- **Reviewed By:** QA Team
- **Date:** 2025-10-12
