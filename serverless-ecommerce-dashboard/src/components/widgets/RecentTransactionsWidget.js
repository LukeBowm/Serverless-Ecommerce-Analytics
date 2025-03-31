import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableRow, Typography, Box } from '@mui/material';

const RecentTransactionsWidget = ({ recentSales = [] }) => {
  if (!recentSales || recentSales.length === 0) {
    return (
      <Box textAlign="center" py={2}>
        <Typography color="text.secondary">No recent transactions</Typography>
      </Box>
    );
  }

  return (
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
        {recentSales.slice(0, 5).map((row, index) => (
          <TableRow key={index}>
            <TableCell>{row.time_value}</TableCell>
            <TableCell>${row.total_sales?.toFixed(2) || '0.00'}</TableCell>
            <TableCell>{row.transaction_count || 0}</TableCell>
            <TableCell>{row.item_count || 0}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export default RecentTransactionsWidget;
