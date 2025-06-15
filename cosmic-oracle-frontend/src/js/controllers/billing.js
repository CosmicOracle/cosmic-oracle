// cosmic-oracle-frontend/public/js/billing.js
// Initialize Stripe with key from server config or environment
let stripe;

// API endpoints configuration
const getBaseUrl = () => {
    // For local development without a proxy
    if (window.location.protocol === 'file:' || 
        window.location.port === '3000' || 
        window.location.port === '5173') {
        return 'http://localhost:5000/api/v1'; // Fixed: Changed from port 80 to 5000
    }
    return '/api/v1';
};

const API_BASE = getBaseUrl();
const endpoints = {
    config: `${API_BASE}/billing/config`,
    checkout: `${API_BASE}/billing/create-checkout-session`,
    portal: `${API_BASE}/billing/create-portal-session`,
    subscriptionStatus: `${API_BASE}/billing/subscription-status`,
    createPaymentIntent: `${API_BASE}/billing/create-payment-intent`, // Added missing endpoint
    subscription: `${API_BASE}/billing/subscription` // Added missing endpoint
};

// Initialize the billing system
async function initializeBilling() {
    try {
        console.log('Initializing billing system...');
        
        const configResponse = await fetch(endpoints.config, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!configResponse.ok) {
            throw new Error(`HTTP error! status: ${configResponse.status}`);
        }

        const config = await configResponse.json();
        
        // Initialize Stripe with the publishable key
        if (config.stripe_publishable_key) { // Fixed: Updated property name to match backend
            stripe = Stripe(config.stripe_publishable_key);
            console.log('Stripe initialized successfully');
        } else {
            console.warn('Stripe publishable key not found in config');
            return;
        }
        
        // Store configuration for later use
        window.STRIPE_CONFIG = {
            plans: config.plans || [],
            monthlyPriceId: config.monthlyPlanId,
            yearlyPriceId: config.yearlyPlanId
        };
        
        // Setup billing UI with plans from config
        setupBillingUI(config.plans || []);
        
        await updateSubscriptionUI();
        
    } catch (error) {
        console.error('Failed to initialize billing:', error);
        // Don't show error in local development
        if (window.location.protocol !== 'file:') {
            showError('Could not initialize payment system. Please try again later.');
        }
    }
}

/**
 * Setup billing UI elements
 */
function setupBillingUI(plans) {
    const billingContainer = document.getElementById('billing-container');
    if (!billingContainer || plans.length === 0) return;
    
    billingContainer.innerHTML = `
        <div class="billing-section">
            <h3>Subscription Plans</h3>
            <div class="plans-container">
                ${plans.map(plan => `
                    <div class="plan-card" data-plan-id="${plan.id}">
                        <h4>${plan.name}</h4>
                        <div class="price">$${plan.price}/${plan.interval}</div>
                        <ul class="features">
                            ${plan.features ? plan.features.map(feature => `<li>${feature}</li>`).join('') : ''}
                        </ul>
                        <button class="subscribe-btn" onclick="selectPlan('${plan.id}')">
                            Select Plan
                        </button>
                    </div>
                `).join('')}
            </div>
            <div id="payment-form" style="display: none;">
                <div id="payment-element"></div>
                <button id="submit-payment" disabled>Subscribe</button>
                <button id="cancel-payment" onclick="cancelPayment()">Cancel</button>
            </div>
            <div id="billing-loading" style="display: none;">Loading...</div>
            <div id="billing-error" style="display: none;"></div>
        </div>
    `;
}

/**
 * Select a subscription plan
 */
async function selectPlan(planId) {
    try {
        if (!stripe) {
            throw new Error('Stripe not initialized');
        }
        
        const accessToken = localStorage.getItem('accessToken') || localStorage.getItem('token');
        if (!accessToken) {
            showError('Please log in to subscribe.');
            return;
        }
        
        showLoading('Setting up payment...');
        
        // Create payment intent
        const response = await fetch(endpoints.createPaymentIntent, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ plan_id: planId })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const { client_secret } = await response.json();
        
        hideLoading();
        
        // Setup payment form
        await setupPaymentForm(client_secret);
        
    } catch (error) {
        hideLoading();
        console.error('Error selecting plan:', error);
        showError(error.message || 'Failed to setup payment. Please try again.');
    }
}

/**
 * Setup Stripe payment form
 */
async function setupPaymentForm(clientSecret) {
    try {
        const paymentForm = document.getElementById('payment-form');
        if (!paymentForm) {
            throw new Error('Payment form element not found');
        }
        
        paymentForm.style.display = 'block';
        
        const elements = stripe.elements({ clientSecret });
        const paymentElement = elements.create('payment');
        
        // Clear previous payment element
        const paymentElementContainer = document.getElementById('payment-element');
        paymentElementContainer.innerHTML = '';
        
        paymentElement.mount('#payment-element');
        
        const submitButton = document.getElementById('submit-payment');
        submitButton.disabled = false;
        
        // Remove previous event listeners
        const newSubmitButton = submitButton.cloneNode(true);
        submitButton.parentNode.replaceChild(newSubmitButton, submitButton);
        
        newSubmitButton.onclick = async () => {
            newSubmitButton.disabled = true;
            showLoading('Processing payment...');
            
            try {
                const { error } = await stripe.confirmPayment({
                    elements,
                    confirmParams: {
                        return_url: `${window.location.origin}/billing-success.html`
                    }
                });
                
                if (error) {
                    throw error;
                }
            } catch (paymentError) {
                hideLoading();
                console.error('Payment failed:', paymentError);
                showError(paymentError.message || 'Payment failed. Please try again.');
                newSubmitButton.disabled = false;
            }
        };
        
    } catch (error) {
        console.error('Error setting up payment form:', error);
        showError('Failed to setup payment form. Please try again.');
    }
}

/**
 * Cancel payment process
 */
function cancelPayment() {
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.style.display = 'none';
    }
    hideLoading();
}

/**
 * Updates the UI based on the user's current subscription status
 */
async function updateSubscriptionUI() {
    try {
        const accessToken = localStorage.getItem('accessToken') || localStorage.getItem('token');
        if (!accessToken) {
            console.log('No access token found, skipping subscription UI update');
            return;
        }

        const response = await fetch(endpoints.subscription, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                console.log('Unauthorized access, user may need to log in');
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const subscription = await response.json();
        
        // Update UI elements based on subscription status
        const subscribeButtons = document.querySelectorAll('.subscribe-btn');
        const manageButton = document.getElementById('manage-subscription-button');
        const statusDisplay = document.getElementById('subscription-status');
        
        if (subscription.subscription && subscription.status !== 'no_subscription') {
            // User has active subscription
            subscribeButtons.forEach(btn => {
                btn.textContent = 'Current Plan';
                btn.disabled = true;
            });
            
            if (manageButton) {
                manageButton.style.display = 'block';
            }
            
            if (statusDisplay) {
                statusDisplay.textContent = `Subscription: Active (${subscription.status})`;
                statusDisplay.className = 'subscription-active';
            }
        } else {
            // No active subscription
            subscribeButtons.forEach(btn => {
                btn.textContent = 'Select Plan';
                btn.disabled = false;
            });
            
            if (manageButton) {
                manageButton.style.display = 'none';
            }
            
            if (statusDisplay) {
                statusDisplay.textContent = 'No active subscription';
                statusDisplay.className = 'subscription-inactive';
            }
        }
        
    } catch (error) {
        console.error('Failed to update subscription UI:', error);
        // Don't show error to user for subscription status checks
    }
}

/**
 * Initiates the Stripe Checkout process for a given price ID.
 * @param {string} priceId - The ID of the Stripe Price object for the subscription plan.
 */
async function subscribeUser(priceId) {
    if (!stripe) {
        console.error('Stripe not initialized');
        showError('Payment system not ready. Please try again later.');
        return;
    }

    const accessToken = localStorage.getItem('accessToken') || localStorage.getItem('token');
    if (!accessToken) {
        showError('Please log in to subscribe.');
        return;
    }

    try {
        showLoading('Setting up payment...');
        
        const response = await fetch(endpoints.checkout, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ priceId })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const session = await response.json();
        hideLoading();

        const { error } = await stripe.redirectToCheckout({
            sessionId: session.sessionId
        });
        
        if (error) {
            throw error;
        }
        
    } catch (error) {
        hideLoading();
        console.error('Subscription request failed:', error);
        showError(error.message || 'Could not process subscription. Please try again.');
    }
}

/**
 * Redirects the user to the Stripe Customer Portal to manage their subscription.
 */
async function redirectToCustomerPortal() {
    const accessToken = localStorage.getItem('accessToken') || localStorage.getItem('token');
    if (!accessToken) {
        showError('Please log in to manage your subscription.');
        return;
    }

    try {
        showLoading('Opening customer portal...');
        
        const response = await fetch(endpoints.portal, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        hideLoading();

        if (data.url) {
            window.location.href = data.url;
        } else {
            throw new Error('Invalid portal URL received');
        }
        
    } catch (error) {
        hideLoading();
        console.error('Customer portal request failed:', error);
        showError(error.message || 'Could not open subscription management. Please try again.');
    }
}

// UI Helper functions
function showError(message) {
    console.error('Billing Error:', message);
    
    const errorElement = document.getElementById('billing-error');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        errorElement.style.cssText = `
            background: #fee;
            color: #c33;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            border: 1px solid #fcc;
            display: block;
        `;
        
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    } else {
        // Fallback to alert if no error element exists
        alert(message);
    }
}

function showLoading(message = 'Loading...') {
    const loadingElement = document.getElementById('billing-loading');
    if (loadingElement) {
        loadingElement.textContent = message;
        loadingElement.style.display = 'block';
        loadingElement.style.cssText = `
            background: #e3f2fd;
            color: #1976d2;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            border: 1px solid #bbdefb;
            display: block;
        `;
    }
}

function hideLoading() {
    const loadingElement = document.getElementById('billing-loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

/**
 * Get current user subscription
 */
async function getCurrentSubscription() {
    try {
        const accessToken = localStorage.getItem('accessToken') || localStorage.getItem('token');
        if (!accessToken) {
            return null;
        }

        const response = await fetch(endpoints.subscriptionStatus, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                console.log('Unauthorized access, user may need to log in');
                return null;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const subscription = await response.json();
        return subscription.subscription;

    } catch (error) {
        console.error('Failed to get current subscription:', error);
        return null;
    }
}
