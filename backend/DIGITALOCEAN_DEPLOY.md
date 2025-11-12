# DigitalOcean Deployment Guide - CiteMesh Backend

## 🚀 Option 1: App Platform (Recommended)

### Why App Platform?
- ✅ Fully managed (zero DevOps)
- ✅ Auto-deploy from GitHub
- ✅ SSL certificates included
- ✅ Easy scaling
- ✅ $5/month for basic tier
- ✅ Perfect for FastAPI/Python apps

### Step-by-Step Deployment

#### 1. Prepare Your App

The `.do/app.yaml` file is already configured! Just need to add Firebase credentials.

#### 2. Add Firebase Service Account as Environment Variable

Since we can't commit `serviceAccountKey.json`, we'll use environment variables:

```bash
# In your local terminal, convert to base64
cd /Users/hemalbadola/Desktop/DBMS\ PBL/backend
cat serviceAccountKey.json | base64 > serviceAccountKey.base64.txt
```

Copy the contents of `serviceAccountKey.base64.txt` - you'll need it in step 5.

#### 3. Update Firebase Auth to Read from Environment

Create a new file or update `backend/app/core/firebase_auth.py`:

```python
# Add this at the top of firebase_auth.py
import os
import base64
import json

# Initialize Firebase Admin
def initialize_firebase():
    # Check if running on DigitalOcean (or any cloud)
    if os.getenv('FIREBASE_SERVICE_ACCOUNT_BASE64'):
        # Decode base64 service account
        service_account_json = base64.b64decode(
            os.getenv('FIREBASE_SERVICE_ACCOUNT_BASE64')
        ).decode('utf-8')
        service_account = json.loads(service_account_json)
        
        cred = credentials.Certificate(service_account)
    else:
        # Local development - use file
        cred = credentials.Certificate('serviceAccountKey.json')
    
    firebase_admin.initialize_app(cred)
```

#### 4. Deploy to DigitalOcean

**Method A: Via Dashboard (Easiest)**

1. Go to https://cloud.digitalocean.com/apps
2. Click **"Create App"**
3. Choose **"GitHub"** as source
4. Select repository: `hemalbadola/CiteMesh`
5. DigitalOcean will auto-detect the `.do/app.yaml` configuration
6. Review the configuration:
   - ✅ Source Directory: `/backend`
   - ✅ Build Command: `pip install -r requirements.txt`
   - ✅ Run Command: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
7. Click **"Next"**

**Method B: Via CLI**

```bash
# Install doctl (DigitalOcean CLI)
brew install doctl

# Authenticate
doctl auth init

# Create app from spec
doctl apps create --spec .do/app.yaml
```

#### 5. Add Environment Variables

In the DigitalOcean App Platform dashboard:

1. Go to your app → **Settings** → **App-Level Environment Variables**
2. Add these variables:

```
FIREBASE_PROJECT_ID = citemesh
DATABASE_URL = sqlite:///./app.db
FIREBASE_SERVICE_ACCOUNT_BASE64 = <paste the base64 content from step 2>
```

3. Click **"Save"**
4. App will automatically redeploy

#### 6. Get Your Backend URL

After deployment completes (~5 minutes):
- Your backend will be live at: `https://citemesh-backend-xxxxx.ondigitalocean.app`
- Copy this URL!

#### 7. Update Frontend

Update `citemesh-ui/src/components/PaperVerseConsole.tsx`:

```typescript
const backendBaseUrl = import.meta.env.PROD
  ? 'https://citemesh-backend-xxxxx.ondigitalocean.app'  // Your DO URL
  : 'http://localhost:8000'
```

#### 8. Update CORS

Update `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://citemesh.web.app",
        "https://citemesh.firebaseapp.com",
        "https://citemesh-backend-xxxxx.ondigitalocean.app",  # Add your DO URL
    ],
    # ...
)
```

#### 9. Commit and Push

```bash
cd /Users/hemalbadola/Desktop/DBMS\ PBL
git add .do/app.yaml backend/app/core/firebase_auth.py backend/app/main.py citemesh-ui/src/components/PaperVerseConsole.tsx
git commit -m "feat: Configure DigitalOcean App Platform deployment"
git push origin main
```

DigitalOcean will auto-deploy on push! 🎉

#### 10. Redeploy Frontend

```bash
cd citemesh-ui
npm run build
firebase deploy --only hosting
```

---

## 🖥️ Option 2: Droplet (More Control, More Work)

### When to use Droplets?
- Need full server control
- Running multiple services
- Custom server configuration
- PostgreSQL + pgvector on same machine

### Quick Droplet Setup

#### 1. Create Droplet

1. Go to https://cloud.digitalocean.com/droplets
2. Click **"Create Droplet"**
3. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: Basic - $6/month (1GB RAM)
   - **Region**: Choose closest to users
4. Add SSH key
5. Create Droplet

#### 2. SSH into Droplet

```bash
ssh root@your_droplet_ip
```

#### 3. Setup Server

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.11
apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx
apt install nginx -y

# Install Supervisor (process manager)
apt install supervisor -y

# Install PostgreSQL (if needed)
apt install postgresql postgresql-contrib -y
```

#### 4. Deploy Application

```bash
# Clone repository
cd /opt
git clone https://github.com/hemalbadola/CiteMesh.git
cd CiteMesh/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add Firebase credentials
nano serviceAccountKey.json  # Paste your credentials
```

#### 5. Configure Supervisor

Create `/etc/supervisor/conf.d/citemesh.conf`:

```ini
[program:citemesh]
directory=/opt/CiteMesh/backend
command=/opt/CiteMesh/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/citemesh.log
environment=FIREBASE_PROJECT_ID="citemesh",DATABASE_URL="sqlite:///./app.db"
```

```bash
# Reload supervisor
supervisorctl reread
supervisorctl update
supervisorctl start citemesh
```

#### 6. Configure Nginx

Create `/etc/nginx/sites-available/citemesh`:

```nginx
server {
    listen 80;
    server_name your_droplet_ip;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/citemesh /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 7. Setup SSL (Optional but Recommended)

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get certificate (requires domain name)
certbot --nginx -d api.yourdomain.com
```

---

## 💰 Cost Comparison

| Service | Monthly Cost | Management | Best For |
|---------|--------------|------------|----------|
| **App Platform** | $5 | Fully managed | Quick deployment, auto-scaling |
| **Droplet Basic** | $6 | Self-managed | Full control, multiple services |
| **Droplet + DB** | $12+ | Self-managed | Production with PostgreSQL |

---

## 🔍 Monitoring & Logs

### App Platform
- Dashboard: https://cloud.digitalocean.com/apps
- Live logs: Click your app → **Runtime Logs**
- Metrics: CPU, Memory, Request count

### Droplet
```bash
# Application logs
tail -f /var/log/citemesh.log

# Supervisor status
supervisorctl status

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🚨 Troubleshooting

### App Platform Issues

**Build fails:**
```bash
# Check build logs in DO dashboard
# Verify requirements.txt has all dependencies
```

**Health check fails:**
```bash
# Verify /health endpoint works locally
curl http://localhost:8000/health
```

**Firebase auth errors:**
```bash
# Check FIREBASE_SERVICE_ACCOUNT_BASE64 is set correctly
# Verify base64 encoding is valid
```

### Droplet Issues

**Service won't start:**
```bash
supervisorctl status citemesh
tail -f /var/log/citemesh.log
```

**Port already in use:**
```bash
lsof -i :8000
kill -9 <PID>
supervisorctl restart citemesh
```

---

## 🎯 Recommended: App Platform

For CiteMesh, I strongly recommend **App Platform** because:
1. ✅ Zero DevOps overhead
2. ✅ Auto-deploys from GitHub
3. ✅ Built-in monitoring
4. ✅ Automatic SSL
5. ✅ Easy scaling when needed

Once deployed, you'll have:
- Frontend: `https://citemesh.web.app`
- Backend: `https://citemesh-backend-xxxxx.ondigitalocean.app`

Both fully managed and production-ready! 🚀
