import axios from 'axios';
import config from '../config';

const api = axios.create({
  baseURL: config.apiUrl,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const fetchDashboardSummary = async () => {
  try {
    console.log('🌐 Making API request to:', `${config.apiUrl}/api`);
    const response = await api.get('/api');
    console.log('🌐 Raw API dashboard response:', response);
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard summary:', error);
    throw error;
  }
};

export const fetchSalesData = async (timeUnit = 'day', period = 'last7') => {
  try {
    console.log('🔍 Making API request to:', `${config.apiUrl}/api/sales?timeUnit=${timeUnit}&period=${period}`);
    const response = await api.get(`/api/sales?timeUnit=${timeUnit}&period=${period}`);
    console.log('🌐 Raw API response:', response);
    
    // Return data in a consistent format
    if (response.data && response.data.data) {
      return response.data.data;  // If data is nested in data property
    } else if (Array.isArray(response.data)) {
      return response.data;       // If data is an array
    } else if (response.data) {
      // Look for arrays in the object
      for (const key in response.data) {
        if (Array.isArray(response.data[key])) {
          return response.data[key];
        }
      }
      return [response.data];     // Last resort - treat the object as a single record
    }
    return [];                   // No data found
  } catch (error) {
    console.error('Error fetching sales data:', error);
    throw error;
  }
};

export const fetchCustomerData = async (cohort = null) => {
  try {
    const url = cohort ? `/api/customers?cohort=${cohort}` : '/api/customers';
    console.log('🌐 Making API request to:', `${config.apiUrl}${url}`);
    const response = await api.get(url);
    console.log('🌐 Raw API customer response:', response);
    return response.data;
  } catch (error) {
    console.error('🌐 Error fetching customer data:', error);
    throw error;
  }
};

export const fetchInventoryData = async (status = null, category = null) => {
  try {
    let url = '/api/inventory';
    const params = [];
    if (status) params.push(`status=${status}`);
    if (category) params.push(`category=${category}`);
    if (params.length > 0) url += `?${params.join('&')}`;
    
    console.log('🌐 Making API request to:', `${config.apiUrl}${url}`);
    const response = await api.get(url);
    console.log('🌐 Raw API inventory response:', response);
    return response.data;
  } catch (error) {
    console.error('🌐 Error fetching inventory data:', error);
    throw error;
  }
};

export const fetchNotifications = async (type = null, limit = 10) => {
  try {
    let url = '/api/notifications';
    const params = [];
    if (type) params.push(`type=${type}`);
    if (limit) params.push(`limit=${limit}`);
    if (params.length > 0) url += `?${params.join('&')}`;
    
    console.log('🌐 Making API request to:', `${config.apiUrl}${url}`);
    const response = await api.get(url);
    console.log('🌐 Raw API notifications response:', response);
    return response.data;
  } catch (error) {
    console.error('Error fetching notifications:', error);
    throw error;
  }
};

export const generateReport = async (reportType, format, period) => {
  try {
    console.log('🌐 Making API report request with:', { reportType, format, period });
    const response = await api.post('/api/reports', {
      reportType,
      format,
      period
    });
    console.log('🌐 Raw API report response:', response);
    return response.data;
  } catch (error) {
    console.error('Error generating report:', error);
    throw error;
  }
};

export default {
  fetchDashboardSummary,
  fetchSalesData,
  fetchCustomerData,
  fetchInventoryData,
  fetchNotifications,
  generateReport
};