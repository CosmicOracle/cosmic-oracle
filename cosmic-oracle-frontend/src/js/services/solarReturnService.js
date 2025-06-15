// public/js/solarReturnService.js
import { post } from './apiClient.js';

/**
 * Calculates the solar return chart for a specific year.
 * @param {object} solarReturnData
 * @param {object} solarReturnData.birth_data - The person's birth data.
 * @param {number} solarReturnData.year - The year for which to calculate the solar return.
 * @returns {Promise<object>} The solar return chart data.
 */
async function getSolarReturnChart(solarReturnData) {
    return await post('/api/solar-return/calculate', solarReturnData);
}

export const solarReturnService = {
    getSolarReturnChart,
};