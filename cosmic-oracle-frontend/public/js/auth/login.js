import { authService } from '../services/authService.js';

const loginForm = document.getElementById('login-form');
const errorContainer = document.getElementById('error-container');
const submitButton = loginForm.querySelector('button');

loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorContainer.style.display = 'none';
    submitButton.disabled = true;
    submitButton.textContent = 'Logging In...';

    const formData = new FormData(loginForm);
    const email = formData.get('email');
    const password = formData.get('password');

    const success = await authService.login(email, password);
    
    if (success) {
        window.location.href = '/index.html'; // Redirect to main app page on success
    } else {
        errorContainer.textContent = 'Login failed. Please check your credentials.';
        errorContainer.style.display = 'block';
        submitButton.disabled = false;
        submitButton.textContent = 'Log In';
    }
});