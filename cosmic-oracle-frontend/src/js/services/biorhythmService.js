// public/js/biorhythmService.js
import { post } from './apiClient.js';

/**
 * Calculates biorhythms for a person on a specific date.
 * @param {object} biorhythmData
 * @param {string} biorhythmData.birth_date - The person's birth date (e.g., '1991-08-15').
 * @param {string} biorhythmData.target_date - The date to calculate for (e.g., '2024-06-12').
 * @returns {Promise<object>} The biorhythm cycles (physical, emotional, intellectual).
 */
async function calculateBiorhythms(biorhythmData) {
    return await post('/api/biorhythm/calculate', biorhythmData);
}

export const biorhythmService = {
    calculateBiorhythms,
};