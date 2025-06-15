// public/js/services/advancedToolsService.js
/**
 * Frontend service for advanced astrological tools like Midpoints, Declinations, etc.
 */
import { api } from '../api/index.js';
import { store } from '../state/store.js';

export const advancedToolsService = {
    /**
     * Fetches a full midpoint tree report.
     * @param {object} natalData - The user's natal data.
     */
    async getMidpointTree(natalData) {
        store.setState({ isLoading: true, error: null });
        try {
            const report = await api.getMidpointTree(natalData);
            store.setState({
                isLoading: false,
                advancedReport: { type: 'Midpoints', data: report }
            });
        } catch (error) {
            store.setState({ isLoading: false, error: error.message });
        }
    },

    /**
     * Fetches a declination analysis report.
     * @param {object} natalData - The user's natal data.
     */
    async getDeclinationReport(natalData) {
        store.setState({ isLoading: true, error: null });
        try {
            const report = await api.getDeclinations(natalData);
            store.setState({
                isLoading: false,
                advancedReport: { type: 'Declinations', data: report }
            });
        } catch (error) {
            store.setState({ isLoading: false, error: error.message });
        }
    },

     /**
     * Fetches a Heliacal events report.
     * @param {object} heliacalData - The request data (date range, location).
     */
    async getHeliacalEvents(heliacalData) {
        store.setState({ isLoading: true, error: null });
        try {
            const report = await api.getHeliacalEvents(heliacalData);
            store.setState({
                isLoading: false,
                advancedReport: { type: 'Heliacal Events', data: report }
            });
        } catch (error) {
            store.setState({ isLoading: false, error: error.message });
        }
    }
};