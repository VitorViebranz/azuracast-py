export interface User {
  id: string;
  email: string;
  username: string;
  display_name: string | null;
  is_active: boolean;
  is_super_admin: boolean;
  created_at: string;
  updated_at: string;
  roles: Role[];
}

export interface Role {
  id: string;
  name: string;
  description: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface MountPoint {
  id: string;
  station_id: string;
  name: string;
  display_name: string | null;
  mount_path: string;
  is_default: boolean;
  is_public: boolean;
  max_listeners: number;
  bitrate: number;
  format: string;
  created_at: string;
  updated_at: string;
}

export interface Station {
  id: string;
  name: string;
  short_name: string;
  description: string | null;
  timezone: string;
  is_enabled: boolean;
  max_bitrate: number;
  max_mounts: number;
  created_at: string;
  updated_at: string;
  mount_points: MountPoint[];
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  display_name?: string;
}
