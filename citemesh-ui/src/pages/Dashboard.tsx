import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { onAuthStateChanged, type User } from 'firebase/auth';
import { auth } from '../firebase';
import Sidebar from '../components/Sidebar';
import PaperVerseConsole from '../components/PaperVerseConsole';
import api, { type Activity, type PaperStats, type CollectionStats, type CitationStats } from '../services/api';
import './Dashboard.css';

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();
  
  // API Data State
  const [paperStats, setPaperStats] = useState<PaperStats | null>(null);
  const [collectionStats, setCollectionStats] = useState<CollectionStats | null>(null);
  const [citationStats, setCitationStats] = useState<CitationStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Set up auth state listener with loading state
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
      } else {
        // Only redirect to login if not loading (auth state is determined)
        navigate('/login');
      }
    });

    return () => unsubscribe();
  }, [navigate]);

  // Fetch dashboard data
  useEffect(() => {
    if (!user) return;

    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all stats in parallel
        const [papers, collections, citations, activity] = await Promise.allSettled([
          api.papers.getStats(),
          api.collections.getStats(),
          api.citations.getStats(),
          api.activity.getRecent(1, 10),
        ]);

        if (papers.status === 'fulfilled') {
          setPaperStats(papers.value);
        }
        if (collections.status === 'fulfilled') {
          setCollectionStats(collections.value);
        }
        if (citations.status === 'fulfilled') {
          setCitationStats(citations.value);
        }
        if (activity.status === 'fulfilled') {
          setRecentActivity(activity.value);
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [user]);

  if (!user) return null;

  const displayName = user.displayName || user.email?.split('@')[0] || 'Researcher';

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
            <h2 className="welcome-text">Welcome back, <span className="highlight">{displayName}</span></h2>
            <p className="subtitle-text">Continue exploring the research universe</p>
          </div>
          
          <button 
            className="action-btn"
            onClick={() => navigate('/scholar-search')}
          >
            <svg viewBox="0 0 24 24" fill="none">
              <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2"/>
              <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <span>Advanced Search</span>
          </button>
        </header>
        
        {/* Quick Search Bar */}
        <div className="quick-search">
          <form onSubmit={(e) => {
            e.preventDefault();
            const formData = new FormData(e.currentTarget);
            const query = formData.get('search') as string;
            if (query.trim()) {
              navigate(`/scholar-search?q=${encodeURIComponent(query)}`);
            }
          }}>
            <div className="search-box">
              <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2"/>
                <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <input
                type="text"
                name="search"
                placeholder="Search for papers, authors, topics..."
                className="search-input"
              />
              <button type="submit" className="search-btn">Search</button>
            </div>
          </form>
        </div>

        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '12px',
            padding: '1rem 1.5rem',
            marginBottom: '1.5rem',
            color: '#fca5a5'
          }}>
            <strong>Error loading dashboard data:</strong> {error}
          </div>
        )}

        <div className="content-grid">
          {/* Quick Stats */}
          <section className="quick-stats">
            <div className="stat-item">
              <div className="stat-icon-wrapper purple">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M19 21L12 16L5 21V5C5 4.46957 5.21071 3.96086 5.58579 3.58579C5.96086 3.21071 6.46957 3 7 3H17C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5V21Z" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </div>
              <div className="stat-info">
                <p className="stat-label">Total Papers</p>
                <p className="stat-value">
                  {loading ? '...' : paperStats?.total_papers ?? 0}
                </p>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon-wrapper blue">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M10 13C10.4295 13.5741 10.9774 14.0492 11.6066 14.3929C12.2357 14.7367 12.9315 14.9411 13.6467 14.9923C14.3618 15.0435 15.0796 14.9404 15.7513 14.6898C16.4231 14.4392 17.0331 14.0471 17.54 13.54L20.54 10.54C21.4508 9.59699 21.9548 8.33397 21.9434 7.02299C21.932 5.71201 21.4061 4.45794 20.4791 3.53091C19.5521 2.60389 18.298 2.07802 16.987 2.06663C15.676 2.05523 14.413 2.55921 13.47 3.47L11.75 5.18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M14 11C13.5705 10.4259 13.0226 9.95084 12.3934 9.60707C11.7642 9.26331 11.0685 9.05886 10.3533 9.00765C9.63819 8.95643 8.92037 9.05961 8.24861 9.3102C7.57685 9.56079 6.96689 9.95289 6.45996 10.46L3.45996 13.46C2.54917 14.403 2.04519 15.666 2.05659 16.977C2.06798 18.288 2.59385 19.5421 3.52087 20.4691C4.4479 21.3961 5.70197 21.922 7.01295 21.9334C8.32393 21.9448 9.58694 21.4408 10.53 20.53L12.24 18.82" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-info">
                <p className="stat-label">Citations</p>
                <p className="stat-value">
                  {loading ? '...' : citationStats?.total_citations ?? 0}
                </p>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon-wrapper green">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-info">
                <p className="stat-label">Collections</p>
                <p className="stat-value">
                  {loading ? '...' : collectionStats?.total_collections ?? 0}
                </p>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon-wrapper orange">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M9.663 17H4.5C3 17 3 16 3 15C3 11.5 5 10.5 6 10C5 9.66667 3 8.5 3 6C3 4 4.5 2 6.5 2C8.5 2 10 3.5 10 5C10 6.5 9 7.66667 8 8C9 8.5 11 9.5 11 12.5V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M14.337 17H19.5C21 17 21 16 21 15C21 11.5 19 10.5 18 10C19 9.66667 21 8.5 21 6C21 4 19.5 2 17.5 2C15.5 2 14 3.5 14 5C14 6.5 15 7.66667 16 8C15 8.5 13 9.5 13 12.5V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-info">
                <p className="stat-label">Papers in Collections</p>
                <p className="stat-value">
                  {loading ? '...' : collectionStats?.total_papers_in_collections ?? 0}
                </p>
              </div>
            </div>
          </section>

          {/* PaperVerse Console */}
          <section className="paperverse-console-section">
            <PaperVerseConsole />
          </section>

          {/* Recent Activity */}
          <section className="activity-card">
            <div className="card-header">
              <h3>Recent Activity</h3>
              <button className="view-all">View all</button>
            </div>
            {loading ? (
              <div className="activity-empty">
                <p>Loading activity...</p>
              </div>
            ) : recentActivity.length > 0 ? (
              <div className="activity-list">
                {recentActivity.slice(0, 5).map((activity) => (
                  <div key={activity.id} className="activity-item">
                    <div className="activity-icon">
                      {activity.activity_type === 'paper_added' && '📄'}
                      {activity.activity_type === 'collection_created' && '📚'}
                      {activity.activity_type === 'citation_added' && '🔗'}
                      {activity.activity_type === 'search_performed' && '🔍'}
                      {!['paper_added', 'collection_created', 'citation_added', 'search_performed'].includes(activity.activity_type) && '✨'}
                    </div>
                    <div className="activity-content">
                      <p className="activity-description">{activity.description}</p>
                      <p className="activity-time">
                        {new Date(activity.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="activity-empty">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M9 11L12 14L22 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M21 12V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <p>No recent activity</p>
                <span>Start by exploring papers or creating a new research project</span>
              </div>
            )}
          </section>

          {/* Recommended Papers */}
          <section className="recommended-card">
            <div className="card-header">
              <h3>Recommended for You</h3>
              <button className="refresh-btn">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M1 4V10H7M23 20V14H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M20.49 9C19.9828 7.56678 19.1209 6.28536 17.9845 5.27541C16.8482 4.26546 15.4745 3.5596 13.9917 3.22422C12.5089 2.88885 10.9652 2.93434 9.50481 3.35677C8.04437 3.77921 6.71475 4.56471 5.64 5.64L1 10M23 14L18.36 18.36C17.2853 19.4353 15.9556 20.2208 14.4952 20.6432C13.0348 21.0657 11.4911 21.1111 10.0083 20.7758C8.52547 20.4404 7.1518 19.7346 6.01547 18.7246C4.87913 17.7146 4.01717 16.4332 3.51 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
            <div className="activity-empty">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <p>No recommendations yet</p>
              <span>Save papers to get personalized recommendations</span>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
