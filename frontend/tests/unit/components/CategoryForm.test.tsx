/**
 * Contract Tests: CategoryForm Component
 * 
 * These tests define the expected behavior of the category create/edit form.
 * Tests should FAIL initially (RED) - implementation comes after.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { CategoryForm } from '../../../src/components/categories/CategoryForm';
import type { Category } from '../../../src/types/category';

describe('CategoryForm Component', () => {
  const mockOnCreate = vi.fn();
  const mockOnUpdate = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Create Mode', () => {
    it('should render empty form for create mode', () => {
      // Act
      render(
        <CategoryForm
          mode="create"
          onCreate={mockOnCreate}
          onCancel={mockOnCancel}
        />
      );

      // Assert
      expect(screen.getByLabelText(/nome/i)).toHaveValue('');
      expect(screen.getByLabelText(/descrição/i)).toHaveValue('');
    });

    it('should have "Criar Categoria" title in create mode', () => {
      // Act
      render(
        <CategoryForm
          mode="create"
          onCreate={mockOnCreate}
          onCancel={mockOnCancel}
        />
      );

      // Assert
      expect(screen.getByRole('heading', { name: /criar categoria/i })).toBeInTheDocument();
    });

    it('should show parent category selector as optional', () => {
      // Arrange
      const mockCategories: Category[] = [
        {
          id: 'cat-1',
          name: 'Electronics',
          is_active: true,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
          tenant_id: 'tenant-1',
        },
      ];

      // Act
      render(
        <CategoryForm
          mode="create"
          onCreate={mockOnCreate}
          onCancel={mockOnCancel}
          availableCategories={mockCategories}
        />
      );

      // Assert
      expect(screen.getByLabelText(/categoria pai/i)).toBeInTheDocument();
      // Should have "Nenhuma" option for root level
      expect(screen.getByRole('option', { name: /nenhuma/i })).toBeInTheDocument();
    });

    it('should validate required name field', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryForm
          mode="create"
          onCreate={mockOnCreate}
          onCancel={mockOnCancel}
        />
      );

      // Act - Try to submit without name (empty string)
      const submitButton = screen.getByRole('button', { name: /criar/i });
      await user.click(submitButton);

      // Wait for any async operations
      await new Promise(resolve => setTimeout(resolve, 200));

      // Assert - onCreate should NOT be called because validation failed
      expect(mockOnCreate).not.toHaveBeenCalled();
    });

    it('should call onCreate on valid submit', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryForm
          mode="create"
          onCreate={mockOnCreate}
          onCancel={mockOnCancel}
        />
      );

      // Act
      await user.type(screen.getByLabelText(/nome/i), 'New Category');
      await user.type(screen.getByLabelText(/descrição/i), 'Test description');
      await user.click(screen.getByRole('button', { name: /criar/i }));

      // Assert
      await waitFor(() => {
        expect(mockOnCreate).toHaveBeenCalledWith({
          name: 'New Category',
          description: 'Test description',
        });
      });
    });

    it('should trim whitespace from name', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryForm
          mode="create"
          onCreate={mockOnCreate}
          onCancel={mockOnCancel}
        />
      );

      // Act
      await user.type(screen.getByLabelText(/nome/i), '  Trimmed Name  ');
      await user.click(screen.getByRole('button', { name: /criar/i }));

      // Assert
      await waitFor(() => {
        expect(mockOnCreate).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'Trimmed Name',
          })
        );
      });
    });
  });

  describe('Edit Mode', () => {
    const mockCategory: Category = {
      id: 'cat-123',
      name: 'Electronics',
      description: 'Electronic devices',
      is_active: true,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      tenant_id: 'tenant-1',
    };

    it('should pre-populate form with category data', () => {
      // Act
      render(
        <CategoryForm
          mode="edit"
          category={mockCategory}
          onUpdate={mockOnUpdate}
          onCancel={mockOnCancel}
        />
      );

      // Assert
      expect(screen.getByLabelText(/nome/i)).toHaveValue('Electronics');
      expect(screen.getByLabelText(/descrição/i)).toHaveValue('Electronic devices');
    });

    it('should have "Editar Categoria" title in edit mode', () => {
      // Act
      render(
        <CategoryForm
          mode="edit"
          category={mockCategory}
          onUpdate={mockOnUpdate}
          onCancel={mockOnCancel}
        />
      );

      // Assert
      expect(screen.getByRole('heading', { name: /editar categoria/i })).toBeInTheDocument();
    });

    it('should call onUpdate on submit with changes', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryForm
          mode="edit"
          category={mockCategory}
          onUpdate={mockOnUpdate}
          onCancel={mockOnCancel}
        />
      );

      // Act
      const nameInput = screen.getByLabelText(/nome/i);
      await user.clear(nameInput);
      await user.type(nameInput, 'Updated Electronics');
      await user.click(screen.getByRole('button', { name: /salvar/i }));

      // Assert
      await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalledWith('cat-123', 
          expect.objectContaining({
            name: 'Updated Electronics',
            description: 'Electronic devices',
          })
        );
      });
    });

    it('should show active status toggle in edit mode', () => {
      // Act
      render(
        <CategoryForm
          mode="edit"
          category={mockCategory}
          onUpdate={mockOnUpdate}
          onCancel={mockOnCancel}
        />
      );

      // Assert
      const statusToggle = screen.getByRole('checkbox', { name: /ativo/i });
      expect(statusToggle).toBeInTheDocument();
      expect(statusToggle).toBeChecked();
    });
  });

  describe('Common Behavior', () => {
    it('should call onCancel when cancel button clicked', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryForm
          mode="create"
          onCreate={mockOnCreate}
          onCancel={mockOnCancel}
        />
      );

      // Act
      await user.click(screen.getByRole('button', { name: /cancelar/i }));

      // Assert
      expect(mockOnCancel).toHaveBeenCalled();
    });

    it('should show loading state during submission', async () => {
      // Arrange
      const user = userEvent.setup();
      const slowOnCreate = vi.fn(() => new Promise(() => {})); // Never resolves
      
      render(
        <CategoryForm
          mode="create"
          onCreate={slowOnCreate}
          onCancel={mockOnCancel}
        />
      );

      // Act
      await user.type(screen.getByLabelText(/nome/i), 'Test');
      await user.click(screen.getByRole('button', { name: /criar/i }));

      // Assert
      await waitFor(() => {
        const submitButton = screen.getByRole('button', { name: /criando/i });
        expect(submitButton).toBeDisabled();
      });
    });

    it('should disable form inputs during submission', async () => {
      // Arrange
      const user = userEvent.setup();
      const slowOnCreate = vi.fn(() => new Promise(() => {}));
      
      render(
        <CategoryForm
          mode="create"
          onCreate={slowOnCreate}
          onCancel={mockOnCancel}
        />
      );

      // Act
      await user.type(screen.getByLabelText(/nome/i), 'Test');
      await user.click(screen.getByRole('button', { name: /criar/i }));

      // Assert
      await waitFor(() => {
        expect(screen.getByLabelText(/nome/i)).toBeDisabled();
        expect(screen.getByLabelText(/descrição/i)).toBeDisabled();
      });
    });
  });
});
