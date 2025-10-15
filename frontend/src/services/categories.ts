/**
 * Category API Service
 * 
 * Client-side API methods for category CRUD operations.
 */

import { api } from './api';
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
   * Get list of categories with optional filters
   */
  getCategoriesList: async (filters: CategoryFilter = {}): Promise<{ data: CategoryListResponse }> => {
    const params = {
      skip: filters.skip ?? 0,
      limit: filters.limit ?? 100,
      ...(filters.name && { name: filters.name }),
      ...(filters.status && { status: filters.status }),
      ...(filters.parent_id && { parent_id: filters.parent_id }),
      ...(filters.root_only !== undefined && { root_only: filters.root_only }),
    };

    return api.get('/categories', { params });
  },

  /**
   * Get single category by ID
   */
  getCategoryById: async (id: string): Promise<{ data: Category }> => {
    return api.get(`/categories/${id}`);
  },

  /**
   * Create new category
   */
  createCategory: async (data: CategoryCreate): Promise<{ data: Category }> => {
    return api.post('/categories', data);
  },

  /**
   * Update existing category
   */
  updateCategory: async (id: string, data: CategoryUpdate): Promise<{ data: Category }> => {
    return api.put(`/categories/${id}`, data);
  },

  /**
   * Delete category
   */
  deleteCategory: async (id: string): Promise<{ data: { message: string } }> => {
    return api.delete(`/categories/${id}`);
  },
};
