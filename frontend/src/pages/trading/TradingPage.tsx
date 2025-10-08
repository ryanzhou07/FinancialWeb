import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Skeleton,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import type { SelectChangeEvent } from '@mui/material/Select'
import Grid from '@mui/material/GridLegacy'
import Autocomplete from '@mui/material/Autocomplete'
import { useAppDispatch, useAppSelector } from '../../hooks/reduxHooks'
import {
  clearOrderStatus,
  fetchHistoricalData,
  placeOrder,
  searchStocks,
  setLatestPrice,
  setSelectedSymbol,
} from '../../store/slices/tradingSlice'
import { fetchPortfolio } from '../../store/slices/portfolioSlice'
import { socketService } from '../../services/socket'
import type { PriceUpdatePayload, StockSummary } from '../../types/stock'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const formatCurrency = (value: number | null | undefined) => {
  if (value === null || value === undefined) return '--'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value)
}

export const TradingPage = () => {
  const dispatch = useAppDispatch()
  const {
    searchResults,
    searching,
    selectedSymbol,
    historicalData,
    loadingHistory,
    latestPrice,
    stats,
    orderError,
    orderStatus,
    orderMessage,
  } = useAppSelector((state) => state.trading)

  const [searchInput, setSearchInput] = useState('')
  const [quantityInput, setQuantityInput] = useState('')
  const [side, setSide] = useState<'Buy' | 'Sell'>('Buy')
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)

  useEffect(() => {
    socketService.connect()
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => {
      dispatch(searchStocks(searchInput.trim()))
    }, 300)
    return () => clearTimeout(timer)
  }, [searchInput, dispatch])

  useEffect(() => {
    if (!selectedSymbol) {
      return
    }

    dispatch(fetchHistoricalData(selectedSymbol))
  }, [dispatch, selectedSymbol])

  useEffect(() => {
    if (!selectedSymbol) {
      return
    }

    socketService.subscribe(selectedSymbol)
    const priceHandler = (payload: PriceUpdatePayload) => {
      const payloadSymbol = payload.symbol?.toUpperCase()
      if (payloadSymbol === selectedSymbol.toUpperCase()) {
        const numericPrice = Number.parseFloat(String(payload.price))
        if (Number.isFinite(numericPrice)) {
          dispatch(setLatestPrice(numericPrice))
        }
      }
    }

    socketService.onPriceUpdate(priceHandler)

    return () => {
      socketService.unsubscribe(selectedSymbol)
      socketService.offPriceUpdate(priceHandler)
    }
  }, [dispatch, selectedSymbol])

  useEffect(() => {
    if (orderStatus === 'succeeded') {
      dispatch(fetchPortfolio())
      setIsPreviewOpen(false)
      setQuantityInput('')
    }
  }, [orderStatus, dispatch])

  const chartData = useMemo(() => {
    const reversed = [...historicalData].reverse()
    return reversed.map((point, index) => {
      const baseClose = Number.parseFloat(point.close)
      const isLatestPoint = index === reversed.length - 1
      const closeValue =
        isLatestPoint && latestPrice != null ? latestPrice : baseClose

      return {
        date: point.datetime,
        close: closeValue,
      }
    })
  }, [historicalData, latestPrice])

  const selectedOption = useMemo(() => {
    if (!selectedSymbol) return null
    return (
      searchResults.find(
        (option) => option.symbol.toUpperCase() === selectedSymbol.toUpperCase(),
      ) ?? null
    )
  }, [searchResults, selectedSymbol])

  const currentPrice =
    latestPrice ??
    (historicalData.length
      ? Number.parseFloat(historicalData[0].close)
      : undefined)

  const parsedQuantity = Number.parseFloat(quantityInput)
  const hasValidQuantity =
    Number.isFinite(parsedQuantity) && parsedQuantity > 0

  const handleSelectSymbol = (
    _: unknown,
    value: StockSummary | null,
  ) => {
    const symbol = value?.symbol ?? null
    dispatch(setSelectedSymbol(symbol))
    setSearchInput(value?.symbol ?? '')
    if (!symbol) {
      setQuantityInput('')
    }
  }

  const handlePreview = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!selectedSymbol || !hasValidQuantity || !currentPrice) {
      return
    }
    setIsPreviewOpen(true)
  }

  const handlePlaceOrder = () => {
    if (!selectedSymbol || !hasValidQuantity || !currentPrice) {
      return
    }
    dispatch(
      placeOrder({
        ticker: selectedSymbol,
        shares: parsedQuantity,
        price: currentPrice,
        side,
      }),
    )
  }

  const handleSideChange = (event: SelectChangeEvent<'Buy' | 'Sell'>) => {
    setSide(event.target.value as 'Buy' | 'Sell')
  }

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Trading terminal
        </Typography>
        <Typography color="text.secondary">
          Search equities, review market data, and place simulated orders with
          live pricing.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Stack spacing={2}>
                <Autocomplete
                  options={searchResults}
                  loading={searching}
                  getOptionLabel={(option) =>
                    `${option.symbol} — ${option.name}`
                  }
                  value={selectedOption}
                  inputValue={searchInput}
                  onInputChange={(_, value) => setSearchInput(value)}
                  isOptionEqualToValue={(option, value) =>
                    option.symbol === value.symbol
                  }
                  onChange={handleSelectSymbol}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Search stocks"
                      helperText="Start typing a symbol or company name"
                    />
                  )}
                />

                <Box>
                  <Typography
                    variant="h3"
                    fontWeight={700}
                    sx={{ mb: 1 }}
                  >
                    {selectedSymbol ?? 'Select a symbol'}
                  </Typography>
                  <Stack direction="row" spacing={3}>
                    <Typography variant="h5">
                      {formatCurrency(currentPrice ?? null)}
                    </Typography>
                    <Typography color="text.secondary">
                      Open {formatCurrency(stats.open)}
                    </Typography>
                    <Typography color="text.secondary">
                      High {formatCurrency(stats.high)}
                    </Typography>
                    <Typography color="text.secondary">
                      Low {formatCurrency(stats.low)}
                    </Typography>
                    <Typography color="text.secondary">
                      Volume{' '}
                      {stats.volume
                        ? `${(stats.volume / 1_000_000).toFixed(2)}M`
                        : '--'}
                    </Typography>
                  </Stack>
                </Box>
              </Stack>
            </CardContent>
          </Card>

          <Card sx={{ height: 380 }}>
            <CardContent sx={{ height: '100%' }}>
              {loadingHistory ? (
                <Skeleton variant="rounded" height="100%" />
              ) : selectedSymbol && chartData.length ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient
                        id="priceGradient"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop offset="0%" stopColor="#3E92CC" stopOpacity={0.7} />
                        <stop offset="90%" stopColor="#3E92CC" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#14203B" />
                    <XAxis
                      dataKey="date"
                      tick={{ fill: '#B4C5E4', fontSize: 12 }}
                    />
                    <YAxis
                      domain={['auto', 'auto']}
                      tick={{ fill: '#B4C5E4', fontSize: 12 }}
                      tickFormatter={(value) => `$${value}`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#07112B',
                        borderRadius: 12,
                        border: '1px solid rgba(62, 146, 204, 0.3)',
                      }}
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Area
                      type="monotone"
                      dataKey="close"
                      stroke="#3E92CC"
                      fill="url(#priceGradient)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <Stack
                  alignItems="center"
                  justifyContent="center"
                  sx={{ height: '100%' }}
                  spacing={1}
                >
                  <Typography variant="subtitle1">
                    Select a stock to view recent price action.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Historical data will populate once you choose a symbol.
                  </Typography>
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order ticket
              </Typography>
              <Typography color="text.secondary" variant="body2" gutterBottom>
                Configure your simulated trade. All orders execute instantly at
                the displayed market price.
              </Typography>

              <Box component="form" onSubmit={handlePreview}>
                <Stack spacing={2.5} mt={2}>
                  <FormControl fullWidth>
                    <InputLabel>Action</InputLabel>
                    <Select
                      label="Action"
                      value={side}
                      onChange={handleSideChange}
                    >
                      <MenuItem value="Buy">Buy</MenuItem>
                      <MenuItem value="Sell">Sell</MenuItem>
                    </Select>
                  </FormControl>

                  <TextField
                    label="Symbol"
                    value={selectedSymbol ?? ''}
                    InputProps={{ readOnly: true }}
                    helperText={
                      selectedSymbol
                        ? 'Orders trade the currently selected symbol.'
                        : 'Pick a stock from search to enable trading.'
                    }
                  />

                  <TextField
                    label="Shares"
                    type="number"
                    value={quantityInput}
                    onChange={(event) => setQuantityInput(event.currentTarget.value)}
                    inputProps={{ min: 0, step: 0.01 }}
                    required
                  />

                  <TextField
                    label="Estimated price"
                    value={formatCurrency(currentPrice ?? null)}
                    InputProps={{ readOnly: true }}
                  />

                  {orderError && (
                    <Alert severity="error" variant="outlined">
                      {orderError}
                    </Alert>
                  )}

                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={!selectedSymbol || !hasValidQuantity || !currentPrice}
                  >
                    Review order
                  </Button>
                </Stack>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={isPreviewOpen} onClose={() => setIsPreviewOpen(false)}>
        <DialogTitle>Confirm simulated order</DialogTitle>
        <DialogContent>
          <Stack spacing={1}>
            <Typography>
              <strong>Action:</strong> {side}
            </Typography>
            <Typography>
              <strong>Symbol:</strong> {selectedSymbol}
            </Typography>
            <Typography>
              <strong>Shares:</strong> {quantityInput || '—'}
            </Typography>
            <Typography>
              <strong>Est. price:</strong> {formatCurrency(currentPrice ?? null)}
            </Typography>
            <Typography>
              <strong>Notional:</strong>{' '}
              {formatCurrency(
                (currentPrice ?? 0) *
                  (hasValidQuantity ? parsedQuantity : 0),
              )}
            </Typography>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsPreviewOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handlePlaceOrder}
            disabled={orderStatus === 'loading'}
          >
            {orderStatus === 'loading' ? 'Placing…' : 'Confirm'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={Boolean(orderMessage)}
        autoHideDuration={4000}
        onClose={() => dispatch(clearOrderStatus())}
        message={orderMessage}
      />
    </Stack>
  )
}

export default TradingPage
