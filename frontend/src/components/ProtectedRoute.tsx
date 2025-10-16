/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 */

import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { tokenStorage } from '../utils/tokenStorage';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { user, isLoading } = useAuth();
  
  const hasValidToken = !!tokenStorage.getAccessToken() && !tokenStorage.isTokenExpired();
  const isAuthenticated = hasValidToken && !!user;

  console.log('🔒 ProtectedRoute check:', { 
    hasValidToken, 
    hasUser: !!user, 
    isAuthenticated, 
    isLoading 
  });

  // Show loading state while checking authentication
  if (isLoading) {
    console.log('⏳ ProtectedRoute: Loading...');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    console.log('🚫 ProtectedRoute: Not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  console.log('✅ ProtectedRoute: Authenticated, rendering children');
  // Render protected content
  return <>{children}</>;
};
