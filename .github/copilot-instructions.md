# CiteMesh - AI Coding Agent Instructions

## Project Overview
**CiteMesh** is a research paper management platform with citation network visualization, AI chat assistance, and collaborative features. Stack: FastAPI backend + React/TypeScript frontend + SQLite/PostgreSQL database + Firebase Auth.

**Live Deployments:**
- Frontend: https://citemesh.web.app/ (Firebase)
- Backend: https://paperverse-kvw2y.ondigitalocean.app/ (DigitalOcean)

## Architecture

### Backend (`backend/`)
**Framework:** FastAPI with SQLModel ORM (SQLAlchemy + Pydantic)

**Key Structure:**
- `app/main.py` - FastAPI app initialization, CORS, router registration
- `app/models.py` - 20+ SQLModel classes (User, SavedPaper, Collection, CitationLink, etc.)
- `app/db.py` - Database engine and session management
- `app/api/` - API routers: users, papers, collections, citations, search, chat, pdf, activity
- `app/core/firebase_auth.py` - Firebase authentication middleware
- `app/services/` - Business logic (PDF processing, etc.)

**Database:**
- Development: SQLite (`app.db` in backend root, auto-created on startup)
- Production: PostgreSQL-compatible (via SQLModel)
- Schema: `backend/schema.sql` (20+ tables, indexes, constraints)

**Authentication Pattern:**
```python
from app.core.firebase_auth import FirebaseUser, get_current_user
from fastapi import Depends

@router.get("/endpoint")
async def endpoint(current_user: FirebaseUser = Depends(get_current_user)):
    user_id = current_user.db_user.id  # Database user ID
    # ... use user_id for queries
```

**Critical:** ALL API endpoints (except health check) MUST use `get_current_user` dependency for authentication. User is auto-created on first login from Firebase token.

### Frontend (`citemesh-ui/`)
**Framework:** React 18 + TypeScript + Vite

**Key Structure:**
- `src/pages/` - Main routes: Dashboard, Library, Search, Chat, Network, Login
- `src/components/` - Reusable components (SearchBar, Sidebar, etc.)
- `src/services/api.ts` - ALL backend API calls (papers, collections, citations, search, chat)
- `src/contexts/AuthContext.tsx` - Firebase auth state management
- `src/firebase.ts` - Firebase client initialization

**API Integration Pattern:**
```typescript
import api from '@/services/api';

// Always use api.ts methods, never direct fetch()
const papers = await api.papers.list(userId);
const session = await api.chat.createSession(title);
```

**Authentication Flow:**
1. Firebase handles passwordless email auth
2. Frontend gets Firebase ID token
3. Token sent in `Authorization: Bearer <token>` header
4. Backend verifies token, creates/updates User in database

### Database Design

**Core Entities:**
- `user` (1) → (N) `savedpaper`, `collection`, `citationlink`
- `collection` (N) ↔ (M) `savedpaper` via `collectionpaper`
- `citationlink` represents directed graph edges (paper citations)
- `researchchatsession` (1) → (N) `researchchatmessage`

**Graph Queries:** CitationLink table enables citation network analysis with recursive CTEs for citation chains.

**Indexing Strategy:** Foreign keys, search fields (email, paper_id), and temporal fields (created_at) are indexed. See `schema.sql` for full index list.

## Development Workflows

### Start Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Access: http://localhost:8000/docs (Swagger UI)

### Start Frontend
```bash
cd citemesh-ui
npm install
npm run dev
```
Access: http://localhost:5173

### Environment Variables

**Backend (.env):**
```bash
FIREBASE_SERVICE_ACCOUNT_BASE64=<base64-encoded-json>  # Production
# OR
FIREBASE_SERVICE_ACCOUNT_PATH=serviceAccountKey.json   # Development
```

**Frontend (.env):**
```bash
VITE_BACKEND_URL=http://localhost:8000  # Development
VITE_FIREBASE_API_KEY=<key>
VITE_FIREBASE_AUTH_DOMAIN=<domain>
# ... other Firebase config
```

### Run Database Queries
```bash
cd backend
python demo_queries.py  # Demonstrates 10 complex SQL queries
```

### Database Access
```bash
sqlite3 backend/app.db
.tables
.schema user
SELECT * FROM user LIMIT 5;
```

## Project-Specific Conventions

### 1. **No Manual User ID Management**
❌ **DON'T:** Hardcode `user_id=1` or pass user IDs in query params
✅ **DO:** Use `current_user: FirebaseUser = Depends(get_current_user)` in all endpoints

### 2. **API Service Layer (Frontend)**
❌ **DON'T:** Use `fetch()` directly in components
✅ **DO:** Add methods to `src/services/api.ts` and import

### 3. **Database Migrations**
- This project uses SQLModel auto-creation (`SQLModel.metadata.create_all()`)
- Schema changes: Update `models.py`, delete `app.db`, restart server (dev only)
- Production: Would require Alembic migrations (not currently implemented)

### 4. **CORS Configuration**
Allowed origins hardcoded in `app/main.py`. Add new origins there if deploying to new domains.

### 5. **Git Ignore Patterns**
- `.venv/`, `venv/`, `**/.venv/` - Virtual environments
- `**/node_modules/` - Node packages
- `app.db` - Local database file
- `serviceAccountKey.json` - Firebase credentials (use BASE64 env var in production)

### 6. **External APIs**
- **OpenAlex:** 269M+ papers via `/api/search/search` endpoint
- **Gemini AI:** Chat assistant via `/api/chat/` endpoints
- **A4F:** Alternative AI provider (gpt-4o-mini)

### 7. **Error Handling Pattern**
```python
from fastapi import HTTPException, status

if not resource:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resource not found"
    )
```

### 8. **Type Safety**
- Backend: SQLModel provides runtime validation + type hints
- Frontend: TypeScript interfaces in `api.ts` mirror backend Pydantic models
- Always define request/response models

## Common Tasks

### Add New API Endpoint
1. Create Pydantic request/response models in router file
2. Add endpoint with `@router.get/post/put/delete()`
3. Include `current_user: FirebaseUser = Depends(get_current_user)`
4. Register router in `app/main.py` if new file
5. Add corresponding method to `citemesh-ui/src/services/api.ts`

### Add New Database Table
1. Define SQLModel class in `app/models.py`
2. Import in `app/main.py` (for auto-creation)
3. Delete `app.db` and restart (dev) or write Alembic migration (prod)
4. Update `backend/schema.sql` with DDL for documentation

### Deploy Backend
```bash
cd backend
# DigitalOcean App Platform auto-deploys from main branch
# Requires FIREBASE_SERVICE_ACCOUNT_BASE64 env var
```

### Deploy Frontend
```bash
cd citemesh-ui
npm run build
firebase deploy --only hosting
```

## Key Files Reference

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app, CORS, router registration |
| `backend/app/models.py` | All database models (20+ tables) |
| `backend/app/core/firebase_auth.py` | Auth middleware (get_current_user) |
| `backend/schema.sql` | Complete DDL with indexes |
| `citemesh-ui/src/services/api.ts` | All API calls (single source of truth) |
| `citemesh-ui/src/contexts/AuthContext.tsx` | Firebase auth state |
| `PROJECT_SUMMARY.md` | Complete project documentation |
| `DATABASE_DESIGN.md` | ER diagrams, normalization, queries |

## Testing

**Backend:**
```bash
cd backend
python test_auth_smoke.py  # Auth tests
python demo_queries.py      # Database query demos
```

**Frontend:** No automated tests yet. Manual testing via browser.

## Debugging Tips

1. **Backend 500 errors:** Check SQLModel relationships and foreign keys
2. **CORS errors:** Verify origin in `app/main.py` CORS config
3. **Auth failures:** Check Firebase token expiration (1 hour default)
4. **Database locked:** Close other SQLite connections (`app.db` is single-writer)
5. **Git slow:** Repository had corruption, now fixed. Avoid committing `.venv/`, `node_modules/`

## What NOT to Do

- ❌ Don't commit `serviceAccountKey.json` or `.env` files
- ❌ Don't bypass authentication (all endpoints need `get_current_user`)
- ❌ Don't use `SELECT *` in production queries (specify columns)
- ❌ Don't create database connections manually (use `Depends(get_session)`)
- ❌ Don't modify `app.db` directly in production (use API/ORM)
- ❌ Don't hardcode URLs (use environment variables)

## Quick Command Reference

```bash
# Backend dev
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# Frontend dev
cd citemesh-ui && npm run dev

# Database shell
sqlite3 backend/app.db

# Push to GitHub
git add -A && git commit -m "message" && git push

# Check API health
curl https://paperverse-kvw2y.ondigitalocean.app/health
```

---

**Last Updated:** November 2024 | **Status:** Production-ready, actively maintained
