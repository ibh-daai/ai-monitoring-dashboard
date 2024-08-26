import React, { useState } from 'react';
import { Container, Box, Button, TextField, Typography, AppBar, Toolbar, Snackbar } from '@mui/material';
import axios from 'axios';
import logo from './thp_logo.png';

function Auth({ setModelId }) {
  const [modelId, setModelIdInput] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const ingestion_url = process.env.REACT_APP_INGESTION_API_URL || 'http://localhost:5001';

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!modelId) {
      setError('Please enter a model ID.');
      return;
    }

    try {
      setError(null);
      const response = await axios.post(`${ingestion_url}/authenticate`, { model_id: modelId, action: 'login' }, { withCredentials: true });
      setModelId(modelId);
      localStorage.setItem('modelId', modelId);
      setSuccess(true);
    } catch (error) {
      console.error('Error authenticating:', error);
      setError(error.response?.data?.message || 'Error during login');
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    if (!modelId) {
      setError('Please enter a model ID.');
      return;
    }

    try {
      setError(null);
      const checkResponse = await axios.post(`${ingestion_url}/check_model_id`, { model_id: modelId });
      if (checkResponse.status === 200) {
        const response = await axios.post(`${ingestion_url}/authenticate`, { model_id: modelId, action: 'signup' }, { withCredentials: true });
        setModelId(modelId);
        localStorage.setItem('modelId', modelId);
        setSuccess(true);
      }
    } catch (error) {
      if (error.response && error.response.status === 409) {
        setError('Model ID already in use. Please choose another one.');
      } else if (error.response && error.response.status === 400 && error.response.data.message === "Model ID does not match the configuration file.") {
        setError('Model ID does not match the configuration file.');
      } else {
        console.error('Error signing up:', error);
        setError(error.response?.data?.message || 'Error during sign up process');
      }
    }
  };

  return (
    <Container maxWidth="md">
      <AppBar position="static" sx={{ boxShadow: 'none', borderRadius: 1 }}>
        <Toolbar>
          <img src={logo} alt="Logo" style={{ height: 90, marginRight: 20 }} />
          <Typography variant="h6">Monitoring Dashboard Authentication</Typography>
        </Toolbar>
      </AppBar>
      <Box my={4}>
        <Typography variant="h6" component="h1" gutterBottom>
          Enter Model ID
        </Typography>
        <form>
          <TextField
            label="Model ID"
            variant="outlined"
            fullWidth
            margin="normal"
            value={modelId}
            onChange={(e) => setModelIdInput(e.target.value)}
            error={!!error}
            helperText={error}
          />
          <Box my={2} display="flex" justifyContent="space-between">
            <Button variant="contained" color="primary" onClick={handleLogin} disableElevation>
              Login
            </Button>
            <Button variant="contained" color="secondary" onClick={handleSignUp} disableElevation>
              Sign Up
            </Button>
          </Box>
        </form>
      </Box>
      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={() => setSuccess(false)}
        message="Authentication successful"
      />
    </Container>
  );
}

export default Auth;