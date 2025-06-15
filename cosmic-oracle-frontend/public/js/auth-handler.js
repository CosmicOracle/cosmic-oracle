// Authentication Handler
class AuthHandler {
    constructor(api) {
        this.api = api;
        this.isAuthenticated = !!localStorage.getItem('token');
        this.setupAuthUI();
        this.setupEventListeners();
    }

    setupAuthUI() {
        const authSection = document.getElementById('auth-section');
        const loginLink = document.getElementById('login-link');
        const registerLink = document.getElementById('register-link');
        const logoutButton = document.getElementById('logout-button');

        if (this.isAuthenticated) {
            loginLink.style.display = 'none';
            registerLink.style.display = 'none';
            logoutButton.style.display = 'block';
        } else {
            loginLink.style.display = 'block';
            registerLink.style.display = 'block';
            logoutButton.style.display = 'none';
        }
    }

    setupEventListeners() {
        const logoutButton = document.getElementById('logout-button');
        logoutButton?.addEventListener('click', () => this.handleLogout());

        // Listen for auth state changes
        window.addEventListener('auth-state-changed', () => {
            this.isAuthenticated = !!localStorage.getItem('token');
            this.setupAuthUI();
        });
    }

    async handleLogin(credentials) {
        try {
            const response = await this.api.login(credentials);
            if (response.token) {
                localStorage.setItem('token', response.token);
                this.isAuthenticated = true;
                window.dispatchEvent(new CustomEvent('auth-state-changed'));
                this.showMessage('Successfully logged in!', 'success');
                return true;
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showMessage('Login failed. Please check your credentials.', 'error');
            return false;
        }
    }

    async handleRegister(userData) {
        try {
            const response = await this.api.register(userData);
            if (response.success) {
                this.showMessage('Registration successful! Please login.', 'success');
                return true;
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showMessage('Registration failed. Please try again.', 'error');
            return false;
        }
    }

    handleLogout() {
        localStorage.removeItem('token');
        this.isAuthenticated = false;
        window.dispatchEvent(new CustomEvent('auth-state-changed'));
        this.showMessage('Successfully logged out!', 'success');
        window.location.href = '/';
    }

    showMessage(message, type = 'info') {
        const container = document.getElementById('message-container');
        if (!container) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;

        container.appendChild(messageElement);

        // Remove message after 5 seconds
        setTimeout(() => {
            messageElement.remove();
        }, 5000);
    }

    checkAuth() {
        return this.isAuthenticated;
    }
}

// Initialize auth handler
window.authHandler = new AuthHandler(window.cosmicOracleAPI);
