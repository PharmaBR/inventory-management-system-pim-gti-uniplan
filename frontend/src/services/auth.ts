/**
 * Authentication API Service
 */

import api from './api';
import type { LoginCredentials, LoginResponse, User } from '../types/auth';

export const authAPI = {
  /**
   * Login user and get access token
   */
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await api.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  /**
   * Refresh access token using refresh token
   */
  refreshToken: async (refreshToken: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  /**
   * Get current authenticated user profile
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Logout user (optional backend call if needed)
   */
  logout: async (): Promise<void> => {
    // Backend may not have a logout endpoint if tokens are stateless
    // Just clear local storage on frontend
    return Promise.resolve();
  },
};
