/**
 * Mock Category Service - Temporary for MVP
 * 
 * Simulates backend API responses for testing without authentication.
 * Replace with real API calls when auth is ready.
 */

import type {
  Category,
  CategoryCreate,
  CategoryUpdate,
  CategoryFilter,
  CategoryListResponse,
} from '../types/category';

// Mock data storage (in-memory)
let mockCategories: Category[] = [
  {
    id: '1',
    name: 'Eletrônicos',
    description: 'Dispositivos eletrônicos e acessórios',
    is_active: true,
    tenant_id: 'demo-tenant',
    created_at: '2025-01-10T10:00:00Z',
    updated_at: '2025-01-10T10:00:00Z',
  },
  {
    id: '2',
    name: 'Computadores',
    description: 'Desktops, laptops e acessórios',
    is_active: true,
    parent_id: '1',
    tenant_id: 'demo-tenant',
    created_at: '2025-01-10T10:05:00Z',
    updated_at: '2025-01-10T10:05:00Z',
  },
  {
    id: '3',
    name: 'Livros',
    description: 'Livros e publicações',
    is_active: true,
    tenant_id: 'demo-tenant',
    created_at: '2025-01-10T10:10:00Z',
    updated_at: '2025-01-10T10:10:00Z',
  },
  {
    id: '4',
    name: 'Ficção',
    description: 'Livros de ficção',
    is_active: true,
    parent_id: '3',
    tenant_id: 'demo-tenant',
    created_at: '2025-01-10T10:15:00Z',
    updated_at: '2025-01-10T10:15:00Z',
  },
  {
    id: '5',
    name: 'Smartphones',
    description: 'Telefones celulares',
    is_active: true,
    parent_id: '1',
    tenant_id: 'demo-tenant',
    created_at: '2025-01-10T10:20:00Z',
    updated_at: '2025-01-10T10:20:00Z',
  },
];

let nextId = 6;

// Simulate network delay
const delay = (ms: number = 300) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Mock Categories API client
 */
export const mockCategoriesAPI = {
  /**
   * Get list of categories with optional filters
   */
  getCategoriesList: async (filters: CategoryFilter = {}): Promise<{ data: CategoryListResponse }> => {
    await delay();
    
    let filtered = [...mockCategories];

    // Apply filters
    if (filters.name) {
      const searchLower = filters.name.toLowerCase();
      filtered = filtered.filter(cat => cat.name.toLowerCase().includes(searchLower));
    }

    if (filters.status !== undefined) {
      const isActive = filters.status === 'active';
      filtered = filtered.filter(cat => cat.is_active === isActive);
    }

    if (filters.parent_id) {
      filtered = filtered.filter(cat => cat.parent_id === filters.parent_id);
    }

    if (filters.root_only) {
      filtered = filtered.filter(cat => !cat.parent_id);
    }

    // Apply pagination
    const skip = filters.skip ?? 0;
    const limit = filters.limit ?? 100;
    const paginated = filtered.slice(skip, skip + limit);

    return {
      data: {
        items: paginated,
        total: filtered.length,
        skip,
        limit,
      },
    };
  },

  /**
   * Get single category by ID
   */
  getCategoryById: async (id: string): Promise<{ data: Category }> => {
    await delay();
    
    const category = mockCategories.find(cat => cat.id === id);
    
    if (!category) {
      throw new Error('Category not found');
    }

    return { data: category };
  },

  /**
   * Create new category
   */
  createCategory: async (data: CategoryCreate): Promise<{ data: Category }> => {
    await delay();

    const newCategory: Category = {
      id: String(nextId++),
      name: data.name,
      description: data.description,
      is_active: true,
      parent_id: data.parent_id,
      tenant_id: 'demo-tenant',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    mockCategories.push(newCategory);

    return { data: newCategory };
  },

  /**
   * Update existing category
   */
  updateCategory: async (id: string, data: CategoryUpdate): Promise<{ data: Category }> => {
    await delay();

    const index = mockCategories.findIndex(cat => cat.id === id);
    
    if (index === -1) {
      throw new Error('Category not found');
    }

    const updated: Category = {
      ...mockCategories[index],
      ...(data.name !== undefined && { name: data.name }),
      ...(data.description !== undefined && { description: data.description }),
      ...(data.is_active !== undefined && { is_active: data.is_active }),
      ...(data.parent_id !== undefined && { parent_id: data.parent_id }),
      updated_at: new Date().toISOString(),
    };

    mockCategories[index] = updated;

    return { data: updated };
  },

  /**
   * Delete category
   */
  deleteCategory: async (id: string): Promise<{ data: { message: string } }> => {
    await delay();

    const index = mockCategories.findIndex(cat => cat.id === id);
    
    if (index === -1) {
      throw new Error('Category not found');
    }

    mockCategories.splice(index, 1);

    return { data: { message: 'Category deleted successfully' } };
  },
};
