// src/js/app.js
import { store } from './state/store.js';
import { UIManager } from './ui/UIManager.js';
import { authService } from './services/authService.js';
import '../styles/main.css';
import '../styles/components.css';

// --- Page Router (Simple) ---
// This function determines what to do based on the current page.
function handlePageLoad() {
  const path = window.location.pathname;

  if (path.includes('/login.html') || path.includes('/register.html')) {
    // Auth pages don't need initial data loading
  } else {
    // For protected pages, check for auth and redirect if not logged in
    if (!authService.isAuthenticated()) {
      console.log("Not authenticated, redirecting to login.");
      // window.location.href = '/login.html';
      return; // Stop further execution
    }
    // If authenticated, maybe fetch initial dashboard data
    // import { personalSkyService } from './services/personalSkyService.js';
    // personalSkyService.fetchDashboard();
  }
}

// --- Main Application Initialization ---
document.addEventListener('DOMContentLoaded', () => {
  console.log("Cosmic Oracle Frontend Initializing with Persistence...");
  
  // Instantiate the UI manager, which subscribes to the store and handles all rendering.
  new UIManager();
  
  // Handle the initial page load logic.
  handlePageLoad();
});