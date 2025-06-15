// public/js/compatibilityService.js
import { post } from './apiClient.js';

/**
 * Calculates a general compatibility score or report for two people.
 * @param {object} comparisonData
 * @param {object} comparisonData.personA_data - Birth data for the first person.
 * @param {object} comparisonData.personB_data - Birth data for the second person.
 * @returns {Promise<object>} A compatibility report.
 */
async function getCompatibilityReport(comparisonData) {
    return await post('/api/compatibility/report', comparisonData);
}

export const compatibilityService = {
    getCompatibilityReport,
};