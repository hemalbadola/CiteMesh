#!/bin/bash

# CiteMesh - DigitalOcean CLI Deployment Script

echo "🚀 CiteMesh - DigitalOcean CLI Deploy"
echo "======================================"
echo ""

# Check if doctl is authenticated
if ! doctl auth list &> /dev/null; then
    echo "❌ You need to authenticate with DigitalOcean first"
    echo ""
    echo "Run: doctl auth init"
    echo "Then run this script again"
    exit 1
fi

echo "✅ doctl authenticated"
echo ""

# Get base64 value
if [ ! -f "backend/serviceAccountKey.json" ]; then
    echo "❌ Error: backend/serviceAccountKey.json not found!"
    exit 1
fi

echo "📦 Reading Firebase credentials..."
BASE64_VALUE=$(cat backend/serviceAccountKey.json | base64 | tr -d '\n')

echo "✅ Credentials loaded"
echo ""

# Create app spec with environment variable
cat > /tmp/citemesh-do-spec.yaml << EOF
name: citemesh-backend
region: nyc
services:
  - name: api
    source_dir: backend
    github:
      repo: hemalbadola/CiteMesh
      branch: main
      deploy_on_push: true
    environment_slug: python
    build_command: pip install -r requirements.txt
    run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
    http_port: 8080
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
      - key: FIREBASE_PROJECT_ID
        value: citemesh
      - key: DATABASE_URL
        value: sqlite:///./app.db
      - key: PORT
        value: "8080"
      - key: FIREBASE_SERVICE_ACCOUNT_BASE64
        value: ${BASE64_VALUE}
    health_check:
      http_path: /health
EOF

echo "📝 App spec created"
echo ""
echo "🚀 Deploying to DigitalOcean..."
echo ""

# Create the app
doctl apps create --spec /tmp/citemesh-do-spec.yaml

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment initiated!"
    echo ""
    echo "📊 Check status:"
    echo "   doctl apps list"
    echo ""
    echo "📝 View logs:"
    echo "   doctl apps logs <app-id> --follow"
    echo ""
    echo "🌐 Your app will be available at:"
    echo "   https://citemesh-backend-xxxxx.ondigitalocean.app"
    echo ""
else
    echo ""
    echo "❌ Deployment failed"
    echo "Check the error message above"
fi

# Cleanup
rm -f /tmp/citemesh-do-spec.yaml
