/**
 * Contract Tests: CategoryList Component
 * 
 * These tests define the expected behavior of the category list view.
 * Tests should FAIL initially (RED) - implementation comes after.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { CategoryList } from '../../../src/components/categories/CategoryList';
import type { Category } from '../../../src/types/category';

describe('CategoryList Component', () => {
  const mockCategories: Category[] = [
    {
      id: 'cat-1',
      name: 'Electronics',
      description: 'Electronic devices',
      is_active: true,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      tenant_id: 'tenant-1',
    },
    {
      id: 'cat-2',
      name: 'Books',
      description: 'Books and magazines',
      parent_id: 'cat-1',
      is_active: true,
      created_at: '2025-01-02T00:00:00Z',
      updated_at: '2025-01-02T00:00:00Z',
      tenant_id: 'tenant-1',
    },
    {
      id: 'cat-3',
      name: 'Inactive Category',
      is_active: false,
      created_at: '2025-01-03T00:00:00Z',
      updated_at: '2025-01-03T00:00:00Z',
      tenant_id: 'tenant-1',
    },
  ];

  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();
  const mockOnFilter = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render categories in table format', () => {
      // Act
      render(
        <CategoryList
          categories={mockCategories}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Assert
      expect(screen.getByRole('table')).toBeInTheDocument();
      // Electronics appears twice (as category name and as parent)
      const electronicsElements = screen.queryAllByText(/Electronics/i);
      expect(electronicsElements.length).toBeGreaterThan(0);
      expect(screen.getByText('Books')).toBeInTheDocument();
    });

    it('should show category name, description, and status', () => {
      // Act
      render(
        <CategoryList
          categories={mockCategories}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Assert
      const electronicsElements = screen.queryAllByText(/Electronics/i);
      expect(electronicsElements.length).toBeGreaterThan(0);
      expect(screen.getByText('Electronic devices')).toBeInTheDocument();
      // Multiple categories can be active
      expect(screen.getAllByText('Ativo').length).toBeGreaterThan(0);
      expect(screen.getByText('Inativo')).toBeInTheDocument();
    });

    it('should show parent category name if exists', () => {
      // Act
      render(
        <CategoryList
          categories={mockCategories}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Assert - Books should show Electronics as parent
      const booksRow = screen.getByText('Books').closest('tr');
      expect(within(booksRow!).getByText('Electronics')).toBeInTheDocument();
    });

    it('should show action buttons (edit, delete)', () => {
      // Act
      render(
        <CategoryList
          categories={mockCategories}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Assert
      const editButtons = screen.getAllByRole('button', { name: /editar/i });
      const deleteButtons = screen.getAllByRole('button', { name: /excluir/i });
      
      expect(editButtons).toHaveLength(3);
      expect(deleteButtons).toHaveLength(3);
    });

    it('should show empty state when no categories', () => {
      // Act
      render(
        <CategoryList
          categories={[]}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Assert
      expect(screen.getByText(/nenhuma categoria encontrada/i)).toBeInTheDocument();
    });
  });

  describe('Filtering', () => {
    it('should show search input for filtering by name', () => {
      // Act
      render(
        <CategoryList
          categories={mockCategories}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
          onFilter={mockOnFilter}
        />
      );

      // Assert
      expect(screen.getByPlaceholderText(/buscar categoria/i)).toBeInTheDocument();
    });

    it('should call onFilter when search input changes', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryList
          categories={mockCategories}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
          onFilter={mockOnFilter}
        />
      );

      // Act
      const searchInput = screen.getByPlaceholderText(/buscar categoria/i);
      await user.type(searchInput, 'Electronics');

      // Assert
      expect(mockOnFilter).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Electronics',
        })
      );
    });

    it('should show status filter toggle (active/inactive/all)', async () => {
      // Act
      render(
        <CategoryList
          categories={mockCategories}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
          onFilter={mockOnFilter}
        />
      );

      // Assert - Find buttons by text content (may have multiple matches due to action buttons)
      const allButtons = screen.getAllByRole('button');
      expect(allButtons.some(btn => btn.textContent?.includes('Todas'))).toBe(true);
      expect(allButtons.some(btn => btn.textContent?.includes('Ativas'))).toBe(true);
      expect(allButtons.some(btn => btn.textContent?.includes('Inativas'))).toBe(true);
    });
  });

  describe('Actions', () => {
    it('should call onEdit when edit button clicked', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryList
          categories={mockCategories}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Act
      const editButtons = screen.getAllByRole('button', { name: /editar/i });
      await user.click(editButtons[0]);

      // Assert
      expect(mockOnEdit).toHaveBeenCalledWith(mockCategories[0]);
    });

    it('should show confirmation modal before delete', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryList
          categories={mockCategories}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Act
      const deleteButtons = screen.getAllByRole('button', { name: /excluir/i });
      await user.click(deleteButtons[0]);

      // Assert
      expect(screen.getByText(/tem certeza que deseja excluir/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /confirmar/i })).toBeInTheDocument();
    });

    it('should call onDelete after confirmation', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryList
          categories={mockCategories}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Act
      const deleteButtons = screen.getAllByRole('button', { name: /excluir/i });
      await user.click(deleteButtons[0]);
      
      const confirmButton = screen.getByRole('button', { name: /confirmar/i });
      await user.click(confirmButton);

      // Assert
      expect(mockOnDelete).toHaveBeenCalledWith('cat-1');
    });
  });

  describe('Loading and Error States', () => {
    it('should show loading skeleton when loading', () => {
      // Act
      render(
        <CategoryList
          categories={[]}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
          isLoading={true}
        />
      );

      // Assert
      expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
    });

    it('should show error message when error occurs', () => {
      // Act
      render(
        <CategoryList
          categories={[]}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
          error="Failed to load categories"
        />
      );

      // Assert
      expect(screen.getByText(/failed to load categories/i)).toBeInTheDocument();
    });
  });
});
