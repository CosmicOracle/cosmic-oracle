/**
 * Represents the main application controller for the Cosmic Oracle frontend.
 * Manages application initialization, routing, settings, and core UI interactions.
 * 
 * @class
 * @description Handles the entire lifecycle of the frontend application, including 
 * navigation, settings management, dashboard loading, and core functionality.
 */
/**
 * Main application controller for the Cosmic Oracle frontend.
 * Manages application initialization, routing, settings, and core UI interactions.
 * 
 * @class
 * @description Handles application lifecycle, navigation, and core frontend logic
 */
// @ts-nocheck
/**
 * Main Application Controller for Cosmic Oracle Frontend
 */
class AppController {
    constructor() {
        // Initialize dependencies
        this.api = window.cosmicOracleAPI;
        this.authHandler = window.authHandler;
        this.chartRenderer = window.chartRenderer;
        this.currentView = 'dashboard';
        this.settings = this.loadSettings();
        
        // Set cloud provider
        this.cloudProvider = localStorage.getItem('cloudProvider') || 'azure';
        this.api.setCloudProvider(this.cloudProvider);
        
        // Initialize the application
        this.initializeApp();
    }

    async initializeApp() {
        await this.setupEventListeners();
        this.setupRouting();
        await this.loadDashboard();
        this.initializeSettings();
    }

    loadSettings() {
        return JSON.parse(localStorage.getItem('userSettings')) || {
            houseSystem: 'placidus',
            aspectOrbs: 'medium',
            theme: 'light'
        };
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const route = e.target.getAttribute('href').replace('/', '');
                this.navigateTo(route || 'dashboard');
            });
        });

        // Settings changes
        const settingsForm = document.getElementById('settings-form');
        if (settingsForm) {
            settingsForm.addEventListener('change', (e) => {
                const setting = e.target.id.replace('-setting', '');
                const value = e.target.value;
                this.updateSetting(setting, value);
            });
        }
    }

    setupRouting() {
        window.addEventListener('popstate', (e) => {
            const route = e.state?.route || 'dashboard';
            this.navigateTo(route, false);
        });
    }

    async navigateTo(route, addToHistory = true) {
        const routeMap = {
            dashboard: () => this.loadDashboard(),
            'birth-chart': () => this.loadBirthChart(),
            synastry: () => this.loadSynastry(),
            'planetary-hours': () => this.loadPlanetaryHours()
        };

        // Hide all sections
        document.querySelectorAll('main > section').forEach(section => {
            section.style.display = 'none';
        });

        // Show loading spinner
        this.showLoading(true);

        try {
            // Load the new route
            if (routeMap[route]) {
                await routeMap[route]();
                this.currentView = route;
                
                if (addToHistory) {
                    history.pushState({ route }, '', `/${route}`);
                }
            }
        } catch (error) {
            console.error(`Error loading route ${route}:`, error);
            this.showError('Failed to load page content');
        }

        // Hide loading spinner
        this.showLoading(false);
    }

    async loadDashboard() {
        const dashboard = document.getElementById('dashboard');
        if (!dashboard) return;

        dashboard.style.display = 'block';

        try {
            // Load current transits
            const transits = await this.api.getCurrentTransits();
            this.updateTransitDisplay(transits);

            // Load moon info
            const moonInfo = await this.api.getMoonInfo();
            this.updateMoonDisplay(moonInfo);

            // Load planetary hours
            const now = new Date();
            const planetaryHours = await this.api.calculatePlanetaryHours({
                date: now.toISOString().split('T')[0],
                time: now.toTimeString().split(' ')[0]
            });
            this.updatePlanetaryHoursDisplay(planetaryHours);

            // Load daily forecast if authenticated
            if (this.authHandler.checkAuth()) {
                const forecast = await this.api.getPersonalForecast({
                    date: now.toISOString().split('T')[0]
                });
                this.updateForecastDisplay(forecast);
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Failed to load some dashboard components');
        }
    }

    updateTransitDisplay(data) {
        const container = document.querySelector('#current-transits .transit-data');
        if (!container) return;

        const html = data.transits.map(transit => `
            <div class="transit-item">
                <span class="planet">${transit.planet}</span>
                <span class="position">${transit.sign} ${transit.degree}°</span>
                ${transit.aspect ? `
                    <span class="aspect">${transit.aspect} ${transit.aspectedPlanet}</span>
                ` : ''}
            </div>
        `).join('');

        container.innerHTML = html;
    }

    updateMoonDisplay(data) {
        const container = document.querySelector('#moon-phase .moon-data');
        if (!container) return;

        container.innerHTML = `
            <div class="moon-info">
                <div class="phase">${data.phase}</div>
                <div class="sign">Moon in ${data.sign}</div>
                <div class="illumination">Illumination: ${(data.illumination * 100).toFixed(1)}%</div>
            </div>
        `;
    }

    showLoading(show = true) {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.style.display = show ? 'flex' : 'none';
        }
    }

    showError(message) {
        const container = document.getElementById('message-container');
        if (!container) return;

        const errorElement = document.createElement('div');
        errorElement.className = 'message error';
        errorElement.textContent = message;

        container.appendChild(errorElement);
        setTimeout(() => errorElement.remove(), 5000);
    }

    async updateSetting(setting, value) {
        this.settings[setting] = value;
        localStorage.setItem('userSettings', JSON.stringify(this.settings));

        if (this.authHandler.checkAuth()) {
            try {
                await this.api.updateUserSettings({ [setting]: value });
            } catch (error) {
                console.error('Failed to sync setting:', error);
            }
        }

        // Apply setting changes
        if (setting === 'theme') {
            document.body.className = value;
        }
    }

    initializeSettings() {
        // Apply saved settings
        document.body.className = this.settings.theme;
        
        // Update form values
        Object.entries(this.settings).forEach(([setting, value]) => {
            const element = document.getElementById(`${setting}-setting`);
            if (element) {
                element.value = value;
            }
        });
    }
}

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log("Cosmic Oracle Frontend is ready. Initializing...");
    window.app = new AppController();
});