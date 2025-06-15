// D:\my_projects\cosmic-oracle\cosmic-oracle-frontend\public\js\personalSkyController.js

// Since we're using ES modules now, we'll properly import our dependencies
const apiService = window.apiService;
const { showLoading, hideLoading, displayError } = window.uiHelpers;

const personalSkyController = {
    container: null,
    startDateInput: null,
    endDateInput: null,
    resultsContainer: null,
    detailsContainer: null,

    async initialize(containerId = 'personal-sky-content') {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.warn('Personal Sky container not found.');
            return;
        }
        this.renderBaseUI();
        this.addEventListeners();

        // Set default dates (e.g., today for start, 30 days out for end)
        const today = new Date();
        const futureDate = new Date();
        futureDate.setDate(today.getDate() + 30);
        this.startDateInput.value = today.toISOString().split('T')[0];
        this.endDateInput.value = futureDate.toISOString().split('T')[0];

        // Optionally, load initial forecast if user is logged in
        if (localStorage.getItem('token')) {
             this.fetchAndDisplayForecast();
        } else {
            this.resultsContainer.innerHTML = '<p>Please log in to view your Personal Sky forecast.</p>';
        }
    },

    renderBaseUI() {
        this.container.innerHTML = `
            <h3>Your Personal Sky Forecast</h3>
            <div class="personal-sky-controls">
                <label for="personal-sky-start-date">Start Date:</label>
                <input type="date" id="personal-sky-start-date" name="personal-sky-start-date">
                <label for="personal-sky-end-date">End Date:</label>
                <input type="date" id="personal-sky-end-date" name="personal-sky-end-date">
                <button id="fetch-personal-sky-btn" class="btn">Get Forecast</button>
            </div>
            <div id="personal-sky-results" class="personal-sky-results-grid">
                </div>
            <div id="personal-sky-event-details" class="personal-sky-event-details" style="display:none;">
                </div>
        `;
        this.startDateInput = document.getElementById('personal-sky-start-date');
        this.endDateInput = document.getElementById('personal-sky-end-date');
        this.resultsContainer = document.getElementById('personal-sky-results');
        this.detailsContainer = document.getElementById('personal-sky-event-details');
    },

    addEventListeners() {
        document.getElementById('fetch-personal-sky-btn')?.addEventListener('click', () => this.fetchAndDisplayForecast());
    },

    async fetchAndDisplayForecast() {
        if (!this.startDateInput.value || !this.endDateInput.value) {
            displayError('Please select both start and end dates.', this.resultsContainer);
            return;
        }
        const startDate = this.startDateInput.value;
        const endDate = this.endDateInput.value;

        showLoading(this.resultsContainer);
        this.detailsContainer.style.display = 'none'; // Hide details when fetching new forecast

        try {
            const forecastData = await apiService.getPersonalSky(startDate, endDate);
            if (forecastData && forecastData.forecast && forecastData.forecast.length > 0) {
                this.renderForecast(forecastData.forecast);
            } else {
                this.resultsContainer.innerHTML = '<p>No significant transits found for the selected period, or data is not yet available.</p>';
            }
        } catch (error) {
            console.error("Error fetching personal sky:", error);
            displayError(error.message || 'Failed to fetch personal sky forecast.', this.resultsContainer);
        } finally {
            hideLoading(this.resultsContainer);
        }
    },

    renderForecast(forecastItems) {
        this.resultsContainer.innerHTML = ''; // Clear previous results
        forecastItems.forEach(item => {
            const itemElem = document.createElement('div');
            itemElem.className = 'personal-sky-item';
            // Basic display - enhance this with icons, colors, etc.
            itemElem.innerHTML = `
                <h4>${item.title}</h4>
                <p class="dates">
                    ${new Date(item.start_time_utc).toLocaleDateString()} 
                    ${item.peak_time_utc ? `(Peak: ${new Date(item.peak_time_utc).toLocaleDateString()})` : ''}
                    - <span class="math-inline">\{new Date\(item\.end\_time\_utc\)\.toLocaleDateString\(\)\}
</p>
<p class="item-theme-summary">{item.theme ? item.theme.substring(0, 100) + '...' : 'View details for more.'}</p>
`;
itemElem.addEventListener('click', () => this.displayEventDetails(item));
this.resultsContainer.appendChild(itemElem);
});
},

    displayEventDetails(item) {
        this.detailsContainer.innerHTML = `
            <button id="close-sky-details-btn" class="close-btn" style="float:right;">&times;</button>
            <h3>${item.title}</h3>
            <p><strong>Duration:</strong> ${new Date(item.start_time_utc).toLocaleString()} - ${new Date(item.end_time_utc).toLocaleString()}</p>
            ${item.peak_time_utc ? `<p><strong>Peak Influence:</strong> ${new Date(item.peak_time_utc).toLocaleString()}</p>` : ''}
            <p><strong>Theme:</strong> ${item.theme || 'N/A'}</p>
            <p><strong>Opportunity:</strong> ${item.opportunity || 'N/A'}</p>
            <p><strong>Challenge:</strong> ${item.challenge || 'N/A'}</p>
            <h4>Reflection Questions:</h4>
            <ul>
                ${(item.questions_for_reflection || []).map(q => `<li>${q}</li>`).join('')}
            </ul>
            ${item.actionable_advice_keywords && item.actionable_advice_keywords.length > 0 ? 
                `<p><strong>Consider focusing on:</strong> ${item.actionable_advice_keywords.join(', ')}</p>
                 <p><small>(You can find relevant meditations or rituals in other sections of the Oracle)</small></p>` : ''}
        `;
        this.detailsContainer.style.display = 'block';
        document.getElementById('close-sky-details-btn').addEventListener('click', () => {
            this.detailsContainer.style.display = 'none';
        });
        this.detailsContainer.scrollIntoView({ behavior: 'smooth' });
    }
};

// Export if using modules, or attach to a global object
// export { personalSkyController }; 
// If not using modules, and script.js handles initialization:
window.personalSkyController = personalSkyController;
