// public/js/tarotService.js
import { post } from './apiClient.js';

/**
 * Performs a tarot draw.
 * @param {object} drawData
 * @param {number} drawData.card_count - The number of cards to draw.
 * @param {string} [drawData.spread_type] - Optional: The type of spread (e.g., 'celtic_cross').
 * @returns {Promise<object>} The drawn cards and their meanings.
 */
async function drawTarotCards(drawData) {
    return await post('/api/tarot/draw', drawData);
}

export const tarotService = {
    drawTarotCards,
};