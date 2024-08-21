import React, { useState, useEffect, lazy, Suspense } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';

const FilterOverlay = lazy(() => import('./FilterOverlay'));
const DashboardComponent = lazy(() => import('./DashboardComponent'));

const AppContent = () => {
  const [dashboardUrl, setDashboardUrl] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const colors = {
    primary: '#02B3E6',
    secondary: '#02B3E6',
    background: '#ffffff',
    text: '#02B3E6'
  };

  // Fetch the initial dashboard URL when the component mounts
  useEffect(() => {
    const fetchDashboardUrl = async () => {
      try {
        const response = await fetch('http://localhost:5002/get_dashboard_url');
        if (response.ok) {
          const data = await response.json();
          setDashboardUrl(data.dashboard_url);
        } else {
          console.error('Error fetching dashboard URL:', response.statusText);
        }
      } catch (error) {
        console.error('Error fetching dashboard URL:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardUrl();
  }, []);

  const handleApplyFilters = async (filters) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5002/apply_filters', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters)
      });
    } catch (error) {
      console.error('Error applying filters:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ height: '100vh', width: '100vw', overflow: 'hidden', position: 'fixed', top: 0, left: 0 }}>
      <FilterOverlay onApplyFilters={handleApplyFilters} colors={colors} />
      <div style={{ height: 'calc(100% - 64px)', marginTop: '64px', overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', backgroundColor: colors.background }}>
            <Box textAlign="center">
              <CircularProgress style={{ color: colors.primary }} />
              <p style={{ color: colors.text, marginTop: '20px', fontFamily: 'Roboto, sans-serif' }}>Loading Dashboard...</p>
            </Box>
          </div>
        ) : (
          <DashboardComponent url={dashboardUrl} />
        )}
      </div>
    </div>
  );
};

const App = () => (
  <Router>
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard/*" element={<AppContent />} />
      </Routes>
    </Suspense>
  </Router>
);

export default App;
