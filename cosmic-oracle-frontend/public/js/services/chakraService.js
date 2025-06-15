// public/js/services/chakraService.js
/**
 * Frontend service for interacting with the Chakra API.
 * This module encapsulates the logic for submitting assessments and fetching healing plans.
 */
import { api } from '../api/index.js';
import { store } from '../state/store.js';

export const chakraService = {
    /**
     * Submits a new chakra assessment to the backend.
     * @param {object} assessmentData - The data for the assessment.
     * @param {string} assessmentData.chakra_key - The key of the chakra (e.g., 'heart').
     * @param {number} assessmentData.balance_score - The user's score (1-10).
     * @param {string} [assessmentData.notes] - Optional notes.
     */
    async submitAssessment(assessmentData) {
        store.setState({ isLoading: true, error: null });
        try {
            const response = await api.submitChakraAssessment(assessmentData);
            store.setState({ 
                isLoading: false, 
                lastActionStatus: { success: true, message: response.message }
            });
            // After submitting, immediately refresh the healing plan to reflect the change.
            this.fetchHealingPlan();
        } catch (error) {
            store.setState({ isLoading: false, error: error.message });
        }
    },

    /**
     * Fetches the user's personalized healing plan from the backend.
     */
    async fetchHealingPlan() {
        store.setState({ isLoading: true, error: null });
        try {
            const planData = await api.getChakraHealingPlan();
            store.setState({ 
                isLoading: false, 
                chakraHealingPlan: planData 
            });
        } catch (error) {
            store.setState({ isLoading: false, error: error.message });
        }
    }
};