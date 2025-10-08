export interface User {
  id: number
  username: string
  email: string
  email_verified: boolean
  is_active: boolean
  created_at: string | null
  last_login: string | null
  money: number
  total_value: number
}

export interface AuthResponse {
  message: string
  access_token: string
  user: User
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
}
