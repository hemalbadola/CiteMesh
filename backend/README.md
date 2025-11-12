# CiteMesh Backend (FastAPI) — Phase 1 Auth Skeleton

This is a minimal FastAPI backend with SQLite + JWT auth to unblock Phase 1.

## How to run (local)

1. Create a virtual environment (recommended) and install deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

3. Open docs:

- Swagger UI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Auth endpoints

- POST /auth/register — body: { email, password, full_name?, role? }
- POST /auth/login — form: username=email, password
- GET /auth/me — bearer token from login response

## Env options

- SECRET_KEY — overrides default dev key
- ACCESS_TOKEN_EXPIRE_MINUTES — default 60

## Notes

- Uses SQLite file `app.db` at project root; tables auto-created on startup.
- This is a stepping stone; can be migrated to Supabase later.