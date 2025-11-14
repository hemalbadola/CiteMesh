import { initializeApp } from 'firebase/app';
import { getAuth, setPersistence, browserLocalPersistence } from 'firebase/auth';

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: 'AIzaSyD_siEWuKuU04fY69ImUxbGwbN9txxKKj8',
  authDomain: 'citemesh.firebaseapp.com',
  projectId: 'citemesh',
  storageBucket: 'citemesh.firebasestorage.app',
  messagingSenderId: '63495277735',
  appId: '1:63495277735:web:f1b48fe795294e3ff89f82',
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
