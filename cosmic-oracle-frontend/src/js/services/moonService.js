// public/js/moonService.js
import { post } from './apiClient.js';

/**
 * Gets detailed information about the Moon for a specific date (phase, sign, etc.).
 * @param {object} moonData
 * @param {string} moonData.dt_utc - The UTC datetime string.
 * @returns {Promise<object>} Detailed information about the Moon.
 */
async function getMoonDetails(moonData) {
    return await post('/api/moon/details', moonData);
}

export const moonService = {
    getMoonDetails,
};