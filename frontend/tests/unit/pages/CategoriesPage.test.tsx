/**
 * Contract Tests: CategoriesPage
 * 
 * Main page for category management with list/tree toggle.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CategoriesPage } from '../../../src/pages/CategoriesPage';
import { useCategories, useCreateCategory, useUpdateCategory, useDeleteCategory } from '../../../src/hooks/useCategories';

// Mock the hooks
vi.mock('../../../src/hooks/useCategories');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  // eslint-disable-next-line react/display-name
  return ({ children }: { children: React.ReactNode }) => {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  };
};

describe('CategoriesPage', () => {
  const mockCategories = [
    {
      id: 'cat-1',
      name: 'Electronics',
      is_active: true,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      tenant_id: 'tenant-1',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();

    // Default mock implementations
    vi.mocked(useCategories).mockReturnValue({
      data: { items: mockCategories, total: 1, skip: 0, limit: 100 },
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    vi.mocked(useCreateCategory).mockReturnValue({
      mutate: vi.fn(),
      isLoading: false,
    } as any);

    vi.mocked(useUpdateCategory).mockReturnValue({
      mutate: vi.fn(),
      isLoading: false,
    } as any);

    vi.mocked(useDeleteCategory).mockReturnValue({
      mutate: vi.fn(),
      isLoading: false,
    } as any);
  });

  describe('Layout', () => {
    it('should render page header with "Categorias" title', () => {
      // Act
      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Assert
      expect(screen.getByRole('heading', { name: /categorias/i })).toBeInTheDocument();
    });

    it('should show "Nova Categoria" button', () => {
      // Act
      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Assert
      expect(screen.getByRole('button', { name: /nova categoria/i })).toBeInTheDocument();
    });

    it('should have toggle between Tree and List views', () => {
      // Act
      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Assert
      expect(screen.getByRole('button', { name: /árvore/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /lista/i })).toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('should show skeleton loader while fetching', () => {
      // Arrange
      vi.mocked(useCategories).mockReturnValue({
        data: undefined,
        isLoading: true,
        isError: false,
        error: null,
      } as any);

      // Act
      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Assert
      expect(screen.getByTestId('categories-loading')).toBeInTheDocument();
    });

    it('should show error message on fetch failure', () => {
      // Arrange
      vi.mocked(useCategories).mockReturnValue({
        data: undefined,
        isLoading: false,
        isError: true,
        error: new Error('Failed to fetch categories'),
      } as any);

      // Act
      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Assert
      expect(screen.getByText(/erro ao carregar categorias/i)).toBeInTheDocument();
    });
  });

  describe('CRUD Operations', () => {
    it('should open create form on "Nova Categoria" click', async () => {
      // Arrange
      const user = userEvent.setup();
      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Act
      await user.click(screen.getByRole('button', { name: /nova categoria/i }));

      // Assert
      expect(screen.getByRole('heading', { name: /criar categoria/i })).toBeInTheDocument();
    });

    it('should call create mutation when form submitted', async () => {
      // Arrange
      const user = userEvent.setup();
      const mutateMock = vi.fn();
      vi.mocked(useCreateCategory).mockReturnValue({
        mutate: mutateMock,
        isLoading: false,
      } as any);

      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Act
      await user.click(screen.getByRole('button', { name: /nova categoria/i }));
      await user.type(screen.getByLabelText(/nome/i), 'New Category');
      await user.click(screen.getByRole('button', { name: /criar/i }));

      // Assert
      await waitFor(() => {
        expect(mutateMock).toHaveBeenCalled();
        const callArgs = mutateMock.mock.calls[0][0];
        expect(callArgs.name).toBe('New Category');
      });
    });

    it('should open edit form when category edit clicked', async () => {
      // Arrange
      const user = userEvent.setup();
      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Act - Assuming edit button is visible in list/tree
      const editButton = screen.getByRole('button', { name: /editar/i });
      await user.click(editButton);

      // Assert
      expect(screen.getByRole('heading', { name: /editar categoria/i })).toBeInTheDocument();
    });

    it('should show toast notification on successful create', async () => {
      // Arrange
      const user = userEvent.setup();
      const mutateMock = vi.fn((data, options: any) => {
        options?.onSuccess?.();
      });
      
      vi.mocked(useCreateCategory).mockReturnValue({
        mutate: mutateMock,
        isLoading: false,
      } as any);

      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Act
      await user.click(screen.getByRole('button', { name: /nova categoria/i }));
      await user.type(screen.getByLabelText(/nome/i), 'New Category');
      await user.click(screen.getByRole('button', { name: /criar/i }));

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/categoria criada com sucesso/i)).toBeInTheDocument();
      });
    });
  });

  describe('View Toggle', () => {
    it('should switch to tree view when tree button clicked', async () => {
      // Arrange
      const user = userEvent.setup();
      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Act
      await user.click(screen.getByRole('button', { name: /árvore/i }));

      // Assert - Tree view should be active
      const treeButton = screen.getByRole('button', { name: /árvore/i });
      expect(treeButton).toHaveClass(/active|selected/);
    });

    it('should switch to list view when list button clicked', async () => {
      // Arrange
      const user = userEvent.setup();
      render(<CategoriesPage />, { wrapper: createWrapper() });

      // Act
      await user.click(screen.getByRole('button', { name: /lista/i }));

      // Assert - List view should be active
      const listButton = screen.getByRole('button', { name: /lista/i });
      expect(listButton).toHaveClass(/active|selected/);
    });
  });
});
