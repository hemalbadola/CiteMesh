import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { onAuthStateChanged, signOut, type User } from 'firebase/auth';
import { auth } from '../firebase';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => Promise<void>;
}

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  logout: async () => {},
});

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    // Fallback: Stop loading after 5 seconds even if auth doesn't respond
    const timeout = setTimeout(() => {
      if (loading) {
        console.warn('Auth loading timeout - setting loading to false');
        setLoading(false);
      }
    }, 5000);

    return () => {
      unsubscribe();
      clearTimeout(timeout);
    };
  }, [loading]);

  const logout = async () => {
    await signOut(auth);
  };

  const value = {
    user,
    loading,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
