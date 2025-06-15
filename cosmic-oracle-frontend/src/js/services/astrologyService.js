// public/js/astrologyService.js

import { post } from './apiClient.js';

/**
 * Fetches a full natal chart from the backend API.
 * @param {object} chartData - The data required for the chart calculation.
 * @param {string} chartData.dt_utc - The UTC datetime string (ISO 8601 format).
 * @param {number} chartData.latitude - The geographic latitude.
 * @param {number} chartData.longitude - The geographic longitude.
 * @param {string} [chartData.house_system_name='Placidus'] - Optional house system.
 * @returns {Promise<object>} The full natal chart data from the API.
 */
async function getNatalChart(chartData) {
    // We assume the endpoint is '/api/astrology/natal-chart'
    return await post('/api/astrology/natal-chart', chartData);
}

export const astrologyService = {
    getNatalChart,
};