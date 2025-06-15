// public/js/auth/register.js
/**
 * Handles the logic for the user registration form.
 * It calls the authService to perform the registration and updates the UI
 * based on the result from the global state store.
 */

// We now import the dedicated authService and the global store
import { authService } from '../services/authService.js';
import { store } from '../state/store.js';

// --- DOM Element Selectors ---
const registerForm = document.getElementById('register-form');
const errorContainer = document.getElementById('error-container');
const submitButton = registerForm.querySelector('button');
const formContainer = document.querySelector('.auth-container');

/**
 * A function that listens to changes in the global state store
 * and updates the UI accordingly.
 */
function handleStateChange(state) {
  // If there's an error in the state, display it.
  if (state.error) {
    errorContainer.textContent = state.error;
    errorContainer.style.display = 'block';
    // Re-enable the button on error so the user can try again.
    submitButton.disabled = false;
    submitButton.textContent = 'Register';
  } else {
    errorContainer.style.display = 'none';
  }

  // Handle the loading state
  if (state.isLoading) {
    submitButton.disabled = true;
    submitButton.textContent = 'Registering...';
  }
}

/**
 * Handles the registration form submission event.
 * @param {Event} event - The form's submit event.
 */
async function handleRegistrationSubmit(event) {
  // Prevent the browser's default page reload
  event.preventDefault();

  // Get the data from the form fields
  const formData = new FormData(registerForm);
  const fullName = formData.get('full_name');
  const email = formData.get('email');
  const password = formData.get('password');
  
  // --- Frontend Validation ---
  if (password.length < 8) {
    // We can directly update the store with a client-side error
    store.setState({ error: 'Password must be at least 8 characters long.' });
    return;
  }
  
  // Call the authService to handle the registration logic
  const success = await authService.register(fullName, email, password);

  if (success) {
    // On success, show a confirmation message and redirect to login
    formContainer.innerHTML = `
      <h1>Registration Successful!</h1>
      <p class="subtitle" style="color: #2ecc71;">
        Your account has been created. Redirecting you to the login page...
      </p>
    `;
    
    setTimeout(() => {
        window.location.href = '/login.html';
    }, 3000); // Redirect after 3 seconds
  }
  // Note: The error case is handled automatically by the state change listener.
}


// --- Initialization ---

// Subscribe our UI update function to the store.
// Now, any time `store.setState` is called anywhere, `handleStateChange` will run.
store.subscribe(handleStateChange);

// Attach the event listener to the form.
if (registerForm) {
  registerForm.addEventListener('submit', handleRegistrationSubmit);
}