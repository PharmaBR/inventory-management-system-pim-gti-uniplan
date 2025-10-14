import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { authAPI } from '../services/api';
import { useToast } from '../components/ui/Toast';
import { useTranslation } from 'react-i18next';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'manager' | 'operator';
  tenant_id: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hasRole: (...roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { showToast } = useToast();
  const { t } = useTranslation();
  
  // Load user from localStorage on mount
  useEffect(() => {
    const loadUser = async () => {
      const storedUser = localStorage.getItem('user');
      const token = localStorage.getItem('access_token');
      
      if (storedUser && token) {
        try {
          // Validate token by fetching current user
          const response = await authAPI.getCurrentUser();
          setUser(response.data);
        } catch (error) {
          // Token invalid, clear storage
          localStorage.removeItem('user');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      
      setIsLoading(false);
    };
    
    loadUser();
  }, []);
  
  const login = async (email: string, password: string) => {
    try {
      const response = await authAPI.login(email, password);
      const { access_token, refresh_token, user: userData } = response.data;
      
      // Store tokens and user
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      setUser(userData);
      showToast('success', t('auth.login_success'));
    } catch (error: any) {
      const message = error.response?.data?.message || t('auth.login_error');
      showToast('error', message);
      throw error;
    }
  };
  
  const logout = () => {
    setUser(null);
    authAPI.logout();
  };
  
  const hasRole = (...roles: string[]) => {
    return user ? roles.includes(user.role) : false;
  };
  
  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    hasRole,
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
