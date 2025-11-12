# Firebase Service Account Setup

## How to Get Your Service Account Key:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **citemesh**
3. Click the gear icon ⚙️ next to "Project Overview" → **Project settings**
4. Go to the **Service accounts** tab
5. Click **Generate new private key**
6. Save the downloaded JSON file as `serviceAccountKey.json` in this directory

## File Location:
Place the file at: `/Users/hemalbadola/Desktop/DBMS PBL/backend/serviceAccountKey.json`

## Security Note:
- ⚠️ Never commit this file to Git (already in .gitignore)
- Keep it secure - it has admin access to your Firebase project
- For production, use environment variables or secret management services

## Alternative: Environment Variable
You can also set the path via environment variable:
```bash
export FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/serviceAccountKey.json
```
