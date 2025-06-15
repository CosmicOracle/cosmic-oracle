// public/js/electionalService.js
import { post } from './apiClient.js';

/**
 * Finds auspicious dates for an event within a given timeframe.
 * @param {object} electionalData
 * @param {string} electionalData.event_type - The type of event (e.g., 'marriage', 'business_launch').
 * @param {string} electionalData.start_date - The start of the date range to search.
 * @param {string} electionalData.end_date - The end of the date range to search.
 * @returns {Promise<object>} A list of recommended dates with explanations.
 */
async function findAuspiciousDates(electionalData) {
    return await post('/api/electional/find', electionalData);
}

export const electionalService = {
    findAuspiciousDates,
};