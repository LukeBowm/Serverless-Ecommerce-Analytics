import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Paper, 
  Typography, 
  Box, 
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import { fetchCustomerData } from '../services/api';
import PeopleIcon from '@mui/icons-material/People';
import RepeatIcon from '@mui/icons-material/Repeat';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import MetricCard from '../components/widgets/MetricCard';

const Customers = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [customerData, setCustomerData] = useState([]);
  const [selectedCohort, setSelectedCohort] = useState('');
  const [availableCohorts, setAvailableCohorts] = useState([]);
  const [summaryMetrics, setSummaryMetrics] = useState({
    totalCustomers: 0,
    repeatCustomers: 0,
    newCustomers: 0,
    totalRevenue: 0
  });

  useEffect(() => {
    const loadCustomerData = async () => {
      try {
        setLoading(true);
        console.log('🔍 About to fetch customer data...');
        const data = await fetchCustomerData(selectedCohort || null);
        console.log('📊 Customer data received:', data);
        console.log('📊 Customer data type:', typeof data);
        console.log('📊 Is array?', Array.isArray(data));
        console.log('Full response structure:', JSON.stringify(data, null, 2));
        
        // Extract the array from the data object
        let processedData = [];
        if (data && data.cohorts) {
          processedData = data.cohorts;
        } else if (data && Array.isArray(data)) {
          processedData = data;
        } else if (data && typeof data === 'object' && Object.keys(data).length > 0) {
          // If there's a different structure, try to find any array in the object
          for (const key in data) {
            if (Array.isArray(data[key])) {
              processedData = data[key];
              break;
            }
          }
        }
        
        console.log('Processed customer data:', processedData);
        setCustomerData(processedData || []);
        
        // Extract cohorts for dropdown
        if (processedData && processedData.length > 0) {
          const cohorts = [...new Set(processedData.map(item => item.cohort))].filter(Boolean);
          setAvailableCohorts(cohorts);
          
          // Calculate summary metrics
          const totalCustomers = processedData.reduce((sum, item) => sum + (item.customer_count || 0), 0);
          const repeatCustomers = processedData.reduce((sum, item) => sum + (item.repeat_customers || 0), 0);
          const newCustomers = processedData.reduce((sum, item) => sum + (item.new_customers || 0), 0);
          const totalRevenue = processedData.reduce((sum, item) => sum + (item.total_revenue || 0), 0);
          
          setSummaryMetrics({
            totalCustomers,
            repeatCustomers,
            newCustomers,
            totalRevenue
          });
        }
        
        setError(null);
      } catch (err) {
        console.error('❌ Customer data loading error:', err);
        setError('Failed to load customer data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
  
    loadCustomerData();
  }, [selectedCohort]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography component="h1" variant="h4" color="primary" gutterBottom>
        Customer Analytics
      </Typography>
      
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel id="cohort-label">Filter by Cohort</InputLabel>
              <Select
                labelId="cohort-label"
                id="cohort"
                value={selectedCohort}
                label="Filter by Cohort"
                onChange={(e) => setSelectedCohort(e.target.value)}
                displayEmpty
                MenuProps={{
                    PaperProps: {
                    style: { maxHeight: 300 }
                    }
                }}
                sx={{
                    height: '56px',  
                    '& .MuiSelect-select': {
                      height: '20px',  
                      display: 'flex',
                      alignItems: 'center'
                    }
                  }}
                >
                <MenuItem value="">All Cohorts</MenuItem>
                {availableCohorts.map(cohort => (
                  <MenuItem key={cohort} value={cohort}>{cohort}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {/* Summary Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Total Customers"
            value={summaryMetrics.totalCustomers}
            icon={<PeopleIcon />}
            color="#2196f3"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Repeat Customers"
            value={summaryMetrics.repeatCustomers}
            icon={<RepeatIcon />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="New Customers"
            value={summaryMetrics.newCustomers}
            icon={<PersonAddIcon />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Total Revenue"
            value={`$${summaryMetrics.totalRevenue.toFixed(2)}`}
            icon={<AttachMoneyIcon />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>
      
      {/* Customer Data Table */}
      <Paper sx={{ p: 2 }}>
        <Typography component="h2" variant="h6" color="primary" gutterBottom>
          Customer Data by Cohort
        </Typography>
        
        {customerData && customerData.length > 0 ? (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Cohort</TableCell>
                  <TableCell align="right">Total Customers</TableCell>
                  <TableCell align="right">New Customers</TableCell>
                  <TableCell align="right">Repeat Customers</TableCell>
                  <TableCell align="right">Total Revenue</TableCell>
                  <TableCell align="right">Avg Revenue/Customer</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {customerData.map((row, index) => {
                  const avgRevenue = row.customer_count > 0 
                    ? (row.total_revenue / row.customer_count).toFixed(2) 
                    : '0.00';
                  
                  return (
                    <TableRow key={index}>
                      <TableCell>
                        <Chip 
                          label={row.cohort || 'Unknown'} 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">{row.customer_count || 0}</TableCell>
                      <TableCell align="right">{row.new_customers || 0}</TableCell>
                      <TableCell align="right">{row.repeat_customers || 0}</TableCell>
                      <TableCell align="right">${(row.total_revenue || 0).toFixed(2)}</TableCell>
                      <TableCell align="right">${avgRevenue}</TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box sx={{ minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">
              No customer data available. Try generating some customer data first.
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default Customers;