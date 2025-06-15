// UI Controller for managing tabs and general UI interactions
export const uiController = {
    initialize() {
        this.setupTabNavigation();
        this.setupAuthUI();
        this.initializeTooltips();
    },

    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = e.target.getAttribute('data-tab');
                this.showTab(tabId);
            });
        });

        // Show default tab
        const defaultTab = document.querySelector('.tab-button').getAttribute('data-tab');
        this.showTab(defaultTab);
    },

    showTab(tabId) {
        // Hide all tabs
        const tabs = document.querySelectorAll('.tab-content');
        tabs.forEach(tab => tab.style.display = 'none');

        // Deactivate all buttons
        const buttons = document.querySelectorAll('.tab-button');
        buttons.forEach(btn => btn.classList.remove('active'));

        // Show the selected tab
        const selectedTab = document.getElementById(tabId);
        if (selectedTab) {
            selectedTab.style.display = 'block';
            // Activate the corresponding button
            const activeButton = document.querySelector(`[data-tab="${tabId}"]`);
            if (activeButton) {
                activeButton.classList.add('active');
            }
        }

        // Trigger a custom event that other controllers can listen to
        const event = new CustomEvent('tabChanged', { detail: { tabId } });
        document.dispatchEvent(event);
    },

    setupAuthUI() {
        const userInfo = document.getElementById('userInfo');
        const loginForm = document.getElementById('loginForm');
        
        if (localStorage.getItem('authToken')) {
            this.updateUserUI(true);
        } else {
            this.updateUserUI(false);
        }
    },

    updateUserUI(isLoggedIn) {
        const userInfo = document.getElementById('userInfo');
        const loginForm = document.getElementById('loginForm');
        const userEmailDisplay = document.getElementById('userEmailDisplay');
        
        if (isLoggedIn) {
            userInfo.style.display = 'block';
            loginForm.style.display = 'none';
            const email = localStorage.getItem('userEmail');
            if (userEmailDisplay && email) {
                userEmailDisplay.textContent = email;
            }
        } else {
            userInfo.style.display = 'none';
            loginForm.style.display = 'block';
        }
    },

    initializeTooltips() {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        tooltips.forEach(element => {
            element.addEventListener('mouseover', (e) => {
                const tooltip = e.target.getAttribute('data-tooltip');
                this.showTooltip(e.target, tooltip);
            });

            element.addEventListener('mouseout', () => {
                this.hideTooltip();
            });
        });
    },

    showTooltip(element, text) {
        let tooltip = document.getElementById('tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'tooltip';
            document.body.appendChild(tooltip);
        }

        tooltip.textContent = text;
        tooltip.style.display = 'block';

        const rect = element.getBoundingClientRect();
        tooltip.style.top = `${rect.bottom + 5}px`;
        tooltip.style.left = `${rect.left}px`;
    },

    hideTooltip() {
        const tooltip = document.getElementById('tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    },

    showLoading(message = 'Loading...') {
        const loader = document.getElementById('loader') || this.createLoader();
        const loaderMessage = loader.querySelector('.loader-message');
        if (loaderMessage) {
            loaderMessage.textContent = message;
        }
        loader.style.display = 'flex';
    },

    hideLoading() {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.display = 'none';
        }
    },

    createLoader() {
        const loader = document.createElement('div');
        loader.id = 'loader';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="spinner"></div>
                <div class="loader-message">Loading...</div>
            </div>
        `;
        document.body.appendChild(loader);
        return loader;
    },

    showError(message) {
        this.showNotification(message, 'error');
    },

    showSuccess(message) {
        this.showNotification(message, 'success');
    },

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        const container = document.getElementById('notification-container') 
            || this.createNotificationContainer();

        container.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    },

    createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        document.body.appendChild(container);
        return container;
    }
};
