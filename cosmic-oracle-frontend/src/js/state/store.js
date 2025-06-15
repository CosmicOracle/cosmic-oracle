// src/js/state/store.js
/**
 * A persistent state management store.
 * It automatically hydrates its initial state from sessionStorage and
 * persists any changes back to storage. It also handles user auth state.
 */

const AUTH_KEY = 'cosmic_oracle_auth'; // Key for localStorage (long-term persistence)
const APP_STATE_KEY = 'cosmic_oracle_app_state'; // Key for sessionStorage (session-only persistence)

class Store {
  constructor(initialState = {}) {
    this.listeners = new Set();
    // Load the initial state by merging defaults with persisted data
    this.state = this._hydrateState(initialState);

    // Persist state changes to sessionStorage automatically
    this.subscribe(() => {
      // Don't save auth or error state to session storage
      const { auth, error, isLoading, ...persistableState } = this.state;
      sessionStorage.setItem(APP_STATE_KEY, JSON.stringify(persistableState));
    });
  }

  _hydrateState(initialState) {
    const persistedAuthState = JSON.parse(localStorage.getItem(AUTH_KEY));
    const persistedSessionState = JSON.parse(sessionStorage.getItem(APP_STATE_KEY));

    // The initial state is the default, overridden by session data,
    // and finally overridden by auth data.
    return {
      ...initialState,
      ...persistedSessionState,
      auth: persistedAuthState || initialState.auth,
    };
  }

  getState() {
    return this.state;
  }

  setState(newState) {
    this.state = { ...this.state, ...newState };
    // Special handling for auth state to persist it to localStorage
    if (newState.auth !== undefined) {
      if (newState.auth) {
        localStorage.setItem(AUTH_KEY, JSON.stringify(newState.auth));
      } else {
        // If auth is set to null (logout), remove it from storage
        localStorage.removeItem(AUTH_KEY);
      }
    }
    this.notify();
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify() {
    this.listeners.forEach((listener) => listener(this.state));
  }
}

// Create the single, global store with its default structure
export const store = new Store({
  isLoading: false,
  error: null,
  // Auth state will be hydrated from localStorage
  auth: {
    token: null,
    user: null,
    isAuthenticated: false,
  },
  // App state will be hydrated from sessionStorage
  currentChart: null,
  currentReport: null,
});