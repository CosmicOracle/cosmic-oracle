// public/js/ritualService.js
import { post } from './apiClient.js';

/**
 * Suggests rituals based on a specific goal or astrological event.
 * @param {object} ritualQuery
 * @param {string} ritualQuery.intent - The goal of the ritual (e.g., 'new_moon', 'prosperity', 'protection').
 * @returns {Promise<object>} A suggested ritual with steps and materials.
 */
async function getRitualSuggestion(ritualQuery) {
    return await post('/api/ritual/suggest', ritualQuery);
}

export const ritualService = {
    getRitualSuggestion,
};