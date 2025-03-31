import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Grid, 
  Paper, 
  Typography, 
  Box, 
  CircularProgress, 
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import { fetchDashboardSummary } from '../services/api';
import MetricCard from '../components/widgets/MetricCard';
import SalesChart from '../components/charts/SalesChart';
import AlertWidget from '../components/widgets/AlertWidget';
import RecentTransactionsWidget from '../components/widgets/RecentTransactionsWidget';

// Icons
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import PeopleIcon from '@mui/icons-material/People';
import InventoryIcon from '@mui/icons-material/Inventory';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import WarningIcon from '@mui/icons-material/Warning';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    recentSales: [],
    customerCohorts: [],
    lowInventoryItems: 0,
    recentNotifications: []
  });

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        console.log('🔍 About to fetch dashboard data...');
        const data = await fetchDashboardSummary();
        console.log('📊 Dashboard data received:', data);
        console.log('📊 Dashboard data type:', typeof data);
        console.log('Full dashboard response structure:', JSON.stringify(data, null, 2));
        
        // Process the dashboard data
        const processedData = {
          recentSales: Array.isArray(data.recentSales) ? data.recentSales : [],
          customerCohorts: Array.isArray(data.customerCohorts) ? data.customerCohorts : [],
          lowInventoryItems: data.lowInventoryItems || 0,
          recentNotifications: Array.isArray(data.recentNotifications) ? data.recentNotifications : []
        };
        
        console.log('Processed dashboard data:', processedData);

        // Generate some placeholder alerts if none exist
        if (!processedData.recentNotifications || processedData.recentNotifications.length === 0) {
          processedData.recentNotifications = [
            {
              id: 'alert-1',
              type: 'inventory_alert',
              message: 'Low stock alert: Sneakers (5 remaining)',
              timestamp: new Date().toISOString(),
              status: 'open'
            },
            {
              id: 'alert-2',
              type: 'inventory_alert',
              message: 'Low stock alert: Headphones (3 remaining)',
              timestamp: new Date().toISOString(),
              status: 'open'
            }
          ];
        }
        
        setDashboardData(processedData);
        setError(null);
      } catch (err) {
        setError('Failed to load dashboard data. Please try again later.');
        console.error('Dashboard data loading error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
    
    // Set up auto-refresh every 30 seconds
    const refreshInterval = setInterval(() => {
      loadDashboardData();
    }, 30000);
    
    // Clear interval on component unmount
    return () => clearInterval(refreshInterval);
  }, []);

  // Calculate summary metrics
  const calculateMetrics = () => {
    const sales = dashboardData.recentSales || [];
    const cohorts = dashboardData.customerCohorts || [];
    
    console.log('Calculating metrics with sales:', sales);
    console.log('Calculating metrics with cohorts:', cohorts);
    
    // Calculate total sales from recent data - robust property checking
    let totalSales = 0;
    if (sales && sales.length > 0) {
      totalSales = sales.reduce((sum, day) => {
        // Try different property names for sales values
        const salesValue = 
          typeof day.total_sales === 'number' ? day.total_sales :
          typeof day.totalSales === 'number' ? day.totalSales : 
          typeof day.sales === 'number' ? day.sales :
          typeof day.amount === 'number' ? day.amount :
          typeof day.revenue === 'number' ? day.revenue :
          typeof day.total_sales === 'string' ? parseFloat(day.total_sales) || 0 :
          typeof day.totalSales === 'string' ? parseFloat(day.totalSales) || 0 :
          typeof day.sales === 'string' ? parseFloat(day.sales) || 0 :
          typeof day.amount === 'string' ? parseFloat(day.amount) || 0 :
          typeof day.revenue === 'string' ? parseFloat(day.revenue) || 0 : 0;
        
        console.log(`Adding ${salesValue} to sales sum (current: ${sum})`);
        return sum + salesValue;
      }, 0);
    }
    
    // Calculate total customers from cohorts - robust property checking
    let totalCustomers = 0;
    if (cohorts && cohorts.length > 0) {
      totalCustomers = cohorts.reduce((sum, cohort) => {
        const customerCount = 
          typeof cohort.customer_count === 'number' ? cohort.customer_count :
          typeof cohort.customerCount === 'number' ? cohort.customerCount : 
          typeof cohort.customers === 'number' ? cohort.customers :
          typeof cohort.count === 'number' ? cohort.count :
          typeof cohort.size === 'number' ? cohort.size :
          typeof cohort.customer_count === 'string' ? parseInt(cohort.customer_count) || 0 :
          typeof cohort.customerCount === 'string' ? parseInt(cohort.customerCount) || 0 :
          typeof cohort.customers === 'string' ? parseInt(cohort.customers) || 0 :
          typeof cohort.count === 'string' ? parseInt(cohort.count) || 0 :
          typeof cohort.size === 'string' ? parseInt(cohort.size) || 0 : 0;
        
        console.log(`Adding ${customerCount} to customer sum (current: ${sum})`);
        return sum + customerCount;
      }, 0);
    }
    
    // Calculate average order value with robust property checking
    let totalOrders = 0;
    if (sales && sales.length > 0) {
      totalOrders = sales.reduce((sum, day) => {
        const transactionCount = 
          typeof day.transaction_count === 'number' ? day.transaction_count :
          typeof day.transactionCount === 'number' ? day.transactionCount :
          typeof day.transactions === 'number' ? day.transactions :
          typeof day.orders === 'number' ? day.orders :
          typeof day.transaction_count === 'string' ? parseInt(day.transaction_count) || 0 :
          typeof day.transactionCount === 'string' ? parseInt(day.transactionCount) || 0 :
          typeof day.transactions === 'string' ? parseInt(day.transactions) || 0 :
          typeof day.orders === 'string' ? parseInt(day.orders) || 0 : 0;
          
        return sum + transactionCount;
      }, 0);
    }
    
    const avgOrderValue = totalOrders > 0 ? totalSales / totalOrders : 0;
    
    console.log('Calculated metrics:', { 
      totalSales, 
      totalCustomers, 
      avgOrderValue, 
      lowInventoryItems: dashboardData.lowInventoryItems 
    });
    
    return {
      totalSales,
      totalCustomers,
      avgOrderValue,
      lowInventoryItems: dashboardData.lowInventoryItems || 0
    };
  };

  const metrics = calculateMetrics();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
          <Typography color="error" gutterBottom>
            {error}
          </Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Summary Metrics */}
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Total Sales"
            value={`$${metrics.totalSales.toFixed(2)}`}
            icon={<AttachMoneyIcon />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Total Customers"
            value={metrics.totalCustomers}
            icon={<PeopleIcon />}
            color="#2196f3"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Avg Order Value"
            value={`$${metrics.avgOrderValue.toFixed(2)}`}
            icon={<TrendingUpIcon />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Low Stock Items"
            value={metrics.lowInventoryItems}
            icon={<InventoryIcon />}
            color={metrics.lowInventoryItems > 0 ? "#f44336" : "#4caf50"}
          />
        </Grid>

        {/* Sales Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Recent Sales
            </Typography>
            <SalesChart data={dashboardData.recentSales} />
          </Paper>
        </Grid>

        {/* Notifications */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240, overflow: 'auto' }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Recent Alerts
            </Typography>
            {dashboardData.recentNotifications && dashboardData.recentNotifications.length > 0 ? (
              <List>
                {dashboardData.recentNotifications.map((notification, index) => (
                  <React.Fragment key={notification.id || index}>
                    <ListItem>
                      <ListItemIcon>
                        <WarningIcon color="warning" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={notification.message} 
                        secondary={new Date(notification.timestamp).toLocaleString()}
                      />
                    </ListItem>
                    {index < dashboardData.recentNotifications.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                <Typography color="textSecondary">No recent alerts</Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Recent Transactions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Recent Transactions
            </Typography>
            {dashboardData.recentSales && dashboardData.recentSales.length > 0 ? (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Sales</TableCell>
                      <TableCell>Transactions</TableCell>
                      <TableCell>Items</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {dashboardData.recentSales.map((row, index) => {
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
                      
                      return (
                        <TableRow key={index}>
                          <TableCell>{timeValue}</TableCell>
                          <TableCell>${totalSales.toFixed(2)}</TableCell>
                          <TableCell>{transactionCount}</TableCell>
                          <TableCell>{itemCount}</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography align="center" sx={{ my: 3, color: 'text.secondary' }}>
                No transaction data available.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;