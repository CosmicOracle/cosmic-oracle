// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\eventListeners.js
import { handleLogin, handleRegister, handleLogout, showLoginForm, showRegisterForm } from './auth.js';
import { showTab } from './script.js'; // Corrected: showTab is exported from script.js, not uiUpdate.js

/**
 * Sets up all the primary event listeners for the application.
 * This approach avoids using inline 'onclick' attributes in the HTML,
 * which is a modern best practice that works with JS modules.
 */
function setupEventListeners() {
    console.log("Setting up application event listeners...");

    // --- Authentication Listeners ---
    const loginRegisterButton = document.getElementById('loginRegisterButton');
    const logoutButton = document.getElementById('logoutButton');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginRegisterButton) {
        loginRegisterButton.addEventListener('click', showLoginForm);
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
    }

    if (loginForm) {
        loginForm.querySelector('button').addEventListener('click', handleLogin);
        loginForm.querySelector('a').addEventListener('click', (e) => {
            e.preventDefault(); // Prevent link from navigating
            showRegisterForm();
        });
    }

    if (registerForm) {
        registerForm.querySelector('button').addEventListener('click', handleRegister);
        registerForm.querySelector('a').addEventListener('click', (e) => {
            e.preventDefault(); // Prevent link from navigating
            showLoginForm();
        });
    }

    // --- Tab Navigation Listener (using Event Delegation) ---
    const navTabs = document.querySelector('.nav-tabs');
    if (navTabs) {
        navTabs.addEventListener('click', (event) => {
            // Check if a tab button was clicked
            if (event.target.matches('.tab-button')) {
                const tabName = event.target.dataset.target;
                if (tabName) {
                    showTab(tabName, event);
                }
            }
        });
    }
    
    console.log("Event listeners setup complete.");
}

// Run the setup function once the DOM is fully loaded
document.addEventListener('DOMContentLoaded', setupEventListeners);