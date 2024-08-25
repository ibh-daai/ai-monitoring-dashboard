import React, { useState, useEffect } from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem, Button, Grid, CircularProgress } from '@mui/material';

const FilterOverlay = ({ onApplyFilters, colors }) => {
  const [filters, setFilters] = useState({
    filter1: '',
    filter2: ''
  });
  const [filterOptions, setFilterOptions] = useState({});
  const [optionToCategory, setOptionToCategory] = useState({});
  const [loading, setLoading] = useState(false);

  const dashboard_url = process.env.REACT_APP_DASHBOARD_API_URL || 'http://localhost:5002';

  useEffect(() => {
    fetch(`${dashboard_url}/get_filter_options`)
      .then(response => response.json())
      .then(data => {
        setFilterOptions(data);
        // Create reverse mapping from option to category
        const reverseMapping = {};
        Object.entries(data).forEach(([category, options]) => {
          options.forEach(option => {
            reverseMapping[option] = category;
          });
        });
        setOptionToCategory(reverseMapping);
      });
  }, []);


  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters({ ...filters, [name]: value });
  };

  // const handleApply = () => {
  //   setLoading(true);
  //   onApplyFilters(filters).finally(() => setLoading(false));
  // };

  const handleApply = () => {
    setLoading(true);
    fetch(`${dashboard_url}/apply_filters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(filters),
    })
      .then(response => response.json())
      .then(data => {
        if (data.filtered_url) {
          window.open(data.filtered_url, '_blank');
        }
      })
      .catch(error => console.error('Error:', error))
      .finally(() => setLoading(false));
  };

  const formatCategory = (category) => {
    return category.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  const isOptionDisabled = (filterName, category, option) => {
    const otherFilter = filterName === 'filter1' ? 'filter2' : 'filter1';
    const selectedOption = filters[otherFilter];
    const selectedCategory = optionToCategory[selectedOption];
    const optionCategory = optionToCategory[option];
    const isDisabled = selectedCategory === optionCategory;
    return isDisabled;
  };


  return (
    <Box sx={{ 
      bgcolor: colors.background, 
      color: colors.text, 
      padding: 2, 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center', 
      width: '100%',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 1000,
      overflowY: 'hidden'
    }}>
      <Grid container spacing={2} alignItems="center" justifyContent={"center"} style={{ width: '95%' }}>
        <Grid item xs={5}>
          <FormControl fullWidth>
            <InputLabel>Data Filter 1</InputLabel>
            <Select name="filter1" value={filters.filter1} onChange={handleFilterChange} variant="standard">
              <MenuItem value="">None</MenuItem>
              {Object.entries(filterOptions).flatMap(([category, options]) => [
                <MenuItem disabled key={`${category}-header`} sx={{ fontSize: '0.9rem' }}>{formatCategory(category)}</MenuItem>,
                ...options.map(option => (
                  <MenuItem 
                    key={option} 
                    value={option} 
                    disabled={isOptionDisabled('filter1', category, option)}
                  >
                    {option}
                  </MenuItem>
                ))
              ])}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={5}>
          <FormControl fullWidth>
            <InputLabel>Data Filter 2</InputLabel>
            <Select name="filter2" value={filters.filter2} onChange={handleFilterChange} variant="standard">
              <MenuItem value="">None</MenuItem>
              {Object.entries(filterOptions).flatMap(([category, options]) => [
                <MenuItem disabled key={`${category}-header`} sx={{ fontSize: '0.9rem' }}>{formatCategory(category)}</MenuItem>,
                ...options.map(option => (
                  <MenuItem 
                    key={option} 
                    value={option} 
                    disabled={isOptionDisabled('filter2', category, option)}
                  >
                    {option}
                  </MenuItem>
                ))
              ])}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={2}>
          <Button variant="outlined" size="large" disableElevation fullWidth onClick={handleApply} disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Apply Filters'}
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FilterOverlay;