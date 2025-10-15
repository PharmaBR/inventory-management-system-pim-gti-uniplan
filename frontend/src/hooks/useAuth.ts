/**
 * Authentication Hooks
 * React Query hooks for authentication operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authAPI } from '../services/auth';
import { tokenStorage } from '../utils/tokenStorage';
import type { LoginCredentials } from '../types/auth';
import { useState, useEffect } from 'react';

/**
 * Hook for user login
 */
export const useLogin = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authAPI.login,
    onSuccess: (data) => {
      // Store tokens
      tokenStorage.setTokens(data.access_token, data.refresh_token, data.expires_in);
      
      // Invalidate user query to refetch
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });
};

/**
 * Hook for user logout
 */
export const useLogout = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authAPI.logout,
    onSuccess: () => {
      // Clear tokens
      tokenStorage.clearTokens();
      
      // Clear all queries
      queryClient.clear();
    },
  });
};

/**
 * Hook to get current authenticated user
 */
export const useCurrentUser = () => {
  const hasToken = !!tokenStorage.getAccessToken();
  
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: authAPI.getCurrentUser,
    enabled: hasToken && !tokenStorage.isTokenExpired(),
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook for authentication state
 * Provides unified auth state and methods
 */
export const useAuth = () => {
  const { data: user, isLoading } = useCurrentUser();
  const loginMutation = useLogin();
  const logoutMutation = useLogout();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const hasValidToken = !!tokenStorage.getAccessToken() && !tokenStorage.isTokenExpired();
    setIsAuthenticated(hasValidToken && !!user);
  }, [user]);

  const login = async (credentials: LoginCredentials) => {
    return loginMutation.mutateAsync(credentials);
  };

  const logout = async () => {
    return logoutMutation.mutateAsync();
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    loginError: loginMutation.error,
    isLoggingIn: loginMutation.isPending,
  };
};
