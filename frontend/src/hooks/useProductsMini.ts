// Hook para buscar produtos simplificados (id, sku, name) para autocomplete
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export interface ProductMini {
  id: string;
  sku: string;
  name: string;
}

export function useProductsMini(query: string) {
  return useQuery<ProductMini[], Error>({
    queryKey: ['products-mini', query],
    queryFn: async () => {
      const { data } = await api.get('/products', {
        params: { page_size: 20, sku: query || undefined, name: query || undefined },
      });
      // Extrai apenas id, sku, name
      return (data.items || []).map((p: any) => ({ id: p.id, sku: p.sku, name: p.name }));
    },
    enabled: !!query,
  });
}
