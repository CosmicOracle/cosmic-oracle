// cosmic-oracle-frontend/public/js/ui-manager.js
/**
 * Manages all user interface interactions, event listeners, and DOM updates.
 */

import { api } from './api.js';
// We don't need the ChartRenderer for this specific form, but it would be here for other forms.
// import { ChartRenderer } from './chart-renderer.js';

// --- DOM Element Selectors ---
// This makes it easy to find and update all element references in one place.
const dignityForm = document.getElementById('dignity-form');
const resultArea = document.getElementById('result-area'); // A more generic name
const errorContainer = document.getElementById('error-message');
const loader = document.getElementById('loader');

/**
 * Displays an error message to the user.
 * @param {string} message - The error message to display.
 */
function displayError(message) {
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    }
    if (resultArea) {
        resultArea.innerHTML = ''; // Clear results on error
    }
    console.error("UI Error:", message);
}

/**
 * Displays successful results in a formatted way.
 * @param {object} data - The JSON data to display.
 */
function displayResult(data) {
    if (resultArea) {
        // Using <pre> preserves the formatting of the JSON string.
        const pre = document.createElement('pre');
        pre.textContent = JSON.stringify(data, null, 2);
        resultArea.innerHTML = ''; // Clear previous content
        resultArea.appendChild(pre);
    }
}

/**
 * Shows or hides the loading spinner.
 * @param {boolean} show - True to show the loader, false to hide it.
 */
function toggleLoader(show) {
    if (loader) {
        loader.style.display = show ? 'block' : 'none';
    }
}

/**
 * Handles the submission of the dignity calculation form.
 * This is the logic from your first app.js, now structured as a dedicated function.
 * @param {Event} event - The form submission event.
 */
async function handleDignityFormSubmit(event) {
    event.preventDefault(); // Prevent default form submission
    toggleLoader(true);
    if (errorContainer) errorContainer.style.display = 'none';
    if (resultArea) resultArea.textContent = 'Calculating...';

    // Get values from the form inputs
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;
    const latitude = parseFloat(document.getElementById('latitude').value);
    const longitude = parseFloat(document.getElementById('longitude').value);

    // Combine date and time and format it for the backend.
    const requestData = {
        datetime_str: `${date}T${time}:00`,
        timezone_str: "UTC", // Assume UTC for this simple form, or add a timezone input
        latitude,
        longitude,
        house_system: "Placidus" // A default is often needed
    };

    try {
        // Call the centralized API service function
        const result = await api.getDignityReport(requestData);

        if (result.error) {
            displayError(result.error);
        } else {
            displayResult(result);
        }

    } catch (error) {
        // Catches network errors or other exceptions from the api.js module
        displayError(error.message);
    } finally {
        toggleLoader(false);
    }
}

/**
 * Initializes all event listeners for the application.
 * This function is called once by app.js when the page loads.
 */
export function initializeUI() {
    // Attach the event listener to the dignity form if it exists on the page.
    if (dignityForm) {
        dignityForm.addEventListener('submit', handleDignityFormSubmit);
    }

    // You would add other event listeners for other forms here.
    // Example:
    // const natalForm = document.getElementById('natal-chart-form');
    // if (natalForm) {
    //     natalForm.addEventListener('submit', handleNatalFormSubmit);
    // }
    
    console.log("UI Initialized and event listeners are active.");
}