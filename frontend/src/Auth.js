import React, { useState } from 'react';
import { Container, Box, Button, TextField, Typography, AppBar, Toolbar, Snackbar, Alert } from '@mui/material';
import axios from 'axios';
import logo from './thp_logo.png';

function Auth({ setModelId }) {
  const [modelId, setModelIdInput] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!modelId) {
      setError('Please enter a model ID.');
      return;
    }

    try {
      setError(null);
      const response = await axios.post('http://localhost:5001/authenticate', { model_id: modelId }, { withCredentials: true });
      setModelId(modelId);
      localStorage.setItem('modelId', modelId);
      setSuccess(true);
    } catch (error) {
      console.error('Error authenticating:', error);
      setError('Model ID not provided or different from configuration file');
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
        <form onSubmit={handleSubmit}>
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
          <Box my={2}>
            <Button variant="contained" color="primary" fullWidth disableElevation type="submit">
              Submit
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
