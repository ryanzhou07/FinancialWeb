import { useMemo } from 'react'
import {
  AppBar,
  Avatar,
  BottomNavigation,
  BottomNavigationAction,
  Box,
  Button,
  Container,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
} from '@mui/material'
import { useTheme } from '@mui/material/styles'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { logout } from '../../store/slices/authSlice'
import { useAppDispatch, useAppSelector } from '../../hooks/reduxHooks'

const navItems = [
  {
    label: 'Portfolio',
    path: '/app/portfolio',
    icon: '📊',
  },
  {
    label: 'Trading',
    path: '/app/trading',
    icon: '📈',
  },
  {
    label: 'Research',
    path: '/app/research',
    icon: '🧠',
  },
]

export const AppLayout = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAppSelector((state) => state.auth)

  const activeIndex = useMemo(() => {
    const idx = navItems.findIndex((item) =>
      location.pathname.startsWith(item.path),
    )
    return idx === -1 ? 0 : idx
  }, [location.pathname])

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: 'background.default',
        color: 'text.primary',
      }}
    >
      <AppBar
        position="fixed"
        color="transparent"
        elevation={0}
        sx={{
          borderBottom: `1px solid ${theme.palette.divider}`,
          backgroundColor: 'rgba(7, 17, 43, 0.85)',
          backdropFilter: 'blur(12px)',
        }}
      >
        <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h5" fontWeight={700}>
              KarsFinance
            </Typography>
            <Typography variant="subtitle2" color="text.secondary">
              Comprehensive wealth simulator
            </Typography>
          </Box>
          {!isMobile && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              {navItems.map((item) => (
                <Button
                  key={item.path}
                  color={
                    location.pathname.startsWith(item.path)
                      ? 'secondary'
                      : 'inherit'
                  }
                  startIcon={
                    <Box component="span" sx={{ fontSize: 18 }}>
                      {item.icon}
                    </Box>
                  }
                  onClick={() => navigate(item.path)}
                >
                  {item.label}
                </Button>
              ))}
            </Box>
          )}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {user && (
              <Tooltip title={`${user.username}`}>
                <Avatar sx={{ bgcolor: theme.palette.secondary.main }}>
                  {user.username.slice(0, 1).toUpperCase()}
                </Avatar>
              </Tooltip>
            )}
            <Button
              color="inherit"
              onClick={handleLogout}
            >
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Toolbar />
      <Container
        maxWidth="lg"
        sx={{ py: { xs: 3, md: 5 }, pb: isMobile ? 10 : 5 }}
      >
        <Outlet />
      </Container>

      {isMobile && (
        <Box
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            borderTop: `1px solid ${theme.palette.divider}`,
            backgroundColor: 'rgba(7, 17, 43, 0.9)',
            backdropFilter: 'blur(8px)',
          }}
        >
          <BottomNavigation
            showLabels
            value={activeIndex}
            onChange={(_, newValue: number) => {
              const target = navItems[newValue]
              if (target) {
                navigate(target.path)
              }
            }}
          >
            {navItems.map((item) => (
              <BottomNavigationAction
                key={item.path}
                label={item.label}
                icon={
                  <Box component="span" sx={{ fontSize: 22 }}>
                    {item.icon}
                  </Box>
                }
              />
            ))}
          </BottomNavigation>
        </Box>
      )}
    </Box>
  )
}

export default AppLayout
