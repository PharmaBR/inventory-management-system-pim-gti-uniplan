/**
 * CategorySelector Component
 * 
 * Dropdown selector for choosing parent category.
 * Shows hierarchical structure with indentation.
 * Filters out category and its children when editing (prevent circular references).
 */

import React from 'react';
import type { Category } from '../../types/category';

interface CategorySelectorProps {
  categories: Category[];
  value?: string;
  onChange: (categoryId: string | undefined) => void;
  excludeId?: string;
  label?: string;
  disabled?: boolean;
}

/**
 * Build hierarchical list of categories for dropdown
 */
function buildCategoryOptions(
  categories: Category[],
  excludeId?: string
): Array<{ id: string; name: string; level: number }> {
  // Filter out excluded category and its children
  let filtered = categories;
  
  if (excludeId) {
    const excluded = new Set<string>([excludeId]);
    
    // Find all children recursively
    const findChildren = (parentId: string) => {
      categories.forEach((cat) => {
        if (cat.parent_id === parentId && !excluded.has(cat.id)) {
          excluded.add(cat.id);
          findChildren(cat.id);
        }
      });
    };
    
    findChildren(excludeId);
    filtered = categories.filter((cat) => !excluded.has(cat.id));
  }

  // Build tree structure
  const categoryMap = new Map<string, Category>();
  filtered.forEach((cat) => categoryMap.set(cat.id, cat));

  const options: Array<{ id: string; name: string; level: number }> = [];

  const addCategory = (cat: Category, level: number) => {
    const indent = '--'.repeat(level);
    options.push({
      id: cat.id,
      name: level > 0 ? `${indent} ${cat.name}` : cat.name,
      level,
    });

    // Add children
    filtered
      .filter((c) => c.parent_id === cat.id)
      .forEach((child) => addCategory(child, level + 1));
  };

  // Add root categories first
  filtered
    .filter((cat) => !cat.parent_id)
    .forEach((cat) => addCategory(cat, 0));

  return options;
}

export const CategorySelector: React.FC<CategorySelectorProps> = ({
  categories,
  value,
  onChange,
  excludeId,
  label = 'Categoria Pai',
  disabled = false,
}) => {
  const options = buildCategoryOptions(categories, excludeId);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = e.target.value;
    onChange(selectedValue === '' ? undefined : selectedValue);
  };

  return (
    <div className="space-y-2">
      <label htmlFor="category-selector" className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      <select
        id="category-selector"
        value={value || ''}
        onChange={handleChange}
        disabled={disabled}
        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
      >
        <option value="">Nenhuma (Raiz)</option>
        {options.map((option) => (
          <option key={option.id} value={option.id}>
            {option.name}
          </option>
        ))}
      </select>
    </div>
  );
};
