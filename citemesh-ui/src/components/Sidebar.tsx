import { signOut, type User } from 'firebase/auth';
import { useNavigate, useLocation } from 'react-router-dom';
import { auth } from '../firebase';

interface SidebarProps {
  user: User;
}

export default function Sidebar({ user }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleSignOut = async () => {
    try {
      await signOut(auth);
      navigate('/login');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const isActive = (path: string) => location.pathname === path;

  const displayName = user.displayName || user.email?.split('@')[0] || 'Researcher';

  return (
    <aside className="sidebar">
      <div className="sidebar-content">
        <div className="logo-section">
          <h1 className="logo">
            <span className="logo-paper">Paper</span>
            <span className="logo-verse">Verse</span>
          </h1>
          <div className="logo-underline"></div>
        </div>

        <nav className="nav">
          <a href="/dashboard" className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}>
            <div className="nav-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>
            <span>Home</span>
            {isActive('/dashboard') && <div className="nav-indicator"></div>}
          </a>

          <a href="/scholar-search" className={`nav-link ${isActive('/scholar-search') ? 'active' : ''}`}>
            <div className="nav-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2"/>
                <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <span>Search</span>
            {isActive('/scholar-search') && <div className="nav-indicator"></div>}
          </a>

          <a href="/library" className={`nav-link ${isActive('/library') ? 'active' : ''}`}>
            <div className="nav-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M19 21L12 16L5 21V5C5 4.46957 5.21071 3.96086 5.58579 3.58579C5.96086 3.21071 6.46957 3 7 3H17C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5V21Z" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>
            <span>Library</span>
            {isActive('/library') && <div className="nav-indicator"></div>}
          </a>

          <a href="/network" className={`nav-link ${isActive('/network') ? 'active' : ''}`}>
            <div className="nav-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <circle cx="18" cy="5" r="3" stroke="currentColor" strokeWidth="2"/>
                <circle cx="6" cy="12" r="3" stroke="currentColor" strokeWidth="2"/>
                <circle cx="18" cy="19" r="3" stroke="currentColor" strokeWidth="2"/>
                <path d="M8.59 13.51L15.42 17.49M15.41 6.51L8.59 10.49" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>
            <span>Network</span>
            {isActive('/network') && <div className="nav-indicator"></div>}
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="user-card">
            <img 
              src={user.photoURL || `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=9333ea&color=fff&size=128`}
              alt="User"
              className="user-avatar"
            />
            <div className="user-details">
              <p className="user-name">{displayName}</p>
              <p className="user-email">{user.email}</p>
            </div>
          </div>
          
          <button onClick={handleSignOut} className="logout-btn">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9M16 17L21 12M21 12L16 7M21 12H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>Logout</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
