# 🚀 CiteMesh Upgrade Roadmap
_Target window: Nov 7 → Dec 31, 2025_

This roadmap tracks every planned upgrade. Checkboxes show current status: ✅ = done, ☐ = pending.

---

## ✅ Phase 0 · Baseline Stabilization (COMPLETE)
- ✅ Restore backend uptime and confirm `/search` endpoint healthy
- ✅ Validate Gemini key rotation and AI fallback behaviour
- ✅ Harden OpenAlex integration (filter enforcement, retries)
- ✅ Document current stack (`FEATURE_ROADMAP.md`, `MVP_SPRINT_PLAN.md`, `FEATURE_SUMMARY.md`, `QUICK_REFERENCE.md`)
- ✅ Produce master upgrade backlog (`UPGRADE_ROADMAP.md`)

---

## 🛠 Phase 1 · Accounts & Identity (Week 1–2)
**Goal:** integrate Firebase Authentication while keeping Supabase/Postgres ready for profiles and mentor data.

1. Platform Decision & Setup
   - ✅ Pivot to Firebase Authentication for identity (07 Nov 2025)
   - ✅ Baseline metadata tables (`users`, `profiles`, `mentor_student_links`) exist for profile enrichment
   - ☐ Create Firebase project, enable Email/Password, Google, ORCID (custom provider)
   - ☐ Generate Firebase web config + service account JSON; store in secrets manager / `.env`
   - ☐ Document Firebase ↔ Supabase hybrid architecture and data flow
2. Backend Integration
   - ☐ Replace custom JWT endpoints with middleware that verifies Firebase ID tokens
   - ☐ Map Firebase users to local profile tables on first login and sync mentor links
   - ☐ Support custom claims for roles (student / mentor / researcher / admin)
   - ☐ Add webhook/cron to refresh local flags when Firebase claims change
3. Frontend Experience
   - ☐ Integrate Firebase Web SDK + Auth UI components
   - ☐ Build login, register, password reset via Firebase hosted flows
   - ☐ Persist sessions and refresh tokens (React Query/Zustand guard)
   - ☐ Gate routes using Firebase auth state + role claims

**Exit Criteria:** Firebase manages sign-in, FastAPI trusts verified tokens, mentors retain role-based access with synced profiles.

---

## 📚 Phase 2 · Personal Libraries & Collaboration (Week 3–4)
**Goal:** give users a research home—save, organize, and collaborate on papers.

1. Paper Vault
   - ☐ Endpoints: save/unsave, mark read, personal notes, ratings
   - ☐ "My Library" UI with filters (status, tags, year, access)
   - ☐ Bulk actions & CSV/JSON export
2. Collections
   - ☐ Collection CRUD with ordering & cover thumbnails
   - ☐ Visibility modes: private / cohort / public
   - ☐ Shareable view page with embedded reader + AI summary
3. Research & Reading Groups
   - ☐ Group creation, invites, roles (owner/mentor/member) for virtual journal clubs
   - ☐ Shared paper shelf + discussion thread per paper
   - ☐ Real-time feed (Supabase realtime channels or WebSocket)
   - ☐ Student post threads with mentor reactions and spotlight highlights

**Exit Criteria:** students can curate libraries, collaborate through groups, mentors can join groups.

---

## 👨‍🏫 Phase 3 · Mentor Intelligence (Week 5–6)
**Goal:** actionable mentor dashboard with student analytics.

1. Tracking & Storage
   - ☐ Instrument backend to log search/save/read/note events
   - ☐ Nightly aggregation job (Supabase Functions/Cron) → metrics tables
2. Mentor Workspace
   - ☐ Mentor dashboard overview (active mentees, alerts, trends)
   - ☐ Student detail pages (timeline, streaks, topic spread)
   - ☐ Assignment workflow (assign paper, deadline, reminders, completion check)
3. Privacy & Compliance
   - ☐ Student visibility preferences (share all / assigned only / custom)
   - ☐ Data retention policy + export tool (CSV/PDF reports)
   - ☐ Notification settings per mentor/student

4. Learning Paths
   - ☐ Curriculum builder for mentors to sequence papers and activities
   - ☐ Progress tracker with auto-updated completion and reflection notes
   - ☐ AI-assisted pathway suggestions to fill knowledge gaps (mentor approval required)

**Exit Criteria:** mentors can monitor progress, assign readings, export reports, respect privacy settings.

---

## 🤖 Phase 4 · AI Research Copilot (Week 7)
**Goal:** elevate research flow with intelligent assistance.

- ☐ AI Research Chat interface with paper context panel and message history
- ☐ Multi-paper summarization pipeline (Gemini + cached embeddings)
- ☐ Auto literature review drafts (structured sections, citations) for collections
- ☐ Paper comparison view (methods/results deltas, tables, charts)
- ☐ Contradiction detector to surface conflicting findings and unresolved debates
- ☐ "Find related" leveraging citation graph + semantic neighbors
- ☐ Safety guardrails: rate limits, prompt sanitization, audit logs

**Exit Criteria:** users converse with AI using selected papers; mentors verify accuracy on sample set.

---

## 🎨 Phase 5 · Visual Discovery Suite (Week 8)
**Goal:** make literature exploration intuitive and delightful.

- ☐ Research timeline of breakthroughs (filters by topic, institution)
- ☐ Smart clustering explorer (2D/3D UMAP/TSNE + Three.js) with hover insights
- ☐ Citation network graph explorer (centrality metrics, paths, communities)
- ☐ Trend analytics (emerging topics, hot authors, geographic spread)

**Exit Criteria:** visual tools load under 3 s, interactive filters stay responsive (<300 ms updates).

---

## 🔄 Phase 6 · Engagement & Retention (Post-MVP)
- ☐ Notification center (assignments, mentions, new papers)
- ☐ Weekly digest emails + in-app recap
- ☐ Gamification (streaks, badges, leaderboards) with mentor overrides
- ☐ Enhanced collaboration (polls, shared mind maps, scheduled discussions)

---

## 📱 Phase 7 · Extensions & Integrations (Post-MVP)
- ☐ Browser extension (arXiv / Scholar one-click save)
- ☐ Mobile-first polish → PWA and/or native shell
- ☐ Integrations (Zotero, Notion, Overleaf, Slack, LMS)
- ☐ Public API/SDK for institutional partners + API key management UI

---

## 📋 Operating Guidelines
- ✅ Keep this roadmap as single source of truth
- ✅ Update checkboxes after each sprint demo; add notes/dates beside completed tasks (Started 07 Nov 2025)
- ☐ Maintain `CHANGELOG.md` for release summaries + migrations
- ☐ Collect mentor/student feedback bi-weekly and adjust scope as needed

_Last updated: 07 Nov 2025_

---

**Change Log Notes:**
- 07 Nov 2025 — roadmap created and verified after file-write issue test.
- 07 Nov 2025 — Phase 1 kicked off: chose temporary local stack (SQLite + JWT). Proceeding to scaffold backend auth.
- 07 Nov 2025 — Backend auth skeleton added: FastAPI app, `/health`, `/auth/register`, `/auth/login`, `/auth/me`.
- 07 Nov 2025 — Pivoted Phase 1 plan to Firebase Authentication; local JWT endpoints will be replaced by Firebase token verification.
