// src/js/services/NatalChartService.js
import { api } from '../api';
import { store } from '../state/store';

export const natalChartService = {
  async fetchAndProcessChart(formData) {
    store.setState({ isLoading: true, error: null });
    try {
      const chartData = await api.getNatalChart(formData);
      store.setState({ isLoading: false, currentChart: chartData });
    } catch (error) {
      store.setState({ isLoading: false, error: error.message });
    }
  },
};