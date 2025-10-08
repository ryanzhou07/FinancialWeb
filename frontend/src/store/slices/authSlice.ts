import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { apiClient, getAuthToken, setAuthToken } from '../../services/api'
import { API_ENDPOINTS } from '../../services/apiEndpoints'
import type {
  AuthResponse,
  LoginPayload,
  RegisterPayload,
  User,
} from '../../types/auth'

export interface AuthState {
  user: User | null
  token: string | null
  status: 'idle' | 'loading' | 'succeeded' | 'failed'
  error: string | null
}

const initialToken = getAuthToken()

const initialState: AuthState = {
  user: null,
  token: initialToken,
  status: 'idle',
  error: null,
}

export const loginUser = createAsyncThunk<AuthResponse, LoginPayload>(
  'auth/login',
  async (payload, { rejectWithValue }) => {
    try {
      const response = await apiClient.post<AuthResponse>(
        API_ENDPOINTS.login,
        payload,
      )
      return response.data
    } catch (error: any) {
      const message =
        error.response?.data?.message ?? 'Unable to login. Please try again.'
      return rejectWithValue(message)
    }
  },
)

export const registerUser = createAsyncThunk<AuthResponse, RegisterPayload>(
  'auth/register',
  async (payload, { rejectWithValue }) => {
    try {
      const response = await apiClient.post<AuthResponse>(
        API_ENDPOINTS.register,
        payload,
      )
      return response.data
    } catch (error: any) {
      const message =
        error.response?.data?.message ??
        'Unable to create your account. Please try again.'
      return rejectWithValue(message)
    }
  },
)

export const fetchCurrentUser = createAsyncThunk<User>(
  'auth/me',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<{ user: User }>(API_ENDPOINTS.me)
      return response.data.user
    } catch (error: any) {
      const message =
        error.response?.data?.message ?? 'Your session has expired.'
      return rejectWithValue(message)
    }
  },
)

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout(state) {
      state.user = null
      state.token = null
      state.status = 'idle'
      state.error = null
      setAuthToken(null)
    },
    setUser(state, action) {
      state.user = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.user = action.payload.user
        state.token = action.payload.access_token
        setAuthToken(action.payload.access_token)
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = 'failed'
        state.error = (action.payload as string) ?? action.error.message ?? null
      })
      .addCase(registerUser.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.user = action.payload.user
        state.token = action.payload.access_token
        setAuthToken(action.payload.access_token)
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.status = 'failed'
        state.error = (action.payload as string) ?? action.error.message ?? null
      })
      .addCase(fetchCurrentUser.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.user = action.payload
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        state.status = 'failed'
        state.error = (action.payload as string) ?? action.error.message ?? null
        state.user = null
        state.token = null
        setAuthToken(null)
      })
  },
})

export const { logout, setUser } = authSlice.actions
export default authSlice.reducer
