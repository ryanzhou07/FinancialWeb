export interface PortfolioHolding {
  id: number
  ticker: string
  shares: number
  price: number
  date: string | null
  account_id: number
}

export interface LivePortfolioResponse {
  holdings: PortfolioHolding[]
  total_cash: number
  total_value: number
  user_id: number
}

export interface LedgerEntry {
  id: number
  ticker: string
  shares: number
  price: number
  buy_or_sell: 'Buy' | 'Sell'
  date: string
  account_id: number
}

export interface LedgerResponse {
  entries: LedgerEntry[]
  total: number
  pages: number
  current_page: number
}
