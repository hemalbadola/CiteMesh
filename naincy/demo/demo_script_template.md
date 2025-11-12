# Demo Walkthrough Script Template

Use this script to plan and deliver the demo. Customize each section with project-specific content and update the timing estimates as practice sessions refine the flow.

## Session Overview
- **Audience:** Faculty advisors and mentor panel
- **Duration:** 20 minutes + 10 minutes Q&A
- **Goal:** Showcase end-to-end research paper lifecycle and citation analytics

## Agenda Timeline
| Time (min) | Segment | Presenter | Key Talking Points |
|------------|---------|-----------|--------------------|
| 0-2 | Introduction | Naincy | Team mission, problem statement |
| 3-8 | Data Model Overview | Maaz | ERD highlights, extensibility |
| 9-14 | Schema & Workflows | Hemal | Schema decisions, normalization |
| 15-20 | Advanced Queries Demo | Ayush | Trend analysis, citation chains |

## Live Demo Steps
1. Log into the application using demo credentials (`demo_lead` / `password123`).
2. Navigate to the paper submission form and create sample entry "AI in Education 2025".
3. Show automatic topic tagging and citation recommendations.
4. Run "Top Emerging Topics" analytic query and display results.
5. Conclude with citation graph visualization export.

## Backup Plan
- **Primary Risk:** Query latency > 3 seconds
- **Mitigation:** Pre-recorded screen capture stored at `demo/assets/backup_run.mp4`
- **Alternative Flow:** Skip live query and walk through screenshots if database load is high

## Props & Visuals
- Slide deck `demo/slides/v1/demo_deck.pptx`
- ERD image `demo/visuals/erd_overview.png`

## Q&A Seed Questions
- How does the system handle new citation formats?
- What indexing strategies were used to accelerate complex joins?

## Next Steps After Demo
- Capture feedback in `management/demo_feedback.md`
- Schedule retrospective meeting within 24 hours
