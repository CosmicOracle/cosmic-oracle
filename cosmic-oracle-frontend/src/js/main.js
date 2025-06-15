// Main application entry point
import { apiService } from './apiService.js';
import { uiController } from './uiController.js';

// Global data store
window.COSMIC_ORACLE = {
    ALL_ZODIAC_SIGNS_DATA: null,
    USER_PREFERENCES: null
};

// Initialize the application
async function initializeApp() {
    try {
        // Initialize UI controller
        uiController.initialize();

        // Load initial data
        const [zodiacSigns, userPrefs] = await Promise.all([
            apiService.fetchAllZodiacSigns(),
            apiService.fetchWithAuth('/user/preferences').catch(() => ({}))
        ]);

        // Store data globally
        window.COSMIC_ORACLE.ALL_ZODIAC_SIGNS_DATA = zodiacSigns;
        window.COSMIC_ORACLE.USER_PREFERENCES = userPrefs;

        // Initialize feature controllers
        const controllers = [
            'zodiacFeaturesController',
            'yearAheadReportController',
            'personalToolsController',
            'journalController',
            'meditationController'
        ];

        controllers.forEach(controllerName => {
            if (window[controllerName] && typeof window[controllerName].initialize === 'function') {
                window[controllerName].initialize();
            }
        });

        // Hide loading screen
        uiController.hideLoading();

    } catch (error) {
        console.error('Error initializing application:', error);
        uiController.showError('Failed to initialize application. Please refresh the page.');
    }
}

// Start initialization when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApp);

// Handle authentication events
document.addEventListener('authStateChanged', (event) => {
    const { isAuthenticated } = event.detail;
    uiController.updateUserUI(isAuthenticated);
});

// Export for use in other modules
export const app = {
    initialize: initializeApp
};
