import { createTheme } from '@mui/material/styles'

const primaryColor = '#0C2340'
const secondaryColor = '#3E92CC'

export const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#020817',
      paper: '#07112B',
    },
    primary: {
      main: primaryColor,
    },
    secondary: {
      main: secondaryColor,
    },
    success: {
      main: '#4caf50',
    },
    error: {
      main: '#f44336',
    },
    text: {
      primary: '#F5F7FA',
      secondary: '#B4C5E4',
    },
  },
  typography: {
    fontFamily: `'Inter', 'Roboto', 'Helvetica', 'Arial', sans-serif`,
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          backgroundImage: 'none',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
})
