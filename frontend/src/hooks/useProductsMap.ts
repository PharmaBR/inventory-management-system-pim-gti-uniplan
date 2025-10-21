// Hook para mapear product_id para nome/SKU rapidamente
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';

export function useProductsMap(ids: string[]) {
  return useQuery<{ [id: string]: { sku: string; name: string } }, Error>({
    queryKey: ['products-map', ids.sort().join(',')],
    queryFn: async () => {
      if (!ids.length) return {};
      const { data } = await api.get('/products', {
        params: { page_size: ids.length, ids: ids.join(',') },
      });
      const map: { [id: string]: { sku: string; name: string } } = {};
      (data.items || []).forEach((p: any) => {
        map[p.id] = { sku: p.sku, name: p.name };
      });
      return map;
    },
    enabled: !!ids.length,
  });
}
