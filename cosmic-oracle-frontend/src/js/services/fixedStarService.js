// public/js/fixedStarService.js
import { post } from './apiClient.js';

/**
 * Identifies conjunctions with major fixed stars in a natal chart.
 * @param {object} chartData - The data required for the chart.
 * @returns {Promise<object>} A list of fixed star conjunctions.
 */
async function getFixedStarConjunctions(chartData) {
    return await post('/api/fixedstars/conjunctions', chartData);
}

export const fixedStarService = {
    getFixedStarConjunctions,
};