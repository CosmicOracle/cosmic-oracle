// utils/notifications.js
/**
 * Utility functions for showing user notifications (success, error, info)
 */

/**
 * Show a success message to the user
 * @param {string} message - The success message to display
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
export function showSuccess(message, duration = 3000) {
    showNotification(message, 'success', duration);
}

/**
 * Show an error message to the user
 * @param {string} message - The error message to display
 * @param {number} duration - Duration in milliseconds (default: 5000)
 */
export function showError(message, duration = 5000) {
    showNotification(message, 'error', duration);
}

/**
 * Show an info message to the user
 * @param {string} message - The info message to display
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
export function showInfo(message, duration = 3000) {
    showNotification(message, 'info', duration);
}

/**
 * Show a warning message to the user
 * @param {string} message - The warning message to display
 * @param {number} duration - Duration in milliseconds (default: 4000)
 */
export function showWarning(message, duration = 4000) {
    showNotification(message, 'warning', duration);
}

/**
 * Core notification function
 * @param {string} message - The message to display
 * @param {string} type - The notification type (success, error, info, warning)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type, duration) {
    // Create notification container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        document.body.appendChild(container);
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    // Create icon based on type
    const icon = getNotificationIcon(type);
    
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${icon}</span>
            <span class="notification-message">${escapeHtml(message)}</span>
            <button class="notification-close" aria-label="Close notification">&times;</button>
        </div>
    `;

    // Add close functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        removeNotification(notification);
    });

    // Add to container
    container.appendChild(notification);

    // Trigger animation
    setTimeout(() => {
        notification.classList.add('notification-show');
    }, 10);

    // Auto-remove after duration
    setTimeout(() => {
        removeNotification(notification);
    }, duration);
}

/**
 * Remove a notification with fade-out animation
 * @param {HTMLElement} notification - The notification element to remove
 */
function removeNotification(notification) {
    if (notification && notification.parentNode) {
        notification.classList.add('notification-hide');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300); // Match CSS transition duration
    }
}

/**
 * Get appropriate icon for notification type
 * @param {string} type - The notification type
 * @returns {string} HTML icon string
 */
function getNotificationIcon(type) {
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    return icons[type] || icons.info;
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Clear all notifications
 */
export function clearAllNotifications() {
    const container = document.getElementById('notification-container');
    if (container) {
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }
    }
}

// Add CSS styles if they don't exist
function addNotificationStyles() {
    if (document.getElementById('notification-styles')) {
        return; // Styles already added
    }

    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        .notification-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            pointer-events: none;
        }

        .notification {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            margin-bottom: 10px;
            min-width: 300px;
            max-width: 500px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            pointer-events: auto;
            border-left: 4px solid;
        }

        .notification-success {
            border-left-color: #10b981;
        }

        .notification-error {
            border-left-color: #ef4444;
        }

        .notification-warning {
            border-left-color: #f59e0b;
        }

        .notification-info {
            border-left-color: #3b82f6;
        }

        .notification-show {
            opacity: 1;
            transform: translateX(0);
        }

        .notification-hide {
            opacity: 0;
            transform: translateX(100%);
        }

        .notification-content {
            display: flex;
            align-items: center;
            padding: 16px;
            gap: 12px;
        }

        .notification-icon {
            font-size: 18px;
            font-weight: bold;
        }

        .notification-success .notification-icon {
            color: #10b981;
        }

        .notification-error .notification-icon {
            color: #ef4444;
        }

        .notification-warning .notification-icon {
            color: #f59e0b;
        }

        .notification-info .notification-icon {
            color: #3b82f6;
        }

        .notification-message {
            flex: 1;
            font-size: 14px;
            line-height: 1.4;
            color: #374151;
        }

        .notification-close {
            background: none;
            border: none;
            font-size: 18px;
            color: #9ca3af;
            cursor: pointer;
            padding: 0;
            margin: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background-color 0.2s ease;
        }

        .notification-close:hover {
            background-color: #f3f4f6;
            color: #374151;
        }
    `;
    document.head.appendChild(style);
}

// Initialize styles when module loads
addNotificationStyles();
