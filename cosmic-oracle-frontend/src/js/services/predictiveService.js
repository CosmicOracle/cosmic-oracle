// public/js/predictiveService.js
import { post } from './apiClient.js';

/**
 * Calculates current or future transits to a natal chart.
 * @param {object} predictiveData
 * @param {object} predictiveData.natal_data - The birth data for the natal chart.
 * @param {string} predictiveData.target_date - The date to calculate transits for.
 * @returns {Promise<object>} A report of significant transits.
 */
async function getTransits(predictiveData) {
    return await post('/api/predictive/transits', predictiveData);
}

export const predictiveService = {
    getTransits,
};