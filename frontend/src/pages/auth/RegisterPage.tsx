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
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../hooks/reduxHooks'
import { registerUser } from '../../store/slices/authSlice'

export const RegisterPage = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { token, status, error } = useAppSelector((state) => state.auth)
  const theme = useTheme()
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'))
  const [formState, setFormState] = useState({
    username: '',
    email: '',
    password: '',
  })

  useEffect(() => {
    if (token) {
      navigate('/app/portfolio', { replace: true })
    }
  }, [token, navigate])

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    dispatch(registerUser(formState))
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
          maxWidth: 460,
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
              Create your account
            </Typography>
            <Typography color="text.secondary">
              Start your journey toward smarter financial decisions.
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" variant="filled">
              {error}
            </Alert>
          )}

          <Box component="form" noValidate onSubmit={handleSubmit}>
            <Stack spacing={2.5}>
              <TextField
                label="Username"
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
                label="Email"
                type="email"
                variant="outlined"
                required
                fullWidth
                value={formState.email}
                onChange={(event: ChangeEvent<HTMLInputElement>) => {
                  const { value } = event.target
                  setFormState((prev) => ({
                    ...prev,
                    email: value,
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
                {status === 'loading' ? 'Creating account…' : 'Sign up'}
              </Button>
            </Stack>
          </Box>

          <Typography variant="body2" color="text.secondary" textAlign="center">
            Already have an account?{' '}
            <Link component={RouterLink} to="/login" color="secondary">
              Sign in
            </Link>
          </Typography>
        </Stack>
      </Paper>
    </Box>
  )
}

export default RegisterPage
