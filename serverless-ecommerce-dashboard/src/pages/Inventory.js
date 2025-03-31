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
import { fetchInventoryData } from '../services/api';
import InventoryIcon from '@mui/icons-material/Inventory';
import WarningIcon from '@mui/icons-material/Warning';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import CategoryIcon from '@mui/icons-material/Category';
import MetricCard from '../components/widgets/MetricCard';

const Inventory = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [inventoryData, setInventoryData] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [categories, setCategories] = useState([]);
  const [summaryMetrics, setSummaryMetrics] = useState({
    totalItems: 0,
    lowStockItems: 0,
    outOfStockItems: 0,
    categoriesCount: 0
  });

  useEffect(() => {
    const loadInventoryData = async () => {
      try {
        setLoading(true);
        console.log('🔍 About to fetch inventory data...');
        const data = await fetchInventoryData(statusFilter || null, categoryFilter || null);
        console.log('📊 Inventory data received:', data);
        console.log('📊 Inventory data type:', typeof data);
        console.log('📊 Is array?', Array.isArray(data));
        console.log('Full response structure:', JSON.stringify(data, null, 2));
        
        // Extract the array from the data object
        let processedData = [];
        // First check for common data structures
        if (data && data.categories) {
          // If data is organized by categories
          const allItems = [];
          for (const category in data.categories) {
            if (Array.isArray(data.categories[category])) {
              allItems.push(...data.categories[category]);
            }
          }
          processedData = allItems;
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
        
        console.log('Processed inventory data:', processedData);
        setInventoryData(processedData || []);
        
        // Extract categories for the dropdown
        if (processedData && processedData.length > 0) {
          const uniqueCategories = [...new Set(processedData.map(item => item.category))].filter(Boolean);
          setCategories(uniqueCategories);
          
          // Calculate summary metrics
          const totalItems = processedData.length;
          const lowStockItems = processedData.filter(item => 
            (item.inventory_status === 'low' || item.stock_level <= 20)
          ).length;
          const outOfStockItems = processedData.filter(item => 
            (item.inventory_status === 'out_of_stock' || item.stock_level <= 0)
          ).length;
          
          setSummaryMetrics({
            totalItems,
            lowStockItems,
            outOfStockItems,
            categoriesCount: uniqueCategories.length
          });
        }
        
        setError(null);
      } catch (err) {
        console.error('❌ Inventory data loading error:', err);
        setError('Failed to load inventory data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
  
    loadInventoryData();
  }, [statusFilter, categoryFilter]);

  const getStatusColor = (status, stockLevel) => {
    if (status === 'out_of_stock' || stockLevel <= 0) return 'error';
    if (status === 'low' || stockLevel <= 20) return 'warning';
    return 'success';
  };

  const getStatusText = (status, stockLevel) => {
    if (status === 'out_of_stock' || stockLevel <= 0) return 'Out of Stock';
    if (status === 'low' || stockLevel <= 20) return 'Low Stock';
    return 'In Stock';
  };

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
        Inventory Management
      </Typography>
      
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="status-label">Filter by Status</InputLabel>
              <Select
                labelId="status-label"
                id="status"
                value={statusFilter}
                label="Filter by Status"
                onChange={(e) => setStatusFilter(e.target.value)}
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
                <MenuItem value="">All Statuses</MenuItem>
                <MenuItem value="in_stock">In Stock</MenuItem>
                <MenuItem value="low_stock">Low Stock</MenuItem>
                <MenuItem value="out_of_stock">Out of Stock</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="category-label">Filter by Category</InputLabel>
              <Select
                labelId="category-label"
                id="category"
                value={categoryFilter}
                label="Filter by Category"
                onChange={(e) => setCategoryFilter(e.target.value)}
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
                <MenuItem value="">All Categories</MenuItem>
                {categories.map(category => (
                  <MenuItem key={category} value={category}>{category}</MenuItem>
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
            title="Total Products"
            value={summaryMetrics.totalItems}
            icon={<InventoryIcon />}
            color="#2196f3"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Low Stock Items"
            value={summaryMetrics.lowStockItems}
            icon={<WarningIcon />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Out of Stock"
            value={summaryMetrics.outOfStockItems}
            icon={<InventoryIcon />}
            color="#f44336"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Categories"
            value={summaryMetrics.categoriesCount}
            icon={<CategoryIcon />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>
      
      {/* Inventory Data Table */}
      <Paper sx={{ p: 2 }}>
        <Typography component="h2" variant="h6" color="primary" gutterBottom>
          Inventory Status
        </Typography>
        
        {inventoryData && inventoryData.length > 0 ? (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Product ID</TableCell>
                  <TableCell>Product Name</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell align="right">Current Stock</TableCell>
                  <TableCell align="right">Reorder Threshold</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {inventoryData.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>{row.product_id || 'N/A'}</TableCell>
                    <TableCell>{row.product_name || row.name || 'N/A'}</TableCell>
                    <TableCell>{row.category || 'N/A'}</TableCell>
                    <TableCell align="right">{row.stock_level || row.current_stock || 0}</TableCell>
                    <TableCell align="right">{row.reorder_threshold || 20}</TableCell>
                    <TableCell>
                      <Chip 
                        label={getStatusText(row.inventory_status, row.stock_level || row.current_stock)} 
                        color={getStatusColor(row.inventory_status, row.stock_level || row.current_stock)}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box sx={{ minHeight: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography color="text.secondary">
              No inventory data available. Try generating some inventory data first.
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default Inventory;