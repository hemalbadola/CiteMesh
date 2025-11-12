import { initializeApp } from 'firebase/app';
import { getAuth, setPersistence, browserLocalPersistence } from 'firebase/auth';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyDXh5vH_QqK9fJ6LxZ2rVNkY8tQ3wE5mFo",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "citemesh.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "citemesh",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "citemesh.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "246567490878",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:246567490878:web:a0c9b8d7e6f5g4h3i2j1k0"
};

// Initialize Firebase
let app;
try {
  app = initializeApp(firebaseConfig);
  console.log('Firebase initialized successfully');
} catch (error) {
  console.error('Firebase initialization error:', error);
  // Re-throw to prevent app from running with broken auth
  throw error;
}

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Set persistence to LOCAL so users stay logged in even after closing the browser
setPersistence(auth, browserLocalPersistence).catch((error) => {
  console.error('Error setting auth persistence:', error);
});

export default app;
