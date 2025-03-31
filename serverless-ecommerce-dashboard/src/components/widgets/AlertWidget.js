import React from 'react';
import { List, ListItem, ListItemText, Typography, Box } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';

const AlertWidget = ({ notifications = [] }) => {
  if (!notifications || notifications.length === 0) {
    return (
      <Box textAlign="center" py={2}>
        <Typography color="text.secondary">No recent alerts</Typography>
      </Box>
    );
  }

  return (
    <List dense>
      {notifications.slice(0, 4).map((notification, index) => (
        <ListItem key={index} divider={index < notifications.length - 1}>
          <NotificationsIcon color="warning" sx={{ mr: 1 }} />
          <ListItemText
            primary={notification.subject || 'Alert'}
            secondary={notification.created_at || ''}
          />
        </ListItem>
      ))}
    </List>
  );
};

export default AlertWidget;
