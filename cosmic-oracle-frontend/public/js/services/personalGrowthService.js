// public/js/services/personalGrowthService.js
/**
 * Frontend service for personal growth features like Rituals and Meditation.
 */
import { api } from '../api/index.js';
import { store } from '../state/store.js';

export const personalGrowthService = {
    /**
     * Fetches a personalized ritual suggestion from the backend.
     * @param {object} ritualRequest - The request data.
     * @param {string} ritualRequest.purpose - The purpose of the ritual (e.g., 'new-moon').
     * @param {string} ritualRequest.zodiac_sign_key - The user's sign key (e.g., 'leo').
     */
    async getRitualSuggestion(ritualRequest) {
        store.setState({ isLoading: true, error: null });
        try {
            const ritual = await api.getRitual(ritualRequest);
            store.setState({ 
                isLoading: false, 
                currentRitual: ritual 
            });
        } catch (error) {
            store.setState({ isLoading: false, error: error.message });
        }
    },

    /**
     * Records a completed meditation session.
     * @param {object} sessionData - The meditation session data.
     */
    async recordMeditation(sessionData) {
        store.setState({ isLoading: true, error: null });
        try {
            const response = await api.recordMeditation(sessionData);
            store.setState({
                isLoading: false,
                lastActionStatus: { success: true, message: response.message, sessionId: response.session_id }
            });
        } catch (error) {
            store.setState({ isLoading: false, error: error.message });
        }
    },

    /**
     * Fetches optimal times for meditation based on astronomical data.
     * @param {object} optimalTimeRequest - The request data.
     */
    async findOptimalMeditationTimes(optimalTimeRequest) {
        store.setState({ isLoading: true, error: null });
        try {
            const times = await api.getMeditationTimes(optimalTimeRequest);
            store.setState({ 
                isLoading: false, 
                optimalMeditationTimes: times.optimal_windows 
            });
        } catch (error) {
            store.setState({ isLoading: false, error: error.message });
        }
    }
};