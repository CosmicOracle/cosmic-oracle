// public/js/horaryService.js
import { post } from './apiClient.js';

/**
 * Generates a horary chart for a specific question asked at a specific time/place.
 * @param {object} chartData - The time/place the question was asked.
 * @returns {Promise<object>} The horary chart data for interpretation.
 */
async function getHoraryChart(chartData) {
    return await post('/api/horary/chart', chartData);
}

export const horaryService = {
    getHoraryChart,
};