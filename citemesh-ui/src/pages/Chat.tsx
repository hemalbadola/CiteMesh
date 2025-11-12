import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from '../components/Sidebar';
import './Chat.css';

interface ChatSession {
  id: number;
  user_id: string;
  title: string;
  model: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

interface ChatMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

const Chat = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [selectedModel, setSelectedModel] = useState<'gemini' | 'anthropic'>('gemini');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    loadSessions();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, navigate]);

  const loadSessions = async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      const token = await user.getIdToken();
      const response = await fetch('https://paperverse-kvw2y.ondigitalocean.app/api/chat/sessions?page=1&page_size=50', {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (!response.ok) throw new Error('Failed to load sessions');

      const sessionList = await response.json();
      setSessions(sessionList);
      if (sessionList.length > 0) {
        selectSession(sessionList[0]);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectSession = async (session: ChatSession) => {
    if (!user) return;
    
    setCurrentSession(session);
    
    try {
      const token = await user.getIdToken();
      const response = await fetch(`https://paperverse-kvw2y.ondigitalocean.app/api/chat/sessions/${session.id}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (!response.ok) throw new Error('Failed to load messages');

      const messageList = await response.json();
      setMessages(messageList);
    } catch (error) {
      console.error('Error loading messages:', error);
      setMessages([]);
    }
  };

  const createNewSession = async () => {
    if (!user) return;
    
    try {
      const token = await user.getIdToken();
      const response = await fetch('https://paperverse-kvw2y.ondigitalocean.app/api/chat/sessions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'New Chat',
          model: selectedModel,
        }),
      });

      if (!response.ok) throw new Error('Failed to create session');

      const newSession = await response.json();
      setSessions([newSession, ...sessions]);
      selectSession(newSession);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || !currentSession || isSending || !user) return;

    const messageContent = inputValue;
    setInputValue('');
    setIsSending(true);

    // Add user message optimistically
    const userMessage: ChatMessage = {
      id: Date.now(),
      session_id: currentSession.id,
      role: 'user',
      content: messageContent,
      created_at: new Date().toISOString(),
    };
    setMessages([...messages, userMessage]);

    try {
      const token = await user.getIdToken();
      const response = await fetch(`https://paperverse-kvw2y.ondigitalocean.app/api/chat/sessions/${currentSession.id}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: messageContent,
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const assistantMessage = await response.json();
      
      // Add assistant response
      setMessages((prev) => [...prev, assistantMessage]);
      
      // Scroll to bottom
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message');
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (loading || !user) {
    return (
      <div style={{ display: 'flex', height: '100vh', background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)' }}>
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'rgba(255, 255, 255, 0.7)' }}>
          <div className="loading-spinner" style={{ width: '40px', height: '40px', border: '3px solid rgba(147, 51, 234, 0.1)', borderTopColor: '#9333ea', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }}></div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-page">
      <Sidebar user={user} />
      
      <div className="chat-sidebar">
        <div className="chat-sidebar-header">
          <h2>Conversations</h2>
          <button onClick={createNewSession} className="new-chat-btn" title="New Chat">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>
        
        <div className="model-selector">
          <label>AI Model:</label>
          <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value as 'gemini' | 'anthropic')}>
            <option value="gemini">Gemini</option>
            <option value="anthropic">Anthropic (A4F)</option>
          </select>
        </div>
        
        <div className="sessions-list">
          {sessions.length === 0 ? (
            <div className="no-sessions">
              <p>No conversations yet</p>
              <button onClick={createNewSession} className="create-first-btn">
                Start a conversation
              </button>
            </div>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
                onClick={() => selectSession(session)}
              >
                <div className="session-title">{session.title}</div>
                <div className="session-meta">
                  {session.model} • {session.message_count || 0} messages
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="chat-main">
        {currentSession ? (
          <>
            <div className="chat-header">
              <h1>{currentSession.title}</h1>
              <span className="model-badge">{currentSession.model}</span>
            </div>

            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="chat-empty">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <h3>Start a conversation</h3>
                  <p>Ask questions about papers, citations, or anything else.</p>
                </div>
              ) : (
                <>
                  {messages.map((message) => (
                    <div key={message.id} className={`message ${message.role}`}>
                      <div className="message-avatar">
                        {message.role === 'user' ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/>
                          </svg>
                        ) : (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                          </svg>
                        )}
                      </div>
                      <div className="message-content">
                        <div className="message-text">{message.content}</div>
                        <div className="message-time">
                          {new Date(message.created_at).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            <div className="chat-input-container">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question..."
                className="chat-input"
                rows={1}
                disabled={isSending}
              />
              <button
                onClick={sendMessage}
                disabled={!inputValue.trim() || isSending}
                className="send-btn"
              >
                {isSending ? (
                  <div className="sending-spinner" />
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </button>
            </div>
          </>
        ) : (
          <div className="no-session-selected">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <h3>No conversation selected</h3>
            <p>Select a conversation or create a new one to get started.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
