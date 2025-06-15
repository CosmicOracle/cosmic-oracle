// js/auth.js

const API_BASE_URL = 'http://127.0.0.1:5000/api'; // Your backend API base URL

// --- Session Management ---
export let currentUser = null;
let sessionRefreshTimer = null;

// API functions
async function getUserProfile() {
    const response = await fetchWithAuth(`${API_BASE_URL}/auth/me`);
    if (!response.ok) {
        throw new Error('Failed to fetch user profile');
    }
    return response.json();
}

async function loginUser(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.message || 'Login failed');
    }
    localStorage.setItem('accessToken', data.access_token);
    localStorage.setItem('refreshToken', data.refresh_token);
    return data.user;
}

async function registerUser(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.message || 'Registration failed');
    }
    return data;
}

/**
 * A wrapper for the fetch API that automatically handles JWT authentication
 * and token refresh.
 */
export async function fetchWithAuth(url, options = {}) {
    let accessToken = localStorage.getItem('accessToken');

    options.headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (accessToken) {
        options.headers['Authorization'] = `Bearer ${accessToken}`;
    }

    let response = await fetch(url, options);

    if (response.status === 401) {
        console.warn("Access token expired or invalid. Attempting to refresh...");
        const refreshTokenVal = localStorage.getItem('refreshToken');
        if (!refreshTokenVal) {
            console.log("No refresh token found. Logging out.");
            await handleLogout(false); 
            updateAuthUI(false);
            return response; 
        }

        try {
            const refreshResponse = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${refreshTokenVal}`,
                    'Content-Type': 'application/json'
                }
            });
            const refreshData = await refreshResponse.json();

            if (!refreshResponse.ok) {
                console.error("Refresh token also invalid or expired. Logging out.", refreshData);
                await handleLogout(false); 
                updateAuthUI(false);
                throw new Error(refreshData.error || refreshData.msg || "Session expired. Please login again.");
            }

            localStorage.setItem('accessToken', refreshData.access_token);
            console.log("Access token refreshed. Retrying original request...");
            
            options.headers['Authorization'] = `Bearer ${refreshData.access_token}`;
            response = await fetch(url, options);

        } catch (refreshError) {
            console.error("Error during token refresh:", refreshError);
            await handleLogout(false);
            updateAuthUI(false);
            throw refreshError; 
        }
    }
    return response;
}

export function showLoginForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginRegisterButton = document.getElementById('loginRegisterButton');
    const loginError = document.getElementById('loginError');

    if (loginForm) loginForm.style.display = 'block';
    if (registerForm) registerForm.style.display = 'none';
    if (loginRegisterButton) loginRegisterButton.style.display = 'none';
    if (loginError) loginError.textContent = '';
    
    const userEmailDisplay = document.getElementById('userEmailDisplay');
    const userInfoDiv = document.getElementById('userInfo');
    if (userEmailDisplay) userEmailDisplay.textContent = '';
    if (userInfoDiv) userInfoDiv.style.display = 'none';
}

export function showRegisterForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginRegisterButton = document.getElementById('loginRegisterButton');
    const registerError = document.getElementById('registerError');

    if (loginForm) loginForm.style.display = 'none';
    if (registerForm) registerForm.style.display = 'block';
    if (loginRegisterButton) loginRegisterButton.style.display = 'none';
    if (registerError) registerError.textContent = '';
}

export function updateAuthUI(isLoggedIn, userData = null) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const userInfoDiv = document.getElementById('userInfo');
    const userEmailDisplay = document.getElementById('userEmailDisplay');
    const loginRegisterButton = document.getElementById('loginRegisterButton');

    if (isLoggedIn && userData) {
        if (loginForm) loginForm.style.display = 'none';
        if (registerForm) registerForm.style.display = 'none';
        if (userInfoDiv) userInfoDiv.style.display = 'block';
        if (userEmailDisplay) userEmailDisplay.textContent = userData.email;
        if (loginRegisterButton) loginRegisterButton.style.display = 'none';
        currentUser = userData; 
    } else {
        if (userInfoDiv) userInfoDiv.style.display = 'none';
        if (loginRegisterButton) loginRegisterButton.style.display = 'block';
        currentUser = null; 
    }
}

// Initialize auth state
export async function initializeAuth() {
    const token = localStorage.getItem('accessToken');
    if (token) {
        try {
            const userData = await getUserProfile();
            updateAuthState(userData);
            startSessionRefreshTimer();
        } catch (error) {
            console.error('Failed to initialize auth:', error);
            await handleLogout(false);
        }
    }
    updateAuthUI(!!currentUser);
}

function startSessionRefreshTimer() {
    if (sessionRefreshTimer) clearInterval(sessionRefreshTimer);
    // Refresh token every 6 days (token expires in 7 days)
    sessionRefreshTimer = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            if (response.ok && data.access_token) {
                localStorage.setItem('accessToken', data.access_token);
            } else {
                throw new Error('Token refresh failed');
            }
        } catch (error) {
            console.error('Session refresh failed:', error);
            await handleLogout(false);
        }
    }, 6 * 24 * 60 * 60 * 1000); // 6 days in milliseconds
}

export async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const loginError = document.getElementById('loginError');

    try {
        const data = await loginUser(email, password);
        updateAuthState(data);
        startSessionRefreshTimer();
        updateAuthUI(true);
        // Assuming showTab is defined elsewhere or imported
        if (window.showTab) window.showTab('daily');
    } catch (error) {
        if (loginError) loginError.textContent = error.message;
        console.error('Login failed:', error);
    }
}

export async function handleRegister(event) {
    event.preventDefault();
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const registerError = document.getElementById('registerError');

    if (password !== confirmPassword) {
        if (registerError) registerError.textContent = 'Passwords do not match';
        return;
    }

    try {
        await registerUser(email, password);
        const loginData = await loginUser(email, password);
        updateAuthState(loginData);
        startSessionRefreshTimer();
        updateAuthUI(true);
        // Assuming showTab is defined elsewhere or imported
        if (window.showTab) window.showTab('daily');
    } catch (error) {
        if (registerError) registerError.textContent = error.message;
        console.error('Registration failed:', error);
    }
}

export async function handleLogout(showConfirm = true) {
    if (showConfirm && !confirm('Are you sure you want to log out?')) {
        return;
    }

    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    if (sessionRefreshTimer) {
        clearInterval(sessionRefreshTimer);
        sessionRefreshTimer = null;
    }
    currentUser = null;
    updateAuthUI(false);
    showLoginForm();
}

function updateAuthState(userData) {
    currentUser = userData;
    const userEmailDisplay = document.getElementById('userEmailDisplay');
    if (userEmailDisplay) {
        userEmailDisplay.textContent = userData?.email || '';
    }
}

// Initialize auth when the script loads
document.addEventListener('DOMContentLoaded', () => {
    initializeAuth().catch(console.error);

    // Set up form event listeners
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginRegisterButton = document.getElementById('loginRegisterButton');
    const loginButton = document.getElementById('loginButton');
    const registerButton = document.getElementById('registerButton');
    const logoutButton = document.getElementById('logoutButton');

    if (loginForm) loginForm.addEventListener('submit', handleLogin);
    if (registerForm) registerForm.addEventListener('submit', handleRegister);
    if (loginRegisterButton) loginRegisterButton.addEventListener('click', showLoginForm);
    if (loginButton) loginButton.addEventListener('click', showLoginForm);
    if (registerButton) registerButton.addEventListener('click', showRegisterForm);
    if (logoutButton) logoutButton.addEventListener('click', handleLogout);
});