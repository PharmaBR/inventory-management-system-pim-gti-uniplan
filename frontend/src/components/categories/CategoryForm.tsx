/**
 * CategoryForm Component
 * 
 * Modal form for creating or editing categories.
 * Supports both create and edit modes with validation.
 */

import React, { useState, useEffect } from 'react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { CategorySelector } from './CategorySelector';
import type { Category, CategoryCreate, CategoryUpdate } from '../../types/category';

interface CategoryFormProps {
  mode: 'create' | 'edit';
  category?: Category;
  availableCategories?: Category[];
  onCreate?: (data: CategoryCreate) => void | Promise<void>;
  onUpdate?: (id: string, data: CategoryUpdate) => void | Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export const CategoryForm: React.FC<CategoryFormProps> = ({
  mode,
  category,
  availableCategories = [],
  onCreate,
  onUpdate,
  onCancel,
  isLoading: externalLoading = false,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [parentId, setParentId] = useState<string | undefined>(undefined);
  const [status, setStatus] = useState<'active' | 'inactive'>('active');
  const [errors, setErrors] = useState<{ name?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Pre-populate form in edit mode
  useEffect(() => {
    if (mode === 'edit' && category) {
      setName(category.name);
      setDescription(category.description || '');
      setParentId(category.parent_id);
      setStatus(category.status);
    }
  }, [mode, category]);

  const validate = (): boolean => {
    const newErrors: { name?: string } = {};

    const trimmedName = name.trim();
    if (!trimmedName) {
      newErrors.name = 'Nome é obrigatório';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const trimmedName = name.trim();
      const trimmedDescription = description.trim();

      if (mode === 'create' && onCreate) {
        const data: CategoryCreate = {
          name: trimmedName,
          description: trimmedDescription || undefined,
          parent_id: parentId,
          status: status,
        };
        await onCreate(data);
      } else if (mode === 'edit' && onUpdate && category) {
        const data: CategoryUpdate = {
          name: trimmedName,
          description: trimmedDescription || undefined,
          parent_id: parentId,
          status: status,
        };
        await onUpdate(category.id, data);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const isLoading = isSubmitting || externalLoading;
  const title = mode === 'create' ? 'Criar Categoria' : 'Editar Categoria';
  const submitLabel = mode === 'create'
    ? (isLoading ? 'Criando...' : 'Criar')
    : (isLoading ? 'Salvando...' : 'Salvar');

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">{title}</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Nome"
          name="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={errors.name}
          disabled={isLoading}
          required
          autoFocus
        />

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Descrição
          </label>
          <textarea
            id="description"
            name="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isLoading}
            rows={3}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
        </div>

        {availableCategories.length > 0 && (
          <CategorySelector
            label="Categoria Pai"
            categories={availableCategories}
            value={parentId}
            onChange={setParentId}
            excludeId={mode === 'edit' ? category?.id : undefined}
            disabled={isLoading}
          />
        )}

        {mode === 'edit' && (
          <div className="flex items-center">
            <input
              type="checkbox"
              id="status"
              name="status"
              checked={status === 'active'}
              onChange={(e) => setStatus(e.target.checked ? 'active' : 'inactive')}
              disabled={isLoading}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            />
            <label htmlFor="status" className="ml-2 block text-sm text-gray-900">
              Ativo
            </label>
          </div>
        )}

        <div className="flex justify-end space-x-3 pt-4">
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={isLoading}
          >
            {submitLabel}
          </Button>
        </div>
      </form>
    </div>
  );
};
