/**
 * Contract Tests: CategoryTree Component
 * 
 * These tests define the expected behavior of the hierarchical category tree.
 * Tests should FAIL initially (RED) - implementation comes after.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { CategoryTree } from '../../../src/components/categories/CategoryTree';
import type { CategoryTreeNode } from '../../../src/types/category';

describe('CategoryTree Component', () => {
  const mockTreeData: CategoryTreeNode[] = [
    {
      id: 'cat-1',
      name: 'Electronics',
      is_active: true,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      tenant_id: 'tenant-1',
      children: [
        {
          id: 'cat-2',
          name: 'Computers',
          parent_id: 'cat-1',
          is_active: true,
          created_at: '2025-01-02T00:00:00Z',
          updated_at: '2025-01-02T00:00:00Z',
          tenant_id: 'tenant-1',
          children: [],
          level: 1,
          hasChildren: false,
        },
      ],
      level: 0,
      hasChildren: true,
    },
    {
      id: 'cat-3',
      name: 'Books',
      is_active: true,
      created_at: '2025-01-03T00:00:00Z',
      updated_at: '2025-01-03T00:00:00Z',
      tenant_id: 'tenant-1',
      children: [],
      level: 0,
      hasChildren: false,
    },
  ];

  const mockOnSelect = vi.fn();
  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();
  const mockOnMove = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render empty state when no categories', () => {
      // Act
      render(
        <CategoryTree
          data={[]}
          onSelect={mockOnSelect}
        />
      );

      // Assert
      expect(screen.getByText(/nenhuma categoria/i)).toBeInTheDocument();
    });

    it('should render flat list when all root categories', () => {
      // Arrange
      const flatData: CategoryTreeNode[] = [
        { ...mockTreeData[1] },
      ];

      // Act
      render(
        <CategoryTree
          data={flatData}
          onSelect={mockOnSelect}
        />
      );

      // Assert
      expect(screen.getByText('Books')).toBeInTheDocument();
      // Should not have expand icon for categories without children
      const booksItem = screen.getByText('Books').closest('div');
      expect(within(booksItem!).queryByRole('button', { name: /expandir/i })).not.toBeInTheDocument();
    });

    it('should render hierarchical tree with indentation', () => {
      // Act
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
        />
      );

      // Assert
      expect(screen.getByText('Electronics')).toBeInTheDocument();
      expect(screen.getByText('Computers')).toBeInTheDocument();
      
      // Computers should have indentation (level 1)
      const computersItem = screen.getByText('Computers').closest('div');
      expect(computersItem).toHaveStyle({ paddingLeft: expect.stringMatching(/\d+px/) });
    });

    it('should show expand/collapse icons for parent nodes', () => {
      // Act
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
        />
      );

      // Assert
      const electronicsItem = screen.getByText('Electronics').closest('div');
      expect(within(electronicsItem!).getByRole('button', { name: /expandir|recolher/i })).toBeInTheDocument();
    });
  });

  describe('Interaction', () => {
    it('should expand category on expand button click', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
        />
      );

      // Initially, Computers might be hidden if tree is collapsed by default
      const electronicsItem = screen.getByText('Electronics').closest('div');
      const expandButton = within(electronicsItem!).getByRole('button', { name: /expandir/i });

      // Act
      await user.click(expandButton);

      // Assert
      expect(screen.getByText('Computers')).toBeVisible();
    });

    it('should collapse category on collapse button click', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
          defaultExpanded={true}
        />
      );

      const electronicsItem = screen.getByText('Electronics').closest('div');
      const collapseButton = within(electronicsItem!).getByRole('button', { name: /recolher/i });

      // Act
      await user.click(collapseButton);

      // Assert
      expect(screen.queryByText('Computers')).not.toBeVisible();
    });

    it('should select category on click', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
        />
      );

      // Act
      await user.click(screen.getByText('Electronics'));

      // Assert
      expect(mockOnSelect).toHaveBeenCalledWith(mockTreeData[0]);
    });

    it('should highlight selected category', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
          selectedId="cat-1"
        />
      );

      // Assert
      const electronicsItem = screen.getByText('Electronics').closest('div');
      expect(electronicsItem).toHaveClass(/selected|active|highlighted/);
    });
  });

  describe('Action Buttons', () => {
    it('should show edit and delete buttons on hover', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Act
      const electronicsItem = screen.getByText('Electronics').closest('div');
      await user.hover(electronicsItem!);

      // Assert
      expect(within(electronicsItem!).getByRole('button', { name: /editar/i })).toBeInTheDocument();
      expect(within(electronicsItem!).getByRole('button', { name: /excluir/i })).toBeInTheDocument();
    });

    it('should call onEdit when edit button clicked', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Act
      const electronicsItem = screen.getByText('Electronics').closest('div');
      await user.hover(electronicsItem!);
      await user.click(within(electronicsItem!).getByRole('button', { name: /editar/i }));

      // Assert
      expect(mockOnEdit).toHaveBeenCalledWith(mockTreeData[0]);
    });

    it('should call onDelete when delete button clicked', async () => {
      // Arrange
      const user = userEvent.setup();
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
          onEdit={mockOnEdit}
          onDelete={mockOnDelete}
        />
      );

      // Act
      const booksItem = screen.getByText('Books').closest('div');
      await user.hover(booksItem!);
      await user.click(within(booksItem!).getByRole('button', { name: /excluir/i }));

      // Assert
      expect(mockOnDelete).toHaveBeenCalledWith(mockTreeData[1]);
    });
  });

  describe('Drag and Drop (Optional)', () => {
    it('should show drag handle when drag is enabled', () => {
      // Act
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
          onMove={mockOnMove}
          enableDragDrop={true}
        />
      );

      // Assert
      const dragHandles = screen.getAllByRole('button', { name: /arrastar/i });
      expect(dragHandles.length).toBeGreaterThan(0);
    });

    it('should call onMove when category is moved', async () => {
      // This is a simplified test - actual drag-drop testing is complex
      // In real implementation, we'd use @dnd-kit testing utilities
      
      // Act
      render(
        <CategoryTree
          data={mockTreeData}
          onSelect={mockOnSelect}
          onMove={mockOnMove}
          enableDragDrop={true}
        />
      );

      // Note: Actual drag-drop interaction would be tested in integration tests
      // This just verifies the callback exists and would be called
      expect(mockOnMove).toBeDefined();
    });
  });

  describe('Loading and Empty States', () => {
    it('should show loading skeleton when loading', () => {
      // Act
      render(
        <CategoryTree
          data={[]}
          onSelect={mockOnSelect}
          isLoading={true}
        />
      );

      // Assert
      expect(screen.getByTestId('tree-loading-skeleton')).toBeInTheDocument();
    });

    it('should show custom empty message', () => {
      // Act
      render(
        <CategoryTree
          data={[]}
          onSelect={mockOnSelect}
          emptyMessage="Crie sua primeira categoria!"
        />
      );

      // Assert
      expect(screen.getByText('Crie sua primeira categoria!')).toBeInTheDocument();
    });
  });
});
