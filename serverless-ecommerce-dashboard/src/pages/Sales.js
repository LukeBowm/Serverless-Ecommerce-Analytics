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
  Card,
  CardContent
} from '@mui/material';
import { fetchSalesData } from '../services/api';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import MetricCard from '../components/widgets/MetricCard';

const Sales = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [salesData, setSalesData] = useState([]);
  const [timeUnit, setTimeUnit] = useState('day');
  const [period, setPeriod] = useState('last7');
  const [summaryMetrics, setSummaryMetrics] = useState({
    totalSales: 0,
    totalTransactions: 0,
    avgOrderValue: 0,
    totalItems: 0
  });

  useEffect(() => {
    const loadSalesData = async () => {
      try {
        setLoading(true);
        console.log('🔍 About to fetch sales data...');
        const data = await fetchSalesData(timeUnit, period);
        
        // Log raw data for debugging
        console.log('🔎 DIRECT SALES DATA:', data);
        console.log('🔎 SALES DATA TYPE:', typeof data);
        console.log('🔎 IS ARRAY?:', Array.isArray(data));
        
        // Enhanced data processing - handle various data structures
        let processedData = [];
        
        if (Array.isArray(data)) {
          // Data is already an array
          processedData = data;
        } else if (data && typeof data === 'object') {
          // Check for common response structures
          if (Array.isArray(data.items)) {
            processedData = data.items;
          } else if (Array.isArray(data.data)) {
            processedData = data.data;
          } else if (Array.isArray(data.sales)) {
            processedData = data.sales;
          } else if (Array.isArray(data.results)) {
            processedData = data.results;
          } else {
            // Last resort: check if any property is an array
            const arrayProps = Object.keys(data).find(key => Array.isArray(data[key]));
            if (arrayProps) {
              processedData = data[arrayProps];
            }
          }
        }
        
        console.log('🔎 FINAL PROCESSED SALES DATA:', processedData);
        setSalesData(processedData);
        
        // Calculate summary metrics with robust property checking
        if (processedData && processedData.length > 0) {
          // Log first item to inspect its structure
          console.log('🔎 FIRST SALES RECORD STRUCTURE:', processedData[0]);
          
          const totalSales = processedData.reduce((sum, item) => {
            // Try different property names for sales values
            const salesValue = 
              typeof item.total_sales === 'number' ? item.total_sales :
              typeof item.totalSales === 'number' ? item.totalSales : 
              typeof item.sales === 'number' ? item.sales :
              typeof item.amount === 'number' ? item.amount :
              typeof item.revenue === 'number' ? item.revenue :
              typeof item.total_sales === 'string' ? parseFloat(item.total_sales) || 0 :
              typeof item.totalSales === 'string' ? parseFloat(item.totalSales) || 0 :
              typeof item.sales === 'string' ? parseFloat(item.sales) || 0 :
              typeof item.amount === 'string' ? parseFloat(item.amount) || 0 :
              typeof item.revenue === 'string' ? parseFloat(item.revenue) || 0 : 0;
            
            console.log(`Adding ${salesValue} to sales sum (current: ${sum})`);
            return sum + salesValue;
          }, 0);
          
          const totalTransactions = processedData.reduce((sum, item) => {
            // Try different property names for transaction count
            const transCount = 
              typeof item.transaction_count === 'number' ? item.transaction_count :
              typeof item.transactionCount === 'number' ? item.transactionCount :
              typeof item.transactions === 'number' ? item.transactions :
              typeof item.orders === 'number' ? item.orders :
              typeof item.transaction_count === 'string' ? parseInt(item.transaction_count) || 0 :
              typeof item.transactionCount === 'string' ? parseInt(item.transactionCount) || 0 :
              typeof item.transactions === 'string' ? parseInt(item.transactions) || 0 :
              typeof item.orders === 'string' ? parseInt(item.orders) || 0 : 0;
                
            return sum + transCount;
          }, 0);
          
          const totalItems = processedData.reduce((sum, item) => {
            // Try different property names for item count
            const itemCount =
              typeof item.item_count === 'number' ? item.item_count :
              typeof item.itemCount === 'number' ? item.itemCount :
              typeof item.items === 'number' ? item.items :
              typeof item.products === 'number' ? item.products :
              typeof item.item_count === 'string' ? parseInt(item.item_count) || 0 :
              typeof item.itemCount === 'string' ? parseInt(item.itemCount) || 0 :
              typeof item.items === 'string' ? parseInt(item.items) || 0 :
              typeof item.products === 'string' ? parseInt(item.products) || 0 : 0;
                
            return sum + itemCount;
          }, 0);
          
          const avgOrderValue = totalTransactions > 0 ? totalSales / totalTransactions : 0;
          
          console.log('🔎 CALCULATED METRICS:', {
            totalSales,
            totalTransactions,
            avgOrderValue,
            totalItems
          });
          
          // Force a specific round on these metrics for display purposes
          const roundedTotalSales = parseFloat(totalSales.toFixed(2));
          const roundedAvgOrderValue = parseFloat(avgOrderValue.toFixed(2));
          
          console.log('🎯 FINAL METRICS FOR DISPLAY:', {
            totalSales: roundedTotalSales,
            totalTransactions,
            avgOrderValue: roundedAvgOrderValue,
            totalItems
          });
          
          // Use the round metrics for the state update
          setSummaryMetrics({
            totalSales: roundedTotalSales,
            totalTransactions,
            avgOrderValue: roundedAvgOrderValue,
            totalItems
          });
          
          // Log after state update to confirm
          console.log('🎯 Updated state with metrics');
        }
        
        setError(null);
      } catch (err) {
        console.error('❌ Sales data loading error:', err);
        setError('Failed to load sales data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
  
    loadSalesData();
  }, [timeUnit, period]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  console.log('🎯 Rendering with metrics:', summaryMetrics);
  console.log('🎯 Rendering with sales data:', salesData);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography component="h1" variant="h4" color="primary" gutterBottom>
        Sales Analytics
      </Typography>
      
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="time-unit-label">Time Unit</InputLabel>
              <Select
                labelId="time-unit-label"
                id="time-unit"
                value={timeUnit}
                label="Time Unit"
                onChange={(e) => setTimeUnit(e.target.value)}
                MenuProps={{
                  PaperProps: {
                    style: { maxHeight: 300 }
                  }
                }}
                renderValue={(selected) => {
                  return selected === "day" ? "Daily" :
                    selected === "week" ? "Weekly" :
                    selected === "month" ? "Monthly" : selected;
                }}
              >
                <MenuItem value="day">Daily</MenuItem>
                <MenuItem value="week">Weekly</MenuItem>
                <MenuItem value="month">Monthly</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="period-label">Period</InputLabel>
              <Select
                labelId="period-label"
                id="period"
                value={period}
                label="Period"
                onChange={(e) => setPeriod(e.target.value)}
                MenuProps={{
                  PaperProps: {
                    style: { maxHeight: 300 }
                  }
                }}
                renderValue={(selected) => {
                  return selected === "last7" ? "Last 7 Days" :
                    selected === "last30" ? "Last 30 Days" :
                    selected === "last90" ? "Last 90 Days" : selected;
                }}
              >
                <MenuItem value="last7">Last 7 Days</MenuItem>
                <MenuItem value="last30">Last 30 Days</MenuItem>
                <MenuItem value="last90">Last 90 Days</MenuItem>
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
            title="Total Sales"
            value={`$${summaryMetrics.totalSales.toFixed(2)}`}
            icon={<AttachMoneyIcon />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Total Transactions"
            value={summaryMetrics.totalTransactions}
            icon={<ShoppingCartIcon />}
            color="#2196f3"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Average Order Value"
            value={`$${summaryMetrics.avgOrderValue.toFixed(2)}`}
            icon={<TrendingUpIcon />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Total Items Sold"
            value={summaryMetrics.totalItems}
            icon={<ShoppingCartIcon />}
            color="#673ab7"
          />
        </Grid>
      </Grid>
      
      {/* Sales Data Table */}
      <Paper sx={{ p: 2 }}>
        <Typography component="h2" variant="h6" color="primary" gutterBottom>
          Sales Data
        </Typography>
        
        {salesData && salesData.length > 0 ? (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Period</TableCell>
                  <TableCell align="right">Total Sales</TableCell>
                  <TableCell align="right">Transactions</TableCell>
                  <TableCell align="right">Items Sold</TableCell>
                  <TableCell>Categories</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {salesData.map((row, index) => {
                    // Safe property access with fallbacks
                    const timeValue = row.time_value || row.timeValue || row.date || row.period || 'N/A';
                    const totalSales = 
                    typeof row.total_sales === 'number' ? row.total_sales :
                    typeof row.totalSales === 'number' ? row.totalSales :
                    typeof row.sales === 'number' ? row.sales :
                    typeof row.amount === 'number' ? row.amount :
                    parseFloat(row.total_sales || row.totalSales || row.sales || row.amount || 0);
                    
                    const transactionCount = 
                    typeof row.transaction_count === 'number' ? row.transaction_count :
                    typeof row.transactionCount === 'number' ? row.transactionCount :
                    typeof row.transactions === 'number' ? row.transactions :
                    typeof row.orders === 'number' ? row.orders :
                    parseInt(row.transaction_count || row.transactionCount || row.transactions || row.orders || 0);
                    
                    const itemCount = 
                    typeof row.item_count === 'number' ? row.item_count :
                    typeof row.itemCount === 'number' ? row.itemCount :
                    typeof row.items === 'number' ? row.items :
                    typeof row.products === 'number' ? row.products :
                    parseInt(row.item_count || row.itemCount || row.items || row.products || 0);
                    
                    // Handle categories with fallbacks
                    const categories = row.categories || row.category || [];
                    const categoryText = Array.isArray(categories) && categories.length > 0
                    ? categories.slice(0, 3).join(', ') + (categories.length > 3 ? '...' : '')
                    : 'N/A';
                    
                    return (
                    <TableRow key={index}>
                        <TableCell>{timeValue}</TableCell>
                        <TableCell align="right">${totalSales.toFixed(2)}</TableCell>
                        <TableCell align="right">{transactionCount}</TableCell>
                        <TableCell align="right">{itemCount}</TableCell>
                        <TableCell>{categoryText}</TableCell>
                    </TableRow>
                    );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box sx={{ minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">
              No sales data available. Try generating some sales data first.
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default Sales;