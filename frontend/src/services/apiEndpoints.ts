export const API_ENDPOINTS = {
  // Authentication
  register: '/auth/register',
  login: '/auth/login',
  me: '/auth/me',

  // Portfolio
  livePortfolio: '/portfolio/live',
  portfolio: '/portfolio',
  holdingDetails: (ticker: string) => `/portfolio/holdings/${ticker}`,

  // Trading
  buy: '/trading/buy',
  sell: '/trading/sell',

  // Ledger
  ledger: '/ledger',

  // Stocks
  searchStocks: '/stocks/search',
  stockInfo: (symbol: string) => `/stocks/${symbol}`,
  stockHistory: (symbol: string) => `/data/${symbol}`,
} as const

export type ApiEndpointKey = keyof typeof API_ENDPOINTS
