import React from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import App from './App';

const theme = createTheme({
  palette: {
    primary: {
      main: '#02B3E6', 
    },
    secondary: {
      main: '#9ACA3B',
    },
    tertiary: {
      main: '#00599D',
    },
  },
  typography: {
    fontFamily: 'Poppins',
  },
});

const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <ThemeProvider theme={theme}>
    <App />
  </ThemeProvider>
);