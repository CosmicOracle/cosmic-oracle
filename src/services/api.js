import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Dashboard services
export const getDashboardStats = () => api.get('/dashboard/stats');
export const getRecentPredictions = () => api.get('/dashboard/recent-predictions');
export const getSystemStatus = () => api.get('/dashboard/system-status');

// Prediction services
export const getPredictions = (params) => api.get('/predictions', { params });
export const createPrediction = (data) => api.post('/predictions', data);
export const getPredictionById = (id) => api.get(`/predictions/${id}`);
export const updatePrediction = (id, data) => api.put(`/predictions/${id}`, data);
export const deletePrediction = (id) => api.delete(`/predictions/${id}`);

// Data Analysis services
export const getDataSources = () => api.get('/data-sources');
export const getDataSourceById = (id) => api.get(`/data-sources/${id}`);
export const analyzeData = (data) => api.post('/data-analysis', data);
export const getAnalysisResults = (id) => api.get(`/data-analysis/${id}`);
export const getHistoricalData = (params) => api.get('/data-analysis/historical', { params });
export const getDataAnalysis = (params) => api.get('/data-analysis/overview', { params });
export const getPredictionAccuracy = (params) => api.get('/data-analysis/accuracy', { params });
export const getMarketTrends = (params) => api.get('/data-analysis/market-trends', { params });

// Settings services
export const getUserSettings = () => api.get('/settings/user');
export const updateUserSettings = (data) => api.put('/settings/user', data);
export const getSystemSettings = () => api.get('/settings/system');
export const updateSystemSettings = (data) => api.put('/settings/system', data);
export const getApiKeys = () => api.get('/settings/api-keys');
export const createApiKey = (data) => api.post('/settings/api-keys', data);
export const deleteApiKey = (id) => api.delete(`/settings/api-keys/${id}`);

export default api;