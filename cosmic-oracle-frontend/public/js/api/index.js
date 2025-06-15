// public/js/api/index.js

import axios from 'axios';

const apiClient = axios.create({ baseURL: '/api/v1' });

// ... (interceptor logic remains the same) ...

export const api = {
    // --- ADD THIS NEW FUNCTION ---
    registerUser: (userData) => apiClient.post('/auth/register', userData),
    
    // This is the login function needed by login.js
    login: (credentials) => apiClient.post('/auth/login', credentials),

    // ... (all your other api functions like getNatalChart, etc.) ...
};