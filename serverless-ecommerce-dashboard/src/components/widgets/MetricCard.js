import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

const MetricCard = ({ title, value, icon, color }) => {
  return (
    <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Box display="flex" alignItems="center" mb={1}>
        <Box mr={1} sx={{ color }}>
          {icon}
        </Box>
        <Typography variant="h6" color="text.secondary">
          {title}
        </Typography>
      </Box>
      <Typography component="p" variant="h4">
        {value}
      </Typography>
    </Paper>
  );
};

export default MetricCard;
