import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { apiClient } from '../../services/api'
import { API_ENDPOINTS } from '../../services/apiEndpoints'
import type {
  LedgerResponse,
  LivePortfolioResponse,
  PortfolioHolding,
} from '../../types/portfolio'

interface PortfolioState {
  holdings: PortfolioHolding[]
  totalCash: number
  totalValue: number
  ledger: LedgerResponse | null
  status: 'idle' | 'loading' | 'succeeded' | 'failed'
  error: string | null
}

const initialState: PortfolioState = {
  holdings: [],
  totalCash: 0,
  totalValue: 0,
  ledger: null,
  status: 'idle',
  error: null,
}

export const fetchPortfolio = createAsyncThunk<LivePortfolioResponse>(
  'portfolio/fetchPortfolio',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get<LivePortfolioResponse>(
        API_ENDPOINTS.livePortfolio,
      )
      return response.data
    } catch (error: any) {
      const message =
        error.response?.data?.message ??
        'Unable to load your portfolio. Please try again.'
      return rejectWithValue(message)
    }
  },
)

export const fetchLedger = createAsyncThunk<
  LedgerResponse,
  { page?: number; per_page?: number } | undefined
>('portfolio/fetchLedger', async (params = {}, { rejectWithValue }) => {
  try {
    const response = await apiClient.get<LedgerResponse>(API_ENDPOINTS.ledger, {
      params,
    })
    return response.data
  } catch (error: any) {
    const message =
      error.response?.data?.message ??
      'Unable to load transaction history. Please try again.'
    return rejectWithValue(message)
  }
})

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchPortfolio.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(fetchPortfolio.fulfilled, (state, action) => {
        state.status = 'succeeded'
        state.holdings = action.payload.holdings
        state.totalCash = action.payload.total_cash
        state.totalValue = action.payload.total_value
      })
      .addCase(fetchPortfolio.rejected, (state, action) => {
        state.status = 'failed'
        state.error =
          (action.payload as string) ?? action.error.message ?? null
      })
      .addCase(fetchLedger.fulfilled, (state, action) => {
        state.ledger = action.payload
      })
  },
})

export default portfolioSlice.reducer
