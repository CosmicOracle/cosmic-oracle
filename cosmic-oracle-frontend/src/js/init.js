// init.js - Main application initializer
import { init } from './script.js';
import { loadInitialContentData } from './uiUpdate.js';
import { initializeAuth } from './auth.js';

// Initialize everything when the DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Wait for authentication to initialize
        await initializeAuth();
        
        // Load initial content data
        await loadInitialContentData();
        
        // Initialize the main application
        await init();
        
        console.log('Application initialization complete');
    } catch (error) {
        console.error('Error during initialization:', error);
        document.body.innerHTML = `
            <div style="text-align: center; padding: 50px;">
                <h2>Error Loading Application</h2>
                <p style="color: red;">${error.message}</p>
                <p>Please refresh the page or contact support if the problem persists.</p>
            </div>
        `;
    }
});
