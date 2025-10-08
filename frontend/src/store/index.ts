import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import portfolioReducer from './slices/portfolioSlice'
import tradingReducer from './slices/tradingSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    portfolio: portfolioReducer,
    trading: tradingReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
