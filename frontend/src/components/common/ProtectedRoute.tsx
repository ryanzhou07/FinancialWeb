import { useEffect } from 'react'
import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../hooks/reduxHooks'
import { fetchCurrentUser } from '../../store/slices/authSlice'

interface ProtectedRouteProps {
  children: ReactNode
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const dispatch = useAppDispatch()
  const location = useLocation()
  const { user, token, status } = useAppSelector((state) => state.auth)

  useEffect(() => {
    if (!user && token && status === 'idle') {
      dispatch(fetchCurrentUser())
    }
  }, [dispatch, token, user, status])

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  if (status === 'loading' && !user) {
    return null
  }

  return <>{children}</>
}
