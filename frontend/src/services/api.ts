import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor - Add auth token and tenant header
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add JWT token
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add tenant slug header
    const tenantSlug = localStorage.getItem('tenant_slug');
    if (tenantSlug && config.headers) {
      config.headers['X-Tenant-Slug'] = tenantSlug;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 Unauthorized - Try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token: newRefreshToken } = response.data;
          
          // Update tokens
          localStorage.setItem('access_token', access_token);
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken);
          }
          
          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // Handle other errors
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },
  
  getCurrentUser: () => api.get('/auth/me'),
};

// Products API
export const productsAPI = {
  list: (params?: Record<string, any>) => api.get('/products', { params }),
  get: (id: string) => api.get(`/products/${id}`),
  create: (data: Record<string, any>) => api.post('/products', data),
  update: (id: string, data: Record<string, any>) => api.put(`/products/${id}`, data),
  delete: (id: string) => api.delete(`/products/${id}`),
};

// Movements API
export const movementsAPI = {
  list: (params?: Record<string, any>) => api.get('/movements', { params }),
  get: (id: string) => api.get(`/movements/${id}`),
  create: (data: Record<string, any>) => api.post('/movements', data),
};

// Alerts API
export const alertsAPI = {
  list: (params?: Record<string, any>) => api.get('/alerts', { params }),
  markRead: (id: string) => api.patch(`/alerts/${id}/read`),
  markResolved: (id: string) => api.patch(`/alerts/${id}/resolve`),
};

// Tenant API
export const tenantAPI = {
  getCurrent: () => api.get('/tenant'),
  updateConfig: (data: Record<string, any>) => api.put('/tenant/config', data),
};

export default api;
