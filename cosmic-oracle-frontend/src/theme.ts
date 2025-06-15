// Theme configuration for the application
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#2C3E50', // Deep blue-grey
      light: '#34495E',
      dark: '#1A2634',
    },
    secondary: {
      main: '#8E44AD', // Mystical purple
      light: '#9B59B6',
      dark: '#6C3483',
    },
    background: {
      default: '#F5F6FA',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2C3E50',
      secondary: '#7F8C8D',
    },
  },
  typography: {
    fontFamily: "'Montserrat', sans-serif",
    h1: {
      fontFamily: "'Cormorant Garamond', serif",
      fontWeight: 600,
    },
    h2: {
      fontFamily: "'Cormorant Garamond', serif",
      fontWeight: 600,
    },
    h3: {
      fontFamily: "'Cormorant Garamond', serif",
      fontWeight: 500,
    },
    h4: {
      fontFamily: "'Cormorant Garamond', serif",
      fontWeight: 500,
    },
    h5: {
      fontFamily: "'Montserrat', sans-serif",
      fontWeight: 500,
    },
    h6: {
      fontFamily: "'Montserrat', sans-serif",
      fontWeight: 500,
    },
    subtitle1: {
      fontFamily: "'Montserrat', sans-serif",
      fontWeight: 400,
    },
    subtitle2: {
      fontFamily: "'Montserrat', sans-serif",
      fontWeight: 400,
    },
    body1: {
      fontFamily: "'Montserrat', sans-serif",
      fontWeight: 400,
    },
    body2: {
      fontFamily: "'Montserrat', sans-serif",
      fontWeight: 400,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontSize: '1rem',
          padding: '8px 24px',
        },
        contained: {
          boxShadow: 'none',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
        },
      },
    },
  },
});
