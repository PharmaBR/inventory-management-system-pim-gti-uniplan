import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { productsAPI } from '../services/api';
import type { Product, ProductCreate, ProductUpdate, ProductFilter, ProductListResponse } from '../types/product';

const productKeys = {
  all: ['products'] as const,
  lists: () => [...productKeys.all, 'list'] as const,
  list: (filters: ProductFilter) => [...productKeys.lists(), filters] as const,
  details: () => [...productKeys.all, 'detail'] as const,
  detail: (id: string) => [...productKeys.details(), id] as const,
};

export const useProducts = (filters: ProductFilter = {}) => {
  return useQuery({
    queryKey: productKeys.list(filters),
    queryFn: async (): Promise<ProductListResponse> => {
      const res = await productsAPI.list(filters);
      return res.data as ProductListResponse;
    },
    placeholderData: keepPreviousData,
  });
};

export const useProduct = (id?: string) => {
  return useQuery({
    queryKey: id ? productKeys.detail(id) : ['products', 'detail', 'undefined'],
    queryFn: async (): Promise<Product> => {
      if (!id) throw new Error('Product ID is required');
      const res = await productsAPI.get(id);
      return res.data as Product;
    },
    enabled: !!id,
  });
};

export const useCreateProduct = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: ProductCreate): Promise<Product> => {
      const res = await productsAPI.create(data);
      return res.data as Product;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
    },
  });
};

export const useUpdateProduct = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: ProductUpdate }): Promise<Product> => {
      const res = await productsAPI.update(id, data);
      return res.data as Product;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
      queryClient.invalidateQueries({ queryKey: productKeys.detail(variables.id) });
    },
  });
};

export const useDeleteProduct = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await productsAPI.delete(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
    },
  });
};
