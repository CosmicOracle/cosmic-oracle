// public/js/numerologyService.js
import { post } from './apiClient.js';

/**
 * Calculates a numerology report based on a full name and birth date.
 * @param {object} numerologyData
 * @param {string} numerologyData.full_name - The person's full birth name.
 * @param {string} numerologyData.birth_date - The person's birth date.
 * @returns {Promise<object>} The numerology report (e.g., Life Path, Destiny Number).
 */
async function getNumerologyReport(numerologyData) {
    return await post('/api/numerology/report', numerologyData);
}

export const numerologyService = {
    getNumerologyReport,
};