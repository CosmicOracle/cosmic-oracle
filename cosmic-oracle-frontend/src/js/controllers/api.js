// cosmic-oracle-frontend/public/js/api.js
/**
 * Centralized API handler for all communication with the Cosmic Oracle backend.
 * This module provides a clean, consistent interface for making API requests.
 */

const API_BASE_URL = '/api/v1'; // Set your API base URL here

/**
 * A generic helper function for making API requests.
 * @param {string} endpoint - The API endpoint to call (e.g., '/astrology/natal-chart').
 * @param {string} method - The HTTP method ('GET', 'POST', 'DELETE', etc.).
 * @param {object} [body=null] - The JSON body for POST/PUT requests.
 * @returns {Promise<object>} - A promise that resolves with the JSON response data.
 * @throws {Error} - Throws an error if the network response is not ok.
 */
async function request(endpoint, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const config = {
        method: method,
        headers: headers,
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'An unknown API error occurred.' }));
            const errorMessage = errorData.error || `HTTP error! status: ${response.status}`;
            throw new Error(errorMessage);
        }
        
        // Handle successful responses that might not have a JSON body (e.g., 204 No Content)
        if (response.status === 204) {
            return { success: true };
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request Failed:', error);
        // Re-throw the error so the calling function can handle it, e.g., to show a UI message.
        throw error;
    }
}

// --- Exported API Functions, One for Each Feature ---

export const api = {
    // Natal Chart & Core Astrology
    getNatalChart: (natalData) => request('/astrology/swisseph/natal-chart', 'POST', natalData),
    
    // Synastry & Compatibility
    getSynastryReport: (synastryData) => request('/astrology/synastry/chart', 'POST', synastryData),
    getCompositeChart: (compositeData) => request('/astrology/composite/chart', 'POST', compositeData),
    getCompatibilityReport: (compatibilityData) => request('/relationship/compatibility/report', 'POST', compatibilityData),

    // Predictive Astrology
    getSolarReturn: (solarReturnData) => request('/astrology/solar-return/chart', 'POST', solarReturnData),
    getTransitForecast: (forecastData) => request('/predictive/transits/report', 'POST', forecastData),
    getPersonalSky: () => request('/user/personal-sky/now', 'GET'),

    // Advanced & Traditional Techniques
    getArabicParts: (natalData) => request('/astrology/arabic-parts/report', 'POST', natalData),
    getDeclinations: (natalData) => request('/astrology/declination/analysis', 'POST', natalData),
    getMidpointTree: (natalData) => request('/astrology/midpoints/tree', 'POST', natalData),
    getHeliacalEvents: (heliacalData) => request('/calendar/heliacal/events', 'POST', heliacalData),
    getPlanetaryHours: (planetaryHoursData) => request('/tools/planetary-hours/schedule', 'POST', planetaryHoursData),

    // Divination & Insights
    getTarotReading: (spreadType) => request(`/divination/tarot/reading/${spreadType}`, 'POST'),
    saveTarotReading: (readingData) => request('/divination/tarot/readings', 'POST', readingData),
    getBiorhythms: (biorhythmData) => request('/insights/biorhythm/current', 'POST', biorhythmData),
    getHoroscope: (zodiacSign) => request(`/insights/horoscope/daily/${zodiacSign}`, 'GET'),
    
    // Personal Growth & Resources
    getRitual: (ritualData) => request('/personal-growth/rituals/suggestion', 'POST', ritualData),
    getMeditationTimes: (meditationData) => request('/personal-growth/meditation/recommendations/optimal-times', 'POST', meditationData),
    recordMeditation: (sessionData) => request('/personal-growth/meditation/sessions', 'POST', sessionData),
    getChakraPlan: () => request('/personal/chakras/healing-plan', 'GET'),
    getCrystalRecommendations: (params) => {
        const query = new URLSearchParams(params).toString();
        return request(`/resources/crystals/recommendations?${query}`, 'GET');
    },

    // Reports (Asynchronous)
    requestYearAheadReport: (natalData) => request('/reports/year-ahead', 'POST', { natal_data: natalData }),
    getReportStatus: (reportId) => request(`/reports/${reportId}/status`, 'GET'),
    // Note: Downloading is handled via a direct link, not an API fetch call.

    // Monitoring (Admin feature)
    getMonitoringMetrics: (days = 30) => request(`/admin/monitoring/metrics?days=${days}`, 'GET'),
    getMonitoringAlerts: () => request('/admin/monitoring/alerts', 'GET'),
};