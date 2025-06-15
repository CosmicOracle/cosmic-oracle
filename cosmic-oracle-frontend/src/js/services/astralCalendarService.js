// public/js/astralCalendarService.js
import { post } from './apiClient.js';

/**
 * Generates an astral calendar for a given date range.
 * @param {object} calendarParams
 * @param {string} calendarParams.start_date - The start date (e.g., '2024-06-01').
 * @param {string} calendarParams.end_date - The end date (e.g., '2024-06-30').
 * @returns {Promise<object>} The calendar with key astrological events.
 */
async function getCalendarEvents(calendarParams) {
    return await post('/api/calendar/events', calendarParams);
}

export const astralCalendarService = {
    getCalendarEvents,
};