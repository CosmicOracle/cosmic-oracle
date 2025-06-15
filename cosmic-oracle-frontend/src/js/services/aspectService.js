// public/js/aspectService.js
import { post } from './apiClient.js';

/**
 * Calculates aspects for a given chart.
 * @param {object} chartData - The data required for the chart.
 * @returns {Promise<object>} The list of aspects and their details.
 */
async function getAspects(chartData) {
    return await post('/api/aspects/get', chartData);
}

export const aspectService = {
    getAspects,
};