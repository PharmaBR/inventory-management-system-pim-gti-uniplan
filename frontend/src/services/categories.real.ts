/**
 * Category API Service
 * 
 * Client-side API methods for category CRUD operations.
 */

import api from './api';
import type {
  Category,
  CategoryCreate,
  CategoryUpdate,
  CategoryFilter,
  CategoryListResponse,
} from '../types/category';

/**
 * Categories API client
 */
export const categoriesAPI = {
  /**
   * Get paginated list of categories with optional filtering
   */
  getCategoriesList: async (filters?: CategoryFilter): Promise<CategoryListResponse> => {
    const params = new URLSearchParams();
    
    if (filters?.name) {
      params.append('name', filters.name);
    }
    
    if (filters?.status) {
      params.append('status', filters.status);
    }
    
    if (filters?.parent_id) {
      params.append('parent_id', filters.parent_id);
    }
    
    if (filters?.root_only !== undefined) {
      params.append('root_only', String(filters.root_only));
    }
    
    if (filters?.skip !== undefined) {
      params.append('skip', String(filters.skip));
    }
    
    if (filters?.limit !== undefined) {
      params.append('limit', String(filters.limit));
    }

    const response = await api.get<CategoryListResponse>('/categories', { params });
    return response.data;
  },

  /**
   * Get a single category by ID
   */
  getCategory: async (id: string): Promise<Category> => {
    const response = await api.get<Category>(`/categories/${id}`);
    return response.data;
  },

  /**
   * Create a new category
   */
  createCategory: async (data: CategoryCreate): Promise<Category> => {
    const response = await api.post<Category>('/categories', data);
    return response.data;
  },

  /**
   * Update an existing category
   */
  updateCategory: async (id: string, data: CategoryUpdate): Promise<Category> => {
    const response = await api.put<Category>(`/categories/${id}`, data);
    return response.data;
  },

  /**
   * Delete a category
   */
  deleteCategory: async (id: string): Promise<void> => {
    await api.delete(`/categories/${id}`);
  },
};
