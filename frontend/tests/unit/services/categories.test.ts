/**
 * Contract Tests: Category API Service
 * 
 * These tests define the expected behavior of the category API client.
 * Tests should FAIL initially (RED) - implementation comes in Session 2.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { categoriesAPI } from '../../../src/services/categories';
import { api } from '../../../src/services/api';

// Mock the api module
vi.mock('../../../src/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('categoriesAPI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('getCategoriesList', () => {
    it('should call GET /categories with default params', async () => {
      // Arrange
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          skip: 0,
          limit: 100,
        },
      };
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.getCategoriesList();

      // Assert
      expect(api.get).toHaveBeenCalledWith('/categories', {
        params: {
          skip: 0,
          limit: 100,
        },
      });
    });

    it('should apply name filter when provided', async () => {
      // Arrange
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.getCategoriesList({ name: 'Electronics' });

      // Assert
      expect(api.get).toHaveBeenCalledWith('/categories', {
        params: {
          name: 'Electronics',
          skip: 0,
          limit: 100,
        },
      });
    });

    it('should apply status filter when provided', async () => {
      // Arrange
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.getCategoriesList({ status: 'active' });

      // Assert
      expect(api.get).toHaveBeenCalledWith('/categories', {
        params: {
          status: 'active',
          skip: 0,
          limit: 100,
        },
      });
    });

    it('should apply parent_id filter when provided', async () => {
      // Arrange
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.getCategoriesList({ parent_id: 'parent-123' });

      // Assert
      expect(api.get).toHaveBeenCalledWith('/categories', {
        params: {
          parent_id: 'parent-123',
          skip: 0,
          limit: 100,
        },
      });
    });

    it('should apply root_only filter when provided', async () => {
      // Arrange
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.getCategoriesList({ root_only: true });

      // Assert
      expect(api.get).toHaveBeenCalledWith('/categories', {
        params: {
          root_only: true,
          skip: 0,
          limit: 100,
        },
      });
    });

    it('should handle pagination with custom skip and limit', async () => {
      // Arrange
      const mockResponse = { data: { items: [], total: 0 } };
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.getCategoriesList({ skip: 20, limit: 50 });

      // Assert
      expect(api.get).toHaveBeenCalledWith('/categories', {
        params: {
          skip: 20,
          limit: 50,
        },
      });
    });
  });

  describe('getCategoryById', () => {
    it('should call GET /categories/{id}', async () => {
      // Arrange
      const categoryId = 'cat-123';
      const mockResponse = {
        data: {
          id: categoryId,
          name: 'Electronics',
          is_active: true,
        },
      };
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      // Act
      const result = await categoriesAPI.getCategoryById(categoryId);

      // Assert
      expect(api.get).toHaveBeenCalledWith(`/categories/${categoryId}`);
      expect(result.data.id).toBe(categoryId);
    });

    it('should handle 404 errors when category not found', async () => {
      // Arrange
      const categoryId = 'nonexistent';
      vi.mocked(api.get).mockRejectedValue({
        response: { status: 404 },
      });

      // Act & Assert
      await expect(categoriesAPI.getCategoryById(categoryId)).rejects.toMatchObject({
        response: { status: 404 },
      });
    });
  });

  describe('createCategory', () => {
    it('should call POST /categories with correct data', async () => {
      // Arrange
      const newCategory = {
        name: 'New Category',
        description: 'Test description',
      };
      const mockResponse = {
        data: {
          id: 'cat-new',
          ...newCategory,
          is_active: true,
        },
      };
      vi.mocked(api.post).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.createCategory(newCategory);

      // Assert
      expect(api.post).toHaveBeenCalledWith('/categories', newCategory);
    });

    it('should handle 409 conflict errors for duplicate names', async () => {
      // Arrange
      const duplicateCategory = {
        name: 'Existing Category',
      };
      vi.mocked(api.post).mockRejectedValue({
        response: { status: 409 },
      });

      // Act & Assert
      await expect(categoriesAPI.createCategory(duplicateCategory)).rejects.toMatchObject({
        response: { status: 409 },
      });
    });

    it('should include parent_id when creating subcategory', async () => {
      // Arrange
      const newSubcategory = {
        name: 'Subcategory',
        parent_id: 'parent-123',
      };
      const mockResponse = {
        data: {
          id: 'cat-sub',
          ...newSubcategory,
          is_active: true,
        },
      };
      vi.mocked(api.post).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.createCategory(newSubcategory);

      // Assert
      expect(api.post).toHaveBeenCalledWith('/categories', newSubcategory);
    });
  });

  describe('updateCategory', () => {
    it('should call PUT /categories/{id} with partial data', async () => {
      // Arrange
      const categoryId = 'cat-123';
      const updates = {
        name: 'Updated Name',
      };
      const mockResponse = {
        data: {
          id: categoryId,
          name: 'Updated Name',
          is_active: true,
        },
      };
      vi.mocked(api.put).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.updateCategory(categoryId, updates);

      // Assert
      expect(api.put).toHaveBeenCalledWith(`/categories/${categoryId}`, updates);
    });

    it('should allow updating is_active status', async () => {
      // Arrange
      const categoryId = 'cat-123';
      const updates = {
        is_active: false,
      };
      const mockResponse = {
        data: {
          id: categoryId,
          is_active: false,
        },
      };
      vi.mocked(api.put).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.updateCategory(categoryId, updates);

      // Assert
      expect(api.put).toHaveBeenCalledWith(`/categories/${categoryId}`, updates);
    });
  });

  describe('deleteCategory', () => {
    it('should call DELETE /categories/{id}', async () => {
      // Arrange
      const categoryId = 'cat-123';
      const mockResponse = { data: { message: 'Category deleted' } };
      vi.mocked(api.delete).mockResolvedValue(mockResponse);

      // Act
      await categoriesAPI.deleteCategory(categoryId);

      // Assert
      expect(api.delete).toHaveBeenCalledWith(`/categories/${categoryId}`);
    });

    it('should handle 400 errors when category has products', async () => {
      // Arrange
      const categoryId = 'cat-with-products';
      vi.mocked(api.delete).mockRejectedValue({
        response: {
          status: 400,
          data: {
            detail: 'Cannot delete category with products',
          },
        },
      });

      // Act & Assert
      await expect(categoriesAPI.deleteCategory(categoryId)).rejects.toMatchObject({
        response: {
          status: 400,
        },
      });
    });
  });
});
