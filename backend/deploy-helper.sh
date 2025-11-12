#!/bin/bash

# CiteMesh - DigitalOcean Quick Deploy Script
# This script prepares your Firebase credentials for DigitalOcean deployment

echo "🚀 CiteMesh - DigitalOcean Deployment Helper"
echo "============================================"
echo ""

# Check if serviceAccountKey.json exists
if [ ! -f "serviceAccountKey.json" ]; then
    echo "❌ Error: serviceAccountKey.json not found!"
    echo "   Make sure you're in the /backend directory"
    exit 1
fi

echo "✅ Found serviceAccountKey.json"
echo ""

# Generate base64 encoding
echo "📦 Generating base64 encoding..."
BASE64_VALUE=$(cat serviceAccountKey.json | base64)

echo "✅ Base64 encoding generated!"
echo ""
echo "============================================"
echo "🔑 COPY THIS VALUE FOR DIGITALOCEAN"
echo "============================================"
echo ""
echo "$BASE64_VALUE"
echo ""
echo "============================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Go to https://cloud.digitalocean.com/apps"
echo "2. Click 'Create App'"
echo "3. Connect GitHub repository: hemalbadola/CiteMesh"
echo "4. DigitalOcean will auto-detect .do/app.yaml"
echo "5. Add Environment Variables:"
echo "   - Name: FIREBASE_SERVICE_ACCOUNT_BASE64"
echo "   - Value: [paste the base64 value above]"
echo ""
echo "6. Add these environment variables too:"
echo "   - FIREBASE_PROJECT_ID = citemesh"
echo "   - DATABASE_URL = sqlite:///./app.db"
echo ""
echo "7. Click 'Create Resources' and wait ~5 minutes"
echo ""
echo "8. Your backend will be live at:"
echo "   https://citemesh-backend-xxxxx.ondigitalocean.app"
echo ""
echo "✨ Done! Check DIGITALOCEAN_DEPLOY.md for full guide."
echo ""
