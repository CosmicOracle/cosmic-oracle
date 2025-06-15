// Filename: js/apiService.js

const API_BASE_URL = 'http://localhost:5000/api/v1'; // Development backend URL

export const apiService = {
    // --- Utility to handle common response logic ---
    async _handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({
                message: `HTTP error! Status: ${response.status} - ${response.statusText}`,
                error: `HTTP error! Status: ${response.status} - ${response.statusText}` // for compatibility
            }));
            // Use 'message' if available from backend error structure, otherwise 'msg' or 'error'
            const message = errorData.message || errorData.msg || errorData.error || 'An unknown error occurred.';
            throw { status: response.status, message: message, data: errorData };
        }
        // Handle cases where response might be empty (e.g., for DELETE 204 No Content)
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            // Check if content length is 0 before trying to parse JSON for 204 No Content
            if (response.status === 204 || response.headers.get("content-length") === "0") {
                return null; // Or an empty object/array depending on expected output for 204
            }
            return response.json();
        }
        return response.text(); // Or handle as per expected response type
    },

    // Authenticated request helper
    async fetchWithAuth(endpoint, options = {}, returnRawResponse = false) {
        const token = localStorage.getItem('authToken');
        const defaultHeaders = {};
        if (token) {
            defaultHeaders['Authorization'] = `Bearer ${token}`;
        }

        const fetchOptions = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        };

        // Automatically set Content-Type if body is a plain object and not FormData
        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData) && !(options.body instanceof URLSearchParams) && !(options.body instanceof Blob) && !(options.body instanceof ArrayBuffer)) {
             if (!fetchOptions.headers['Content-Type']) { // Don't override if already set
                fetchOptions.headers['Content-Type'] = 'application/json';
             }
        }


        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, fetchOptions);

            if (returnRawResponse) {
                return response; // Return the raw response object for manual handling (e.g., downloads)
            }
            return await this._handleResponse(response);
        } catch (error) {
            console.error('API Request failed:', error);
            throw error; // Re-throw to be caught by calling function
        }
    },
    
    // --- DEPRECATED/REPLACED: fetchDataFile is no longer used for dynamic JSON content ---
    // async fetchDataFile(filename) {
    //     const response = await fetch(`${API_BASE_URL}/data/${filename}`); // Assuming /data routes are public
    //     return this._handleResponse(response);
    // },

    // --- Login and Registration API Calls ---
    async login(email, password) { // Renamed from loginUser for consistency
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await this._handleResponse(response);
        // Assuming login success includes a token (e.g., data.token or data.access_token)
        if (data.token) { // Standardized to 'token'
            localStorage.setItem('authToken', data.token);
            localStorage.setItem('userEmail', email); // Storing email might be useful for UI
        } else if (data.access_token) { // Fallback for access_token
             localStorage.setItem('authToken', data.access_token);
             localStorage.setItem('userEmail', email);
        }
        return data;
    },

    async registerUser(email, password) {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        return this._handleResponse(response);
    },

    async getUserProfile() {
        // fetchWithAuth should handle the token and base URL prefixing implicitly
        return this.fetchWithAuth(`/auth/me`); // Corrected path assuming /auth/me
    },
    
    async logout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userEmail');
        // Optionally, call a backend logout endpoint if it exists
        // await this.fetchWithAuth('/auth/logout', { method: 'POST' });
        window.location.href = '/login.html'; // Or your app's login page
    },

    isAuthenticated() {
        return !!localStorage.getItem('authToken');
    },

    // --- Content Fetching API Calls (from various UI controllers) ---
    // Standardized to use the /content/ prefix and match backend routes
    async fetchAllZodiacSigns() {
        const response = await fetch(`${API_BASE_URL}/content/zodiac_signs`);
        return this._handleResponse(response);
    },

    async fetchZodiacSignDetail(signKey) {
        const response = await fetch(`${API_BASE_URL}/content/zodiac_signs/${signKey}`);
        return this._handleResponse(response);
    },

    async fetchTarotDeck() {
        const response = await fetch(`${API_BASE_URL}/content/tarot_deck`);
        return this._handleResponse(response);
    },

    async fetchCrystalData() {
        try {
            const response = await fetch(`${API_BASE_URL}/content/crystals`);
            return await this._handleResponse(response);
        } catch (error) {
            console.warn('Backend API for crystals unavailable, loading local crystal data:', error.message);
            // Fallback path if backend fails, assuming public/data folder access
            const localResponse = await fetch('/data/crystal_data.json'); 
            if (!localResponse.ok) throw new Error('Failed to load crystal data from local fallback');
            return localResponse.json();
        }
    },

    async fetchChakraData() {
        try {
            // If chakra data might be user-specific or requires auth, use fetchWithAuth
            // If public, standard fetch is fine.
            const response = await fetch(`${API_BASE_URL}/content/chakras`); // Changed to public fetch, assuming /content/chakras is public
            return await this._handleResponse(response); 
        } catch (error) {
            console.warn('Backend API for chakras unavailable, loading local chakra data:', error.message);
            // Fallback path if backend fails, assuming public/data folder access
            const localResponse = await fetch('/data/chakra_data.json');
            if (!localResponse.ok) throw new Error('Failed to load chakra data from local fallback');
            return localResponse.json();
        }
    },

    async fetchDreamSymbols() {
        const response = await fetch(`${API_BASE_URL}/content/dream_symbols`);
        return this._handleResponse(response);
    },

    async fetchRandomAffirmation() {
        const response = await fetch(`${API_BASE_URL}/content/affirmation/random`);
        return this._handleResponse(response);
    },

    async fetchCompatibilityMatrix() {
        const response = await fetch(`${API_BASE_URL}/content/compatibility_matrix`);
        return this._handleResponse(response);
    },

    // NEW/UPDATED CONTENT FETCHERS TO MATCH BACKEND content.py ROUTES
    async fetchPlanetaryData() {
        const response = await fetch(`${API_BASE_URL}/content/planetary_data`);
        return this._handleResponse(response);
    },

    async fetchNumerologyMeanings() {
        // Use the v2 route as per backend
        const response = await fetch(`${API_BASE_URL}/content/numerology/meanings`);
        return this._handleResponse(response);
    },

    async fetchRitualsData() {
        const response = await fetch(`${API_BASE_URL}/content/rituals`);
        return this._handleResponse(response);
    },

    async fetchDignityInterpretations() {
        const response = await fetch(`${API_BASE_URL}/content/dignity/interpretations`);
        return this._handleResponse(response);
    },

    async fetchFixedStarsData() {
        const response = await fetch(`${API_BASE_URL}/content/fixed_stars`);
        return this._handleResponse(response);
    },

    async fetchHouseSystemsData() {
        const response = await fetch(`${API_BASE_URL}/content/house_systems`);
        return this._handleResponse(response);
    },

    async fetchAspectData() {
        const response = await fetch(`${API_BASE_URL}/content/aspects`);
        return this._handleResponse(response);
    },

    async fetchPartOfFortuneInterpretations() {
        const response = await fetch(`${API_BASE_URL}/content/part_of_fortune_interpretations`);
        return this._handleResponse(response);
    },

    async fetchHoroscopeInterpretations() {
        const response = await fetch(`${API_BASE_URL}/content/horoscope_interpretations`);
        return this._handleResponse(response);
    },

    async fetchLunarMansionsData() {
        // Use the explicit /lunar_mansions_data route as per backend content.py
        const response = await fetch(`${API_BASE_URL}/content/lunar_mansions_data`);
        return this._handleResponse(response);
    },

    async fetchArabicPartsFormulas() {
        const response = await fetch(`${API_BASE_URL}/content/arabic_parts/formulas`);
        return this._handleResponse(response);
    },

    // NEW: Methods for all other data files from app/data/
    async fetchProgressionInterpretationsData() {
        const response = await fetch(`${API_BASE_URL}/content/progression_interpretations`); // Assuming route /content/progression_interpretations
        return this._handleResponse(response);
    },

    async fetchMarsWeatherData() {
        const response = await fetch(`${API_BASE_URL}/content/mars_weather`); // Assuming route /content/mars_weather
        return this._handleResponse(response);
    },

    async fetchLifePathCompatibilityData() {
        const response = await fetch(`${API_BASE_URL}/content/life_path_compatibility`); // Assuming route /content/life_path_compatibility
        return this._handleResponse(response);
    },

    async fetchDonkiCMEData() {
        const response = await fetch(`${API_BASE_URL}/content/donki_cme`); // Assuming route /content/donki_cme
        return this._handleResponse(response);
    },

    async fetchCosmicEventsCalendarData() {
        const response = await fetch(`${API_BASE_URL}/content/cosmic_events_calendar`); // Assuming route /content/cosmic_events_calendar
        return this._handleResponse(response);
    },

    // --- Astrology API Calls ---
    async fetchDailyHoroscope(signKey, targetDate) { // Added targetDate parameter
        let url = `${API_BASE_URL}/astrology/daily_horoscope/${signKey}`;
        if (targetDate) {
            url += `?date=${targetDate}`; // Append date if provided
        }
        const response = await fetch(url);
        return this._handleResponse(response);
    },

    async calculateAndSaveNatalChart(birthDetails) {
        return this.fetchWithAuth(`/astrology/natal_chart`, { // Ensure endpoint matches backend
            method: 'POST',
            body: JSON.stringify(birthDetails)
        });
    },

    async fetchSavedNatalChart() {
        const response = await this.fetchWithAuth(`/astrology/natal_chart`); // Assuming GET to this endpoint
        // _handleResponse will throw if 404, which is then caught by calling function
        return response; 
    },

    async geocodeLocation(locationQuery) {
        const response = await fetch(`${API_BASE_URL}/astrology/geocode?q=${encodeURIComponent(locationQuery)}`);
        return this._handleResponse(response);
    },

    async getTransits(date = new Date()) {
        const response = await fetch(`${API_BASE_URL}/astrology/transits?date=${date.toISOString().split('T')[0]}`);
        return this._handleResponse(response);
    },
    
    async getCosmicWeather(date = new Date().toISOString().split('T')[0]) {
        const response = await fetch(`${API_BASE_URL}/astrology/cosmic_weather?date=${date}`);
        return this._handleResponse(response);
    },

    async getCompatibilityReport(person1Details, person2Details) {
        return this.fetchWithAuth(`/astrology/compatibility`, {
            method: 'POST',
            body: JSON.stringify({ person1: person1Details, person2: person2Details })
        });
    },

    // --- User Data API Calls (Journal, Saved Readings/Reports) ---
    async createJournalEntry(entryData) {
        return this.fetchWithAuth(`/user/journal`, {
            method: 'POST',
            body: JSON.stringify(entryData)
        });
    },

    async fetchJournalEntries(page = 1, perPage = 10, type = null) {
        let url = `/user/journal?page=${page}&per_page=${perPage}`;
        if (type) url += `&type=${encodeURIComponent(type)}`;
        return this.fetchWithAuth(url);
    },

    async deleteJournalEntry(entryId) {
        return this.fetchWithAuth(`/user/journal/${entryId}`, {
            method: 'DELETE'
        }); // Might be 204 No Content
    },

    async saveTarotReading(readingData) {
        return this.fetchWithAuth(`/user/tarot_readings`, {
            method: 'POST',
            body: JSON.stringify(readingData)
        });
    },

    async fetchSavedTarotReadings() {
        return this.fetchWithAuth(`/user/tarot_readings`);
    },
    
    async calculateAndSaveNumerology(fullName, birthDate, saveReport = true) {
        const payload = { full_name: fullName, birth_date: birthDate, save_report: saveReport };
        return this.fetchWithAuth(`/user/numerology_reports`, { 
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async fetchSavedNumerologyReports() {
        return this.fetchWithAuth(`/user/numerology_reports`);
    },

    // --- Divination API Calls (Public aspects) ---
    async performTarotReading(spreadType, question = null) {
        const payload = { spread_type: spreadType };
        if (question) payload.question = question;
        const response = await fetch(`${API_BASE_URL}/divination/tarot/perform_reading`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        return this._handleResponse(response);
    },

    async fetchCrystalRecommendations(zodiacSign, need) {
        let url = `${API_BASE_URL}/divination/crystals/recommendations?`;
        const params = [];
        if (zodiacSign) params.push(`zodiac_sign=${encodeURIComponent(zodiacSign)}`);
        if (need) params.push(`need=${encodeURIComponent(need)}`);
        url += params.join('&');
        const response = await fetch(url);
        return this._handleResponse(response);
    },

    async fetchRitualSuggestion(purpose, zodiacSign = null) {
        let url = `${API_BASE_URL}/divination/rituals/suggestion?purpose=${encodeURIComponent(purpose)}`;
        if (zodiacSign) url += `&zodiac_sign=${encodeURIComponent(zodiacSign)}`;
        const response = await fetch(url);
        return this._handleResponse(response);
    },

    // --- Personal Tools API Calls ---
    async fetchMoonDetails(dateStr = null) {
        let url = `${API_BASE_URL}/tools/moon/details`;
        if (dateStr) url += `?date=${dateStr}`;
        const response = await fetch(url);
        return this._handleResponse(response);
    },

    async fetchBiorhythms(birthDate, analysisDate) {
        const formattedBirthDate = new Date(birthDate).toISOString().split('T')[0];
        const formattedAnalysisDate = new Date(analysisDate).toISOString().split('T')[0];
        const response = await fetch(`${API_BASE_URL}/tools/biorhythms?birth_date=${formattedBirthDate}&analysis_date=${formattedAnalysisDate}`);
        return this._handleResponse(response);
    },
    
    async calculateChakraAssessment(answers) {
        return this.fetchWithAuth(`/tools/chakra_assessment`, {
            method: 'POST',
            body: JSON.stringify({ answers })
        });
    },

    async fetchUserChakraAssessment() {
        // Check if user has an assessment, might 404 if not
        try {
            return await this.fetchWithAuth(`/tools/chakra_assessment`);
        } catch (error) {
            if (error.status === 404) return null; // No assessment found is not an error in this context
            throw error; // Re-throw other errors
        }
    },

    // --- Calendar and Cosmic Events API Calls ---
    async fetchCosmicEventsCalendar(startDate, endDate, timezone) {
        const startDateStr = new Date(startDate).toISOString();
        const endDateStr = new Date(endDate).toISOString();
        const tzParam = timezone ? `&timezone=${encodeURIComponent(timezone)}` : '';
        const response = await fetch(`${API_BASE_URL}/astral-calendar/cosmic-events?start_date=${startDateStr}&end_date=${endDateStr}${tzParam}`);
        return this._handleResponse(response);
    },

    async fetchPersonalEventsCalendar(startDate, endDate) {
        const startDateStr = new Date(startDate).toISOString();
        const endDateStr = new Date(endDate).toISOString();
        return this.fetchWithAuth(`/astral-calendar/personal-events?start_date=${startDateStr}&end_date=${endDateStr}`);
    },

    async createPersonalEventCalendar(eventData) {
        return this.fetchWithAuth(`/astral-calendar/personal-events`, {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
    },

    async updatePersonalEventCalendar(eventId, eventData) {
        return this.fetchWithAuth(`/astral-calendar/personal-events/${eventId}`, {
            method: 'PUT',
            body: JSON.stringify(eventData)
        });
    },

    async deletePersonalEventCalendar(eventId) {
        return this.fetchWithAuth(`/astral-calendar/personal-events/${eventId}`, {
            method: 'DELETE'
        });
    },

    async fetchCalendarSettings() {
         try {
            return await this.fetchWithAuth(`/astral-calendar/settings`);
        } catch (error) {
            if (error.status === 404) return null; // No settings saved yet
            throw error;
        }
    },

    async updateCalendarSettings(settingsData) {
        return this.fetchWithAuth(`/astral-calendar/settings`, {
            method: 'PUT',
            body: JSON.stringify(settingsData)
        });
    },
    
    // --- Forecasting & Reports API Calls ---
    async getPersonalSky(startDate, endDate) {
        return this.fetchWithAuth(`/forecasting/personal-sky?start_date=${startDate}&end_date=${endDate}`);
    },

    async generateYearAheadReport(data = {}) {
        return this.fetchWithAuth(`/forecasting/reports/year-ahead/generate`, {
            method: 'POST',
            body: JSON.stringify(data) // data might include { target_start_date: "YYYY-MM-DD" }
        });
    },

    async getYearAheadReportStatus(reportId) {
        return this.fetchWithAuth(`/forecasting/reports/year-ahead/${reportId}`);
    },
    
    async listYearAheadReports() {
        return this.fetchWithAuth(`/forecasting/reports/year-ahead`);
    },

    async downloadYearAheadReport(reportId) {
        // Use fetchWithAuth with returnRawResponse = true
        const response = await this.fetchWithAuth(`/forecasting/reports/year-ahead/${reportId}/download`, {}, true);

        if (!response.ok) {
            // Try to parse error as JSON, otherwise use status text
            let errorPayload = { message: `File download failed: HTTP error! Status: ${response.status}` };
            try {
                const errorJson = await response.json();
                errorPayload = errorJson;
            } catch (e) {
                // Could not parse JSON, stick with the simpler error message.
            }
            throw { status: response.status, message: errorPayload.message || errorPayload.error, data: errorPayload };
        }

        const blob = await response.blob();
        const contentDisposition = response.headers.get('content-disposition');
        let filename = `year_ahead_report_${reportId}.pdf`; // Default filename
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
            if (filenameMatch && filenameMatch.length > 1) {
                filename = filenameMatch[1];
            }
        }
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        return { success: true, filename: filename }; // Indicate success
    },

    // --- Billing API Calls ---
    async getBillingConfig() { // For fetching public keys or basic config
        const response = await fetch(`${API_BASE_URL}/billing/config`); // No auth usually
        return this._handleResponse(response);
    },

    async createCheckoutSession(priceId, quantity = 1) {
        return this.fetchWithAuth(`/billing/create-checkout-session`, {
            method: 'POST',
            body: JSON.stringify({ price_id: priceId, quantity: quantity })
        });
    },

    async createPortalSession() {
        return this.fetchWithAuth(`/billing/create-portal-session`, {
            method: 'POST'
        });
    },

    // --- Keep these specific methods for clarity, even if they wrap fetchWithAuth ---
    // Year Ahead Report methods (already defined, good)
    // async generateYearAheadReport(birthData) { // This was duplicated from above, keeping the one in forecasting section
    // return this.fetchWithAuth('/reports/year-ahead', { // Endpoint might be different, e.g. /forecasting/reports...
    // method: 'POST',
    // body: JSON.stringify(birthData)
    // });
    // },

    async getUserReports() { // General reports listing, might be different from specific year-ahead list
        return this.fetchWithAuth('/user/reports'); // Example endpoint
    },

    // Zodiac Features methods
    async getZodiacFeatures(sign) {
         // Assuming a public or specific endpoint for this feature that might not require auth
         // or if it does, fetchWithAuth is appropriate.
         // If this is the same as fetchZodiacSignDetail, use that.
         // For now, assuming a different specific endpoint:
        const response = await fetch(`${API_BASE_URL}/zodiac/features/${sign}`);
        return this._handleResponse(response);
    },
};

// If not using ES6 modules, this object is globally available as apiService.
// If using ES6 modules, you would export it:
// export { apiService }; // This is already at the top

window.apiService = apiService; // Ensure it's available globally for non-module scripts