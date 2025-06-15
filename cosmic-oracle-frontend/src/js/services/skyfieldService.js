// public/js/skyfieldService.js

import { post } from './apiClient.js';

/**
 * Fetches the positions of specific celestial bodies using the Skyfield service.
 * @param {object} positionData - The data for the position lookup.
 * @param {string} positionData.dt_utc - The UTC datetime string (ISO 8601 format).
 * @param {string[]} positionData.bodies - An array of celestial body names (e.g., ["Mars", "Jupiter", "Saturn"]).
 * @returns {Promise<object>} A dictionary of celestial body positions.
 */
async function getBodyPositions(positionData) {
    // We assume the endpoint is '/api/skyfield/positions'
    return await post('/api/skyfield/positions', positionData);
}

export const skyfieldService = {
    getBodyPositions,
};