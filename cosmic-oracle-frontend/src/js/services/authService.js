// src/js/services/authService.js
/**
 * Handles all user authentication logic, including login, logout,
 * and managing the user's authentication state.
 */
import { api } from '../api/index.js';
import { store } from '../state/store.js';

export const authService = {
  /**
   * Attempts to log in a user with the provided credentials.
   * @param {string} email - The user's email.
   * @param {string} password - The user's password.
   */
  async login(email, password) {
    store.setState({ isLoading: true, error: null });
    try {
      const response = await api.login({ email, password });
      if (response.access_token) {
        // Successful login: get user profile
        const userProfile = await this.getProfile(response.access_token);
        
        // Update the global state with auth info
        store.setState({
          isLoading: false,
          auth: {
            token: response.access_token,
            user: userProfile,
            isAuthenticated: true,
          },
        });
        return true; // Indicate success
      }
    } catch (error) {
      store.setState({ isLoading: false, error: error.message });
      return false; // Indicate failure
    }
  },

  /**
   * Fetches the profile of the currently authenticated user.
   * @param {string} token - The JWT access token.
   */
  async getProfile(token) {
    try {
      // The API client will be configured to use this token for auth
      const profile = await api.getUserProfile(token);
      return profile;
    } catch (error) {
      // If the token is invalid, log the user out
      console.error("Failed to get profile, token might be expired.", error);
      this.logout();
      return null;
    }
  },

  /**
   * Logs the user out by clearing the authentication state.
   */
  logout() {
    // Setting auth state to null will trigger the store to remove it from localStorage
    store.setState({
      auth: null,
      // Also clear any session-specific data
      currentChart: null,
      currentReport: null,
    });
    console.log('User has been logged out.');
    // In a real app, you would redirect to the login page here.
    // window.location.href = '/login.html';
  },

  /**
   * Checks if the user is currently authenticated based on the store's state.
   */
  isAuthenticated() {
    const authState = store.getState().auth;
    return authState && authState.isAuthenticated && authState.token;
  },
};