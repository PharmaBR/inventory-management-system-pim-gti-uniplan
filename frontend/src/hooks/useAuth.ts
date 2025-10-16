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
    onSuccess: async (data) => {
      console.log('💾 Login mutation success, storing tokens:', {
        hasAccessToken: !!data.access_token,
        hasRefreshToken: !!data.refresh_token,
        expiresIn: data.expires_in
      });
      
      // Store tokens FIRST
      tokenStorage.setTokens(data.access_token, data.refresh_token, data.expires_in);
      
      console.log('💾 Tokens stored, fetching user data');
      
      // Fetch user data directly and put in cache
      try {
        const userData = await authAPI.getCurrentUser();
        console.log('📊 User data fetched:', userData);
        
        // Set user data in cache
        queryClient.setQueryData(['currentUser'], userData);
        console.log('📊 User data set in cache');
        
        console.log('✅ Login mutation completed, user data loaded');
      } catch (error) {
        console.error('❌ Failed to fetch user data:', error);
        throw error;
      }
    },
    onError: (error) => {
      console.error('❌ Login mutation failed:', error);
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
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: authAPI.getCurrentUser,
    enabled: !!tokenStorage.getAccessToken() && !tokenStorage.isTokenExpired(),
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
    const authState = hasValidToken && !!user;
    console.log('🔐 useAuth state update:', {
      hasValidToken,
      hasUser: !!user,
      isAuthenticated: authState,
      user: user ? { email: user.email, id: user.id } : null
    });
    setIsAuthenticated(authState);
  }, [user]);

  const login = async (credentials: LoginCredentials) => {
    console.log('🔑 useAuth.login called with:', credentials.email);
    const result = await loginMutation.mutateAsync(credentials);
    console.log('🔑 useAuth.login completed:', result);
    return result;
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
