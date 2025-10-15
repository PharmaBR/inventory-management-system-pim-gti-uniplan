/**
 * Contract Tests: CategorySelector Component
 * 
 * Dropdown selector for choosing parent category (used in forms).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { CategorySelector } from '../../../src/components/categories/CategorySelector';
import type { Category } from '../../../src/types/category';

describe('CategorySelector Component', () => {
  const mockCategories: Category[] = [
    {
      id: 'cat-1',
      name: 'Electronics',
      is_active: true,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      tenant_id: 'tenant-1',
    },
    {
      id: 'cat-2',
      name: 'Computers',
      parent_id: 'cat-1',
      is_active: true,
      created_at: '2025-01-02T00:00:00Z',
      updated_at: '2025-01-02T00:00:00Z',
      tenant_id: 'tenant-1',
    },
    {
      id: 'cat-3',
      name: 'Laptops',
      parent_id: 'cat-2',
      is_active: true,
      created_at: '2025-01-03T00:00:00Z',
      updated_at: '2025-01-03T00:00:00Z',
      tenant_id: 'tenant-1',
    },
  ];

  const mockOnChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render as dropdown/select', () => {
      // Act
      render(
        <CategorySelector
          categories={mockCategories}
          onChange={mockOnChange}
        />
      );

      // Assert
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });

    it('should show "Nenhuma" option for root level', () => {
      // Act
      render(
        <CategorySelector
          categories={mockCategories}
          onChange={mockOnChange}
        />
      );

      // Assert
      expect(screen.getByRole('option', { name: /nenhuma/i })).toBeInTheDocument();
    });

    it('should show hierarchical structure with indentation', () => {
      // Act
      render(
        <CategorySelector
          categories={mockCategories}
          onChange={mockOnChange}
        />
      );

      // Assert
      // Options should show indentation: Electronics, -- Computers, ---- Laptops
      const options = screen.getAllByRole('option');
      expect(options.length).toBeGreaterThan(0);
      
      // Check that nested categories have visual indicator (e.g., "-- Computers")
      expect(screen.getByRole('option', { name: /computers/i })).toBeInTheDocument();
    });

    it('should pre-select current value', () => {
      // Act
      render(
        <CategorySelector
          categories={mockCategories}
          value="cat-1"
          onChange={mockOnChange}
        />
      );

      // Assert
      const select = screen.getByRole('combobox') as HTMLSelectElement;
      expect(select.value).toBe('cat-1');
    });
  });

  describe('Interaction', () => {
    it('should call onChange when selection changes', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategorySelector
          categories={mockCategories}
          onChange={mockOnChange}
        />
      );

      // Act
      await user.selectOptions(screen.getByRole('combobox'), 'cat-1');

      // Assert
      expect(mockOnChange).toHaveBeenCalledWith('cat-1');
    });

    it('should call onChange with undefined when "Nenhuma" selected', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategorySelector
          categories={mockCategories}
          value="cat-1"
          onChange={mockOnChange}
        />
      );

      // Act
      await user.selectOptions(screen.getByRole('combobox'), '');

      // Assert
      expect(mockOnChange).toHaveBeenCalledWith(undefined);
    });
  });

  describe('Filtering (when editing)', () => {
    it('should filter out category itself when excludeId provided', () => {
      // Act
      render(
        <CategorySelector
          categories={mockCategories}
          excludeId="cat-1"
          onChange={mockOnChange}
        />
      );

      // Assert - Electronics should be excluded, but its children too (to prevent circular refs)
      expect(screen.queryByRole('option', { name: /^electronics$/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('option', { name: /computers/i })).not.toBeInTheDocument();
    });

    it('should filter out children when excludeId provided', () => {
      // Act
      render(
        <CategorySelector
          categories={mockCategories}
          excludeId="cat-1"
          onChange={mockOnChange}
        />
      );

      // Assert - Electronics and its children (Computers, Laptops) should be excluded
      expect(screen.queryByRole('option', { name: /electronics/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('option', { name: /computers/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('option', { name: /laptops/i })).not.toBeInTheDocument();
    });
  });
});
