import { useState, type FormEvent, useEffect } from 'react';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signInWithPopup, 
  GoogleAuthProvider,
  GithubAuthProvider,
  sendSignInLinkToEmail,
  isSignInWithEmailLink,
  signInWithEmailLink
} from 'firebase/auth';
import { auth } from '../firebase';
import './Login.css';

export default function Login() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // Check if the user is completing sign-in via email link
  useEffect(() => {
    const completeSignIn = async () => {
      if (isSignInWithEmailLink(auth, window.location.href)) {
        let emailForSignIn = window.localStorage.getItem('emailForSignIn');
        
        if (!emailForSignIn) {
          // User opened the link on a different device. Ask for email again.
          emailForSignIn = window.prompt('Please provide your email for confirmation');
        }
        
        if (emailForSignIn) {
          try {
            await signInWithEmailLink(auth, emailForSignIn, window.location.href);
            window.localStorage.removeItem('emailForSignIn');
            setSuccess('Successfully signed in! Redirecting...');
            setTimeout(() => {
              window.location.href = '/dashboard';
            }, 1500);
          } catch (err: unknown) {
            if (err instanceof Error) {
              setError(err.message);
            }
          }
        }
      }
    };
    
    completeSignIn();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (isSignUp) {
        await createUserWithEmailAndPassword(auth, email, password);
      } else {
        await signInWithEmailAndPassword(auth, email, password);
      }
      window.location.href = '/dashboard';
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError('');
    setLoading(true);
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
      window.location.href = '/dashboard';
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubSignIn = async () => {
    setError('');
    setLoading(true);
    try {
      const provider = new GithubAuthProvider();
      await signInWithPopup(auth, provider);
      window.location.href = '/dashboard';
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleMagicLink = async () => {
    if (!email) {
      setError('Please enter your email first');
      return;
    }
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      const actionCodeSettings = {
        url: window.location.origin + '/login',
        handleCodeInApp: true,
      };
      await sendSignInLinkToEmail(auth, email, actionCodeSettings);
      window.localStorage.setItem('emailForSignIn', email);
      setSuccess('✨ Magic link sent! Check your email.');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Animated background particles */}
      <div className="login-background">
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
      </div>

      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">
            <span className="title-paper">Paper</span>
            <span className="title-verse">Verse</span>
          </h1>
          <p className="login-subtitle">
            {isSignUp ? 'Create your research account' : 'Welcome back, researcher'}
          </p>
        </div>

        {/* Social Auth Buttons */}
        <div className="social-auth-grid">
          <button onClick={handleGoogleSignIn} className="social-button google" disabled={loading}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M19.6 10.227c0-.709-.064-1.39-.182-2.045H10v3.868h5.382a4.6 4.6 0 01-1.996 3.018v2.51h3.232c1.891-1.742 2.982-4.305 2.982-7.35z"
                fill="#4285F4"
              />
              <path
                d="M10 20c2.7 0 4.964-.895 6.618-2.423l-3.232-2.509c-.895.6-2.04.955-3.386.955-2.605 0-4.81-1.76-5.595-4.123H1.064v2.59A9.996 9.996 0 0010 20z"
                fill="#34A853"
              />
              <path
                d="M4.405 11.9c-.2-.6-.314-1.24-.314-1.9 0-.66.114-1.3.314-1.9V5.51H1.064A9.996 9.996 0 000 10c0 1.614.386 3.14 1.064 4.49l3.34-2.59z"
                fill="#FBBC05"
              />
              <path
                d="M10 3.977c1.468 0 2.786.505 3.823 1.496l2.868-2.868C14.959.99 12.695 0 10 0 6.09 0 2.71 2.24 1.064 5.51l3.34 2.59C5.192 5.736 7.396 3.977 10 3.977z"
                fill="#EA4335"
              />
            </svg>
            Google
          </button>

          <button onClick={handleGitHubSignIn} className="social-button github" disabled={loading}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" clipRule="evenodd" d="M10 0C4.477 0 0 4.477 0 10c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0110 4.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C17.137 18.165 20 14.418 20 10c0-5.523-4.477-10-10-10z" />
            </svg>
            GitHub
          </button>
        </div>

        <div className="divider">
          <span>or continue with email</span>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path
                  d="M8 1.5C4.41 1.5 1.5 4.41 1.5 8C1.5 11.59 4.41 14.5 8 14.5C11.59 14.5 14.5 11.59 14.5 8C14.5 4.41 11.59 1.5 8 1.5ZM8.75 11.25H7.25V9.75H8.75V11.25ZM8.75 8.25H7.25V4.75H8.75V8.25Z"
                  fill="currentColor"
                />
              </svg>
              {error}
            </div>
          )}

          {success && (
            <div className="success-message">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path
                  d="M8 1.5C4.41 1.5 1.5 4.41 1.5 8C1.5 11.59 4.41 14.5 8 14.5C11.59 14.5 14.5 11.59 14.5 8C14.5 4.41 11.59 1.5 8 1.5ZM6.75 11.25L3.5 8L4.56 6.94L6.75 9.13L11.44 4.44L12.5 5.5L6.75 11.25Z"
                  fill="currentColor"
                />
              </svg>
              {success}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.email@university.edu"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              disabled={loading}
            />
          </div>

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? (
              <span className="loading-spinner"></span>
            ) : (
              isSignUp ? 'Create Account' : 'Sign In'
            )}
          </button>

          {!isSignUp && (
            <button 
              type="button" 
              onClick={handleMagicLink} 
              className="magic-link-button"
              disabled={loading}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ marginRight: '8px' }}>
                <path
                  d="M13 7h-1V5c0-2.21-1.79-4-4-4S4 2.79 4 5v2H3c-.55 0-1 .45-1 1v6c0 .55.45 1 1 1h10c.55 0 1-.45 1-1V8c0-.55-.45-1-1-1zM8 12c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm2.5-5h-5V5c0-1.38 1.12-2.5 2.5-2.5S10.5 3.62 10.5 5v2z"
                  fill="currentColor"
                />
              </svg>
              Send Magic Link Instead
            </button>
          )}
        </form>

        <div className="login-footer">
          <p>
            {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              type="button"
              onClick={() => setIsSignUp(!isSignUp)}
              className="toggle-mode"
              disabled={loading}
            >
              {isSignUp ? 'Sign In' : 'Sign Up'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
