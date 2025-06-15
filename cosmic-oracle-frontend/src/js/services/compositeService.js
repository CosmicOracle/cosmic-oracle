// public/js/compositeService.js
import { post } from './apiClient.js';

/**
 * Generates a composite chart for two individuals, representing their relationship.
 * @param {object} comparisonData
 * @param {object} comparisonData.personA_data - Birth data for the first person.
 * @param {object} comparisonData.personB_data - Birth data for the second person.
 * @returns {Promise<object>} The composite chart data.
 */
async function getCompositeChart(comparisonData) {
    return await post('/api/composite/calculate', comparisonData);
}

export const compositeService = {
    getCompositeChart,
};