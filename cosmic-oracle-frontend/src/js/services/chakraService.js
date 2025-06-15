// public/js/chakraService.js
import { post } from './apiClient.js';

/**
 * Provides a chakra analysis based on a natal chart.
 * @param {object} chartData - The data required for the natal chart.
 * @returns {Promise<object>} An analysis of chakra energies based on planetary placements.
 */
async function getChakraAnalysis(chartData) {
    return await post('/api/chakra/analyze', chartData);
}

export const chakraService = {
    getChakraAnalysis,
};