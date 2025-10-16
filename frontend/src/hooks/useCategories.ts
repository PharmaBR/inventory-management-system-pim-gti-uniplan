/**
 * useCategories Hook
 * 
 * React Query hooks for category CRUD operations.
 * This is a placeholder - implementation comes in Session 2.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { categoriesAPI } from '../services/categories';
import type { CategoryFilter, CategoryCreate, CategoryUpdate } from '../types/category';

/**
 * Query key factory for categories
 */
const categoryKeys = {
  all: ['categories'] as const,
  lists: () => [...categoryKeys.all, 'list'] as const,
  list: (filters: CategoryFilter) => [...categoryKeys.lists(), filters] as const,
  details: () => [...categoryKeys.all, 'detail'] as const,
  detail: (id: string) => [...categoryKeys.details(), id] as const,
};

/**
 * Fetch list of categories
 */
export const useCategories = (filters: CategoryFilter = {}) => {
  return useQuery({
    queryKey: categoryKeys.list(filters),
    queryFn: () => categoriesAPI.getCategoriesList(filters),
  });
};

/**
 * Fetch single category by ID
 */
export const useCategory = (id: string | undefined) => {
  return useQuery({
    queryKey: id ? categoryKeys.detail(id) : ['categories', 'detail', 'undefined'],
    queryFn: () => {
      if (!id) throw new Error('Category ID is required');
      return categoriesAPI.getCategory(id);
    },
    enabled: !!id,
  });
};

/**
 * Create new category mutation
 */
export const useCreateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CategoryCreate) => {
      return categoriesAPI.createCategory(data);
    },
    onSuccess: () => {
      // Invalidate all category lists to refetch
      queryClient.invalidateQueries({ queryKey: categoryKeys.lists() });
    },
  });
};

/**
 * Update category mutation
 */
export const useUpdateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: CategoryUpdate }) => {
      return categoriesAPI.updateCategory(id, data);
    },
    onSuccess: (_, variables) => {
      // Invalidate lists and the specific category detail
      queryClient.invalidateQueries({ queryKey: categoryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: categoryKeys.detail(variables.id) });
    },
  });
};

/**
 * Delete category mutation
 */
export const useDeleteCategory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      return categoriesAPI.deleteCategory(id);
    },
    onSuccess: () => {
      // Invalidate all category lists to refetch
      queryClient.invalidateQueries({ queryKey: categoryKeys.lists() });
    },
  });
};
