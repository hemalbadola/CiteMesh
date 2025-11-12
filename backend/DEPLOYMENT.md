# Backend Deployment Guide

## Quick Deploy Options

### Option 1: Render.com (Recommended - Free Tier Available)

1. **Create a Render Account**: https://render.com
2. **New Web Service**:
   - Connect your GitHub repository
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
3. **Environment Variables** (Add in Render Dashboard):
   ```
   FIREBASE_PROJECT_ID=citemesh
   DATABASE_URL=sqlite:///./app.db
   ```

4. **Add Service Account**:
   - In Render dashboard, go to "Secret Files"
   - Add `serviceAccountKey.json` with your Firebase credentials

5. **Update CORS in `app/main.py`**:
   - Add your Render URL to `allow_origins` list

### Option 2: Railway.app

1. **Create a Railway Account**: https://railway.app
2. **New Project** → **Deploy from GitHub**
3. **Configure**:
   - Root Directory: `/backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
4. **Environment Variables**:
   ```
   FIREBASE_PROJECT_ID=citemesh
   DATABASE_URL=sqlite:///./app.db
   ```

5. **Add Firebase Service Account**:
   - Base64 encode your `serviceAccountKey.json`
   - Add as environment variable `FIREBASE_SERVICE_ACCOUNT_BASE64`
   - Update `firebase_auth.py` to decode it

### Option 3: Fly.io

1. **Install Fly CLI**: `brew install flyctl` (macOS)
2. **Login**: `flyctl auth login`
3. **Initialize**:
   ```bash
   cd backend
   flyctl launch
   ```

4. **Set Secrets**:
   ```bash
   flyctl secrets set FIREBASE_PROJECT_ID=citemesh
   cat serviceAccountKey.json | flyctl secrets set FIREBASE_SERVICE_ACCOUNT=-
   ```

5. **Deploy**:
   ```bash
   flyctl deploy
   ```

## Production Database Setup

### PostgreSQL with pgvector (Required for full features)

#### On Render:
1. Create PostgreSQL database in Render
2. Install pgvector extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Update `DATABASE_URL` environment variable

#### On Railway:
1. Add PostgreSQL plugin
2. Connect to database
3. Install pgvector (available by default on Railway)

#### Local PostgreSQL Setup:
```bash
# Install PostgreSQL and pgvector
brew install postgresql pgvector

# Start PostgreSQL
brew services start postgresql

# Create database
createdb citemesh_db

# Connect and enable extension
psql citemesh_db -c "CREATE EXTENSION vector;"
```

## Environment Configuration

### Required Environment Variables

```bash
# Firebase
FIREBASE_PROJECT_ID=citemesh

# Database (SQLite for development)
DATABASE_URL=sqlite:///./app.db

# Database (PostgreSQL for production)
# DATABASE_URL=postgresql://user:password@host:5432/dbname

# Optional
CORS_ORIGINS=https://citemesh.web.app,https://citemesh.firebaseapp.com
```

### Firebase Service Account

**Never commit `serviceAccountKey.json` to git!**

For deployment:
1. **Render/Railway**: Upload as secret file
2. **Fly.io**: Use secrets
3. **Docker**: Mount as volume

## Health Check

After deployment, verify:
```bash
curl https://your-backend-url.com/health
```

Should return:
```json
{"status":"ok","message":"CiteMesh API is running"}
```

## Update Frontend CORS

After deploying backend, update `citemesh-ui/src/components/PaperVerseConsole.tsx`:

```typescript
const backendBaseUrl = import.meta.env.PROD
  ? 'https://your-backend-url.com'  // Your deployed backend URL
  : 'http://localhost:8000'
```

## Monitoring & Logs

- **Render**: Built-in logs and metrics
- **Railway**: Logs tab in dashboard
- **Fly.io**: `flyctl logs`

## Common Issues

### CORS Errors
- Add your frontend URL to `allow_origins` in `app/main.py`

### Firebase Auth Errors
- Verify `serviceAccountKey.json` is correctly uploaded
- Check `FIREBASE_PROJECT_ID` environment variable

### Database Connection
- For PostgreSQL, ensure connection string format is correct
- Check if database service is running

## Quick Deploy Script (Render)

```bash
# 1. Push code to GitHub
git push origin main

# 2. Create render.yaml (auto-deploy)
cat > render.yaml << 'EOF'
services:
  - type: web
    name: citemesh-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: FIREBASE_PROJECT_ID
        value: citemesh
      - key: DATABASE_URL
        value: sqlite:///./app.db
EOF

# 3. Commit and push render.yaml
git add render.yaml
git commit -m "Add Render deployment config"
git push origin main
```

## Cost Estimates

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Render | 750 hours/month | $7/month |
| Railway | $5 credit/month | $0.01/hour |
| Fly.io | 3 VMs free | $1.94/month/VM |

## Next Steps

1. Deploy backend to chosen platform
2. Update frontend with backend URL
3. Redeploy frontend: `firebase deploy --only hosting`
4. Test end-to-end authentication and API calls
5. Setup PostgreSQL for production (when ready for local database features)
