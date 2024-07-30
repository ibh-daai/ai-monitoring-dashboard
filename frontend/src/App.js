import React, { useState, useEffect } from 'react';
import { Container, Box, Button, MenuItem, Select, InputLabel, FormControl, Typography, AppBar, Toolbar, CircularProgress, Alert, Snackbar } from '@mui/material';
import axios from 'axios';
import logo from './thp_logo.png';
import Auth from './Auth';

function App() {
  const [file, setFile] = useState(null);
  const [endpoint, setEndpoint] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [modelId, setModelId] = useState(localStorage.getItem('modelId') || '');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
    setSuccess(false);
  };

  const handleEndpointChange = (e) => {
    setEndpoint(e.target.value);
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError(null);
    setSuccess(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !endpoint) {
      alert('Please select a file and endpoint.');
      return;
    }

    const formData = new FormData();
    formData.append('csvFile', file);
    formData.append('model_id', modelId);

    try {
      setLoading(true);
      setError(null);
      setSuccess(false);
      const response = await axios.post(`http://localhost:5001/${endpoint}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSuccess(true);
      setFile(null); 
    } catch (error) {
      console.error('Error uploading file:', error);
      setError(error.response?.data?.message || 'Error uploading file');
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem('modelId');
    setModelId('');
  };

  if (!modelId) {
    return <Auth setModelId={setModelId} />;
  }

  return (
    <Container maxWidth="md">
      <AppBar position="static" sx={{ boxShadow: 'none', borderRadius: 1 }}>        
        <Toolbar>
          <img src={logo} alt="Logo" style={{ height: 90, marginRight: 20 }} />
          <Typography variant="h6">Monitoring Dashboard CSV Upload</Typography>
          <Button color="inherit" onClick={handleSignOut} style={{ marginLeft: 'auto' }}>
            Sign Out
          </Button>
        </Toolbar>
      </AppBar>
      <Box my={4}>
        <Typography variant="h6" component="h1" gutterBottom>
          Select CSV File
        </Typography>
        <FormControl fullWidth margin="normal">
          <InputLabel id="endpoint-label">Select Endpoint</InputLabel>
          <Select
            labelId="endpoint-label"
            value={endpoint}
            onChange={handleEndpointChange}
            label="Select Endpoint"
          >
            <MenuItem value="ingest_results">Ingest Results</MenuItem>
            <MenuItem value="ingest_labels">Ingest Labels</MenuItem>
          </Select>
        </FormControl>
        <Button variant="contained" component="label" fullWidth disableElevation color="secondary">
          Select CSV File
          <input type="file" accept=".csv" hidden onChange={handleFileChange} />
        </Button>
        {file && (
          <Box mt={2}>
            <Typography variant="body2" gutterBottom>{file.name}</Typography>
            <Button variant="outlined" color="tertiary" size="small" onClick={handleRemoveFile}>
              Remove File
            </Button>
          </Box>
        )}
        {error && (
          <Box mt={2}>
            <Alert severity="error">{error}</Alert>
          </Box>
        )}
        <Box my={2}>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            disableElevation
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Upload'}
          </Button>
        </Box>
        <Snackbar
          open={success}
          autoHideDuration={6000}
          onClose={() => setSuccess(false)}
          message="File uploaded successfully"
        />
      </Box>
    </Container>
  );
}

export default App;
