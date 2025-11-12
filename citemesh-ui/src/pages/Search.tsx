import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { onAuthStateChanged, type User } from 'firebase/auth';
import { auth } from '../firebase';
import Sidebar from '../components/Sidebar.tsx';
import PaperVerseConsole from '../components/PaperVerseConsole.tsx';
import './Search.css';

export default function Search() {
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Set up auth state listener - Firebase will automatically restore session
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
      } else {
        // Only redirect if no persisted session found
        navigate('/login');
      }
    });

    return () => unsubscribe();
  }, [navigate]);

  if (!user) return null;

  return (
    <div className="dashboard-wrapper">
      {/* Animated Background */}
      <div className="dashboard-bg">
        <div className="bg-gradient"></div>
        <div className="bg-grid"></div>
      </div>

      <Sidebar user={user} />

      {/* Main Content */}
      <main className="main-content">
        <header className="main-header">
          <div>
            <h2 className="welcome-text">Search Research Papers</h2>
            <p className="subtitle-text">Explore 269M+ papers with AI-powered search</p>
          </div>
        </header>

        <div className="content-grid">
          <section className="full-width-section">
            <PaperVerseConsole />
          </section>
        </div>
      </main>
    </div>
  );
}
