# React Frontend Setup Guide

## Quick Start

### 1. Create React App
```bash
# Navigate to project root
cd /Users/ryanzhou/Documents/FinancialWeb/FinancialWeb

# Create React app in frontend directory
npx create-react-app frontend --template typescript

# Or using Vite (recommended for faster development)
npm create vite@latest frontend -- --template react-ts
```

### 2. Install Dependencies
```bash
cd frontend

# Core dependencies
npm install axios socket.io-client

# UI Library (choose one)
npm install @mui/material @emotion/react @emotion/styled  # Material-UI
# OR
npm install antd  # Ant Design

# State Management (choose one)
npm install @reduxjs/toolkit react-redux  # Redux Toolkit
# OR
npm install zustand  # Zustand

# Charts for financial data
npm install recharts

# Routing
npm install react-router-dom

# Development dependencies
npm install --save-dev @types/react @types/react-dom
```

### 3. Basic Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── portfolio/
│   │   │   ├── Portfolio.tsx
│   │   │   ├── HoldingsList.tsx
│   │   │   └── PortfolioChart.tsx
│   │   ├── trading/
│   │   │   ├── TradingInterface.tsx
│   │   │   ├── StockSearch.tsx
│   │   │   └── OrderForm.tsx
│   │   └── common/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Layout.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── websocket.ts
│   ├── store/
│   │   ├── index.ts
│   │   ├── authSlice.ts
│   │   └── portfolioSlice.ts
│   ├── types/
│   │   ├── auth.ts
│   │   ├── portfolio.ts
│   │   └── api.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   └── helpers.ts
│   ├── App.tsx
│   └── index.tsx
├── package.json
└── vite.config.ts (if using Vite)
```

### 4. API Configuration
Create `src/services/api.ts`:
```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 5. WebSocket Configuration
Create `src/services/websocket.ts`:
```typescript
import { io } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:8000';

export const socket = io(SOCKET_URL);

export const subscribeToStock = (symbol: string) => {
  socket.emit('subscribe', { symbol });
};

export const unsubscribeFromStock = (symbol: string) => {
  socket.emit('unsubscribe', { symbol });
};

export const onPriceUpdate = (callback: (data: any) => void) => {
  socket.on('price_update', callback);
};

export const onSubscriptionUpdate = (callback: (data: any) => void) => {
  socket.on('subscribed', callback);
  socket.on('unsubscribed', callback);
};
```

### 6. Environment Configuration
Create `frontend/.env`:
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_SOCKET_URL=http://localhost:8000
```

### 7. Start Development
```bash
# Start backend (from project root)
python api.py

# Start frontend (from frontend directory)
npm run dev  # if using Vite
# OR
npm start    # if using Create React App
```

## Key Features to Implement

### Authentication
- Login/Register forms
- JWT token management
- Protected routes
- User profile management

### Trading Interface
- Stock search with autocomplete
- Real-time price charts
- Buy/Sell order forms
- Order confirmation modals

### Portfolio Management
- Holdings overview
- Performance charts
- Transaction history
- Portfolio analytics

### Responsive Design
- Mobile-first approach
- Modern UI components
- Dark/light theme support
- Accessibility compliance

## Development Tips

1. **API Integration**: Use Axios interceptors for token management
2. **Real-time Updates**: Implement WebSocket connections for live prices
3. **State Management**: Use Redux Toolkit or Zustand for complex state
4. **Error Handling**: Implement proper error boundaries and user feedback
5. **Performance**: Use React.memo and useMemo for optimization
6. **Testing**: Set up Jest and React Testing Library
7. **TypeScript**: Leverage TypeScript for better development experience
