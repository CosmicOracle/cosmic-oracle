// public/js/crystalService.js
import { post } from './apiClient.js';

/**
 * Recommends crystals based on a natal chart's needs.
 * @param {object} chartData - The data required for the natal chart.
 * @returns {Promise<object>} A list of recommended crystals and their properties.
 */
async function getCrystalRecommendations(chartData) {
    return await post('/api/crystal/recommend', chartData);
}

export const crystalService = {
    getCrystalRecommendations,
};