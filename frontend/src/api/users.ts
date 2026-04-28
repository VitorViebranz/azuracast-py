import { useQuery } from '@tanstack/react-query';
import apiClient from './client';
import { User } from '../types/api';

export function useUsers() {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await apiClient.get<User[]>('/api/v1/users');
      return res.data;
    },
  });
}
