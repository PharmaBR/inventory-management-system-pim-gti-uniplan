// React Query hooks para Movements
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { movementsAPI } from '../services/movements';
import { Movement, MovementCreate, MovementFilter, MovementListResponse } from '../types/movement';

export function useMovements(filters: MovementFilter = {}) {
  return useQuery<MovementListResponse, Error>({
    queryKey: ['movements', filters],
    queryFn: () => movementsAPI.list(filters),
    placeholderData: (prev) => prev,
    // keepPreviousData não existe mais na v5, placeholderData já cobre o caso
  });
}

export function useCreateMovement() {
  const queryClient = useQueryClient();
  return useMutation<Movement, Error, MovementCreate>({
    mutationFn: (data) => movementsAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['movements'] });
    },
  });
}

export function useMovement(id: string) {
  return useQuery<Movement, Error>({
    queryKey: ['movements', id],
    queryFn: () => movementsAPI.get(id),
    enabled: !!id,
  });
}
