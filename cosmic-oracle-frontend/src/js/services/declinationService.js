// public/js/declinationService.js
import { post } from './apiClient.js';

/**
 * Calculates parallel and contra-parallel aspects based on declination.
 * @param {object} chartData - The data required for the chart.
 * @returns {Promise<object>} The declination aspect results.
 */
async function getDeclinationAspects(chartData) {
    return await post('/api/declination/calculate', chartData);
}

export const declinationService = {
    getDeclinationAspects,
};