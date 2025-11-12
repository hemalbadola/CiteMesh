# DigitalOcean Deployment Fix Guide

## Problem Encountered

DigitalOcean App Platform failed to detect the Python buildpack during deployment:

```
✘ could not detect app files that match known buildpacks.
  please ensure that the files required by the desired language's buildpack exist in the repo.
```

## Solutions Implemented

### 1. Added `runtime.txt` ✅
**File**: `backend/runtime.txt`
```
python-3.11.9
```

**Why**: Explicitly tells DigitalOcean which Python version to use.

### 2. Updated `.do/app.yaml` ✅
**Changes**:
- More explicit build command with pip upgrade
- Fixed PORT environment variable usage with ${PORT:-8080}
- Added OPENALEX_BASE_URL environment variable
- Added PYTHON_VERSION build-time variable

**Before**:
```yaml
build_command: pip install -r requirements.txt
run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
```

**After**:
```yaml
build_command: pip install --upgrade pip && pip install -r requirements.txt
run_command: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
envs:
  - key: OPENALEX_BASE_URL
    value: https://api.openalex.org
    scope: RUN_TIME
  - key: PYTHON_VERSION
    value: "3.11.9"
    scope: BUILD_TIME
```

## What Happens Next

### Automatic Deployment Triggered ✅
Your push to GitHub (`ae605d1`) will automatically trigger a new deployment on DigitalOcean because:
- `deploy_on_push: true` is set in app.yaml
- GitHub webhook is configured to notify DigitalOcean

### Expected Deployment Flow

1. **DigitalOcean receives webhook** from GitHub
2. **Clones your repo** at commit `ae605d1`
3. **Detects Python buildpack** using:
   - `requirements.txt`
   - `runtime.txt`
   - Python code in `backend/` directory
4. **Builds the app**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. **Starts the server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
   ```
6. **Health check** at `/health` endpoint
7. **Deployment complete** 🎉

## Monitoring the Deployment

### Option 1: DigitalOcean Web Console
1. Go to: https://cloud.digitalocean.com/apps
2. Click on your app (likely "citemesh-backend")
3. Watch the "Deployments" tab for progress

### Option 2: Command Line (if using doctl)
```bash
doctl apps list
doctl apps get <app-id>
doctl apps logs <app-id> --type RUN
```

## Verifying Success

Once deployment completes (usually 5-10 minutes):

### 1. Check Health Endpoint
```bash
curl https://paperverse-kvw2y.ondigitalocean.app/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Test Walden API Integration
```bash
curl -X POST "https://paperverse-kvw2y.ondigitalocean.app/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "page": 1, "per_page": 3}'
```

Look for:
- Response with results
- No errors about OpenAlex API
- Fast response time (<2 seconds)

### 3. Run Full Test Suite
```bash
cd "/Users/hemalbadola/Desktop/DBMS PBL"
bash test_walden_api.sh
```

## Common Issues & Solutions

### Issue: Build Still Fails
**Solution**: Check if `requirements.txt` has all dependencies
```bash
cd backend
pip install -r requirements.txt --dry-run
```

### Issue: App Crashes on Startup
**Solution**: Check logs in DigitalOcean console
- Look for missing environment variables
- Check for import errors
- Verify database connection string

### Issue: 503 Service Unavailable
**Solution**: App might still be starting up
- Wait 2-3 minutes for full startup
- Check if instance size is sufficient (basic-xxs)
- Verify health check endpoint works

### Issue: Environment Variables Not Set
**Solution**: Add them in DigitalOcean Console
1. Go to app settings
2. Click "Environment Variables"
3. Add any missing variables (especially Firebase config)

## Files Changed in This Deployment

### New Files
- `backend/runtime.txt` - Python version specification
- `WALDEN_API_UPDATE.md` - Technical documentation
- `WALDEN_INTEGRATION_SUCCESS.md` - Success summary
- `WALDEN_BEFORE_AFTER.md` - Visual comparison
- `WALDEN_QUICK_REF.txt` - Quick reference
- `test_walden_api.sh` - Test script
- `citemesh-ui/src/config/openalex.ts` - OpenAlex configuration

### Modified Files
- `.do/app.yaml` - Updated deployment config
- `backend/app/api/search.py` - Added Walden parameters
- `citemesh-ui/src/pages/PaperDetail.tsx` - Uses new config
- `citemesh guide.txt` - Added Walden appendix

## Next Steps

1. ⏳ **Wait for deployment** (5-10 minutes)
2. ✅ **Verify health endpoint** works
3. ✅ **Test search API** with Walden parameters
4. ✅ **Check frontend** at https://citemesh.web.app
5. ✅ **Run test script** to validate integration
6. 📝 **Monitor for 24 hours** to catch any issues

## Rollback Plan (If Needed)

If something goes wrong:

```bash
cd "/Users/hemalbadola/Desktop/DBMS PBL"

# Revert to previous commit
git revert ae605d1

# Push to trigger redeployment
git push origin main
```

Or use DigitalOcean console:
1. Go to app → Deployments
2. Find previous successful deployment
3. Click "Redeploy"

## Support Resources

- **DigitalOcean Buildpacks**: https://do.co/apps-buildpacks
- **Python Buildpack**: https://github.com/heroku/heroku-buildpack-python
- **App Platform Docs**: https://docs.digitalocean.com/products/app-platform/

## Summary

✅ **Fixed**: Python buildpack detection  
✅ **Added**: runtime.txt for Python 3.11.9  
✅ **Updated**: app.yaml with better configuration  
✅ **Integrated**: Walden API (data-version=2)  
✅ **Deployed**: Frontend to Firebase  
⏳ **In Progress**: Backend to DigitalOcean  

**Status**: Waiting for automatic deployment to complete

---

**Last Updated**: November 10, 2025  
**Commit**: ae605d1  
**Next Check**: In 10 minutes (03:18 UTC)
