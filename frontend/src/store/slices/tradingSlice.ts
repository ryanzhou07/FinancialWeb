import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import { apiClient } from '../../services/api'
import { API_ENDPOINTS } from '../../services/apiEndpoints'
import type {
  StockHistoricalPoint,
  StockHistoricalResponse,
  StockSummary,
} from '../../types/stock'

interface TradePayload {
  ticker: string
  shares: number
  price: number
  side: 'Buy' | 'Sell'
}

interface TradingState {
  searchResults: StockSummary[]
  searching: boolean
  selectedSymbol: string | null
  historicalData: StockHistoricalPoint[]
  loadingHistory: boolean
  latestPrice: number | null
  stats: {
    open: number | null
    high: number | null
    low: number | null
    volume: number | null
  }
  orderStatus: 'idle' | 'loading' | 'succeeded' | 'failed'
  orderError: string | null
  orderMessage: string | null
}

const initialState: TradingState = {
  searchResults: [],
  searching: false,
  selectedSymbol: null,
  historicalData: [],
  loadingHistory: false,
  latestPrice: null,
  stats: {
    open: null,
    high: null,
    low: null,
    volume: null,
  },
  orderStatus: 'idle',
  orderError: null,
  orderMessage: null,
}

export const searchStocks = createAsyncThunk<
  StockSummary[],
  string,
  { rejectValue: string }
>('trading/searchStocks', async (query, { rejectWithValue }) => {
  try {
    if (!query) {
      return []
    }
    const response = await apiClient.get<StockSummary[]>(API_ENDPOINTS.searchStocks, {
      params: { q: query },
    })
    return response.data
  } catch (error: any) {
    const message =
      error.response?.data?.message ??
      'Unable to search stocks right now. Please try again.'
    return rejectWithValue(message)
  }
})

export const fetchHistoricalData = createAsyncThunk<
  StockHistoricalPoint[],
  string,
  { rejectValue: string }
>('trading/fetchHistoricalData', async (symbol, { rejectWithValue }) => {
  try {
    const response = await apiClient.get<StockHistoricalResponse>(
      API_ENDPOINTS.stockHistory(symbol),
    )
    if (import.meta.env.DEV) {
      console.debug('[tradingSlice] Raw historical data', symbol, response.data)
    }

    const raw = response.data
    let valuesCandidate: unknown

    if (Array.isArray(raw)) {
      valuesCandidate = raw
    } else if (raw && typeof raw === 'object' && 'values' in raw) {
      valuesCandidate = (raw as { values: unknown }).values
    }

    if (!Array.isArray(valuesCandidate)) {
      if (import.meta.env.DEV) {
        console.warn(
          '[tradingSlice] Historical data not an array, defaulting to empty list',
          symbol,
          valuesCandidate,
        )
      }
      return []
    }

    return valuesCandidate
  } catch (error: any) {
    const message =
      error.response?.data?.message ??
      'Unable to load historical data. Please try again.'
    return rejectWithValue(message)
  }
})

export const placeOrder = createAsyncThunk<
  { message: string },
  TradePayload,
  { rejectValue: string }
>('trading/placeOrder', async (payload, { rejectWithValue }) => {
  try {
    const endpoint =
      payload.side === 'Buy' ? API_ENDPOINTS.buy : API_ENDPOINTS.sell
    const response = await apiClient.post(endpoint, {
      ticker: payload.ticker.toUpperCase(),
      shares: payload.shares,
      price: payload.price,
    })
    return response.data
  } catch (error: any) {
    const message =
      error.response?.data?.message ??
      'Unable to place order right now. Please try again.'
    return rejectWithValue(message)
  }
})

const computeStats = (historicalData: StockHistoricalPoint[]) => {
  if (!historicalData.length) {
    return {
      open: null,
      high: null,
      low: null,
      volume: null,
    }
  }

  const latest = historicalData[0]
  const open = Number.parseFloat(latest.open)
  const high = Number.parseFloat(latest.high)
  const low = Number.parseFloat(latest.low)
  const volume = historicalData.reduce((acc, point) => {
    const parsed = Number.parseFloat(point.volume ?? '0')
    return acc + (Number.isNaN(parsed) ? 0 : parsed)
  }, 0)

  return {
    open: Number.isFinite(open) ? open : null,
    high: Number.isFinite(high) ? high : null,
    low: Number.isFinite(low) ? low : null,
    volume: Number.isFinite(volume) ? volume : null,
  }
}

const tradingSlice = createSlice({
  name: 'trading',
  initialState,
  reducers: {
    setSelectedSymbol(state, action: PayloadAction<string | null>) {
      state.selectedSymbol = action.payload
      state.latestPrice = null
      if (!action.payload) {
        state.historicalData = []
        state.stats = {
          open: null,
          high: null,
          low: null,
          volume: null,
        }
      }
    },
    setLatestPrice(state, action: PayloadAction<number>) {
      state.latestPrice = action.payload
    },
    clearOrderStatus(state) {
      state.orderStatus = 'idle'
      state.orderError = null
      state.orderMessage = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(searchStocks.pending, (state) => {
        state.searching = true
      })
      .addCase(searchStocks.fulfilled, (state, action) => {
        state.searching = false
        state.searchResults = action.payload
      })
      .addCase(searchStocks.rejected, (state, action) => {
        state.searching = false
        state.searchResults = []
        state.orderError =
          action.payload ?? action.error.message ?? 'Search failed'
      })
      .addCase(fetchHistoricalData.pending, (state) => {
        state.loadingHistory = true
      })
      .addCase(fetchHistoricalData.fulfilled, (state, action) => {
        state.loadingHistory = false
        const payloadArray = Array.isArray(action.payload)
          ? action.payload
          : []
        if (!Array.isArray(action.payload) && import.meta.env.DEV) {
          console.warn(
            '[tradingSlice] Expected historical payload array, got:',
            action.payload,
          )
        }
        const sorted = [...payloadArray].sort(
          (a, b) =>
            new Date(b.datetime).getTime() - new Date(a.datetime).getTime(),
        )
        state.historicalData = sorted
        state.stats = computeStats(sorted)
        const latestClose = Number.parseFloat(sorted[0]?.close ?? '0')
        state.latestPrice = Number.isFinite(latestClose) ? latestClose : null
      })
      .addCase(fetchHistoricalData.rejected, (state, action) => {
        state.loadingHistory = false
        state.historicalData = []
        state.stats = {
          open: null,
          high: null,
          low: null,
          volume: null,
        }
        state.orderError =
          action.payload ?? action.error.message ?? 'Failed to load data'
      })
      .addCase(placeOrder.pending, (state) => {
        state.orderStatus = 'loading'
        state.orderError = null
        state.orderMessage = null
      })
      .addCase(placeOrder.fulfilled, (state, action) => {
        state.orderStatus = 'succeeded'
        state.orderMessage = action.payload.message
      })
      .addCase(placeOrder.rejected, (state, action) => {
        state.orderStatus = 'failed'
        state.orderError =
          action.payload ?? action.error.message ?? 'Order failed'
      })
  },
})

export const { setSelectedSymbol, setLatestPrice, clearOrderStatus } =
  tradingSlice.actions

export default tradingSlice.reducer
