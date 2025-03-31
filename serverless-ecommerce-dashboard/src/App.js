import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box, Drawer, List, ListItem, ListItemText, ListItemIcon, CssBaseline } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import BarChartIcon from '@mui/icons-material/BarChart';
import PeopleIcon from '@mui/icons-material/People';
import InventoryIcon from '@mui/icons-material/Inventory';
import DescriptionIcon from '@mui/icons-material/Description';

import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';
import Sales from './pages/Sales'; 
import Customers from './pages/Customers'; 
import Inventory from './pages/Inventory'; 

// Error boundary component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Container sx={{ mt: 4 }}>
          <Typography variant="h4" color="error">Something went wrong.</Typography>
          <Typography variant="body1">There was an error loading this page. Please try again later.</Typography>
        </Container>
      );
    }
    return this.props.children;
  }
}

const drawerWidth = 240;

function App() {
  return (
    <Router>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <Typography variant="h6" noWrap component="div">
              E-commerce Analytics Dashboard
            </Typography>
          </Toolbar>
        </AppBar>
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto' }}>
            <List>
              <ListItem button component={Link} to="/">
                <ListItemIcon><DashboardIcon /></ListItemIcon>
                <ListItemText primary="Dashboard" />
              </ListItem>
              <ListItem button component={Link} to="/sales">
                <ListItemIcon><BarChartIcon /></ListItemIcon>
                <ListItemText primary="Sales" />
              </ListItem>
              <ListItem button component={Link} to="/customers">
                <ListItemIcon><PeopleIcon /></ListItemIcon>
                <ListItemText primary="Customers" />
              </ListItem>
              <ListItem button component={Link} to="/inventory">
                <ListItemIcon><InventoryIcon /></ListItemIcon>
                <ListItemText primary="Inventory" />
              </ListItem>
              <ListItem button component={Link} to="/reports">
                <ListItemIcon><DescriptionIcon /></ListItemIcon>
                <ListItemText primary="Reports" />
              </ListItem>
            </List>
          </Box>
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/sales" element={
              <ErrorBoundary>
                <Sales />
              </ErrorBoundary>
            } />
            <Route path="/customers" element={
              <ErrorBoundary>
                <Customers />
              </ErrorBoundary>
            } />
            <Route path="/inventory" element={
              <ErrorBoundary>
                <Inventory />
              </ErrorBoundary>
            } />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </Box>
      </Box>
    </Router>
  );
}

export default App;