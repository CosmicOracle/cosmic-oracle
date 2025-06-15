// Planet Tracker Client Module
import { apiService } from './apiService.js';

class PlanetTrackerClient {
    constructor() {
        this.planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'];
        this.currentPositions = null;
        this.updateInterval = null;
    }

    async initialize() {
        try {
            await this.updatePlanetaryPositions();
            // Update positions every 5 minutes
            this.updateInterval = setInterval(() => this.updatePlanetaryPositions(), 300000);
        } catch (error) {
            console.error('Failed to initialize planet tracker:', error);
        }
    }

    async updatePlanetaryPositions() {
        try {
            const positions = await apiService.fetchWithAuth('/planets/current-positions');
            this.currentPositions = positions;
            this.updateUI();
            return positions;
        } catch (error) {
            console.error('Failed to update planetary positions:', error);
            // Load fallback data if API fails
            return this.loadFallbackData();
        }
    }

    updateUI() {
        const container = document.getElementById('planetPositions');
        if (!container || !this.currentPositions) return;

        const html = this.planets.map(planet => {
            const position = this.currentPositions[planet.toLowerCase()] || {};
            return `
                <div class="planet-info">
                    <h4>${planet}</h4>
                    <p>Sign: ${position.sign || 'Unknown'}</p>
                    <p>Degree: ${position.degree?.toFixed(2) || 'Unknown'}°</p>
                    ${position.isRetrograde ? '<p class="retrograde">Retrograde</p>' : ''}
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    }

    loadFallbackData() {
        // Basic fallback data when API is unavailable
        return this.planets.reduce((acc, planet) => {
            acc[planet.toLowerCase()] = {
                sign: 'Data unavailable',
                degree: 0,
                isRetrograde: false
            };
            return acc;
        }, {});
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Create and export a single instance
export const planetTracker = new PlanetTrackerClient();
