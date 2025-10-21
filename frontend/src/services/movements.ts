// API client para Movements
import { api } from './api';
import {
  Movement,
  MovementCreate,
  MovementListResponse,
  MovementFilter,
} from '../types/movement';

export const movementsAPI = {
  async list(params: MovementFilter = {}): Promise<MovementListResponse> {
    const { data } = await api.get<MovementListResponse>('/movements', { params });
    return data;
  },
  async create(payload: MovementCreate): Promise<Movement> {
    const { data } = await api.post<Movement>('/movements', payload);
    return data;
  },
  async get(id: string): Promise<Movement> {
    const { data } = await api.get<Movement>(`/movements/${id}`);
    return data;
  },
};
