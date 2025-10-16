/**
 * CategoryList Component
 * 
 * Table view of categories with filters, search, and actions.
 */

import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Modal } from '../ui/Modal';
import type { Category, CategoryFilter } from '../../types/category';

interface CategoryListProps {
  categories: Category[];
  onEdit: (category: Category) => void;
  onDelete: (id: string) => void;
  onFilter?: (filters: CategoryFilter) => void;
  isLoading?: boolean;
  error?: string;
}

export const CategoryList: React.FC<CategoryListProps> = ({
  categories,
  onEdit,
  onDelete,
  onFilter,
  isLoading = false,
  error,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; categoryId?: string; categoryName?: string }>({
    isOpen: false,
  });

  // Find category name by ID (for parent display)
  const getCategoryName = (id: string): string => {
    const category = categories.find(c => c.id === id);
    return category?.name || 'N/A';
  };

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    if (onFilter) {
      onFilter({ name: value || undefined });
    }
  };

  // Handle status filter change
  const handleStatusFilter = (status: 'all' | 'active' | 'inactive') => {
    setStatusFilter(status);
    if (onFilter) {
      const statusValue = status === 'all' ? undefined : status;
      onFilter({ status: statusValue as 'active' | 'inactive' | undefined });
    }
  };

  // Open delete confirmation
  const openDeleteConfirm = (category: Category) => {
    setDeleteConfirm({
      isOpen: true,
      categoryId: category.id,
      categoryName: category.name,
    });
  };

  // Confirm delete
  const confirmDelete = () => {
    if (deleteConfirm.categoryId) {
      onDelete(deleteConfirm.categoryId);
      setDeleteConfirm({ isOpen: false });
    }
  };

  // Loading skeleton
  if (isLoading) {
    return (
      <div data-testid="loading-skeleton" className="space-y-4">
        <div className="h-10 bg-gray-200 rounded animate-pulse" />
        <div className="h-64 bg-gray-200 rounded animate-pulse" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 text-lg">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Buscar categoria..."
            value={searchQuery}
            onChange={handleSearchChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex gap-2">
          <Button
            variant={statusFilter === 'all' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => handleStatusFilter('all')}
          >
            Todas
          </Button>
          <Button
            variant={statusFilter === 'active' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => handleStatusFilter('active')}
          >
            Ativas
          </Button>
          <Button
            variant={statusFilter === 'inactive' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => handleStatusFilter('inactive')}
          >
            Inativas
          </Button>
        </div>
      </div>

      {/* Table */}
      {categories.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500 text-lg">Nenhuma categoria encontrada</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Descrição
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Categoria Pai
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {categories.map((category) => (
                <tr key={category.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{category.name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-500">{category.description || '-'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {category.parent_id ? getCategoryName(category.parent_id) : '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        category.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {category.status === 'active' ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onEdit(category)}
                      >
                        Editar
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => openDeleteConfirm(category)}
                      >
                        Excluir
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteConfirm.isOpen}
        onClose={() => setDeleteConfirm({ isOpen: false })}
        title="Confirmar Exclusão"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            Tem certeza que deseja excluir a categoria <strong>{deleteConfirm.categoryName}</strong>?
          </p>
          <p className="text-sm text-gray-500">
            Esta ação não pode ser desfeita.
          </p>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <Button
            variant="secondary"
            onClick={() => setDeleteConfirm({ isOpen: false })}
          >
            Cancelar
          </Button>
          <Button
            variant="danger"
            onClick={confirmDelete}
          >
            Confirmar
          </Button>
        </div>
      </Modal>
    </div>
  );
};
