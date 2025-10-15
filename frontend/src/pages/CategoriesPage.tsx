/**
 * CategoriesPage
 * 
 * Main page for category management with list/tree toggle.
 */

import React, { useState } from 'react';
import { CategoryList } from '../components/categories/CategoryList';
import { CategoryTree } from '../components/categories/CategoryTree';
import { CategoryForm } from '../components/categories/CategoryForm';
import { Button } from '../components/ui/Button';
import { 
  useCategories, 
  useCreateCategory, 
  useUpdateCategory, 
  useDeleteCategory 
} from '../hooks/useCategories';
import type { Category, CategoryFilter, CategoryCreate, CategoryUpdate } from '../types/category';

type ViewMode = 'list' | 'tree';
type FormMode = 'create' | 'edit' | null;

export const CategoriesPage: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [formMode, setFormMode] = useState<FormMode>(null);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [filters, setFilters] = useState<CategoryFilter>({});
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Queries and mutations
  const { data, isLoading, isError } = useCategories(filters);
  const createMutation = useCreateCategory();
  const updateMutation = useUpdateCategory();
  const deleteMutation = useDeleteCategory();

  const categories = data?.items || [];

  // Show toast
  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  // Handlers
  const handleCreate = (data: CategoryCreate) => {
    createMutation.mutate(data, {
      onSuccess: () => {
        showToast('Categoria criada com sucesso!');
        setFormMode(null);
      },
      onError: () => {
        showToast('Erro ao criar categoria', 'error');
      },
    });
  };

  const handleUpdate = (id: string, data: CategoryUpdate) => {
    updateMutation.mutate({ id, data }, {
      onSuccess: () => {
        showToast('Categoria atualizada com sucesso!');
        setFormMode(null);
        setSelectedCategory(null);
      },
      onError: () => {
        showToast('Erro ao atualizar categoria', 'error');
      },
    });
  };

  const handleDelete = (id: string) => {
    const category = categories.find(c => c.id === id);
    if (!category || !window.confirm(`Deseja realmente excluir "${category.name}"?`)) {
      return;
    }

    deleteMutation.mutate(id, {
      onSuccess: () => {
        showToast('Categoria excluída com sucesso!');
      },
      onError: () => {
        showToast('Erro ao excluir categoria', 'error');
      },
    });
  };

  const handleEdit = (category: Category) => {
    setSelectedCategory(category);
    setFormMode('edit');
  };

  const handleCloseForm = () => {
    setFormMode(null);
    setSelectedCategory(null);
  };

  const handleFilterChange = (newFilters: CategoryFilter) => {
    setFilters(newFilters);
  };

  // Build tree data from flat list
  const buildTreeData = (items: Category[]) => {
    const map = new Map<string, any>();
    const roots: any[] = [];

    items.forEach(item => {
      map.set(item.id, {
        ...item,
        children: [],
        level: 0,
        hasChildren: false,
      });
    });

    items.forEach(item => {
      const node = map.get(item.id)!;
      if (item.parent_id && map.has(item.parent_id)) {
        const parent = map.get(item.parent_id)!;
        parent.children.push(node);
        parent.hasChildren = true;
        node.level = (parent.level || 0) + 1;
      } else {
        roots.push(node);
      }
    });

    return roots;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Categorias</h1>
        
        <div className="flex gap-4">
          {/* View Toggle */}
          <div className="flex gap-1 border rounded-md p-1">
            <Button
              variant={viewMode === 'tree' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('tree')}
              className={viewMode === 'tree' ? 'active' : ''}
            >
              Árvore
            </Button>
            <Button
              variant={viewMode === 'list' ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              className={viewMode === 'list' ? 'active' : ''}
            >
              Lista
            </Button>
          </div>

          {/* New Category Button */}
          <Button
            variant="primary"
            onClick={() => setFormMode('create')}
          >
            Nova Categoria
          </Button>
        </div>
      </div>

      {/* Toast Notification */}
      {toast && (
        <div
          className={`mb-4 p-4 rounded-md ${
            toast.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}
        >
          {toast.message}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div data-testid="categories-loading" className="text-center py-12">
          <p className="text-gray-500">Carregando categorias...</p>
        </div>
      )}

      {/* Error State */}
      {isError && (
        <div className="text-center py-12 text-red-600">
          <p>Erro ao carregar categorias. Por favor, tente novamente.</p>
        </div>
      )}

      {/* Content */}
      {!isLoading && !isError && (
        <>
          {viewMode === 'list' && (
            <CategoryList
              categories={categories}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onFilter={handleFilterChange}
            />
          )}

          {viewMode === 'tree' && (
            <CategoryTree
              data={buildTreeData(categories)}
              onSelect={(category) => console.log('Selected:', category)}
              onEdit={handleEdit}
              onDelete={(category) => handleDelete(category.id)}
            />
          )}
        </>
      )}

      {/* Create/Edit Form Modal */}
      {formMode && (
        <CategoryForm
          mode={formMode}
          category={formMode === 'edit' && selectedCategory ? selectedCategory : undefined}
          onCreate={handleCreate}
          onUpdate={(id, data) => handleUpdate(id, data)}
          onCancel={handleCloseForm}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />
      )}
    </div>
  );
};
