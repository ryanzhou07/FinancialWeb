export interface StockSummary {
  id: number
  symbol: string
  name: string
  exchange: string | null
  is_active: boolean
}

export interface StockHistoricalPoint {
  datetime: string
  open: string
  high: string
  low: string
  close: string
  volume: string
}

export interface StockHistoricalResponse {
  message?: string
  symbol?: string
  values: StockHistoricalPoint[]
}

export interface PriceUpdatePayload {
  symbol?: string
  price?: number | string
  [key: string]: unknown
}
