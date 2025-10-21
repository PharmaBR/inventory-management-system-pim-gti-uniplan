
// Tipos para Movements
type MovementType = 'entry' | 'exit' | 'adjustment';

export interface Movement {
  id: string;
  tenant_id: string;
  product_id: string;
  type: MovementType;
  quantity: number; // delta (positivo ou negativo)
  balance_after: number;
  reason?: string;
  notes?: string;
  user_id?: string;
  created_at: string;
  updated_at: string;
}

export interface MovementCreate {
  product_id: string;
  type: MovementType;
  quantity: number;
  reason?: string;
  notes?: string;
}

export interface MovementListResponse {
  items: Movement[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface MovementFilter {
  page?: number;
  page_size?: number;
  product_id?: string;
  type?: MovementType;
  min_date?: string;
  max_date?: string;
}
