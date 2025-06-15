// API Client for Cosmic Oracle
const API_CONFIG = {
    baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
    apiKey: process.env.REACT_APP_API_KEY,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.REACT_APP_API_KEY
    }
};

class CosmicOracleAPI {
    constructor() {
        this.baseUrl = API_CONFIG.baseUrl;
        this.headers = API_CONFIG.headers;
    }

    async fetchWithAuth(endpoint, options = {}) {
        const token = localStorage.getItem('token');
        const headers = {
            ...this.headers,
            ...(token && { Authorization: `Bearer ${token}` }),
            ...options.headers
        };

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication Endpoints
    async login(credentials) {
        return this.fetchWithAuth('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }

    async register(userData) {
        return this.fetchWithAuth('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    // Birth Chart Endpoints
    async getBirthChart(params) {
        const queryString = new URLSearchParams(params).toString();
        return this.fetchWithAuth(`/astronomical/birth-chart?${queryString}`);
    }

    async saveBirthChart(chartData) {
        return this.fetchWithAuth('/charts', {
            method: 'POST',
            body: JSON.stringify(chartData)
        });
    }

    // Transit Endpoints
    async getCurrentTransits() {
        return this.fetchWithAuth('/astronomical/current-transits');
    }

    async getTransitForecast(params) {
        const queryString = new URLSearchParams(params).toString();
        return this.fetchWithAuth(`/predictive/transits?${queryString}`);
    }

    // Lunar Information
    async getMoonInfo() {
        return this.fetchWithAuth('/astronomical/moon-info');
    }

    async getLunarMansion() {
        return this.fetchWithAuth('/astronomical/lunar-mansion');
    }

    // Advanced Calculations
    async calculatePlanetaryHours(params) {
        const queryString = new URLSearchParams(params).toString();
        return this.fetchWithAuth(`/astronomical/planetary-hours?${queryString}`);
    }

    async getArabicParts(params) {
        const queryString = new URLSearchParams(params).toString();
        return this.fetchWithAuth(`/astronomical/arabic-parts?${queryString}`);
    }

    async getFixedStars(params) {
        const queryString = new URLSearchParams(params).toString();
        return this.fetchWithAuth(`/astronomical/fixed-stars?${queryString}`);
    }

    // Relationship Astrology
    async calculateSynastry(params) {
        return this.fetchWithAuth('/synastry/calculate', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    async calculateComposite(params) {
        return this.fetchWithAuth('/composite/calculate', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    async getCompatibility(params) {
        return this.fetchWithAuth('/compatibility/analyze', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    // Predictive Astrology
    async calculateSolarReturn(params) {
        const queryString = new URLSearchParams(params).toString();
        return this.fetchWithAuth(`/predictive/solar-return?${queryString}`);
    }

    async getPersonalForecast(params) {
        const queryString = new URLSearchParams(params).toString();
        return this.fetchWithAuth(`/predictive/personal-forecast?${queryString}`);
    }

    // Spiritual Tools
    async getChakraAnalysis(params) {
        return this.fetchWithAuth('/spiritual/chakra-analysis', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    async getCrystalRecommendations(params) {
        return this.fetchWithAuth('/spiritual/crystal-recommendations', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    async getMeditationGuidance(params) {
        return this.fetchWithAuth('/spiritual/meditation-guidance', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    // Subscription Management
    async getSubscriptionPlans() {
        return this.fetchWithAuth('/subscription/plans');
    }

    async subscribeToPlan(planData) {
        return this.fetchWithAuth('/subscription/subscribe', {
            method: 'POST',
            body: JSON.stringify(planData)
        });
    }

    // User Profile
    async getUserProfile() {
        return this.fetchWithAuth('/users/me');
    }

    async updateUserProfile(profileData) {
        return this.fetchWithAuth('/users/me', {
            method: 'PATCH',
            body: JSON.stringify(profileData)
        });
    }

    // Settings
    async getUserSettings() {
        return this.fetchWithAuth('/users/settings');
    }

    async updateUserSettings(settings) {
        return this.fetchWithAuth('/users/settings', {
            method: 'PATCH',
            body: JSON.stringify(settings)
        });
    }
}

// Export API instance
window.cosmicOracleAPI = new CosmicOracleAPI();
