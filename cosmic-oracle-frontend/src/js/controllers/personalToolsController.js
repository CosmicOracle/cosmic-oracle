// Filename: personalToolsController.js

/**
 * Manages client-side logic for Personal Tools:
 * - Biorhythms
 * - Planet Tracker
 * - Chakra Analysis
 */

// --- Biorhythms Tool ---

/**
 * Initializes the Biorhythms tool.
 * Sets up event listeners for date inputs and the calculate button.
 * Sets default analysis date to today.
 */
function initBiorhythmsTool() {
    const birthDateInput = document.getElementById('biorhythmBirthDateInput');
    const analysisDateInput = document.getElementById('biorhythmAnalysisDateInput');
    const calculateButton = document.getElementById('calculateBiorhythmsBtn'); // Ensure this ID exists on your button

    if (analysisDateInput && !analysisDateInput.value) {
        analysisDateInput.value = new Date().toISOString().split('T')[0]; // Default to today
    }

    if (birthDateInput) {
        birthDateInput.addEventListener('change', handleBiorhythmInputChange);
    }
    if (analysisDateInput) {
        analysisDateInput.addEventListener('change', handleBiorhythmInputChange);
    }
    if (calculateButton) {
        calculateButton.addEventListener('click', handleCalculateBiorhythms);
    } else {
        // Fallback if button uses direct onclick in HTML
        console.warn("Biorhythms calculate button 'calculateBiorhythmsBtn' not found. Ensure HTML is updated or use direct onclick for handleCalculateBiorhythms.");
    }

    // Initial state for displays
    if (typeof updateBiorhythmDisplayUI === 'function') {
        updateBiorhythmDisplayUI('physical', null, true); // Reset display
        updateBiorhythmDisplayUI('emotional', null, true);
        updateBiorhythmDisplayUI('intellectual', null, true);
    }
    const chartContainer = document.getElementById('biorhythmChartDisplay');
    if (chartContainer) chartContainer.innerHTML = '<p style="text-align:center; padding-top: 80px;">Enter birth date to view chart.</p>';
    const interpretationEl = document.getElementById('biorhythmInterpretation');
    if (interpretationEl) interpretationEl.innerHTML = '';
}

/**
 * Handles input changes for biorhythm dates to potentially auto-calculate or enable button.
 */
function handleBiorhythmInputChange() {
    const birthDateStr = document.getElementById('biorhythmBirthDateInput')?.value;
    const analysisDateStr = document.getElementById('biorhythmAnalysisDateInput')?.value;
    // Could enable/disable calculate button here or auto-calculate if desired
    if (birthDateStr && analysisDateStr) {
        // Optionally auto-calculate: handleCalculateBiorhythms();
        // For now, let's assume user clicks the button.
    }
}

/**
 * Fetches and displays biorhythm data and chart.
 */
async function handleCalculateBiorhythms() {
    const birthDateStr = document.getElementById('biorhythmBirthDateInput')?.value;
    const analysisDateStr = document.getElementById('biorhythmAnalysisDateInput')?.value;
    const chartContainer = document.getElementById('biorhythmChartDisplay');
    const interpretationEl = document.getElementById('biorhythmInterpretation');

    if (!birthDateStr) {
        alert('Please enter your birth date to calculate biorhythms.');
        if (chartContainer) chartContainer.innerHTML = '<p style="text-align:center; padding-top: 80px;">Enter birth date to view chart.</p>';
        return;
    }
    if (!analysisDateStr) {
        alert('Please select an analysis date.');
        return;
    }

    if (chartContainer) chartContainer.innerHTML = '<p>Calculating your cosmic rhythms...</p>';
    if (interpretationEl) interpretationEl.innerHTML = '';


    try {
        const biorhythmData = await fetchBiorhythmsAPI(birthDateStr, analysisDateStr); // from apiService.js
        if (biorhythmData.error) {
            throw new Error(biorhythmData.error);
        }

        if (biorhythmData.cycles && typeof updateBiorhythmDisplayUI === 'function') {
            updateBiorhythmDisplayUI('physical', biorhythmData.cycles.physical?.value_sin);
            updateBiorhythmDisplayUI('emotional', biorhythmData.cycles.emotional?.value_sin);
            updateBiorhythmDisplayUI('intellectual', biorhythmData.cycles.intellectual?.value_sin);
        }

        if (interpretationEl && biorhythmData.cycles) {
            interpretationEl.innerHTML = `<h4>Secondary Rhythms for ${biorhythmData.analysis_date}:</h4><ul>`;
            const secondaryCyclesOrder = ['intuition', 'aesthetic', 'awareness', 'spiritual'];
            secondaryCyclesOrder.forEach(cycleKey => {
                if (biorhythmData.cycles[cycleKey]) {
                    const cycle = biorhythmData.cycles[cycleKey];
                    interpretationEl.innerHTML += `<li><strong>${cycle.label} (${cycle.length_days} days):</strong> ${cycle.status} (${cycle.percentage}%)</li>`;
                }
            });
            interpretationEl.innerHTML += `</ul><p><em>Use this as a guide for self-awareness. Highs = peak energy; Lows = rest/recharge; Critical days (near 50%) = potential instability or heightened sensitivity.</em></p>`;
        }

        const chartPlotData = await fetchBiorhythmChartDataAPI(birthDateStr, analysisDateStr); // from apiService.js
        if (chartPlotData && !chartPlotData.error && typeof drawBiorhythmChartUI === 'function') {
            drawBiorhythmChartUI(chartPlotData);
        } else if (chartPlotData && chartPlotData.error) {
            if (chartContainer) chartContainer.innerHTML = `<p style="color:red;">Could not load chart: ${chartPlotData.error}</p>`;
        }

    } catch (error) {
        console.error("Error calculating biorhythms:", error);
        if (chartContainer) chartContainer.innerHTML = `<p style="color:red;">Could not calculate biorhythms: ${error.message}</p>`;
        if (typeof updateBiorhythmDisplayUI === 'function') {
            updateBiorhythmDisplayUI('physical', null, true);
            updateBiorhythmDisplayUI('emotional', null, true);
            updateBiorhythmDisplayUI('intellectual', null, true);
        }
        if (interpretationEl) interpretationEl.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
    }
}


// --- Planet Tracker Tool ---

/**
 * Initializes and updates the Planet Tracker tool.
 */
async function initPlanetTrackerTool() {
    const container = document.getElementById('planetPositions');
    const influencesContainer = document.getElementById('planetaryInfluences');
    const retrogradeAlertContainer = document.getElementById('retrogradeAlert');

    if (!container || !influencesContainer || !retrogradeAlertContainer) {
        console.error("Planet tracker UI elements not found.");
        return;
    }
    if (!ALL_PLANETARY_DATA || typeof ALL_PLANETARY_DATA !== 'object' ||
        !ALL_ZODIAC_SIGNS_DATA || typeof ALL_ZODIAC_SIGNS_DATA !== 'object') {
        container.innerHTML = "<p>Planetary or Zodiac definition data not loaded yet. Please wait for initial app load.</p>";
        influencesContainer.innerHTML = "<h3>Current Planetary Influences</h3><ul><li>Loading...</li></ul>";
        retrogradeAlertContainer.innerHTML = "";
        return;
    }

    container.innerHTML = "<p>Tracking current celestial movements...</p>";
    influencesContainer.innerHTML = "<h3>Current Planetary Influences</h3><ul><li>Loading insights...</li></ul>";
    retrogradeAlertContainer.innerHTML = "";

    try {
        // Fetch current transits (planetary positions, aspects etc.)
        // The backend /api/astrology/transits should provide this.
        // get_current_transits_for_daily is the apiService function for this.
        const transitData = await get_current_transits_for_daily(null, null, null, 0, 'Placidus'); // Use default location for general transits

        if (transitData.error || !transitData.points) {
            throw new Error(transitData.error || "Planetary points data missing in transit response.");
        }

        // Display Planet Positions
        container.innerHTML = Object.values(transitData.points).map(point => {
            if (point.error || !point.key || point.name === "Part of Fortune" || point.name.includes("House")) return ''; // Skip PoF and House Cusps here
            const planetBase = ALL_PLANETARY_DATA[point.key.toLowerCase()] || { name: point.name, symbol: '?', influence: 'General influence.' };
            const signInfo = ALL_ZODIAC_SIGNS_DATA[point.sign_key] || { name: point.sign_name || 'N/A', symbol: '?' };
            return `
                <div class="planet-item">
                    <div style="font-size: 1.5rem;">${point.symbol || planetBase.symbol}</div>
                    <strong>${point.name} ${point.is_retrograde ? '(R)' : ''}</strong>
                    <div>in ${signInfo.symbol} ${signInfo.name}</div>
                    <p style="font-size: 0.8rem; margin-top: 5px;">${(point.degrees_in_sign || 0).toFixed(2)}°</p>
                </div>`;
        }).join('');

        // Display Planetary Influences & Retrograde Alerts
        let influencesHTML = '<ul>';
        let retroAlerts = [];
        Object.values(transitData.points).forEach(point => {
            if (point.error || !point.key || point.name === "Part of Fortune" || point.name.includes("House")) return;
            const planetBase = ALL_PLANETARY_DATA[point.key.toLowerCase()] || { name: point.name, influence: 'Planetary influence.' };
            const signBase = ALL_ZODIAC_SIGNS_DATA[point.sign_key] || { name: point.sign_name || 'N/A', keywords: ['general themes'] };

            let influenceText = `Focus on ${planetBase.influence ? planetBase.influence.split(',')[0].toLowerCase() : 'its core themes'} via ${signBase.keywords[0].toLowerCase()} energies.`;
            if (ALL_HOROSCOPE_INTERPRETATIONS && ALL_HOROSCOPE_INTERPRETATIONS.planet_in_sign && ALL_HOROSCOPE_INTERPRETATIONS.planet_in_sign[point.key.toLowerCase()] && ALL_HOROSCOPE_INTERPRETATIONS.planet_in_sign[point.key.toLowerCase()][point.sign_key]) {
                influenceText = ALL_HOROSCOPE_INTERPRETATIONS.planet_in_sign[point.key.toLowerCase()][point.sign_key];
            }
            influencesHTML += `<li><strong>${point.name} in ${point.sign_name}:</strong> ${influenceText}</li>`;

            if (point.is_retrograde) {
                let retroGuidance = `A time to review, reflect, and re-evaluate matters related to ${planetBase.influence ? planetBase.influence.split(',')[0].toLowerCase() : 'its domain'} and themes of ${point.sign_name.toLowerCase()}.`;
                 if (ALL_HOROSCOPE_INTERPRETATIONS && ALL_HOROSCOPE_INTERPRETATIONS.retrograde_guidance && ALL_HOROSCOPE_INTERPRETATIONS.retrograde_guidance[point.key.toLowerCase()]) {
                    retroGuidance = ALL_HOROSCOPE_INTERPRETATIONS.retrograde_guidance[point.key.toLowerCase()];
                }
                retroAlerts.push(`<strong>${point.name} is currently retrograde in ${point.sign_name}:</strong> ${retroGuidance}`);
            }
        });
        influencesHTML += '</ul>';
        influencesContainer.innerHTML = `<h3>Current Planetary Influences</h3>${influencesHTML}`;

        if (retroAlerts.length > 0) {
            retrogradeAlertContainer.innerHTML = `<div style="background: rgba(255, 107, 107, 0.2); padding: 15px; border-radius: 10px; border: 1px solid #ff6b6b;">
                <h4>⚠️ Retrograde Alert(s)</h4>
                ${retroAlerts.map(alert => `<p>${alert}</p>`).join('')}
            </div>`;
        } else {
            retrogradeAlertContainer.innerHTML = `<div style="background: rgba(107, 255, 107, 0.2); padding: 15px; border-radius: 10px; border: 1px solid #6bff6b;">
                <h4>🌟 All Key Planets Currently Direct</h4>
                <p>Major personal and faster-moving planets appear direct, supporting forward momentum. (Outer planets may be retrograde, representing deeper collective shifts).</p>
            </div>`;
        }

    } catch (error) {
        console.error("Error updating planet tracker:", error);
        if (container) container.innerHTML = `<p style="color:red;">Could not load planetary positions: ${error.message}</p>`;
        if (influencesContainer) influencesContainer.innerHTML = "<h3>Current Planetary Influences</h3><p style='color:red;'>Could not load influences.</p>";
        if (retrogradeAlertContainer) retrogradeAlertContainer.innerHTML = `<p style='color:red;'>Could not load retrograde status.</p>`;
    }
}


// --- Chakra Analysis Tool ---

/**
 * Initializes the Chakra Analysis tool.
 * Populates the chakra selector and sets up its event listener.
 */
function initChakraAnalysisTool() {
    const chakraSelect = document.getElementById('chakraSelect');
    if (chakraSelect) {
        populateChakraSelector();
        chakraSelect.addEventListener('change', displaySelectedChakraInfo);
        displaySelectedChakraInfo(); // Display info for default selected chakra
    } else {
        console.error("Chakra selector 'chakraSelect' not found.");
    }
}

/**
 * Populates the chakra selector dropdown.
 */
function populateChakraSelector() {
    const selector = document.getElementById('chakraSelect');
    if (!selector) return;

    if (ALL_CHAKRA_DATA && typeof ALL_CHAKRA_DATA === 'object') {
        selector.innerHTML = ''; // Clear existing options
        Object.entries(ALL_CHAKRA_DATA).forEach(([key, chakra]) => {
            if (chakra && chakra.name) {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = chakra.name;
                selector.appendChild(option);
            }
        });
    } else {
        selector.innerHTML = '<option value="">Chakra Data Error</option>';
        console.warn("ALL_CHAKRA_DATA not available for chakra selector.");
    }
}

/**
 * Displays detailed information for the selected chakra.
 */
function displaySelectedChakraInfo() {
    const selectedChakraKey = document.getElementById('chakraSelect')?.value || 'root'; // Default to root if none selected
    const container = document.getElementById('chakraInfo');
    const wheelDisplay = document.getElementById('chakraWheelDisplay'); // Assuming this ID for the visual

    if (!container) {
        console.error("Chakra info container 'chakraInfo' not found.");
        return;
    }
    if (!ALL_CHAKRA_DATA || typeof ALL_CHAKRA_DATA !== 'object') {
        container.innerHTML = "<p style='color:red;'>Chakra definition data is not available. Please try refreshing.</p>";
        if (wheelDisplay) wheelDisplay.style.borderColor = '#CCCCCC'; // Default border for wheel
        return;
    }

    const info = ALL_CHAKRA_DATA[selectedChakraKey];

    if (info) {
        container.innerHTML = `
            <h3 class="chakra-title">${info.name || 'Selected Chakra'} <span class="chakra-key">(${info.key || selectedChakraKey})</span></h3>
            <div class="chakra-header-info">
                <div class="chakra-color-indicator" style="background-color: ${info.color || '#CCCCCC'}; box-shadow: 0 0 10px ${info.color || '#CCCCCC'};"></div>
                <div class="chakra-basic-info">
                    <p><strong>Location:</strong> ${info.location || 'N/A'}</p>
                    <p><strong>Element:</strong> ${info.element || 'N/A'}</p>
                    <p><strong>Bija Mantra:</strong> ${info.bija_mantra || 'N/A'}</p>
                </div>
            </div>
            <div class="chakra-details">
                <h4>Primary Focus:</h4>
                <p class="chakra-primary-focus">${info.primary_focus || 'Core energetic functions.'}</p>
                
                <h4>Balanced Qualities:</h4>
                <p class="chakra-balanced-qualities">${(info.balanced_qualities && Array.isArray(info.balanced_qualities) ? info.balanced_qualities.join('; ') : 'General well-being.')}</p>
                
                <h4>Physical Imbalance Symptoms:</h4>
                <p class="chakra-imbalance-physical">${(info.imbalanced_symptoms_physical && Array.isArray(info.imbalanced_symptoms_physical) ? info.imbalanced_symptoms_physical.join('; ') : 'Various physical discomforts.')}</p>
                
                <h4>Emotional Imbalance Symptoms:</h4>
                <p class="chakra-imbalance-emotional">${(info.imbalanced_symptoms_emotional && Array.isArray(info.imbalanced_symptoms_emotional) ? info.imbalanced_symptoms_emotional.join('; ') : 'Emotional disturbances.')}</p>
                
                <h4>Healing Crystals:</h4>
                <p class="chakra-crystals">${(info.associated_crystals && Array.isArray(info.associated_crystals) ? info.associated_crystals.join(', ') : 'General healing crystals like Clear Quartz.')}</p>
                
                <h4>Healing Affirmation:</h4>
                <p class="chakra-affirmation"><em>"${info.affirmation || 'I am balanced and whole.'}"</em></p>
                
                <h4>Healing Practices:</h4>
                <ul class="chakra-healing-practices">
                    ${(info.healing_practices && Array.isArray(info.healing_practices) ? info.healing_practices.map(practice => `<li>${practice}</li>`).join('') : '<li>Mindful breathing and meditation.</li>')}
                    ${info.element ? `<li>Connect with element: ${getChakraElementActivityHelper(info.element)}</li>` : ''}
                </ul>
            </div>`;

        if (wheelDisplay) { // Update visual wheel border to match chakra color
            wheelDisplay.style.borderColor = info.color || '#CCCCCC';
            wheelDisplay.style.boxShadow = `0 0 15px ${info.color || '#CCCCCC'}, inset 0 0 10px rgba(0,0,0,0.2)`;
        }

    } else {
        container.innerHTML = "<p>Select a chakra to learn more about its properties and balancing techniques.</p>";
        if (wheelDisplay) wheelDisplay.style.borderColor = '#CCCCCC';
    }
}

/**
 * Helper function to get elemental activity text for chakras.
 * (This could be moved to a shared utils.js if used elsewhere)
 */
function getChakraElementActivityHelper(element) {
    if (!element) return 'Engage in mindful practices.';
    element = element.toLowerCase();
    if (element.includes('earth')) return 'Connect with nature: walk barefoot (earthing), gardening, hiking. Eat grounding root vegetables. Practice stability and routine.';
    if (element.includes('water')) return 'Engage with water: swim, take ritual baths with Epsom salts, be near oceans, lakes, or rivers. Creative dance or fluid movements. Honor and express your emotions healthily.';
    if (element.includes('fire')) return 'Sunbathe (safely for short periods). Engage in dynamic exercises (cardio, martial arts). Eat warming, spicy foods. Pursue passions with vigor and courage. Sit by a campfire.';
    if (element.includes('air')) return 'Practice deep conscious breathwork (pranayama). Spend time in fresh, open air. Engage in intellectual pursuits, stimulating conversations. Sing, play wind instruments, or listen to wind chimes.';
    if (element.includes('ether') || element.includes('sound') || element.includes('akasha')) return 'Sing, chant mantras, listen to healing music (especially singing bowls, tuning forks, or Solfeggio frequencies). Express your authentic truth. Practice active, mindful listening.';
    // --- FIX APPLIED HERE ---
    if (element.includes('light') || element.includes('intuition') || element.includes('mind')) return 'Meditate in soft natural light or candlelight. Gentle sun and moon gazing (at appropriate, safe times). Visualize pure, healing light. Trust your intuitive hits and insights. Keep a dream journal.';
    if (element.includes('thought') || element.includes('cosmic energy') || element.includes('consciousness')) return 'Practice mindfulness and presence. Engage in spiritual study and contemplation. Connect with higher consciousness through prayer, deep meditation, or periods of silence.';
    return `Engage in practices that resonate deeply with this chakra's essence (${element}), focusing on its core qualities.`;
}


// Expose init functions to be callable from script.js when tabs are activated
window.initBiorhythmsTool = initBiorhythmsTool;
window.initPlanetTrackerTool = initPlanetTrackerTool;
window.initChakraAnalysisTool = initChakraAnalysisTool;

// Expose handlers if they are called by direct onclick in HTML (prefer event listeners set in init)
window.handleCalculateBiorhythms = handleCalculateBiorhythms;
window.displaySelectedChakraInfo = displaySelectedChakraInfo; // If chakraSelect onchange calls this directly
