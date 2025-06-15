// public/js/synastryService.js
import { post } from './apiClient.js';

/**
 * Creates a detailed synastry report (inter-aspects) between two charts.
 * @param {object} comparisonData
 * @param {object} comparisonData.personA_data - Birth data for the first person.
 * @param {object} comparisonData.personB_data - Birth data for the second person.
 * @returns {Promise<object>} A detailed synastry aspect report.
 */
async function getSynastryReport(comparisonData) {
    return await post('/api/synastry/report', comparisonData);
}

export const synastryService = {
    getSynastryReport,
};