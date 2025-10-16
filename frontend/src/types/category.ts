/**
 * Category Type Definitions
 * 
 * TypeScript interfaces matching backend CategoryResponse schemas.
 */

/**
 * Main Category interface matching backend CategoryResponse
 */
export interface Category {
  id: string;
  name: string;
  description?: string;
  parent_id?: string;
  status: 'active' | 'inactive';
  created_at: string;
  updated_at: string;
  tenant_id: string;
}

/**
 * Category creation payload
 */
export interface CategoryCreate {
  name: string;
  description?: string;
  parent_id?: string;
  status?: 'active' | 'inactive';
}

/**
 * Category update payload (all fields optional)
 */
export interface CategoryUpdate {
  name?: string;
  description?: string;
  parent_id?: string;
  status?: 'active' | 'inactive';
}

/**
 * Category list filters
 */
export interface CategoryFilter {
  name?: string;
  status?: 'active' | 'inactive';
  parent_id?: string;
  root_only?: boolean;
  skip?: number;
  limit?: number;
}

/**
 * Category list response from API
 */
export interface CategoryListResponse {
  items: Category[];
  total: number;
  skip: number;
  limit: number;
}

/**
 * Category tree node with children for hierarchical display
 */
export interface CategoryTreeNode extends Category {
  children: CategoryTreeNode[];
  level: number;
  hasChildren: boolean;
  isExpanded?: boolean;
}

/**
 * Sort options for category list
 */
export type CategorySortField = 'name' | 'created_at' | 'updated_at';
export type CategorySortOrder = 'asc' | 'desc';

export interface CategorySort {
  field: CategorySortField;
  order: CategorySortOrder;
}
