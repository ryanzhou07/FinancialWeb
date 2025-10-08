import { useEffect } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './components/common/ProtectedRoute'
import AppLayout from './components/layout/AppLayout'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import PortfolioPage from './pages/portfolio/PortfolioPage'
import TradingPage from './pages/trading/TradingPage'
import ResearchPage from './pages/research/ResearchPage'
import { useAppDispatch, useAppSelector } from './hooks/reduxHooks'
import { fetchCurrentUser } from './store/slices/authSlice'
import './App.css'

const App = () => {
  const dispatch = useAppDispatch()
  const { token, user, status } = useAppSelector((state) => state.auth)

  useEffect(() => {
    if (token && !user && status === 'idle') {
      dispatch(fetchCurrentUser())
    }
  }, [dispatch, token, user, status])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/app/portfolio" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<RegisterPage />} />

        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="portfolio" replace />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="trading" element={<TradingPage />} />
          <Route path="research" element={<ResearchPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/app/portfolio" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
