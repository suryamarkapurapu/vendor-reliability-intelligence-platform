export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  full_name: string;
  email: string;
  password: string;
  role_id: number;
}

export interface UserResponse {
  user_id: string;
  username: string;
  full_name: string;
  email: string;
  role_id: number;
  role_name?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
