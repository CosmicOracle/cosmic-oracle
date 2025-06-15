// src/js/ui/UIManager.js
/**
 * UIManager - Centralized UI management for the Cosmic Oracle application
 */

import { store } from '../state/store.js';
import { showSuccess, showError, showInfo } from '../utils/notifications.js';

export class UIManager {
    constructor() {
        this.currentPage = null;
        this.modals = new Map();
        this.initialized = false;
    }

    /**
     * Initialize the UI Manager
     */
    init() {
        if (this.initialized) return;
        
        this.setupGlobalEventListeners();
        this.detectCurrentPage();
        this.setupModalHandlers();
        this.initialized = true;
        
        console.log('UIManager initialized');
    }

    /**
     * Setup global event listeners
     */
    setupGlobalEventListeners() {
        // Handle escape key for closing modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeTopModal();
            }
        });

        // Handle clicks outside modals
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.closeModal(e.target.querySelector('.modal'));
            }
        });

        // Handle navigation
        window.addEventListener('popstate', () => {
            this.detectCurrentPage();
        });
    }

    /**
     * Detect current page and load appropriate components
     */
    detectCurrentPage() {
        const path = window.location.pathname;
        const page = this.getPageFromPath(path);
        
        if (page !== this.currentPage) {
            this.currentPage = page;
            this.loadPageComponents(page);
        }
    }

    /**
     * Get page identifier from path
     */
    getPageFromPath(path) {
        if (path.includes('login')) return 'login';
        if (path.includes('register')) return 'register';
        if (path.includes('dashboard')) return 'dashboard';
        if (path.includes('birth-chart')) return 'birth-chart';
        if (path.includes('horoscope')) return 'horoscope';
        if (path.includes('tarot')) return 'tarot';
        if (path.includes('numerology')) return 'numerology';
        if (path.includes('astral-calendar')) return 'astral-calendar';
        if (path.includes('profile')) return 'profile';
        return 'home';
    }

    /**
     * Load components for specific page
     */
    async loadPageComponents(page) {
        try {
            switch (page) {
                case 'dashboard':
                    await this.loadDashboard();
                    break;
                case 'birth-chart':
                    await this.loadBirthChart();
                    break;
                case 'horoscope':
                    await this.loadHoroscope();
                    break;
                case 'tarot':
                    await this.loadTarot();
                    break;
                case 'numerology':
                    await this.loadNumerology();
                    break;
                case 'astral-calendar':
                    await this.loadAstralCalendar();
                    break;
                default:
                    console.log(`No specific loader for page: ${page}`);
            }
        } catch (error) {
            console.error(`Error loading page ${page}:`, error);
            showError(`Failed to load page content`);
        }
    }

    /**
     * Load dashboard components
     */
    async loadDashboard() {
        // Dashboard components would be loaded here
        console.log('Loading dashboard components');
    }

    /**
     * Load birth chart components
     */
    async loadBirthChart() {
        console.log('Loading birth chart components');
    }

    /**
     * Load horoscope components
     */
    async loadHoroscope() {
        console.log('Loading horoscope components');
    }

    /**
     * Load tarot components
     */
    async loadTarot() {
        console.log('Loading tarot components');
    }

    /**
     * Load numerology components
     */
    async loadNumerology() {
        console.log('Loading numerology components');
    }

    /**
     * Load astral calendar components
     */
    async loadAstralCalendar() {
        console.log('Loading astral calendar components');
    }

    /**
     * Setup modal handlers
     */
    setupModalHandlers() {
        // Find all modal triggers
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('[data-modal]');
            if (trigger) {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                this.openModal(modalId);
            }

            // Handle modal close buttons
            const closeBtn = e.target.closest('[data-modal-close]');
            if (closeBtn) {
                e.preventDefault();
                const modal = closeBtn.closest('.modal');
                this.closeModal(modal);
            }
        });
    }

    /**
     * Open a modal
     */
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.error(`Modal with ID ${modalId} not found`);
            return;
        }

        modal.classList.add('modal-open');
        modal.setAttribute('aria-hidden', 'false');
        
        // Add to modal stack
        this.modals.set(modalId, modal);
        
        // Focus management
        const firstFocusable = modal.querySelector('input, button, textarea, select, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            firstFocusable.focus();
        }

        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close a modal
     */
    closeModal(modal) {
        if (!modal) return;

        const modalId = modal.id;
        modal.classList.remove('modal-open');
        modal.setAttribute('aria-hidden', 'true');
        
        // Remove from modal stack
        this.modals.delete(modalId);
        
        // Restore body scroll if no modals open
        if (this.modals.size === 0) {
            document.body.style.overflow = '';
        }
    }

    /**
     * Close the topmost modal
     */
    closeTopModal() {
        if (this.modals.size === 0) return;
        
        const lastModal = Array.from(this.modals.values()).pop();
        this.closeModal(lastModal);
    }

    /**
     * Show loading state
     */
    showLoading(element = document.body) {
        const loader = document.createElement('div');
        loader.className = 'ui-loader';
        loader.innerHTML = `
            <div class="loader-spinner"></div>
            <div class="loader-text">Loading...</div>
        `;
        
        element.appendChild(loader);
        element.classList.add('ui-loading');
    }

    /**
     * Hide loading state
     */
    hideLoading(element = document.body) {
        const loader = element.querySelector('.ui-loader');
        if (loader) {
            loader.remove();
        }
        element.classList.remove('ui-loading');
    }

    /**
     * Update navigation active state
     */
    updateNavigation() {
        const navLinks = document.querySelectorAll('nav a, .nav-link');
        const currentPath = window.location.pathname;

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href)) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    /**
     * Handle form submissions with loading states
     */
    handleFormSubmit(form, submitHandler) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = form.querySelector('[type="submit"]');
            const originalText = submitBtn.textContent;
            
            try {
                // Show loading state
                submitBtn.disabled = true;
                submitBtn.textContent = 'Loading...';
                
                // Call the submit handler
                await submitHandler(new FormData(form));
                
                showSuccess('Form submitted successfully!');
                
            } catch (error) {
                console.error('Form submission error:', error);
                showError(error.message || 'An error occurred');
            } finally {
                // Restore button state
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    /**
     * Utility method to create and show notifications
     */
    notify(message, type = 'info') {
        switch (type) {
            case 'success':
                showSuccess(message);
                break;
            case 'error':
                showError(message);
                break;
            case 'info':
                showInfo(message);
                break;
            default:
                showInfo(message);
        }
    }

    /**
     * Update page title
     */
    setPageTitle(title) {
        document.title = `${title} - Cosmic Oracle`;
    }

    /**
     * Get current user from store
     */
    getCurrentUser() {
        return store.getState().user;
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        const user = this.getCurrentUser();
        return user && user.token;
    }

    /**
     * Redirect to login if not authenticated
     */
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    }
}

// Create global instance
export const uiManager = new UIManager();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => uiManager.init());
} else {
    uiManager.init();
}
