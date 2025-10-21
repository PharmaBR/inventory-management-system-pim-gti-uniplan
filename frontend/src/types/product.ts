/**
 * Product Type Definitions
 * Matches backend ProductResponse and request schemas
 */

export type ProductStatus = 'active' | 'inactive';

export interface Product {
  id: string;
  tenant_id: string;
  name: string;
  sku: string;
  description?: string;
  quantity: number;
  min_quantity?: number | null;
  max_quantity?: number | null;
  price: number;
  category_id?: string | null;
  custom_fields?: Record<string, any> | null;
  unit?: string | null;
  location?: string | null;
  status: ProductStatus;
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  name: string;
  sku: string;
  description?: string;
  quantity: number;
  min_quantity?: number | null;
  max_quantity?: number | null;
  price: number;
  category_id?: string | null;
  custom_fields?: Record<string, any> | null;
  unit?: string | null;
  location?: string | null;
  status?: ProductStatus;
}

export interface ProductUpdate {
  name?: string;
  sku?: string;
  description?: string;
  quantity?: number;
  min_quantity?: number | null;
  max_quantity?: number | null;
  price?: number;
  category_id?: string | null;
  custom_fields?: Record<string, any> | null;
  unit?: string | null;
  location?: string | null;
  status?: ProductStatus;
}

export interface ProductFilter {
  page?: number;
  page_size?: number;
  name?: string;
  sku?: string;
  category_id?: string;
  status?: ProductStatus;
  min_quantity?: number;
  max_quantity?: number;
  min_price?: number;
  max_price?: number;
  sort_by?: 'name' | 'sku' | 'quantity' | 'price' | 'created_at' | 'updated_at';
  sort_order?: 'asc' | 'desc';
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
