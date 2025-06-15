// dist/js/errorHandler.js

/**
 * Attaches event listeners to UI elements in a safe way,
 * preventing "ReferenceError" issues from onclick attributes in HTML.
 */
function setupSafeEventListeners() {
    // Find the button that is supposed to show the login form.
    // NOTE: You might need to change '#login-button' to the actual ID or class of your login button.
    const loginButton = document.querySelector('#login-button'); // ASSUMING your button has id="login-button"
    const registerButton = document.querySelector('#register-button'); // ASSUMING your button has id="register-button"

    if (loginButton) {
        // We assume you have a function called `showLoginForm` in another file (e.g., authController.js)
        // Make sure that function is available.
        loginButton.addEventListener('click', () => {
            // Check if the function exists before calling it
            if (typeof showLoginForm === 'function') {
                showLoginForm();
            } else {
                console.error('The function "showLoginForm" was not found. Make sure it is defined and loaded.');
                alert('Login functionality is currently unavailable.');
            }
        });
    }

    if (registerButton) {
        registerButton.addEventListener('click', () => {
            if (typeof showRegisterForm === 'function') {
                showRegisterForm();
            } else {
                console.error('The function "showRegisterForm" was not found.');
            }
        });
    }

    console.log('Safe event listeners have been set up.');
}


/**
 * Global error handler to catch uncaught exceptions.
 * This will give you a clear report in the console for any errors that are missed.
 */
window.onerror = function(message, source, lineno, colno, error) {
    console.error('--- Global Uncaught Error ---');
    console.error('Message:', message);
    console.error('Source:', source);
    console.error('Line:', lineno, 'Column:', colno);
    console.error('Error Object:', error);
    console.error('-----------------------------');
    return true; // Prevents the default browser error handling
};

// Run the setup function once the document is fully loaded
document.addEventListener('DOMContentLoaded', setupSafeEventListeners);