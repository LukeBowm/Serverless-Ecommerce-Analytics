import React, { useState } from 'react';
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
  Button, 
  CircularProgress,
  Alert,
  Snackbar,
  Link
} from '@mui/material';
import { generateReport } from '../services/api';
import DescriptionIcon from '@mui/icons-material/Description';
import FileDownloadIcon from '@mui/icons-material/FileDownload';

const Reports = () => {
  const [reportType, setReportType] = useState('sales');
  const [reportFormat, setReportFormat] = useState('json');
  const [timePeriod, setTimePeriod] = useState('last30');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [reportUrl, setReportUrl] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      
      const result = await generateReport(reportType, reportFormat, timePeriod);
      
      setReportUrl(result.reportUrl);
      setSuccess(true);
    } catch (err) {
      setError('Failed to generate report. Please try again later.');
      console.error('Report generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(false);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 4, display: 'flex', flexDirection: 'column' }}>
        <Typography component="h1" variant="h4" color="primary" gutterBottom>
          <DescriptionIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Generate Reports
        </Typography>
        
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Generate custom reports for sales, customer insights, and inventory status
          in your preferred format.
        </Typography>
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mb: 4 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel id="report-type-label">Report Type</InputLabel>
                <Select
                  labelId="report-type-label"
                  id="report-type"
                  value={reportType}
                  label="Report Type"
                  onChange={(e) => setReportType(e.target.value)}
                >
                  <MenuItem value="sales">Sales Report</MenuItem>
                  <MenuItem value="customers">Customer Insights</MenuItem>
                  <MenuItem value="inventory">Inventory Status</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel id="report-format-label">Format</InputLabel>
                <Select
                  labelId="report-format-label"
                  id="report-format"
                  value={reportFormat}
                  label="Format"
                  onChange={(e) => setReportFormat(e.target.value)}
                >
                  <MenuItem value="json">JSON</MenuItem>
                  <MenuItem value="csv">CSV</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            {reportType === 'sales' && (
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel id="time-period-label">Time Period</InputLabel>
                  <Select
                    labelId="time-period-label"
                    id="time-period"
                    value={timePeriod}
                    label="Time Period"
                    onChange={(e) => setTimePeriod(e.target.value)}
                  >
                    <MenuItem value="last7">Last 7 Days</MenuItem>
                    <MenuItem value="last30">Last 30 Days</MenuItem>
                    <MenuItem value="last12">Last 12 Months</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}
          </Grid>
          
          <Box sx={{ mt: 3 }}>
            <Button 
              type="submit" 
              variant="contained" 
              color="primary" 
              size="large"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <FileDownloadIcon />}
            >
              {loading ? 'Generating...' : 'Generate Report'}
            </Button>
          </Box>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        
        {reportUrl && (
          <Paper variant="outlined" sx={{ p: 3, mt: 3, bgcolor: 'background.default' }}>
            <Typography variant="h6" gutterBottom>
              Your Report is Ready!
            </Typography>
            <Link 
              href={reportUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              sx={{ display: 'flex', alignItems: 'center' }}
            >
              <FileDownloadIcon sx={{ mr: 1 }} />
              Download Report
            </Link>
          </Paper>
        )}
        
        <Snackbar
          open={success}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
        >
          <Alert onClose={handleCloseSnackbar} severity="success">
            Report generated successfully!
          </Alert>
        </Snackbar>
      </Paper>
    </Container>
  );
};

export default Reports;