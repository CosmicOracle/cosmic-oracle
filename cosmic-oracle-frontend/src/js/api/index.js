// src/js/api/index.js
import axios from 'axios';
import { store } from '../state/store.js'; // Import the store

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// --- THIS IS THE PERSISTENCE UPGRADE ---
// Use an interceptor to dynamically add the Authorization header to every request.
apiClient.interceptors.request.use(
  (config) => {
    const token = store.getState().auth?.token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// The response interceptor remains the same...
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error.response?.data || { error: 'A network error occurred.' })
);

// --- Exported API Functions ---
export const api = {
  // Auth and User routes
  registerUser: (userData) => apiClient.post('/auth/register', userData),
  login: (credentials) => apiClient.post('/auth/login', credentials),
  getUserProfile: () => apiClient.get('/users/me'), // No token needed here, interceptor adds it

  // Other services...
  getNatalChart: (natalData) => apiClient.post('/astrology/swisseph/natal-chart', natalData),
  // ... all your other API functions ...
};