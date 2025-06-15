// src/js/api.js
import axios from 'axios';

const apiClient = axios.create({ baseURL: '/api/v1' });

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error.response?.data || { error: 'A network error occurred.' })
);

export const api = {
  // Add all your API functions here.
  getPersonalSkyDashboard: () => apiClient.get('/user/personal-sky/dashboard'),
};