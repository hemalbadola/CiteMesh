# CiteMesh Login Setup

## Firebase Configuration

### 1. Get Your Firebase Config

1. Go to [Firebase Console](https://console.firebase.google.com/project/citemesh/settings/general/web)
2. Under "Your apps" section, click on your web app (or create one if you haven't)
3. Copy the Firebase configuration object

### 2. Create Environment File

Create a `.env` file in the `citemesh-ui` directory:

```bash
cd citemesh-ui
cp .env.example .env
```

### 3. Add Your Firebase Credentials

Edit `.env` and replace the placeholder values with your actual Firebase config:

```env
VITE_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXX
VITE_FIREBASE_AUTH_DOMAIN=citemesh.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=citemesh
VITE_FIREBASE_STORAGE_BUCKET=citemesh.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:xxxxxxxxxxxxx
```

### 4. Enable Authentication Methods

1. Go to [Firebase Console > Authentication](https://console.firebase.google.com/project/citemesh/authentication/providers)
2. Click on **"Get started"** if you haven't enabled Authentication
3. Enable **Email/Password** sign-in method:
   - Click on "Email/Password"
   - Toggle "Enable" for both "Email/Password" and **"Email link (passwordless sign-in)"**
   - Click "Save"
4. Enable **Google** sign-in method:
   - Click on "Google"
   - Toggle "Enable"
   - Add your support email
   - Click "Save"

### 5. Configure Authorized Domains

For email link authentication to work, you need to authorize your domains:

1. Go to [Firebase Console > Authentication > Settings](https://console.firebase.google.com/project/citemesh/authentication/settings)
2. Scroll to **"Authorized domains"**
3. Add your domains:
   - `citemesh.web.app` (already added)
   - `citemesh.firebaseapp.com` (already added)
   - Add `localhost` if testing locally

### 6. Test the Login

1. Visit https://citemesh.web.app/login
2. Try signing up with email/password
3. Try signing in with Google
4. Try **passwordless magic link** (check the box and click "Send Magic Link")

## Login Page Features

✨ **Beautiful animated UI** with floating particles
🔐 **Email/Password authentication**
🪄 **Passwordless magic link** (no password needed!)
🌐 **Google OAuth sign-in**
📱 **Fully responsive** design
⚡ **Loading states** and error handling
🎨 **Matches your PaperVerse** theme with purple gradients
✉️ **Email verification** built-in

## Routes

- `/` - Main landing page
- `/login` - Login/Sign up page

## Next Steps

After a user logs in, they'll be redirected to the main page. You can:

1. Add user state management (detect if user is logged in)
2. Show user profile/avatar in the header
3. Add protected routes that require authentication
4. Create a user dashboard

## Security Note

⚠️ **Never commit your `.env` file!** It's already in `.gitignore`.
