import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from './client';
import { Station } from '../types/api';

export interface StationCreate {
  name: string;
  short_name: string;
  description?: string;
  timezone?: string;
  is_enabled?: boolean;
  max_bitrate?: number;
  max_mounts?: number;
}

export function useStations() {
  return useQuery<Station[]>({
    queryKey: ['stations'],
    queryFn: async () => {
      const res = await apiClient.get<Station[]>('/api/v1/stations');
      return res.data;
    },
  });
}

export function useCreateStation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: StationCreate) => {
      const res = await apiClient.post<Station>('/api/v1/stations', data);
      return res.data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['stations'] }),
  });
}

export function useDeleteStation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/stations/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['stations'] }),
  });
}
