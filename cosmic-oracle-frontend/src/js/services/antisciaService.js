// public/js/antisciaService.js
import { post } from './apiClient.js';

/**
 * Calculates antiscia and contra-antiscia points for a chart.
 * @param {object} chartData - The data required for the chart.
 * @returns {Promise<object>} The antiscia calculation result.
 */
async function calculateAntiscia(chartData) {
    return await post('/api/antiscia/calculate', chartData);
}

export const antisciaService = {
    calculateAntiscia,
};