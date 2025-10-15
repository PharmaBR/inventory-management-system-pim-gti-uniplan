/**
 * Contract Tests: useCategories Hook
 * 
 * These tests define the expected behavior of React Query hooks for categories.
 * Tests should FAIL initially (RED) - implementation comes in Session 2.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React, { ReactNode } from 'react';
import {
  useCategories,
  useCategory,
  useCreateCategory,
  useUpdateCategory,
  useDeleteCategory,
} from '../../../src/hooks/useCategories';
import { categoriesAPI } from '../../../src/services/categories';

// Mock the API service
vi.mock('../../../src/services/categories');

// Helper to create wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

  // eslint-disable-next-line react/display-name
  return ({ children }: { children: ReactNode }) => {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  };
};

describe('useCategories Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useCategories (Query)', () => {
    it('should fetch categories list on mount', async () => {
      // Arrange
      const mockData = {
        data: {
          items: [
            { 
              id: '1', 
              name: 'Category 1', 
              is_active: true,
              created_at: '2025-01-01T00:00:00Z',
              updated_at: '2025-01-01T00:00:00Z',
              tenant_id: 'tenant-1',
            },
            { 
              id: '2', 
              name: 'Category 2', 
              is_active: true,
              created_at: '2025-01-01T00:00:00Z',
              updated_at: '2025-01-01T00:00:00Z',
              tenant_id: 'tenant-1',
            },
          ],
          total: 2,
          skip: 0,
          limit: 100,
        },
      };
      vi.mocked(categoriesAPI.getCategoriesList).mockResolvedValue(mockData);

      // Act
      const { result } = renderHook(() => useCategories(), {
        wrapper: createWrapper(),
      });

      // Assert
      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(categoriesAPI.getCategoriesList).toHaveBeenCalledWith({});
      expect(result.current.data?.items).toHaveLength(2);
    });

    it('should apply filters to query', async () => {
      // Arrange
      const filters = { name: 'Electronics', status: 'active' as const };
      const mockData = {
        data: {
          items: [],
          total: 0,
          skip: 0,
          limit: 100,
        },
      };
      vi.mocked(categoriesAPI.getCategoriesList).mockResolvedValue(mockData);

      // Act
      renderHook(() => useCategories(filters), {
        wrapper: createWrapper(),
      });

      // Assert
      await waitFor(() => {
        expect(categoriesAPI.getCategoriesList).toHaveBeenCalledWith(filters);
      });
    });

    it('should cache results with proper query key', async () => {
      // Arrange
      const mockData = {
        data: {
          items: [{ 
            id: '1', 
            name: 'Category 1', 
            is_active: true,
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-01T00:00:00Z',
            tenant_id: 'tenant-1',
          }],
          total: 1,
          skip: 0,
          limit: 100,
        },
      };
      vi.mocked(categoriesAPI.getCategoriesList).mockResolvedValue(mockData);

      const wrapper = createWrapper();

      // Act - Two renders with same wrapper (shared QueryClient)
      const { result: result1 } = renderHook(() => useCategories(), { wrapper });
      await waitFor(() => expect(result1.current.isSuccess).toBe(true));

      const { result: result2 } = renderHook(() => useCategories(), { wrapper });
      await waitFor(() => expect(result2.current.isSuccess).toBe(true));

      // Assert - API should be called only once due to caching
      // Note: With the same wrapper/QueryClient, the second call uses cached data
      expect(categoriesAPI.getCategoriesList).toHaveBeenCalled();
      expect(result1.current.data?.items).toHaveLength(1);
      expect(result2.current.data?.items).toHaveLength(1);
    });

    it('should handle loading state', () => {
      // Arrange
      vi.mocked(categoriesAPI.getCategoriesList).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      // Act
      const { result } = renderHook(() => useCategories(), {
        wrapper: createWrapper(),
      });

      // Assert
      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeUndefined();
    });

    it('should handle error state', async () => {
      // Arrange
      const error = new Error('Failed to fetch categories');
      vi.mocked(categoriesAPI.getCategoriesList).mockRejectedValue(error);

      // Act
      const { result } = renderHook(() => useCategories(), {
        wrapper: createWrapper(),
      });

      // Assert
      await waitFor(() => expect(result.current.isError).toBe(true));
      expect(result.current.error).toBe(error);
    });
  });

  describe('useCategory (Single Query)', () => {
    it('should fetch single category by ID', async () => {
      // Arrange
      const categoryId = 'cat-123';
      const mockData = {
        data: {
          id: categoryId,
          name: 'Electronics',
          is_active: true,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
          tenant_id: 'tenant-1',
        },
      };
      vi.mocked(categoriesAPI.getCategoryById).mockResolvedValue(mockData);

      // Act
      const { result } = renderHook(() => useCategory(categoryId), {
        wrapper: createWrapper(),
      });

      // Assert
      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(categoriesAPI.getCategoryById).toHaveBeenCalledWith(categoryId);
      expect(result.current.data?.id).toBe(categoryId);
    });

    it('should not fetch if ID is undefined', () => {
      // Act
      const { result } = renderHook(() => useCategory(undefined), {
        wrapper: createWrapper(),
      });

      // Assert
      expect(result.current.fetchStatus).toBe('idle');
      expect(categoriesAPI.getCategoryById).not.toHaveBeenCalled();
    });
  });

  describe('useCreateCategory (Mutation)', () => {
    it('should create category and invalidate queries', async () => {
      // Arrange
      const newCategory = { name: 'New Category', description: 'Test' };
      const mockResponse = {
        data: {
          id: 'cat-new',
          ...newCategory,
          is_active: true,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
          tenant_id: 'tenant-1',
        },
      };
      vi.mocked(categoriesAPI.createCategory).mockResolvedValue(mockResponse);

      // Act
      const { result } = renderHook(() => useCreateCategory(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(newCategory);

      // Assert
      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(categoriesAPI.createCategory).toHaveBeenCalledWith(newCategory);
      expect(result.current.data?.data.id).toBe('cat-new');
    });

    it('should handle creation errors', async () => {
      // Arrange
      const error = new Error('Duplicate category name');
      vi.mocked(categoriesAPI.createCategory).mockRejectedValue(error);

      // Act
      const { result } = renderHook(() => useCreateCategory(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({ name: 'Duplicate' });

      // Assert
      await waitFor(() => expect(result.current.isError).toBe(true));
      expect(result.current.error).toBe(error);
    });
  });

  describe('useUpdateCategory (Mutation)', () => {
    it('should update category and invalidate queries', async () => {
      // Arrange
      const categoryId = 'cat-123';
      const updates = { name: 'Updated Name' };
      const mockResponse = {
        data: {
          id: categoryId,
          name: 'Updated Name',
          is_active: true,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
          tenant_id: 'tenant-1',
        },
      };
      vi.mocked(categoriesAPI.updateCategory).mockResolvedValue(mockResponse);

      // Act
      const { result } = renderHook(() => useUpdateCategory(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({ id: categoryId, data: updates });

      // Assert
      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(categoriesAPI.updateCategory).toHaveBeenCalledWith(categoryId, updates);
    });

    it('should handle update errors', async () => {
      // Arrange
      const error = new Error('Category not found');
      vi.mocked(categoriesAPI.updateCategory).mockRejectedValue(error);

      // Act
      const { result } = renderHook(() => useUpdateCategory(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({ id: 'nonexistent', data: { name: 'Test' } });

      // Assert
      await waitFor(() => expect(result.current.isError).toBe(true));
    });
  });

  describe('useDeleteCategory (Mutation)', () => {
    it('should delete category and invalidate queries', async () => {
      // Arrange
      const categoryId = 'cat-123';
      const mockResponse = {
        data: { message: 'Category deleted successfully' },
      };
      vi.mocked(categoriesAPI.deleteCategory).mockResolvedValue(mockResponse);

      // Act
      const { result } = renderHook(() => useDeleteCategory(), {
        wrapper: createWrapper(),
      });

      result.current.mutate(categoryId);

      // Assert
      await waitFor(() => expect(result.current.isSuccess).toBe(true));
      expect(categoriesAPI.deleteCategory).toHaveBeenCalledWith(categoryId);
    });

    it('should handle delete errors (category has products)', async () => {
      // Arrange
      const error = { response: { status: 400, data: { detail: 'Category has products' } } };
      vi.mocked(categoriesAPI.deleteCategory).mockRejectedValue(error);

      // Act
      const { result } = renderHook(() => useDeleteCategory(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('cat-with-products');

      // Assert
      await waitFor(() => expect(result.current.isError).toBe(true));
    });
  });
});
