import { useEffect, useMemo } from 'react'
import {
  Avatar,
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import Grid from '@mui/material/GridLegacy'
import { useAppDispatch, useAppSelector } from '../../hooks/reduxHooks'
import { fetchPortfolio } from '../../store/slices/portfolioSlice'
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip as RechartsTooltip,
} from 'recharts'

const accentColors = ['#3E92CC', '#7FDBFF', '#39CCCC', '#2ECC40', '#B10DC9']

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: value >= 1000 ? 0 : 2,
  }).format(value)

export const PortfolioPage = () => {
  const dispatch = useAppDispatch()
  const { holdings, totalCash, totalValue, status } = useAppSelector(
    (state) => state.portfolio,
  )

  useEffect(() => {
    dispatch(fetchPortfolio())
  }, [dispatch])

  const allocationData = useMemo(() => {
    if (!holdings.length) {
      return []
    }
    const mapped = holdings.map((holding) => ({
      name: holding.ticker,
      value: holding.shares * holding.price,
    }))
    return mapped.sort((a, b) => b.value - a.value)
  }, [holdings])

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Portfolio overview
        </Typography>
        <Typography color="text.secondary">
          Track your holdings, cash position, and diversification in real time.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar
                  sx={{
                    bgcolor: 'rgba(62,146,204,0.18)',
                    color: 'secondary.main',
                    fontSize: 22,
                    width: 48,
                    height: 48,
                  }}
                >
                  📈
                </Avatar>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Total portfolio value
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(totalValue || 0)}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar
                  sx={{
                    bgcolor: 'rgba(46,204,64,0.18)',
                    color: 'success.main',
                    fontSize: 22,
                    width: 48,
                    height: 48,
                  }}
                >
                  💵
                </Avatar>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Available cash
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(totalCash || 0)}
                  </Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar
                  sx={{
                    bgcolor: 'rgba(177,13,201,0.18)',
                    color: 'secondary.main',
                    fontSize: 22,
                    width: 48,
                    height: 48,
                  }}
                >
                  🧺
                </Avatar>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Active positions
                  </Typography>
                  <Typography variant="h5">{holdings.length}</Typography>
                </Box>
                <Chip
                  label="Simulated"
                  color="secondary"
                  variant="outlined"
                  sx={{ ml: 'auto' }}
                />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={5}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Allocation snapshot
              </Typography>
              <Typography color="text.secondary" variant="body2" gutterBottom>
                Visualize how your capital is distributed across open positions.
              </Typography>

              <Box sx={{ height: 280 }}>
                {allocationData.length ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <RechartsTooltip
                        formatter={(value: number) => formatCurrency(value)}
                      />
                      <Pie
                        data={allocationData}
                        dataKey="value"
                        innerRadius="55%"
                        outerRadius="80%"
                        paddingAngle={4}
                      >
                        {allocationData.map((entry, index) => (
                          <Cell
                            key={entry.name}
                            fill={
                              accentColors[index % accentColors.length] ?? '#fff'
                            }
                          />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <Stack
                    spacing={1}
                    alignItems="center"
                    justifyContent="center"
                    sx={{ height: '100%' }}
                  >
                    <Typography variant="subtitle1">
                      No positions yet
                    </Typography>
                    <Typography color="text.secondary" variant="body2">
                      Your allocation chart will appear after your first trade.
                    </Typography>
                  </Stack>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={7}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Holdings detail
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Ticker</TableCell>
                    <TableCell align="right">Shares</TableCell>
                    <TableCell align="right">Avg cost</TableCell>
                    <TableCell align="right">Market value*</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {holdings.map((holding) => {
                    const marketValue = holding.shares * holding.price
                    return (
                      <TableRow key={holding.id} hover>
                        <TableCell>
                          <Typography fontWeight={600}>
                            {holding.ticker}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          {holding.shares.toLocaleString()}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(holding.price)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(marketValue)}
                        </TableCell>
                      </TableRow>
                    )
                  })}
                  {!holdings.length && status === 'succeeded' && (
                    <TableRow>
                      <TableCell colSpan={4} align="center">
                        <Typography color="text.secondary" py={2}>
                          You have no holdings yet. Execute a trade to build
                          your simulated portfolio.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                  {status === 'loading' && (
                    <TableRow>
                      <TableCell colSpan={4} align="center">
                        <Typography color="text.secondary" py={2}>
                          Loading positions…
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
                sx={{ mt: 2 }}
              >
                * Market value is calculated using your average cost price until
                live pricing is enabled.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  )
}

export default PortfolioPage
