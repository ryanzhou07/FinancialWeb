import { useEffect, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import {
  Alert,
  Box,
  Button,
  Link,
  Paper,
  Stack,
  TextField,
  Typography,
  useMediaQuery,
} from '@mui/material'
import { useTheme } from '@mui/material/styles'
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../hooks/reduxHooks'
import { loginUser } from '../../store/slices/authSlice'

export const LoginPage = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const location = useLocation()
  const { token, status, error } = useAppSelector((state) => state.auth)
  const theme = useTheme()
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'))

  const [formState, setFormState] = useState({
    username: '',
    password: '',
  })

  useEffect(() => {
    if (token) {
      const redirectPath =
        (location.state as { from?: Location })?.from?.pathname ||
        '/app/portfolio'
      navigate(redirectPath, { replace: true })
    }
  }, [token, navigate, location.state])

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    dispatch(loginUser(formState))
  }

  return (
    <Box
      sx={{
        minHeight: '100dvh',
        display: 'flex',
        alignItems: isSmallScreen ? 'flex-start' : 'center',
        justifyContent: 'center',
        background: 'radial-gradient(circle at top, #0C2340, #020817)',
        p: 2,
        py: isSmallScreen ? 6 : 2,
        overflowY: 'auto',
      }}
    >
      <Paper
        elevation={12}
        sx={{
          width: '100%',
          maxWidth: 420,
          p: { xs: 3, sm: 4 },
          borderRadius: 4,
          backdropFilter: 'blur(6px)',
          backgroundColor: 'rgba(7, 17, 43, 0.9)',
          mt: isSmallScreen ? 4 : 0,
        }}
      >
        <Stack spacing={3}>
          <Box>
            <Typography variant="h4" fontWeight={700}>
              Welcome back
            </Typography>
            <Typography color="text.secondary">
              Sign in with your credentials to continue.
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" variant="filled">
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} noValidate>
            <Stack spacing={2.5}>
              <TextField
                label="Username or Email"
                variant="outlined"
                required
                fullWidth
                value={formState.username}
                onChange={(event: ChangeEvent<HTMLInputElement>) => {
                  const { value } = event.target
                  setFormState((prev) => ({
                    ...prev,
                    username: value,
                  }))
                }}
              />
              <TextField
                label="Password"
                type="password"
                variant="outlined"
                required
                fullWidth
                value={formState.password}
                onChange={(event: ChangeEvent<HTMLInputElement>) => {
                  const { value } = event.target
                  setFormState((prev) => ({
                    ...prev,
                    password: value,
                  }))
                }}
              />
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={status === 'loading'}
              >
                {status === 'loading' ? 'Signing in…' : 'Sign in'}
              </Button>
            </Stack>
          </Box>

          <Typography variant="body2" color="text.secondary" textAlign="center">
            Don&apos;t have an account?{' '}
            <Link component={RouterLink} to="/signup" color="secondary">
              Create one
            </Link>
          </Typography>
        </Stack>
      </Paper>
    </Box>
  )
}

export default LoginPage
