// public/js/dignityService.js

import { post } from './apiClient.js';

/**
 * Calculates essential dignities by calling the backend API.
 * @param {object} chartData - The data required for the chart calculation.
 * @param {string} chartData.dt_utc - The UTC datetime string (ISO 8601 format).
 * @param {number} chartData.latitude - The geographic latitude.
 * @param {number} chartData.longitude - The geographic longitude.
 * @param {string} [chartData.house_system_name='Placidus'] - Optional house system.
 * @param {string[]} [chartData.points_to_assess] - Optional list of points.
 * @returns {Promise<object>} The dignity calculation result from the API.
 */
async function calculateDignities(chartData) {
    return await post('/api/dignities/calculate', chartData);
}

export const dignityService = {
    calculateDignities,
};