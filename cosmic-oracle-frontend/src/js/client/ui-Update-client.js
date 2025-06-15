/**
 * uiUpdate.js
 *
 * This file manages the UI updates and application state for "The Ultimate Horoscope Experience."
 * It defines a globalState object to store all necessary data and provides functions
 * to render and update different sections of the application based on user interaction.
 */

// --- 1. Global State Definition ---
/**
 * @typedef {object} GlobalState
 * @property {string} currentView - The currently active section/feature (e.g., 'dailyHoroscope', 'natalChart').
 * @property {object} userData - Stores user-specific input (e.g., birth date, time, location).
 * @property {object} horoscopeData - Stores data related to daily horoscopes, signs, etc.
 * @property {object} natalChartData - Stores computed natal chart data.
 * @property {object} moonSunData - Stores Moon and Sun specific data.
 * @property {object} planetaryHoursData - Stores planetary hours calculations.
 * @property {object} dignitiesData - Stores planetary dignities data.
 * @property {object} arabicPartsData - Stores Arabic Parts calculations.
 * @property {object} fixedStarsData - Stores Fixed Stars data.
 * @property {object} midpointsData - Stores Midpoints calculations.
 * @property {object} lunarMansionsData - Stores Lunar Mansions data.
 * @property {object} antisciaData - Stores Antiscia calculations.
 * @property {object} declinationData - Stores Declination data.
 * @property {object} heliacalData - Stores Heliacal calculations.
 * @property {object} cosmicCalendarData - Stores Cosmic Calendar data.
 * @property {object} personalSkyData - Stores Personal Sky data.
 * @property {object} yearAheadData - Stores Year Ahead predictions/transits.
 * @property {object} signCombinationsData - Stores Sign Combinations data.
 * @property {object} compatibilityData - Stores Compatibility analysis data.
 * @property {object} zodiacKnowledgeData - Stores Zodiac sign properties, elements, modalities etc.
 * @property {object} tarotReadingData - Stores Tarot card meanings, spread results.
 * @property {object} numerologyData - Stores Numerology calculations and interpretations.
 * @property {object} crystalGuideData - Stores Crystal properties and uses.
 * @property {object} planetTrackerData - Stores real-time or historical planetary positions.
 * @property {object} chakraAnalysisData - Stores Chakra information and analysis.
 * @property {object} meditationData - Stores Meditation guides, audio links.
 * @property {object} cosmicJournalData - Stores user's journal entries.
 * @property {object} dreamAnalysisData - Stores Dream analysis tools/interpretations.
 * @property {object} sacredRitualsData - Stores Sacred Rituals information.
 * @property {object} biorhythmsData - Stores Biorhythm calculations.
 * @property {boolean} isLoading - Flag to indicate if data is being loaded (e.g., from an API).
 * @property {string|null} errorMessage - Stores any error messages to display to the user.
 * @property {Date} selectedCalendarDate - The currently selected date for calendar-related features.
 * @property {object} ALL_ZODIAC_SIGNS_DATA - Data for all zodiac signs.
 * @property {object} ALL_TAROT_DECK_DATA - Data for the full Tarot deck.
 * @property {object} ALL_CRYSTAL_DATA - Data for various crystals.
 * @property {object} ALL_CHAKRA_DATA - Data for all chakras.
 * @property {object} ALL_DREAM_SYMBOLS_DATA - Data for dream symbols.
 * @property {Array<string>} ALL_AFFIRMATIONS_DATA - List of affirmations.
 * @property {object} ALL_COMPATIBILITY_MATRIX - Compatibility data between signs.
 * @property {object} ALL_PLANETARY_DATA - Data for planets.
 * @property {object} ALL_RITUAL_DATA - Data for rituals.
 * @property {object} ALL_NUMEROLOGY_MEANINGS_DATA - Meanings for numerology numbers.
 * @property {object} ALL_HOUSE_SYSTEM_DATA - Data for astrological house systems.
 * @property {object} ALL_ASPECT_DATA - Data for astrological aspects.
 * @property {object} ALL_DIGNITY_INTERPRETATIONS - Interpretations for planetary dignities.
 * @property {object} ALL_POF_INTERPRETATIONS - Interpretations for Part of Fortune.
 * @property {object} ALL_HOROSCOPE_INTERPRETATIONS - General horoscope interpretations.
 */

// Global state object to store shared data.
// This is THE core fix for `globalState is not defined`.
// It is declared here at the top-level of the module.
/** @type {GlobalState} */
export let globalState = { // Export globalState
    currentView: 'daily-horoscope-tab', // Default view on load (adjust to your preferred default)
    userData: {},
    horoscopeData: {},
    natalChartData: null,
    moonSunData: null,
    planetaryHoursData: null, // ADDED
    dignitiesData: null,
    arabicPartsData: null,
    fixedStarsData: null, // ADDED
    midpointsData: null, // ADDED
    lunarMansionsData: null, // ADDED
    antisciaData: null, // ADDED
    declinationData: null, // ADDED
    heliacalData: null, // ADDED
    cosmicCalendarData: null,
    personalSkyData: null, // ADDED
    yearAheadData: null, // ADDED
    signCombinationsData: null,
    compatibilityData: null,
    zodiacKnowledgeData: null,
    tarotReadingData: null,
    numerologyData: null,
    crystalGuideData: null,
    planetTrackerData: null,
    chakraAnalysisData: null,
    meditationData: null,
    cosmicJournalData: [],
    dreamAnalysisData: null,
    sacredRitualsData: null,
    biorhythmsData: null,
    isLoading: false,
    errorMessage: null,
    selectedCalendarDate: new Date(), // Now part of globalState
    ALL_ZODIAC_SIGNS_DATA: null,
    ALL_TAROT_DECK_DATA: null,
    ALL_CRYSTAL_DATA: null,
    ALL_CHAKRA_DATA: null,
    ALL_DREAM_SYMBOLS_DATA: null,
    ALL_AFFIRMATIONS_DATA: ["Embrace your inner light today."],
    ALL_COMPATIBILITY_MATRIX: null,
    ALL_PLANETARY_DATA: null,
    ALL_RITUAL_DATA: null,
    ALL_NUMEROLOGY_MEANINGS_DATA: null,
    ALL_HOUSE_SYSTEM_DATA: null,
    ALL_ASPECT_DATA: null,
    ALL_DIGNITY_INTERPRETATIONS: null,
    ALL_POF_INTERPRETATIONS: null,
    ALL_HOROSCOPE_INTERPRETATIONS: null,
};

// External dependency: apiService object/module for backend API calls.
// This is typically imported from apiService.js if using ES Modules,
// or made available globally (e.g., window.apiService) if using script tags.
// Import the real API service
import { apiService } from '../services/apiService.js';

// Ensure apiService is available globally for compatibility with existing code
window.apiService = apiService;


// External dependency: currentUser variable for authentication state.
// Typically set by your authentication system (e.g., in auth.js or app.js).
// Initialize as null; your authentication logic should update this.
export let currentUser = null; // Export currentUser too
// To simulate a logged-in user for testing, you could uncomment:
// window.currentUser = { id: 1, username: 'testuser', email: 'test@example.com', full_name_for_numerology: 'Test User', birth_data: { birth_datetime_utc: '1990-05-15T12:00:00Z', birth_location: { latitude: 42.00, longitude: -123.00, timezone_str: 'America/Los_Angeles' } } };


// Biorhythm Cycles (constant data, defined here in uiUpdate.js as it's static config)
const BIORHYTHM_CYCLES = {
    physical: { length: 23, label: 'Physical' },
    emotional: { length: 28, label: 'Emotional' },
    intellectual: { length: 33, label: 'Intellectual' },
    intuition: { length: 38, label: 'Intuition' },
    aesthetic: { length: 43, label: 'Aesthetic' },
    awareness: { length: 48, label: 'Awareness' },
    spiritual: { length: 53, label: 'Spiritual' }
};

// --- Web Speech API global utterance & Voice Initialization ---
let currentSpeechUtterance = null;
let speechVoices = []; // Stores available voices for Web Speech API

// Asynchronously load voices for speech synthesis
if ('speechSynthesis' in window) {
    // This event fires when the list of SpeechSynthesisVoice objects changes.
    // This is important because voices might not be immediately available.
    speechSynthesis.onvoiceschanged = () => {
        speechVoices = speechSynthesis.getVoices();
        console.log("Web Speech API voices loaded.");
    };
    // Attempt to load voices immediately if they are already available (e.g., on subsequent page loads)
    speechVoices = speechSynthesis.getVoices();
} else {
    console.warn("Web Speech API (speechSynthesis) not supported by this browser.");
}


// --- Core Tab Switching Logic ---
export function showTab(tabId, event = null) { // Export showTab
    if (event) event.preventDefault(); //

    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
        tab.style.display = 'none'; // Ensure it's hidden
    });

    // Deactivate all tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show the selected tab content
    const tabContent = document.getElementById(tabId);
    if (tabContent) {
        tabContent.classList.add('active');
        tabContent.style.display = 'block'; // Make it visible
    } else {
        console.warn(`Tab content with ID '${tabId}' not found.`);
        // Don't proceed to set innerHTML if tabContent is null
        return;
    }

    // Activate the clicked button
    const targetButton = event?.currentTarget ||
        document.querySelector(`.tab-button[data-target="${tabId}"]`);
    if (targetButton) {
        targetButton.classList.add('active');
    }

    // Update global state
    globalState.currentView = tabId;

    // Trigger any tab-specific initialization (e.g., loading data for a tab)
    window.dispatchEvent(new CustomEvent('tabChanged', { detail: { tabId } }));
}

// Initialize tab system on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    // Add click handlers to all tab buttons that have a 'data-target' attribute
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const target = button.getAttribute('data-target');
            if (target) {
                showTab(target, e);
            } else {
                console.warn("Tab button missing 'data-target' attribute:", button);
            }
        });
    });

    // Handle tab change events to update specific UI components
    window.addEventListener('tabChanged', (event) => {
        const tabId = event.detail.tabId;
        console.log(`Tab changed to: ${tabId}`);
        // Call specific UI update functions based on the active tab
        switch (tabId) {
            case 'daily-horoscope-tab':
                // Default to a sign or prompt user
                if (globalState.ALL_ZODIAC_SIGNS_DATA) {
                    displayDailyHoroscopeUI(globalState.ALL_ZODIAC_SIGNS_DATA.aries ? 'aries' : Object.keys(globalState.ALL_ZODIAC_SIGNS_DATA)[0]);
                } else {
                    document.getElementById('dailyInsight').innerHTML = '<p>Loading zodiac data for daily horoscope...</p>';
                }
                break;
            case 'natal-chart-tab':
                // Prompt user for birth data or use saved data
                renderNatalChartInputForm();
                break;
            case 'moon-sun-tab':
                updateMoonPhaseDisplayUI();
                updateMoonSunAnalysisUI(); // For the Sun-Moon combination analysis
                break;
            case 'planetary-hours-tab':
                renderPlanetaryHoursUI();
                break;
            case 'dignities-tab':
                renderDignitiesUI();
                break;
            case 'arabic-parts-tab':
                renderArabicPartsUI();
                break;
            case 'fixed-stars-tab':
                renderFixedStarsUI();
                break;
            case 'midpoints-tab':
                renderMidpointsUI();
                break;
            case 'lunar-mansions-tab':
                renderLunarMansionsUI();
                break;
            case 'antiscia-tab':
                renderAntisciaUI();
                break;
            case 'declination-tab':
                renderDeclinationUI();
                break;
            case 'heliacal-tab':
                renderHeliacalUI();
                break;
            case 'cosmic-calendar-tab':
                generateCosmicEventsUI();
                updateMoonPhaseDisplayUI(); // Moon phase is relevant for calendar
                break;
            case 'personal-sky-tab':
                renderPersonalSkyUI();
                break;
            case 'year-ahead-tab':
                renderYearAheadUI();
                break;
            case 'sign-combinations-tab':
                updateCombinationUI();
                break;
            case 'compatibility-tab':
                updateCompatibilityUI();
                break;
            case 'zodiac-knowledge-tab':
                populateKnowledgeUI();
                break;
            case 'tarot-reading-tab':
                setupTarotReadingUI();
                loadSavedTarotReadingsUI();
                break;
            case 'numerology-tab':
                // Prefill if user is logged in
                if (currentUser) {
                    prefillAndCalculateNumerology(currentUser);
                } else {
                    document.getElementById('numerologyResults').innerHTML = '';
                    document.getElementById('numerologyInterpretation').innerHTML = '<p>Enter your full birth name and birth date to calculate your numerological profile.</p>';
                }
                loadSavedNumerologyReportsUI();
                break;
            case 'crystal-guide-tab':
                updateCrystalGuidanceUI();
                break;
            case 'planet-tracker-tab':
                updatePlanetTrackerUI();
                break;
            case 'chakra-analysis-tab':
                updateChakraInfoUI(); // Default to root or first chakra
                break;
            case 'meditation-tab':
                updateMeditationUI();
                populateMantraListUI();
                break;
            case 'cosmic-journal-tab':
                loadUserJournalEntriesUI();
                break;
            case 'dream-analysis-tab':
                populateDreamSymbolGridUI();
                break;
            case 'sacred-rituals-tab':
                updateRitualsUI();
                break;
            case 'biorhythms-tab':
                // Initial state for biorhythms tab
                const today = new Date();
                const todayStr = today.toISOString().split('T')[0];
                const analysisDateInput = document.getElementById('biorhythmAnalysisDateInput');
                if (analysisDateInput) analysisDateInput.value = todayStr;
                calculateBiorhythmsUI(); // Trigger initial calculation if dates are set
                break;
            // Add more cases for each tab
            default:
                console.log(`No specific action for tab: ${tabId}`);
                break;
        }
    });

    // Show initial default tab on load
    showTab(globalState.currentView);
});

// --- UI Helper functions (exposed via window.uiHelpers) ---
export const uiHelpers = { // Export uiHelpers
    showLoading: function(container, message = 'Loading...') {
        if (container) {
            container.innerHTML = `<p class="loading-message">${message}</p>`;
        } else {
            console.warn("showLoading called without a valid container element.");
        }
    },

    hideLoading: function(container) {
        if (container && container.querySelector('.loading-message')) {
            container.querySelector('.loading-message').remove();
        } else if (container) {
            // Already hidden or no loading message
        } else {
            console.warn("hideLoading called without a valid container element.");
        }
    },

    displayError: function(message, container) {
        if (container) {
            container.innerHTML = `<p class="error-message">${message}</p>`;
        } else {
            console.error(`displayError (no container): ${message}`);
        }
    },

    displaySuccess: function(message, container) {
        if (container) {
            container.innerHTML = `<p class="success-message">${message}</p>`;
        } else {
            console.log(`displaySuccess (no container): ${message}`); // Log success messages even without a specific container
        }
    }
};

// Global error/success message displays (for specific elements)
export function displayError(message) { // Export displayError
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        setTimeout(() => {
            errorElement.style.display = 'none';
            errorElement.textContent = ''; // Clear text after hiding
        }, 5000);
    } else {
        console.error(`Global Error Display: ${message}`);
    }
}

export function displaySuccess(message) { // Export displaySuccess
    const successElement = document.getElementById('success-message');
    if (successElement) {
        successElement.textContent = message;
        successElement.style.display = 'block';
        setTimeout(() => {
            successElement.style.display = 'none';
            successElement.textContent = ''; // Clear text after hiding
        }, 5000);
    } else {
        console.log(`Global Success Display: ${message}`);
    }
}

// Global loading overlay
export function showLoading(message = 'Loading...') { // Export showLoading
    const loader = document.getElementById('loader');
    if (loader) {
        const loaderMessage = loader.querySelector('.loader-message');
        if (loaderMessage) {
            loaderMessage.textContent = message;
        }
        loader.style.display = 'flex'; // Use flex to center content
    } else {
        console.warn("Loader element with ID 'loader' not found.");
    }
}

export function hideLoading() { // Export hideLoading
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'none';
    }
}

// --- Make UI helpers and globalState available globally ---
// This is done once after uiHelpers and globalState are defined.
// These are not needed if you import directly as done in script.js.
// Keeping them only if external, non-module scripts also access them directly.
// window.uiHelpers = uiHelpers;
// window.globalState = globalState;

// --- Main function to load initial content data from backend ---
export async function loadInitialContentData() { // Export loadInitialContentData
    console.log("Loading initial content data from backend...");
    try {
        // Use Promise.allSettled instead of Promise.all to ensure all promises
        // complete (succeed or fail) before proceeding. This prevents a single
        // failed API call from crashing the entire initial data load.
        const [
                zodiacs, tarot, crystals, chakras, dreams, affirmationsResponse, compatMatrix,
                planets, rituals, numerologyMeanings, houseSystems, aspects,
                dignityInterpretations, pofInterpretations, horoscopeInterpretations,
                planetaryHours, fixedStars, midpoints, lunarMansions, antiscia,
                declination, heliacal, personalSkyData, yearAheadForecast
            ] = await Promise.allSettled([ // Changed to Promise.allSettled
                apiService.fetchAllZodiacSigns(),
                apiService.fetchTarotDeck(),
                apiService.fetchCrystalData(),
                apiService.fetchChakraData(),
                apiService.fetchDreamSymbols(),
                apiService.fetchRandomAffirmation(),
                apiService.fetchCompatibilityMatrix(),
                apiService.fetchPlanetaryData(),
                apiService.fetchRitualsData(),
                apiService.fetchNumerologyMeanings(),
                apiService.fetchHouseSystemsData(),
                apiService.fetchAspectData(),
                apiService.fetchDignityInterpretations(),
                apiService.fetchPartOfFortuneInterpretations(),
                apiService.fetchHoroscopeInterpretations(),
                // --- ADDED NEW API CALLS TO INITIAL LOAD ---
                apiService.fetchPlanetaryHours(),
                apiService.fetchFixedStars(),
                apiService.fetchMidpoints(),
                apiService.fetchLunarMansions(),
                apiService.fetchAntiscia(),
                apiService.fetchDeclination(),
                apiService.fetchHeliacal(),
                apiService.fetchPersonalSkyData(),
                apiService.fetchYearAheadForecast()
            ]);

        // Process results from Promise.allSettled
        // A 'fulfilled' status means the promise resolved successfully.
        // A 'rejected' status means the promise threw an error.
        globalState.ALL_ZODIAC_SIGNS_DATA = zodiacs.status === 'fulfilled' ? zodiacs.value : null;
        if (zodiacs.status === 'rejected') console.error("Failed to load zodiacs:", zodiacs.reason);

        globalState.ALL_TAROT_DECK_DATA = tarot.status === 'fulfilled' ? tarot.value : null;
        if (tarot.status === 'rejected') console.error("Failed to load tarot:", tarot.reason);

        globalState.ALL_CRYSTAL_DATA = crystals.status === 'fulfilled' ? crystals.value : null;
        if (crystals.status === 'rejected') console.error("Failed to load crystals:", crystals.reason);

        globalState.ALL_CHAKRA_DATA = chakras.status === 'fulfilled' ? chakras.value : null;
        if (chakras.status === 'rejected') console.error("Failed to load chakras:", chakras.reason);

        globalState.ALL_DREAM_SYMBOLS_DATA = dreams.status === 'fulfilled' ? dreams.value : null;
        if (dreams.status === 'rejected') console.error("Failed to load dream symbols:", dreams.reason);

        // Ensure affirmations data is always an array, even if initial fetch fails
        globalState.ALL_AFFIRMATIONS_DATA = affirmationsResponse.status === 'fulfilled' && affirmationsResponse.value && affirmationsResponse.value.affirmation
                                            ? [affirmationsResponse.value.affirmation]
                                            : ["Embrace your inner light today."];
        if (affirmationsResponse.status === 'rejected') console.error("Failed to load initial affirmation:", affirmationsResponse.reason);

        globalState.ALL_COMPATIBILITY_MATRIX = compatMatrix.status === 'fulfilled' ? compatMatrix.value : null;
        if (compatMatrix.status === 'rejected') console.error("Failed to load compatibility matrix:", compatMatrix.reason);

        globalState.ALL_PLANETARY_DATA = planets.status === 'fulfilled' ? planets.value : null;
        if (planets.status === 'rejected') console.error("Failed to load planetary data:", planets.reason);

        globalState.ALL_RITUAL_DATA = rituals.status === 'fulfilled' ? rituals.value : null;
        if (rituals.status === 'rejected') console.error("Failed to load rituals data:", rituals.reason);

        globalState.ALL_NUMEROLOGY_MEANINGS_DATA = numerologyMeanings.status === 'fulfilled' ? numerologyMeanings.value : null;
        if (numerologyMeanings.status === 'rejected') console.error("Failed to load numerology meanings:", numerologyMeanings.reason);

        globalState.ALL_HOUSE_SYSTEM_DATA = houseSystems.status === 'fulfilled' ? houseSystems.value : null;
        if (houseSystems.status === 'rejected') console.error("Failed to load house systems:", houseSystems.reason);

        globalState.ALL_ASPECT_DATA = aspects.status === 'fulfilled' ? aspects.value : null;
        if (aspects.status === 'rejected') console.error("Failed to load aspect data:", aspects.reason);

        globalState.ALL_DIGNITY_INTERPRETATIONS = dignityInterpretations.status === 'fulfilled' ? dignityInterpretations.value : null;
        if (dignityInterpretations.status === 'rejected') console.error("Failed to load dignity interpretations:", dignityInterpretations.reason);

        globalState.ALL_POF_INTERPRETATIONS = pofInterpretations.status === 'fulfilled' ? pofInterpretations.value : null;
        if (pofInterpretations.status === 'rejected') console.error("Failed to load PoF interpretations:", pofInterpretations.reason);

        globalState.ALL_HOROSCOPE_INTERPRETATIONS = horoscopeInterpretations.status === 'fulfilled' ? horoscopeInterpretations.value : null;
        if (horoscopeInterpretations.status === 'rejected') console.error("Failed to load horoscope interpretations:", horoscopeInterpretations.reason);

        // --- ASSIGN NEWLY ADDED DATA TO GLOBAL STATE ---
        globalState.planetaryHoursData = planetaryHours.status === 'fulfilled' ? planetaryHours.value : null;
        if (planetaryHours.status === 'rejected') console.error("Failed to load planetary hours:", planetaryHours.reason);

        globalState.fixedStarsData = fixedStars.status === 'fulfilled' ? fixedStars.value : null;
        if (fixedStars.status === 'rejected') console.error("Failed to load fixed stars:", fixedStars.reason);

        globalState.midpointsData = midpoints.status === 'fulfilled' ? midpoints.value : null;
        if (midpoints.status === 'rejected') console.error("Failed to load midpoints:", midpoints.reason);

        globalState.lunarMansionsData = lunarMansions.status === 'fulfilled' ? lunarMansions.value : null;
        if (lunarMansions.status === 'rejected') console.error("Failed to load lunar mansions:", lunarMansions.reason);

        globalState.antisciaData = antiscia.status === 'fulfilled' ? antiscia.value : null;
        if (antiscia.status === 'rejected') console.error("Failed to load antiscia:", antiscia.reason);

        globalState.declinationData = declination.status === 'fulfilled' ? declination.value : null;
        if (declination.status === 'rejected') console.error("Failed to load declination:", declination.reason);

        globalState.heliacalData = heliacal.status === 'fulfilled' ? heliacal.value : null;
        if (heliacal.status === 'rejected') console.error("Failed to load heliacal:", heliacal.reason);

        globalState.personalSkyData = personalSkyData.status === 'fulfilled' ? personalSkyData.value : null;
        if (personalSkyData.status === 'rejected') console.error("Failed to load personal sky data:", personalSkyData.reason);

        globalState.yearAheadData = yearAheadForecast.status === 'fulfilled' ? yearAheadForecast.value : null;
        if (yearAheadForecast.status === 'rejected') console.error("Failed to load year ahead forecast:", yearAheadForecast.reason);


        console.log("Initial content data load attempt complete. Check individual console logs for failed data types.");

        // UI population functions should be robust against null/empty data in globalState
        populateZodiacSelectorUI();
        populateSignSelectors();
        setupTarotReadingUI();
        populateDreamSymbolGridUI();
        updatePlanetTrackerUI();
        updateChakraInfoUI();
        updateRitualsUI();
        generateAffirmationUI();
        populateMantraListUI();

        // Dynamically call these functions if they are defined globally or imported elsewhere.
        // It's assumed these are either global or part of other modules that get loaded.
        // These can be removed from here if script.js takes over direct calls.
        // Keeping for now if uiUpdate.js has its own internal triggers for them.
        if (typeof updateCombinationUI === 'function') updateCombinationUI();
        if (typeof updateCompatibilityUI === 'function') updateCompatibilityUI();
        if (typeof updateMoonSunAnalysisUI === 'function') updateMoonSunAnalysisUI();
        if (typeof populateKnowledgeUI === 'function') populateKnowledgeUI();

        // After initial load, if a user is logged in, attempt to prefill relevant forms
        if (currentUser) {
            prefillAndCalculateNumerology(currentUser);
            loadSavedTarotReadingsUI();
            loadUserJournalEntriesUI();
            loadSavedNumerologyReportsUI();
        }

    } catch (error) {
        console.error("An unexpected error occurred during initial content data loading:", error);
        // Using `displayError` from uiUpdate.js itself for consistency
        displayError("Failed to load essential cosmic data. Some features may not work correctly. Please try refreshing the page.");
    }
}


// --- Daily Horoscope Tab UI ---
export async function displayDailyHoroscopeUI(signKey) { // Export displayDailyHoroscopeUI
    const dailyInsightContainer = document.getElementById('dailyInsight');
    if (!dailyInsightContainer) { console.error("dailyInsight container not found"); return; }

    if (!globalState.ALL_ZODIAC_SIGNS_DATA) {
        dailyInsightContainer.innerHTML = "<p>Zodiac data not available yet. Please wait for initial load.</p>";
        return;
    }
    const signData = globalState.ALL_ZODIAC_SIGNS_DATA[signKey];

    if (!signData) {
        dailyInsightContainer.innerHTML = `<p>Details for sign '${signKey}' not found.</p>`;
        return;
    }

    dailyInsightContainer.innerHTML = `<h3>${signData.symbol || '?'} ${signData.name} - Daily Horoscope</h3><p>Summoning today's cosmic forecast...</p>`;

    try {
        const result = await apiService.fetchDailyHoroscope(signKey);

        if (result.error) {
            throw new Error(result.error);
        }

        let sectionsHTML = "";
        if (result.sections && Array.isArray(result.sections)) {
            sectionsHTML = result.sections.map(section => `
                <div style="margin-top:10px;">
                    <h4>${section.title}</h4>
                    <p>${section.content ? section.content.replace(/\n/g, '<br>') : 'Content not available.'}</p>
                </div>
            `).join('');
        } else if (result.horoscope_text) {
             sectionsHTML = `<p>${result.horoscope_text.replace(/\n/g, '<br>')}</p>`;
        } else {
            sectionsHTML = "<p>Detailed forecast sections are currently unavailable.</p>";
        }

        dailyInsightContainer.innerHTML = `
            <h3>${result.sign_symbol || signData.symbol} ${result.sign_name || signData.name} - Daily Horoscope</h3>
            <p><strong>Date:</strong> ${result.date || new Date().toLocaleDateString()}</p>
            <div class="interpretation">
                <p><strong>Overview:</strong> ${result.overview || 'General cosmic energies are at play today. Stay mindful and open to opportunities.'}</p>
                ${sectionsHTML}
            </div>
            <div style="margin-top: 15px; background: rgba(0,0,0,0.1); padding:10px; border-radius: 5px;">
                <p><strong>Element:</strong> ${signData.element} | <strong>Quality:</strong> ${signData.quality} | <strong>Ruler:</strong> ${signData.ruler}</p>
                <p><strong>Mantra for ${signData.name}:</strong> "${result.affirmation || signData.mantra || 'Embrace your inner strength today.'}"</p>
            </div>`;
    } catch (error) {
        console.error(`Error fetching/displaying daily horoscope for ${signKey}:`, error);
        dailyInsightContainer.innerHTML = `<h3>${signData.symbol || '?'} ${signData.name} - Daily Horoscope</h3><p>Could not load today's horoscope: ${error.message}. Please try again later.</p>`;
    }
}

// --- Calendar Tab UI ---
export async function updateMoonPhaseDisplayUI() { // Export updateMoonPhaseDisplayUI
    const moonPhaseTextEl = document.getElementById('moonPhaseText');
    const moonInfluenceEl = document.getElementById('moonInfluence');
    const moonVisualEl = document.getElementById('moonPhaseVisual');
    if (!moonPhaseTextEl || !moonInfluenceEl || !moonVisualEl) return;

    moonPhaseTextEl.textContent = "Loading moon phase...";
    moonInfluenceEl.textContent = "";

    try {
        const dateToFetch = globalState.selectedCalendarDate; // Use from globalState
        const moonDetails = await apiService.fetchMoonDetails(dateToFetch.toISOString().split('T')[0]);


        if (moonDetails && !moonDetails.error) {
            const moonSignName = moonDetails.moon_sign && moonDetails.moon_sign.name ? ` • Moon in ${moonDetails.moon_sign.name}` : '';
            moonPhaseTextEl.textContent = `${moonDetails.phase_name} (${moonDetails.illumination_percent}% illuminated)${moonSignName}`;
            moonInfluenceEl.textContent = moonDetails.influence_text || "General lunar energies are at play.";

            const phaseName = moonDetails.phase_name;
            const illumination = parseFloat(moonDetails.illumination_percent);

            if (phaseName === "New Moon") {
                moonVisualEl.style.background = '#333333';
                moonVisualEl.style.boxShadow = 'inset -5px 0px 10px rgba(0,0,0,0.2)';
            } else if (phaseName === "Full Moon") {
                moonVisualEl.style.background = '#f0f0f0';
                moonVisualEl.style.boxShadow = 'inset 0px 0px 10px rgba(0,0,0,0.1)';
            } else if (phaseName && phaseName.includes("Waxing")) {
                 moonVisualEl.style.background = `linear-gradient(to left, #f0f0f0 ${illumination}%, #333333 ${illumination}%)`;
                 moonVisualEl.style.boxShadow = `inset ${-5 + (illumination/20)}px 0px 10px rgba(0,0,0,0.3)`;
            } else { // Waning or other
                 moonVisualEl.style.background = `linear-gradient(to right, #f0f0f0 ${illumination}%, #333333 ${illumination}%)`;
                 moonVisualEl.style.boxShadow = `inset ${5 - (illumination/20)}px 0px 10px rgba(0,0,0,0.3)`;
            }
        } else {
            moonPhaseTextEl.textContent = `Error: ${moonDetails?.error || 'Could not load moon phase.'}`;
        }
    } catch (error) {
        console.error("Error updating moon phase display:", error);
        moonPhaseTextEl.textContent = "Error loading moon phase.";
        moonInfluenceEl.textContent = `Details: ${error.message}`;
    }
}


// --- Knowledge Tab UI ---
export function populateKnowledgeUI() { // Export populateKnowledgeUI
    const container = document.getElementById('knowledgeContent');
    if (!container) return;
    if (!globalState.ALL_ZODIAC_SIGNS_DATA) {
        container.innerHTML = "<p>Zodiac knowledge data not available. Please try refreshing.</p>";
        return;
    }
    container.innerHTML = '';

    Object.values(globalState.ALL_ZODIAC_SIGNS_DATA).forEach(sign => {
        if (!sign || !sign.name) return;
        const signDiv = document.createElement('div');
        signDiv.className = 'knowledge-section';
        const keywordsString = `${sign.name} ${sign.element || ''} ${sign.quality || ''} ${sign.ruler || ''} ${(sign.keywords || []).join(' ')} ${(sign.strengths || []).join(' ')} ${(sign.weaknesses || []).join(' ')} ${(sign.description || "").substring(0,150)}`;
        signDiv.setAttribute('data-keywords', keywordsString.toLowerCase());
        signDiv.innerHTML = `
            <h3 class="knowledge-title">${sign.symbol || '?'} ${sign.name} (${sign.dates || 'N/A'})</h3>
            <div class="element-card">
                <p><strong>Element:</strong> ${sign.element || 'N/A'}</p><p><strong>Quality (Modality):</strong> ${sign.quality || 'N/A'}</p>
                <p><strong>Ruling Planet:</strong> ${sign.ruler || 'N/A'}</p><p><strong>Keywords:</strong> ${(sign.keywords || ['General traits']).join(', ')}</p>
            </div>
            <div class="interpretation" style="margin-top:15px;">
                <h4>Detailed Description:</h4><p>${sign.description || 'No detailed description available.'}</p><h4>Strengths:</h4><p>${(sign.strengths || ['Many hidden talents']).join(', ')}.</p>
                <h4>Weaknesses (Areas for Awareness & Growth):</h4><p>${(sign.weaknesses || ['Opportunities for growth']).join(', ')}.</p>
                <h4>Harmonizing Crystals:</h4><p>${(sign.crystals || ['Clear Quartz, Amethyst']).join(', ')}.</p><h4>Affirmation/Mantra:</h4><p>"<em>${sign.mantra || `I embrace the energy of ${sign.name}.`}</em>"</p>
            </div>`;
        container.appendChild(signDiv);
    });
}

// --- Tarot Tab UI ---
export function setupTarotReadingUI() { // Export setupTarotReadingUI
    const interpretationContainer = document.getElementById('tarotInterpretation');
    const cardsContainer = document.getElementById('tarotCards');
    const saveButton = document.getElementById('saveTarotReadingBtn');

    if (!interpretationContainer || !cardsContainer || !globalState.ALL_TAROT_DECK_DATA || !globalState.ALL_TAROT_DECK_DATA.major_arcana) {
        console.warn("Tarot UI elements or deck data not ready. Displaying fallback message.");
        if (interpretationContainer) interpretationContainer.innerHTML = "<p>Tarot data not loaded. Please try reloading.</p>";
        return;
    }

    interpretationContainer.innerHTML = '<p>Select a reading type, optionally enter a question, then click "Draw Cards" to reveal your divine guidance.</p>';
    cardsContainer.innerHTML = '';
    if(saveButton) saveButton.style.display = 'none';

    let drawButton = document.getElementById('drawTarotBtnActual');
    if (!drawButton) {
        drawButton = document.createElement('button');
        drawButton.id = 'drawTarotBtnActual';
        drawButton.textContent = 'Draw Cards';
        drawButton.className = 'tab-button';
        drawButton.style.display = 'block';
        drawButton.style.margin = '15px auto';

        const tarotSpreadSelect = document.getElementById('tarotSpread');
        // Ensure parentElement and its parent exist before trying to insert
        if (tarotSpreadSelect && tarotSpreadSelect.parentElement && tarotSpreadSelect.parentElement.parentElement) {
             tarotSpreadSelect.parentElement.parentElement.insertAdjacentElement('afterend', drawButton);
        } else if (cardsContainer.parentElement) { // Fallback insertion
             cardsContainer.parentElement.insertBefore(drawButton, cardsContainer);
        } else {
            console.warn("Could not find a suitable place to insert the Draw Cards button for Tarot. UI might be incomplete.");
        }
    }
    drawButton.onclick = handleDrawTarotReading;
}

async function handleDrawTarotReading() {
    const spreadType = document.getElementById('tarotSpread')?.value || 'single';
    const cardsContainer = document.getElementById('tarotCards');
    const interpretationContainer = document.getElementById('tarotInterpretation');
    const saveButton = document.getElementById('saveTarotReadingBtn');

    if (!cardsContainer || !interpretationContainer) {
        console.error("Tarot UI containers not found for drawing cards.");
        return;
    }

    cardsContainer.innerHTML = '<p>Shuffling the cosmic deck...</p>';
    interpretationContainer.innerHTML = '';

    try {
        const readingResult = await apiService.performTarotReading(spreadType);
        if (readingResult.error) throw new Error(readingResult.error);

        cardsContainer.innerHTML = '';
        window.currentTarotReading = readingResult; // Store for saving

        interpretationContainer.innerHTML = `<p>Interpreting the <strong>${readingResult.spread_type.replace('-', ' ')}</strong> spread:</p>`;

        readingResult.cards.forEach(cardDetail => {
            const cardWrapper = document.createElement('div');
            cardWrapper.style.textAlign = 'center';
            cardWrapper.style.margin = '5px';

            const cardEl = document.createElement('div');
            cardEl.className = 'tarot-card';
            cardEl.innerHTML = `
                <div style="font-size: 0.9rem; text-align: center; padding: 5px; display: flex; flex-direction: column; justify-content: space-around; height: 100%;">
                    <div style="font-weight: bold; margin-bottom: 5px; font-size: 0.8em;">${cardDetail.card_name}</div>
                    <div style="font-size: 2.5em; margin: 5px 0;">${cardDetail.symbol}</div>
                    ${cardDetail.is_reversed ? '<div style="font-size: 0.7em; color: #ff6b6b;">(Reversed)</div>' : ''}
                </div>`;
            cardEl.style.background = 'linear-gradient(135deg, #fffacd, #ffe4b5)';
            cardEl.style.color = '#4a148c';

            const positionText = document.createElement('p');
            positionText.textContent = cardDetail.position_name;
            positionText.style.fontSize = '0.8rem';
            positionText.style.marginTop = '5px';

            cardWrapper.appendChild(cardEl);
            cardWrapper.appendChild(positionText);
            cardsContainer.appendChild(cardWrapper);

            interpretationContainer.innerHTML += `
                <div class="interpretation" style="margin-bottom: 10px; padding: 10px; background: rgba(255,255,255,0.08); border-radius: 8px;">
                    <h4>${cardDetail.position_name}: ${cardDetail.card_name} ${cardDetail.is_reversed ? '(R)' : ''} ${cardDetail.symbol}</h4>
                    <p><strong>Meaning:</strong> ${cardDetail.interpretation}</p>
                </div>`;
        });

        if (currentUser && saveButton) {
            saveButton.style.display = 'block';
            saveButton.style.marginLeft = 'auto';
            saveButton.style.marginRight = 'auto';
        }
    } catch (error) {
        console.error("Error performing tarot reading:", error);
        interpretationContainer.innerHTML = `<p>Could not perform reading: ${error.message}</p>`;
        if(saveButton) saveButton.style.display = 'none';
    }
}

export async function saveCurrentTarotReading() { // Export saveCurrentTarotReading
    if (!currentUser) {
        alert("Please login to save your tarot reading.");
        return;
    }
    if (!window.currentTarotReading || !window.currentTarotReading.cards || window.currentTarotReading.cards.length === 0) {
        alert("No reading to save. Please draw cards first.");
        return;
    }

    const question = document.getElementById('tarotQuestion')?.value || 'General Guidance';
    const userNotes = prompt("Add any personal notes or reflections for this reading (optional):", "");

    const readingToSave = {
        spread_type: window.currentTarotReading.spread_type,
        cards: window.currentTarotReading.cards, // This should match what API expects (e.g., 'cards_drawn')
        question_asked: question,
        user_notes: userNotes // This should match what API expects (e.g., 'interpretation_notes')
    };

    try {
        const result = await apiService.saveTarotReading(readingToSave);
        alert(result.message || "Reading saved successfully!");
        loadSavedTarotReadingsUI();
    } catch (error) {
        console.error("Error saving tarot reading:", error);
        alert(`Failed to save reading: ${error.message || 'Please try again.'}`);
    }
}

export async function loadSavedTarotReadingsUI() { // Export loadSavedTarotReadingsUI
    const container = document.getElementById('savedTarotReadingsContainer');
    if (!container) return;
    if (!currentUser) {
        container.innerHTML = "<h4>Your Saved Tarot Readings:</h4><p>Login to view your saved readings.</p>";
        return;
    }
    container.innerHTML = '<h4>Your Saved Tarot Readings:</h4><p>Loading readings...</p>';

    try {
        const readings = await apiService.fetchSavedTarotReadings();
        if (readings && readings.length > 0) {
            container.innerHTML = '<h4>Your Saved Tarot Readings:</h4>';
            readings.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)); // Sort newest first

            readings.forEach(reading => {
                const readingDiv = document.createElement('div');
                readingDiv.className = 'journal-entry'; // Re-using class name, ensure styles are appropriate
                let readingHTML = `<p><strong>${reading.spread_type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} - Saved: ${new Date(reading.created_at).toLocaleDateString()}</strong></p>`;
                if(reading.question_asked) readingHTML += `<p><em>Question: ${reading.question_asked}</em></p>`;

                // API might return 'cards' or 'cards_drawn'
                const cardsArray = reading.cards_drawn || reading.cards;
                if(cardsArray && Array.isArray(cardsArray)){
                    readingHTML += '<ul>';
                    cardsArray.forEach(card => {
                         readingHTML += `<li><strong>${card.position_name || 'Card'}: ${card.card_name} ${card.is_reversed ? '(R)' : ''}</strong> - ${card.interpretation ? card.interpretation.substring(0,100) + '...' : 'No interpretation provided.'}</li>`;
                    });
                    readingHTML += '</ul>';
                }
                // API might return 'user_notes' or 'interpretation_notes'
                const notes = reading.user_notes || reading.interpretation_notes;
                if(notes) readingHTML += `<p><strong>Your Notes:</strong> ${notes}</p>`;
                readingHTML += `<button onclick="deleteTarotReadingUI(${reading.id})" style="background: #c0392b; color: white; border: none; padding: 5px 10px; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 5px; font-size: 0.8em;">Delete</button>`;
                readingDiv.innerHTML = readingHTML;
                container.appendChild(readingDiv);
            });
        } else {
            container.innerHTML = '<h4>Your Saved Tarot Readings:</h4><p>No saved readings found.</p>';
        }
    } catch (error) {
        console.error("Error loading saved tarot readings:", error);
        container.innerHTML = `<h4>Your Saved Tarot Readings:</h4><p>Could not load readings: ${error.message}</p>`;
    }
}

export async function deleteTarotReadingUI(readingId) { // Export deleteTarotReadingUI
     if (!confirm('Are you sure you want to delete this tarot reading?')) return;
    try {
        const result = await apiService.deleteTarotReading(readingId);
        alert(result.message || "Reading deleted.");
        loadSavedTarotReadingsUI();
    } catch (error) {
        console.error("Error deleting tarot reading:", error);
        alert(`Failed to delete reading: ${error.message || 'Please try again.'}`);
    }
}
// Make deleteTarotReadingUI globally accessible if called from inline HTML
// This is redundant if you're using ES Modules for everything, but harmless for onclick.
window.deleteTarotReadingUI = deleteTarotReadingUI;

// --- Chakra Info UI ---
export function updateChakraInfoUI() { // Export updateChakraInfoUI
    const selectedChakraKey = document.getElementById('chakraSelect')?.value || 'root';
    const container = document.getElementById('chakraInfo');
    if (!container) { console.warn("Chakra info container 'chakraInfo' not found."); return; }
    if (!globalState.ALL_CHAKRA_DATA) {
        container.innerHTML = "<p>Chakra data is not available. Please try refreshing.</p>";
        return;
    }
    const info = globalState.ALL_CHAKRA_DATA[selectedChakraKey];

    if (info) {
        container.innerHTML = `
            <h3>${info.name} (${info.key})</h3>
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <div style="width: 50px; height: 50px; background-color: ${info.color}; border-radius: 50%; margin-right: 15px; border: 2px solid white; box-shadow: 0 0 10px ${info.color};"></div>
                <div>
                    <p><strong>Location:</strong> ${info.location}</p>
                    <p><strong>Element:</strong> ${info.element}</p>
                    <p><strong>Bija Mantra:</strong> ${info.bija_mantra}</p>
                </div>
            </div>
            <h4>Primary Focus:</h4><p>${info.primary_focus}.</p>
            <h4>Balanced Qualities:</h4><p>${(info.balanced_qualities || []).join('; ')}.</p>
            <h4>Physical Imbalance Symptoms:</h4><p>${(info.imbalanced_symptoms_physical || []).join('; ')}.</p>
            <h4>Emotional Imbalance Symptoms:</h4><p>${(info.imbalanced_symptoms_emotional || []).join('; ')}.</p>
            <h4>Healing Crystals:</h4><p>${(info.associated_crystals || []).join(', ')}.</p>
            <h4>Healing Affirmation:</h4><p><em>"${info.affirmation}"</em></p>
            <h4>Healing Practices:</h4>
            <ul>
                ${(info.healing_practices || []).map(practice => `<li>${practice}</li>`).join('')}
                <li>Connect with element: ${getChakraElementActivity(info.element)}.</li>
            </ul>`;
    } else {
        container.innerHTML = "<p>Select a chakra to learn more. Data for selected chakra not found.</p>";
    }
}

// --- Dream Symbols Grid UI ---
export function populateDreamSymbolGridUI() { // Export populateDreamSymbolGridUI
    const container = document.getElementById('dreamSymbolsGrid');
    if (!container) { console.warn("Dream symbols grid container 'dreamSymbolsGrid' not found."); return; }
    if (!globalState.ALL_DREAM_SYMBOLS_DATA) {
        container.innerHTML = '<h4>Dream symbols data not available.</h4>';
        return;
    }

    let header = container.querySelector('h4');
    if (!header) {
        header = document.createElement('h4');
        header.textContent = 'Common Dream Symbols (click to add to dream description):';
        container.innerHTML = ''; // Clear previous content if any, before adding header
        container.appendChild(header);
    } else {
        // Remove only symbol cards, not the header
        const existingSymbols = Array.from(container.querySelectorAll('.symbol-card'));
        existingSymbols.forEach(s => s.remove());
    }


    Object.keys(globalState.ALL_DREAM_SYMBOLS_DATA).sort().forEach(symbolKey => {
        const symbolData = globalState.ALL_DREAM_SYMBOLS_DATA[symbolKey];
        const card = document.createElement('div');
        card.className = 'symbol-card';
        card.textContent = symbolKey.charAt(0).toUpperCase() + symbolKey.slice(1);
        card.title = symbolData?.general_meaning || "Click to add symbol to your dream description.";
        card.onclick = () => {
            const dreamDesc = document.getElementById('dreamDescription');
            if (dreamDesc) {
                const currentText = dreamDesc.value;
                const selectionStart = dreamDesc.selectionStart || 0;
                const selectionEnd = dreamDesc.selectionEnd || 0;
                const spaceBefore = (selectionStart > 0 && currentText[selectionStart-1] !== ' ') ? ' ' : '';
                const textToInsert = spaceBefore + symbolKey + ' ';

                dreamDesc.value = currentText.substring(0, selectionStart) + textToInsert + currentText.substring(selectionEnd);
                dreamDesc.focus();
                dreamDesc.selectionStart = dreamDesc.selectionEnd = selectionStart + textToInsert.length;
            } else {
                console.warn("Dream description input 'dreamDescription' not found.");
            }
        };
        container.appendChild(card);
    });
}

// --- Calendar Events UI ---
export async function generateCosmicEventsUI() { // Export generateCosmicEventsUI
    const container = document.getElementById('cosmicEvents');
    if (!container) { console.warn("Cosmic events container 'cosmicEvents' not found."); return; }
    container.innerHTML = "<p>Loading this month's cosmic highlights...</p>";

    try {
        const today = globalState.selectedCalendarDate; // Use from globalState
        const year = today.getFullYear();
        const month = today.getMonth(); // 0-indexed
        const firstDayOfMonth = new Date(year, month, 1);
        const lastDayOfMonth = new Date(year, month + 1, 0);

        const eventsData = await apiService.getCosmicEventsForMonth(firstDayOfMonth.toISOString().split('T')[0], lastDayOfMonth.toISOString().split('T')[0]);

        if (eventsData.error) {
            throw new Error(eventsData.error);
        }

        let eventsHTML = '<ul>';
        if (eventsData && eventsData.length > 0) {
             // Filter for the current month if API returns broader results
            const relevantEvents = eventsData.filter(event => {
                const eventDate = new Date(event.date + "T00:00:00Z"); // Ensure consistent date interpretation
                return eventDate.getUTCFullYear() === year && eventDate.getUTCMonth() === month;
            });

            if (relevantEvents.length > 0) {
                relevantEvents.sort((a,b) => new Date(a.date + "T00:00:00Z") - new Date(b.date + "T00:00:00Z")).forEach(event => {
                    eventsHTML += `<li><strong>${new Date(event.date + "T00:00:00Z").toLocaleDateString([], {month: 'short', day: 'numeric', timeZone: 'UTC'})}: ${event.title}</strong> - ${event.description}</li>`;
                });
            } else {
                eventsHTML += '<li>No major cosmic events listed for this specific month.</li>';
            }
        } else {
            eventsHTML += '<li>Cosmic event data is currently unavailable or no events this month.</li>';
        }
        eventsHTML += '</ul>';
        container.innerHTML = eventsHTML;
    } catch (error) {
        console.error("Error generating cosmic events UI:", error);
        container.innerHTML = `<p>Could not load cosmic events: ${error.message}</p>`;
    }
}

// --- Zodiac Sign Selectors ---
export function populateZodiacSelectorUI() { // Export populateZodiacSelectorUI
    const selector = document.getElementById('zodiacSelector');
    if (!selector) { console.warn("Zodiac selector 'zodiacSelector' not found."); return; }
    if (!globalState.ALL_ZODIAC_SIGNS_DATA) {
        selector.innerHTML = '<option value="">Zodiac Data Error</option>';
        return;
    }
    selector.innerHTML = '<option value="">Select Your Sign</option>';
    Object.entries(globalState.ALL_ZODIAC_SIGNS_DATA).forEach(([key, sign]) => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = `${sign.symbol || '?'} ${sign.name}`;
        selector.appendChild(option);
    });
}

export function populateSignSelectors() { // Export populateSignSelectors
    const selectorIds = ['sunSign', 'moonSign', 'risingSign', 'compatSign1', 'compatSign2', 'sunAnalysis', 'moonAnalysis', 'crystalSign', 'ritualSign'];
    if (!globalState.ALL_ZODIAC_SIGNS_DATA) {
        console.warn("Zodiac data not loaded for populating general sign selectors.");
        selectorIds.forEach(id => {
            const selectEl = document.getElementById(id);
            if (selectEl) selectEl.innerHTML = '<option value="">Zodiac Data Loading Error</option>';
        });
        return;
    }

    selectorIds.forEach(id => {
        const selectEl = document.getElementById(id);
        if (selectEl) {
            const currentValue = selectEl.value; // Preserve selection if already made
            selectEl.innerHTML = '<option value="">Select Sign</option>';
            Object.entries(globalState.ALL_ZODIAC_SIGNS_DATA).forEach(([key, sign]) => {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = `${sign.symbol || '?'} ${sign.name}`;
                selectEl.appendChild(option);
            });
            // Restore previous selection if it's still a valid option
            if(currentValue && Array.from(selectEl.options).some(opt => opt.value === currentValue)) {
                 selectEl.value = currentValue;
            }
        } else {
            console.warn(`Sign selector with ID '${id}' not found.`);
        }
    });
}

// --- Birth Chart UI ---
function getElementColor(element) {
    if (!element) return '#CCCCCC'; // Default color if element is undefined
    switch (element.toLowerCase()) {
        case 'fire': return '#FF4500';
        case 'earth': return '#228B22';
        case 'air': return '#87CEEB';
        case 'water': return '#1E90FF';
        default: return '#CCCCCC';
    }
}

export function renderNatalChartInputForm() { // Export renderNatalChartInputForm
    const analysisContainer = document.getElementById('birthChartAnalysis');
    const wheelContainer = document.getElementById('birthChartWheel');
    if (!analysisContainer || !wheelContainer) { console.warn("Birth chart UI containers not found."); return; }

    analysisContainer.innerHTML = `
        <h3>Generate Your Natal Chart</h3>
        <p>To see your unique cosmic blueprint, please enter your birth details.</p>
        <form id="natal-chart-form">
            <label for="birth-datetime">Date & Time of Birth (UTC):</label>
            <input type="datetime-local" id="birth-datetime" required><br>
            <label for="birth-latitude">Latitude:</label>
            <input type="number" id="birth-latitude" placeholder="e.g., 42.3601" step="0.0001" required><br>
            <label for="birth-longitude">Longitude:</label>
            <input type="number" id="birth-longitude" placeholder="e.g., -71.0589" step="0.0001" required><br>
            <label for="birth-timezone">Timezone (e.g., America/Los_Angeles):</label>
            <input type="text" id="birth-timezone" placeholder="America/New_York" required><br>
            <label for="house-system">House System:</label>
            <select id="house-system">
                <option value="Placidus">Placidus</option>
                <option value="Koch">Koch</option>
                <option value="Whole Sign">Whole Sign</option>
                <option value="Equal House">Equal House</option>
            </select><br>
            <button type="submit">Generate Chart</button>
        </form>
    `;
    wheelContainer.innerHTML = ''; // Clear previous wheel

    // Prefill with user data if available
    if (currentUser && currentUser.birth_data) {
        const { birth_datetime_utc, birth_location } = currentUser.birth_data;
        if (birth_datetime_utc) {
            // Convert UTC ISO string to local datetime-local format
            const dt = new Date(birth_datetime_utc);
            const localIso = new Date(dt.getTime() - (dt.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
            document.getElementById('birth-datetime').value = localIso;
        }
        if (birth_location) {
            document.getElementById('birth-latitude').value = birth_location.latitude;
            document.getElementById('birth-longitude').value = birth_location.longitude;
            document.getElementById('birth-timezone').value = birth_location.timezone_str || '';
        }
    }


    document.getElementById('natal-chart-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const datetimeLocal = document.getElementById('birth-datetime').value;
        const latitude = document.getElementById('birth-latitude').value;
        const longitude = document.getElementById('birth-longitude').value;
        const timezone = document.getElementById('birth-timezone').value;
        const houseSystem = document.getElementById('house-system').value;

        if (!datetimeLocal || !latitude || !longitude || !timezone) {
            alert('Please fill in all birth details.');
            return;
        }

        // Convert datetime-local string to UTC for API (assuming API expects UTC)
        const datetimeUTC = new Date(datetimeLocal).toISOString();

        analysisContainer.innerHTML = '<p>Calculating your Natal Chart...</p>';
        wheelContainer.innerHTML = '';

        try {
            // Call an API to get chart data (this is a placeholder for your actual API call)
            const chartData = await apiService.getCurrentTransitsForDaily(
                parseFloat(latitude),
                parseFloat(longitude),
                datetimeUTC,
                timezone, // Pass timezone string
                houseSystem
            );
            globalState.natalChartData = chartData; // Store the chart data in globalState for re-rendering
            displayBirthChartUI(chartData); // Render the chart
        } catch (error) {
            console.error("Error generating natal chart:", error);
            analysisContainer.innerHTML = `<p>Error generating chart: ${error.message}. Please check your inputs.</p>`;
        }
    });
}


export async function displayBirthChartUI(chartData) { // Export displayBirthChartUI
    const analysisContainer = document.getElementById('birthChartAnalysis');
    const wheelContainer = document.getElementById('birthChartWheel');
    if (!analysisContainer || !wheelContainer) { console.warn("Birth chart UI containers not found."); return; }

    if (chartData && chartData.error) {
        analysisContainer.innerHTML = `<p>Error generating chart: ${chartData.error}</p>`;
        wheelContainer.innerHTML = '';
        return;
    }
    if (!chartData || !chartData.points || !chartData.angles || !chartData.house_cusps) {
        analysisContainer.innerHTML = "<p>Natal chart data is incomplete. Please ensure all birth details are correct and try again.</p>";
        wheelContainer.innerHTML = '';
        return;
    }

    let analysisHTML = `<h3>Your Cosmic Blueprint</h3>`;
    if (chartData.chart_info) {
        analysisHTML += `<p><strong>Chart Calculated for:</strong> ${new Date(chartData.chart_info.datetime_utc).toLocaleString()} UTC</p>`;
        analysisHTML += `<p><strong>Location:</strong> Lat ${parseFloat(chartData.chart_info.latitude).toFixed(4)}, Lon ${parseFloat(chartData.chart_info.longitude).toFixed(4)}</p>`;
        analysisHTML += `<p><strong>House System:</strong> ${chartData.chart_info.house_system}</p>`;
    }


    analysisHTML += `<h4>Key Angles:</h4><ul>`;
    Object.values(chartData.angles).forEach(angle => {
        if (angle.error) return; // Skip if angle data has an error
        analysisHTML += `<li><strong>${angle.name} (${angle.symbol || 'Angle'}):</strong> ${angle.display_dms || angle.display_short || 'N/A'} (House ${angle.house || 'N/A'})</li>`;
    });
    analysisHTML += `</ul>`;

    analysisHTML += `<h4>Planetary Positions:</h4><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 10px;">`;
    Object.values(chartData.points).forEach(point => {
        if (point.error) return; // Skip if point data has an error
        const dignityText = point.dignities?.status && point.dignities.status !== 'N/A' && point.dignities.status !== 'Peregrine' ? ` (${point.dignities.status})` : '';
        analysisHTML += `<div class="planet-item" style="text-align:left; padding:8px; font-size:0.9em;">
                            <strong>${point.symbol || '?'} ${point.name}${point.is_retrograde ? ' (R)' : ''}:</strong> ${point.display_dms || point.display_short || 'N/A'} <br/>
                            In House ${point.house || 'N/A'}${dignityText}
                         </div>`;
    });
    analysisHTML += `</div>`;

    if (chartData.part_of_fortune && !chartData.part_of_fortune.error) {
        const pof = chartData.part_of_fortune;
        analysisHTML += `<h4 style="margin-top:15px;">Part of Fortune (${pof.symbol || '⊗'}):</h4>
                         <p>${pof.display_dms || pof.display_short || 'N/A'} in House ${pof.house || 'N/A'}</p>
                         <p><em>${pof.sign_interpretation || ''} ${pof.house_interpretation || ''}</em></p>`;
    }

    analysisHTML += `<h4 style="margin-top:15px;">House Cusps:</h4><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; font-size:0.85em;">`;
    for (let i = 1; i <= 12; i++) {
        const cusp = chartData.house_cusps[i];
        if (cusp && !cusp.error) { // Check for cusp data and no error
            analysisHTML += `<div style="background:rgba(0,0,0,0.1); padding:5px; border-radius:4px;"><strong>H${i}:</strong> ${cusp.display_dms || cusp.display_short || 'N/A'}</div>`;
        }
    }
    analysisHTML += `</div>`;

    if (chartData.aspects && chartData.aspects.length > 0) {
        analysisHTML += `<h4 style="margin-top:15px;">Key Aspects (Major Orb < 6°, Minor Orb < 2°):</h4><ul>`;
        chartData.aspects
            .filter(asp => asp && !asp.error && ((asp.aspect_type_category === 'major' && asp.orb_degrees < 6) || (asp.aspect_type_category === 'minor' && asp.orb_degrees < 2)))
            .slice(0, 15) // Limit displayed aspects
            .forEach(aspect => {
            analysisHTML += `<li>${aspect.point1_symbol || '?'} ${aspect.point1_name} ${aspect.aspect_symbol || ''} ${aspect.point2_symbol || '?'} ${aspect.point2_name} (Orb: ${aspect.orb_degrees.toFixed(1)}°)</li>`;
        });
        analysisHTML += `</ul>`;
    }

    analysisContainer.innerHTML = analysisHTML;
    drawBirthChartWheel(chartData);
}

export function drawBirthChartWheel(chartData) { // Export drawBirthChartWheel
    const wheel = document.getElementById('birthChartWheel');
    if (!wheel) { console.warn("Birth chart wheel container 'birthChartWheel' not found."); return; }
    wheel.innerHTML = ''; // Clear previous wheel
    let size = Math.min(wheel.clientWidth, wheel.clientHeight);
    if (size === 0) {
        const tempParent = wheel.parentElement;
        size = (tempParent ? Math.min(tempParent.clientWidth, 300) : 300) || 300; // Ensure size is not 0
    }
    wheel.style.width = `${size}px`;
    wheel.style.height = `${size}px`;

    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute('width', size);
    svg.setAttribute('height', size);
    svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
    svg.style.backgroundColor = 'rgba(0,0,0,0.1)';
    svg.style.borderRadius = '50%';
    wheel.appendChild(svg);

    const center = size / 2;
    const zodiacOuterRadius = size * 0.475; // size / 2 * 0.95
    const zodiacInnerRadius = size * 0.375; // size / 2 * 0.75
    const houseNumberRadius = (zodiacOuterRadius + zodiacInnerRadius) * 0.45; // (zodiacOuterRadius + zodiacInnerRadius) / 2 * 0.9
    const planetBandOuterRadius = zodiacInnerRadius * 0.95;
    const planetBandInnerRadius = zodiacInnerRadius * 0.4;

    const ascendantLon = chartData.angles?.Ascendant?.longitude;
    if (typeof ascendantLon !== 'number') {
        svg.innerHTML = '<text x="50%" y="50%" text-anchor="middle" fill="white">Ascendant data missing for wheel.</text>';
        return;
    }


    // Draw Zodiac Signs Ring
    if (globalState.ALL_ZODIAC_SIGNS_DATA) {
        const zodiacKeys = Object.keys(globalState.ALL_ZODIAC_SIGNS_DATA);
        zodiacKeys.forEach((signKey, index) => {
            const signData = globalState.ALL_ZODIAC_SIGNS_DATA[signKey];
            if(!signData) return;

            const signStartDegrees = index * 30;
            const signEndDegrees = (index + 1) * 30;

            const startAngleRad = (signStartDegrees - ascendantLon + 180) * Math.PI / 180;
            const endAngleRad = (signEndDegrees - ascendantLon + 180) * Math.PI / 180;

            const xOuterStart = center + zodiacOuterRadius * Math.cos(startAngleRad);
            const yOuterStart = center + zodiacOuterRadius * Math.sin(startAngleRad);
            const xOuterEnd = center + zodiacOuterRadius * Math.cos(endAngleRad);
            const yOuterEnd = center + zodiacOuterRadius * Math.sin(endAngleRad);
            const xInnerStart = center + zodiacInnerRadius * Math.cos(startAngleRad);
            const yInnerStart = center + zodiacInnerRadius * Math.sin(startAngleRad);
            const xInnerEnd = center + zodiacInnerRadius * Math.cos(endAngleRad);
            const yInnerEnd = center + zodiacInnerRadius * Math.sin(endAngleRad);

            const path = document.createElementNS(svgNS, "path");
            const largeArcFlag = (signEndDegrees - signStartDegrees) <= 180 ? "0" : "1";
            const d = `M ${xInnerStart} ${yInnerStart}
                       L ${xOuterStart} ${yOuterStart}
                       A ${zodiacOuterRadius} ${zodiacOuterRadius} 0 ${largeArcFlag} 1 ${xOuterEnd} ${yOuterEnd}
                       L ${xInnerEnd} ${yInnerEnd}
                       A ${zodiacInnerRadius} ${zodiacInnerRadius} 0 ${largeArcFlag} 0 ${xInnerStart} ${yInnerStart} Z`;
            path.setAttribute("d", d);
            path.setAttribute("fill", getElementColor(signData.element) + "40");
            path.setAttribute("stroke", "rgba(255,255,255,0.4)");
            path.setAttribute("stroke-width", "0.75");
            svg.appendChild(path);

            const symbolAngleRad = (signStartDegrees + 15 - ascendantLon + 180) * Math.PI / 180; // Midpoint of the sign
            const symbolX = center + ((zodiacOuterRadius + zodiacInnerRadius) / 2) * Math.cos(symbolAngleRad);
            const symbolY = center + ((zodiacOuterRadius + zodiacInnerRadius) / 2) * Math.sin(symbolAngleRad);
            const textSymbol = document.createElementNS(svgNS, "text");
            textSymbol.setAttribute("x", symbolX);
            textSymbol.setAttribute("y", symbolY);
            textSymbol.setAttribute("dy", "0.35em");
            textSymbol.setAttribute("fill", getElementColor(signData.element));
            textSymbol.setAttribute("font-size", `${Math.max(10, size * 0.04)}px`);
            textSymbol.setAttribute("font-family", "Arial, sans-serif");
            textSymbol.setAttribute("text-anchor", "middle");
            textSymbol.textContent = signData.symbol || '?';
            svg.appendChild(textSymbol);
        });
    }

    // Draw House Cusp Lines & Numbers
    for (let i = 1; i <= 12; i++) {
        const cuspData = chartData.house_cusps?.[i];
        if (!cuspData || cuspData.error || typeof cuspData.longitude !== 'number') continue;
        const cuspLon = cuspData.longitude;
        const lineAngleRad = (cuspLon - ascendantLon + 180) * Math.PI / 180;

        const line = document.createElementNS(svgNS, "line");
        line.setAttribute("x1", center);
        line.setAttribute("y1", center);
        line.setAttribute("x2", center + zodiacInnerRadius * Math.cos(lineAngleRad));
        line.setAttribute("y2", center + zodiacInnerRadius * Math.sin(lineAngleRad));
        line.setAttribute("stroke", "rgba(255, 215, 0, 0.6)"); // Gold-like color for house lines
        line.setAttribute("stroke-width", (i === 1 || i === 4 || i === 7 || i === 10) ? "1.5" : "0.75"); // Thicker for angular houses
        svg.appendChild(line);

        const nextCuspIndex = (i % 12) + 1;
        const nextCuspData = chartData.house_cusps?.[nextCuspIndex];
        if(!nextCuspData || nextCuspData.error || typeof nextCuspData.longitude !== 'number') continue;

        let midHouseLon = (cuspLon + nextCuspData.longitude) / 2;
        // Handle wrap-around for average longitude (e.g. house spanning 0 Aries)
        if (Math.abs(cuspLon - nextCuspData.longitude) > 180) {
            midHouseLon = ((cuspLon + nextCuspData.longitude + 360) / 2) % 360;
        }
        const numberAngleRad = (midHouseLon - ascendantLon + 180) * Math.PI / 180;
        const numX = center + houseNumberRadius * Math.cos(numberAngleRad);
        const numY = center + houseNumberRadius * Math.sin(numberAngleRad);
        const houseNumText = document.createElementNS(svgNS, "text");
        houseNumText.setAttribute("x", numX);
        houseNumText.setAttribute("y", numY);
        houseNumText.setAttribute("dy", "0.35em");
        houseNumText.setAttribute("fill", "rgba(255,255,255,0.8)");
        houseNumText.setAttribute("font-size", `${Math.max(8, size * 0.03)}px`);
        houseNumText.setAttribute("font-family", "Arial, sans-serif");
        houseNumText.setAttribute("text-anchor", "middle");
        houseNumText.textContent = i;
        svg.appendChild(houseNumText);
    }

    // Draw Planets
    const planetPoints = Object.values(chartData.points || {}).filter(p => p && !p.error && typeof p.longitude === 'number');
    planetPoints.forEach((point, index) => {
        const pointLon = point.longitude;
        const planetAngleRad = (pointLon - ascendantLon + 180) * Math.PI / 180;
        const orbitRadius = planetBandInnerRadius + ((planetBandOuterRadius - planetBandInnerRadius) * ((index % 5) / 4.5)); // Slightly adjust staggering

        const planetX = center + orbitRadius * Math.cos(planetAngleRad);
        const planetY = center + orbitRadius * Math.sin(planetAngleRad);

        const planetText = document.createElementNS(svgNS, "text");
        planetText.setAttribute("x", planetX);
        planetText.setAttribute("y", planetY);
        planetText.setAttribute("dy", "0.35em");
        const signKeyForPlanet = point.sign_key;
        const planetSignElement = globalState.ALL_ZODIAC_SIGNS_DATA?.[signKeyForPlanet]?.element;
        planetText.setAttribute("fill", getElementColor(planetSignElement) || "#FFF");
        planetText.setAttribute("font-size", `${Math.max(9, size * 0.035)}px`);
        planetText.setAttribute("font-family", "Arial, sans-serif");
        planetText.setAttribute("text-anchor", "middle");
        const degreeInSign = Math.floor(point.degrees_in_sign || 0);
        planetText.textContent = `${point.symbol || '?'}${degreeInSign}°${point.is_retrograde ? 'R' : ''}`;
        planetText.setAttribute("title", `${point.name} at ${point.display_dms || point.display_short} in House ${point.house}`);
        svg.appendChild(planetText);
    });

    // Ascendant Label
    const ascLabel = document.createElementNS(svgNS, "text");
    ascLabel.setAttribute("x", center - zodiacInnerRadius * 1.08); // Position outside wheel, near 9 o'clock
    ascLabel.setAttribute("y", center);
    ascLabel.setAttribute("dy", "0.35em");
    ascLabel.setAttribute("fill", "#FFD700");
    ascLabel.setAttribute("font-size", `${Math.max(9, size * 0.035)}px`);
    ascLabel.setAttribute("font-family", "Arial, sans-serif");
    ascLabel.setAttribute("font-weight", "bold");
    ascLabel.setAttribute("text-anchor", "end");
    ascLabel.textContent = "AS";
    svg.appendChild(ascLabel);

    // Midheaven Label
    const mcLon = chartData.angles?.Midheaven?.longitude;
    if (typeof mcLon === 'number') {
        const mcAngleRad = (mcLon - ascendantLon + 180) * Math.PI / 180;
        const mcX = center + zodiacInnerRadius * 1.08 * Math.cos(mcAngleRad);
        const mcY = center + zodiacInnerRadius * 1.08 * Math.sin(mcAngleRad);
        const mcLabel = document.createElementNS(svgNS, "text");
        mcLabel.setAttribute("x", mcX);
        mcLabel.setAttribute("y", mcY);

        // Adjust anchor and dy for MC label based on its position
        if (Math.sin(mcAngleRad) < -0.8) { // Near top
            mcLabel.setAttribute("dy", "1.2em"); // Below point
            mcLabel.setAttribute("text-anchor", "middle");
        } else if (Math.sin(mcAngleRad) > 0.8) { // Near bottom
            mcLabel.setAttribute("dy", "-0.5em"); // Above point
            mcLabel.setAttribute("text-anchor", "middle");
        } else { // General case
            mcLabel.setAttribute("text-anchor", "middle");
            mcLabel.setAttribute("dy", "0.35em");
        }

        mcLabel.setAttribute("fill", "#FFAA00"); // Different color for MC
        mcLabel.setAttribute("font-size", `${Math.max(9, size * 0.035)}px`);
        mcLabel.setAttribute("font-family", "Arial, sans-serif");
        mcLabel.setAttribute("font-weight", "bold");
        mcLabel.textContent = "MC";
        svg.appendChild(mcLabel);
    }
}

// --- ADDED: Planetary Hours UI ---
export async function renderPlanetaryHoursUI() { // Export renderPlanetaryHoursUI
    const container = document.getElementById('planetaryHoursContent');
    if (!container) { console.warn("Planetary Hours container 'planetaryHoursContent' not found."); return; }
    container.innerHTML = "<p>Calculating current Planetary Hour...</p>";

    try {
        const data = await apiService.fetchPlanetaryHours();
        if (data.error) throw new Error(data.error);

        globalState.planetaryHoursData = data; // Store in global state

        container.innerHTML = `
            <h3>Planetary Hours</h3>
            <p>Current Time (Local): ${new Date().toLocaleTimeString()}</p>
            <p><strong>Current Planetary Hour:</strong> ${data.currentHour || 'N/A'}</p>
            <p><strong>Influence:</strong> ${data.interpretation || 'No specific interpretation available.'}</p>
            <p style="margin-top: 15px;">Planetary hours are ancient astrological divisions of time where each hour of the day is ruled by a different planet, influencing the energy and suitability for various activities.</p>
        `;
    } catch (error) {
        console.error("Error fetching planetary hours:", error);
        container.innerHTML = `<p>Could not load planetary hours: ${error.message}</p>`;
    }
}

// --- ADDED: Dignities UI ---
export async function renderDignitiesUI() { // Export renderDignitiesUI
    const container = document.getElementById('dignitiesContent');
    if (!container) { console.warn("Dignities container 'dignitiesContent' not found."); return; }
    container.innerHTML = "<p>Loading Planetary Dignities data...</p>";

    try {
        // Assuming dignities are typically calculated as part of a natal chart or transits.
        // For a standalone dignities view, you might need a different API call or use pre-loaded interpretations.
        const data = globalState.ALL_DIGNITY_INTERPRETATIONS; // Use pre-loaded interpretations
        if (!data) {
            const fetchedData = await apiService.fetchDignityInterpretations();
            if (fetchedData.error) throw new Error(fetchedData.error);
            globalState.ALL_DIGNITY_INTERPRETATIONS = fetchedData;
        }

        let dignitiesHTML = `<h3>Planetary Dignities (General)</h3>
                             <p>Planetary dignities refer to the strength or weakness of a planet based on its zodiac sign placement. A planet is "dignified" when it is in a sign it rules or exalts in, and "debilitated" when it is in its detriment or fall.</p>
                             <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">`;

        if (globalState.ALL_DIGNITY_INTERPRETATIONS) {
            for (const planetKey in globalState.ALL_DIGNITY_INTERPRETATIONS) {
                const interpretations = globalState.ALL_DIGNITY_INTERPRETATIONS[planetKey];
                dignitiesHTML += `<div style="background: rgba(0,0,0,0.05); padding: 10px; border-radius: 5px;">
                                    <h4>${planetKey.charAt(0).toUpperCase() + planetKey.slice(1)}</h4>`;
                for (const dignityType in interpretations) {
                    dignitiesHTML += `<p><strong>${dignityType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> ${interpretations[dignityType]}</p>`;
                }
                dignitiesHTML += `</div>`;
            }
        } else {
            dignitiesHTML += '<p>No general dignity interpretations available.</p>';
        }
        dignitiesHTML += `</div>`;
        container.innerHTML = dignitiesHTML;

    } catch (error) {
        console.error("Error rendering dignities UI:", error);
        container.innerHTML = `<p>Could not load dignities data: ${error.message}</p>`;
    }
}

// --- ADDED: Arabic Parts UI ---
export async function renderArabicPartsUI() { // Export renderArabicPartsUI
    const container = document.getElementById('arabicPartsContent');
    if (!container) { console.warn("Arabic Parts container 'arabicPartsContent' not found."); return; }
    container.innerHTML = "<p>Loading Arabic Parts data...</p>";

    try {
        // If Part of Fortune is already part of natal chart, this could be a general overview.
        // For specific calculation, users would need to input birth data.
        const data = globalState.ALL_POF_INTERPRETATIONS; // Use pre-loaded interpretations
        if (!data) {
            const fetchedData = await apiService.fetchPartOfFortuneInterpretations();
            if (fetchedData.error) throw new Error(fetchedData.error);
            globalState.ALL_POF_INTERPRETATIONS = fetchedData;
        }

        let arabicPartsHTML = `<h3>Arabic Parts (General)</h3>
                               <p>Arabic Parts are calculated points in a chart, derived from the longitudes of planets and angles. They are considered sensitive points indicating specific areas of focus or fortune.</p>`;

        if (globalState.ALL_POF_INTERPRETATIONS) {
             arabicPartsHTML += `<h4>Part of Fortune (Pars Fortunae)</h4>
                                <p><strong>General Meaning:</strong> ${globalState.ALL_POF_INTERPRETATIONS.general_meaning || 'Represents physical well-being, material success, and where you find joy.'}</p>`;
             if (globalState.ALL_POF_INTERPRETATIONS.interpretations_by_sign) {
                arabicPartsHTML += `<h5>Interpretations by Sign:</h5><ul>`;
                for (const signKey in globalState.ALL_POF_INTERPRETATIONS.interpretations_by_sign) {
                    const signName = globalState.ALL_ZODIAC_SIGNS_DATA?.[signKey]?.name || signKey;
                    arabicPartsHTML += `<li><strong>${signName}:</strong> ${globalState.ALL_POF_INTERPRETATIONS.interpretations_by_sign[signKey]}</li>`;
                }
                arabicPartsHTML += `</ul>`;
             }
             if (globalState.ALL_POF_INTERPRETATIONS.interpretations_by_house) {
                arabicPartsHTML += `<h5>Interpretations by House:</h5><ul>`;
                for (const houseNum in globalState.ALL_POF_INTERPRETATIONS.interpretations_by_house) {
                    arabicPartsHTML += `<li><strong>House ${houseNum}:</strong> ${globalState.ALL_POF_INTERPRETATIONS.interpretations_by_house[houseNum]}</li>`;
                }
                arabicPartsHTML += `</ul>`;
             }
        } else {
            arabicPartsHTML += '<p>No general Arabic Parts interpretations available.</p>';
        }
        container.innerHTML = arabicPartsHTML;

    } catch (error) {
        console.error("Error rendering Arabic Parts UI:", error);
        container.innerHTML = `<p>Could not load Arabic Parts data: ${error.message}</p>`;
    }
}

// --- ADDED: Fixed Stars UI ---
export async function renderFixedStarsUI() { // Export renderFixedStarsUI
    const container = document.getElementById('fixedStarsContent');
    if (!container) { console.warn("Fixed Stars container 'fixedStarsContent' not found."); return; }
    container.innerHTML = "<p>Loading Fixed Stars data...</p>";

    try {
        const data = globalState.fixedStarsData; // Check if already loaded
        if (!data) {
            const fetchedData = await apiService.fetchFixedStars();
            if (fetchedData.error) throw new Error(fetchedData.error);
            globalState.fixedStarsData = fetchedData;
        }

        let fixedStarsHTML = `<h3>Fixed Stars</h3>
                              <p>Fixed Stars are celestial bodies far beyond our solar system, but some are historically considered to have significant astrological influence based on their conjunctions with natal planets or angles.</p>`;

        if (globalState.fixedStarsData && globalState.fixedStarsData.length > 0) {
            fixedStarsHTML += `<ul>`;
            globalState.fixedStarsData.forEach(star => {
                fixedStarsHTML += `<li><strong>${star.name} (${star.position || 'N/A'}):</strong> ${star.influence || 'General influence.'}</li>`;
            });
            fixedStarsHTML += `</ul>`;
        } else {
            fixedStarsHTML += '<p>No fixed star data available or no significant fixed stars influencing the current chart/data.</p>';
        }
        container.innerHTML = fixedStarsHTML;

    } catch (error) {
        console.error("Error rendering Fixed Stars UI:", error);
        container.innerHTML = `<p>Could not load fixed stars data: ${error.message}</p>`;
    }
}

// --- ADDED: Midpoints UI ---
export async function renderMidpointsUI() { // Export renderMidpointsUI
    const container = document.getElementById('midpointsContent');
    if (!container) { console.warn("Midpoints container 'midpointsContent' not found."); return; }
    container.innerHTML = "<p>Loading Midpoints data...</p>";

    try {
        const data = globalState.midpointsData; // Check if already loaded
        if (!data) {
            const fetchedData = await apiService.fetchMidpoints();
            if (fetchedData.error) throw new Error(fetchedData.error);
            globalState.midpointsData = fetchedData;
        }

        let midpointsHTML = `<h3>Midpoints</h3>
                             <p>Midpoints are sensitive points in a chart located halfway between two planets or astrological points. They can reveal deeper insights into the interplay of energies between those points.</p>`;

        if (globalState.midpointsData && globalState.midpointsData.length > 0) {
            midpointsHTML += `<ul>`;
            globalState.midpointsData.forEach(midpoint => {
                midpointsHTML += `<li><strong>${midpoint.point1} / ${midpoint.point2}:</strong> ${midpoint.midpoint || 'N/A'} - ${midpoint.interpretation || 'No specific interpretation available.'}</li>`;
            });
            midpointsHTML += `</ul>`;
        } else {
            midpointsHTML += '<p>No midpoint data available or no significant midpoints calculated for the current chart/data.</p>';
        }
        container.innerHTML = midpointsHTML;

    } catch (error) {
        console.error("Error rendering Midpoints UI:", error);
        container.innerHTML = `<p>Could not load midpoints data: ${error.message}</p>`;
    }
}

// --- ADDED: Lunar Mansions UI ---
export async function renderLunarMansionsUI() { // Export renderLunarMansionsUI
    const container = document.getElementById('lunarMansionsContent');
    if (!container) { console.warn("Lunar Mansions container 'lunarMansionsContent' not found."); return; }
    container.innerHTML = "<p>Loading Lunar Mansions data...</p>";

    try {
        const data = globalState.lunarMansionsData; // Check if already loaded
        if (!data) {
            const fetchedData = await apiService.fetchLunarMansions(globalState.selectedCalendarDate.toISOString().split('T')[0]);
            if (fetchedData.error) throw new Error(fetchedData.error);
            globalState.lunarMansionsData = fetchedData;
        }

        let mansionsHTML = `<h3>Lunar Mansions</h3>
                            <p>Lunar Mansions (also known as Nakshatras in Vedic astrology, or Manazil al-Qamar in Arabic astrology) are divisions of the zodiac that mark the Moon's daily progress. Each mansion has specific energies and influences.</p>`;

        if (globalState.lunarMansionsData && globalState.lunarMansionsData.mansion) {
            mansionsHTML += `
                <p><strong>Current Lunar Mansion:</strong> ${globalState.lunarMansionsData.mansion}</p>
                <p><strong>Meaning/Influence:</strong> ${globalState.lunarMansionsData.meaning || 'No specific meaning provided.'}</p>
                <p>Date: ${new Date(globalState.lunarMansionsData.date || globalState.selectedCalendarDate).toLocaleDateString()}</p>
            `;
        } else {
            mansionsHTML += '<p>No lunar mansion data available for today.</p>';
        }
        container.innerHTML = mansionsHTML;

    } catch (error) {
        console.error("Error rendering Lunar Mansions UI:", error);
        container.innerHTML = `<p>Could not load lunar mansions data: ${error.message}</p>`;
    }
}

// --- ADDED: Antiscia UI ---
export async function renderAntisciaUI() { // Export renderAntisciaUI
    const container = document.getElementById('antisciaContent');
    if (!container) { console.warn("Antiscia container 'antisciaContent' not found."); return; }
    container.innerHTML = "<p>Loading Antiscia data...</p>";

    try {
        // Antiscia are sensitive points mirrored across the Cancer-Capricorn axis.
        // Typically calculated for natal charts, this view provides general info or requires user birth data.
        const data = globalState.antisciaData; // Check if already loaded or part of a chart
        if (!data) {
            // For a standalone view, you might fetch general explanations or require user input
            const fetchedData = await apiService.fetchAntiscia(); // This stub returns generic data
            if (fetchedData.error) throw new Error(fetchedData.error);
            globalState.antisciaData = fetchedData;
        }

        let antisciaHTML = `<h3>Antiscia (Contra-Antiscia)</h3>
                            <p>Antiscia are points of equal light or power, mirrored across the solsticial axis (0° Cancer - 0° Capricorn). They are considered "shadow" points that can reveal hidden influences or connections in a chart.</p>`;

        if (globalState.antisciaData && globalState.antisciaData.length > 0) {
            antisciaHTML += `<ul>`;
            globalState.antisciaData.forEach(anti => {
                antisciaHTML += `<li><strong>${anti.planet || 'Point'}:</strong> Antiscia at ${anti.antiscia_position || 'N/A'}. <em>${anti.interpretation || 'General influence.'}</em></li>`;
            });
            antisciaHTML += `</ul>`;
        } else {
            antisciaHTML += '<p>No antiscia data available or no specific antiscia calculated for the current chart/data.</p>';
        }
        container.innerHTML = antisciaHTML;

    } catch (error) {
        console.error("Error rendering Antiscia UI:", error);
        container.innerHTML = `<p>Could not load antiscia data: ${error.message}</p>`;
    }
}

// --- ADDED: Declination UI ---
export async function renderDeclinationUI() { // Export renderDeclinationUI
    const container = document.getElementById('declinationContent');
    if (!container) { console.warn("Declination container 'declinationContent' not found."); return; }
    container.innerHTML = "<p>Loading Declination data...</p>";

    try {
        const data = globalState.declinationData; // Check if already loaded
        if (!data) {
            const fetchedData = await apiService.fetchDeclination(globalState.selectedCalendarDate.toISOString().split('T')[0]);
            if (fetchedData.error) throw new Error(fetchedData.error);
            globalState.declinationData = fetchedData;
        }

        let declinationHTML = `<h3>Planetary Declination</h3>
                               <p>Declination measures a celestial body's angular distance north or south of the celestial equator. It highlights another dimension of planetary influence, often related to magnetic and energetic alignments.</p>`;

        if (globalState.declinationData && globalState.declinationData.length > 0) {
            declinationHTML += `<ul>`;
            globalState.declinationData.forEach(decl => {
                declinationHTML += `<li><strong>${decl.body}:</strong> ${decl.declination || 'N/A'}. <em>${decl.interpretation || 'General influence.'}</em></li>`;
            });
            declinationHTML += `</ul>`;
        } else {
            declinationHTML += '<p>No declination data available for today.</p>';
        }
        container.innerHTML = declinationHTML;

    } catch (error) {
        console.error("Error rendering Declination UI:", error);
        container.innerHTML = `<p>Could not load declination data: ${error.message}</p>`;
    }
}

// --- ADDED: Heliacal UI ---
export async function renderHeliacalUI() { // Export renderHeliacalUI
    const container = document.getElementById('heliacalContent');
    if (!container) { console.warn("Heliacal container 'heliacalContent' not found."); return; }
    container.innerHTML = "<p>Loading Heliacal Events data...</p>";

    try {
        const data = globalState.heliacalData; // Check if already loaded
        if (!data) {
            // Fetch for current year/month or based on user input
            const fetchedData = await apiService.fetchHeliacal(new Date().getFullYear()); // Fetch for current year
            if (fetchedData.error) throw new Error(fetchedData.error);
            globalState.heliacalData = fetchedData;
        }

        let heliacalHTML = `<h3>Heliacal Risings & Settings</h3>
                            <p>Heliacal events refer to when a celestial body first becomes visible (rising) or last becomes visible (setting) above the horizon at dawn or dusk. These were highly significant in ancient astrology, often marking turning points or auspicious periods.</p>`;

        if (globalState.heliacalData && globalState.heliacalData.length > 0) {
            heliacalHTML += `<ul>`;
            globalState.heliacalData.forEach(event => {
                heliacalHTML += `<li><strong>${event.event}:</strong> On ${new Date(event.date).toLocaleDateString()}. <em>${event.description || 'No detailed description.'}</em></li>`;
            });
            heliacalHTML += `</ul>`;
        } else {
            heliacalHTML += '<p>No heliacal event data available for the current period.</p>';
        }
        container.innerHTML = heliacalHTML;

    } catch (error) {
        console.error("Error rendering Heliacal UI:", error);
        container.innerHTML = `<p>Could not load heliacal data: ${error.message}</p>`;
    }
}

// --- ADDED: Personal Sky UI ---
export async function renderPersonalSkyUI() { // Export renderPersonalSkyUI
    const container = document.getElementById('personalSkyContent');
    if (!container) { console.warn("Personal Sky container 'personalSkyContent' not found."); return; }
    container.innerHTML = "<p>Generating your Personal Sky visualization...</p>";

    try {
        const data = globalState.personalSkyData; // Check if already loaded
        if (!data) {
            // This would ideally require user's current location to generate a map
            // For now, use a placeholder API call or default data
            const fetchedData = await apiService.fetchPersonalSkyData();
            if (fetchedData.error) throw new Error(fetchedData.error);
            globalState.personalSkyData = fetchedData;
        }

        let personalSkyHTML = `<h3>Your Personal Sky</h3>
                               <p>Experience a visualization of the celestial sphere from your unique perspective (or a general view if location is not provided).</p>`;

        if (globalState.personalSkyData && globalState.personalSkyData.imageUrl) {
            personalSkyHTML += `<div style="text-align: center; margin-top: 20px;">
                                    <img src="${globalState.personalSkyData.imageUrl}" alt="Personal Sky Visualization" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                                    <p style="font-size: 0.9em; margin-top: 10px;"><em>A static representation. An interactive version would allow for real-time sky viewing.</em></p>
                                </div>`;
        } else {
            personalSkyHTML += '<p>No personal sky visualization available. Please ensure your location data is entered or try again.</p>';
        }
        container.innerHTML = personalSkyHTML;

    } catch (error) {
        console.error("Error rendering Personal Sky UI:", error);
        container.innerHTML = `<p>Could not load personal sky data: ${error.message}</p>`;
    }
}

// --- ADDED: Year Ahead UI ---
export async function renderYearAheadUI() { // Export renderYearAheadUI
    const container = document.getElementById('yearAheadContent');
    if (!container) { console.warn("Year Ahead container 'yearAheadContent' not found."); return; }
    container.innerHTML = "<p>Generating your Year Ahead Forecast...</p>";

    try {
        const data = globalState.yearAheadData; // Check if already loaded
        if (!data) {
            // This would likely require user birth data for personalized transits/progressions
            const fetchedData = await apiService.fetchYearAheadForecast(); // Placeholder
            if (fetchedData.error) throw new Error(fetchedData.error);
            globalState.yearAheadData = fetchedData;
        }

        let yearAheadHTML = `<h3>Your Year Ahead Forecast</h3>
                             <p>This forecast highlights key astrological transits and themes influencing your year.</p>`;

        if (globalState.yearAheadData && globalState.yearAheadData.summary) {
            yearAheadHTML += `<p><strong>Summary:</strong> ${globalState.yearAheadData.summary}</p>`;
            if (globalState.yearAheadData.key_transits && globalState.yearAheadData.key_transits.length > 0) {
                yearAheadHTML += `<h4>Key Transits:</h4><ul>`;
                globalState.yearAheadData.key_transits.forEach(transit => {
                    yearAheadHTML += `<li>${transit}</li>`;
                });
                yearAheadHTML += `</ul>`;
            }
            if (globalState.yearAheadData.advice) {
                yearAheadHTML += `<h4>Guidance for the Year:</h4><p>${globalState.yearAheadData.advice}</p>`;
            }
        } else {
            yearAheadHTML += '<p>No year ahead forecast available. Please ensure your birth data is entered or try again.</p>';
        }
        container.innerHTML = yearAheadHTML;

    } catch (error) {
        console.error("Error rendering Year Ahead UI:", error);
        container.innerHTML = `<p>Could not load year ahead forecast: ${error.message}</p>`;
    }
}


// --- Numerology UI ---
export async function displayNumerologyUI(numerologyData) { // Export displayNumerologyUI
    const resultsContainer = document.getElementById('numerologyResults');
    const interpretationContainer = document.getElementById('numerologyInterpretation');
    if (!resultsContainer || !interpretationContainer) {
         console.warn("Numerology display containers not found.");
         return;
    }
     if (!globalState.ALL_NUMEROLOGY_MEANINGS_DATA) {
        resultsContainer.innerHTML = "<p>Numerology meanings data not available.</p>";
        interpretationContainer.innerHTML = "";
        return;
    }

    if (numerologyData.error) {
        resultsContainer.innerHTML = "";
        interpretationContainer.innerHTML = `<p>Error: ${numerologyData.error}</p>`;
        return;
    }

    resultsContainer.innerHTML = '';
    interpretationContainer.innerHTML = `<h3>Your Sacred Numerology for ${numerologyData.full_name_used || 'N/A'} (Born: ${numerologyData.birth_date_used || 'N/A'}):</h3>`;

    for (const key in numerologyData) {
        if (numerologyData[key] && typeof numerologyData[key] === 'object' && numerologyData[key].hasOwnProperty('number')) {
            const numberInfo = numerologyData[key];
            const displayName = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

            const itemDiv = document.createElement('div');
            itemDiv.className = 'numerology-item';
            itemDiv.innerHTML = `<h4>${displayName}</h4>
                                 <div style="font-size: 2rem; color: #ffd700;">${numberInfo.number}</div>
                                 <p><strong>${numberInfo.keyword || 'N/A'}:</strong> ${numberInfo.summary || 'Interpretation details below.'}</p>`;
            resultsContainer.appendChild(itemDiv);

            interpretationContainer.innerHTML += `
                <div class="interpretation-block" style="margin-bottom: 15px; padding: 10px; background: rgba(255,255,255,0.08); border-radius: 8px;">
                    <h4>${displayName}: ${numberInfo.number} (${numberInfo.keyword || 'N/A'})</h4>
                    <p>${numberInfo.summary || 'Detailed interpretation not available.'}</p>
                </div>`;
        }
    }
    if(numerologyData.id && interpretationContainer) { // Check interpretationContainer exists
        interpretationContainer.innerHTML += `<p><small>Report ID: ${numerologyData.id}, Saved: ${new Date(numerologyData.created_at || Date.now()).toLocaleDateString()}</small></p>`;
    }
     if (currentUser) {
        loadSavedNumerologyReportsUI();
    }
}

// --- Crystal Guidance UI ---
export async function updateCrystalGuidanceUI() { // Export updateCrystalGuidanceUI
    const signKey = document.getElementById('crystalSign')?.value;
    const needKey = document.getElementById('crystalNeed')?.value;
    const container = document.getElementById('crystalRecommendations');

    if (!container) { console.warn("Crystal recommendations container 'crystalRecommendations' not found."); return; }
    if (!signKey && !needKey) {
        container.innerHTML = '<p>Select your zodiac sign or a current need for crystal recommendations.</p>';
        return;
    }
    container.innerHTML = '<p>Summoning crystal wisdom...</p>';

    try {
        const data = await apiService.fetchCrystalRecommendations(signKey, needKey);
        if (data.error) throw new Error(data.error);

        if (data.recommendations && data.recommendations.length > 0) {
            container.innerHTML = data.recommendations.map(crystal => `
                <div class="crystal-card">
                    <h4>${crystal.name} ${crystal.image_placeholder_symbol || ''}</h4>
                    <p style="font-size:0.9em;"><strong>Properties:</strong> ${(Array.isArray(crystal.key_properties) ? crystal.key_properties.join('; ') : crystal.key_properties || 'General harmonizing properties.')}</p>
                    <p style="font-size:0.9em;"><strong>Chakra(s):</strong> ${(Array.isArray(crystal.chakra_association) ? crystal.chakra_association.join(', ') : crystal.chakra_association || 'Varies')}</p>
                    <p style="font-size:0.9em;"><strong>Reason:</strong> ${crystal.reason || 'Generally beneficial.'}</p>
                    <p style="font-size:0.8em; margin-top:5px;"><em>Affirm: "${crystal.affirmation || 'I am aligned with this crystal\'s healing energy.'}"</em></p>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p>No specific crystal recommendations found. Consider Clear Quartz or Selenite for general well-being.</p>';
        }
    } catch (error) {
        console.error("Error fetching crystal recommendations:", error);
        container.innerHTML = `<p>Could not load crystal guidance: ${error.message}</p>`;
    }
}

// --- Planet Tracker UI ---
export async function updatePlanetTrackerUI() { // Export updatePlanetTrackerUI
    const container = document.getElementById('planetPositions');
    const influencesContainer = document.getElementById('planetaryInfluences');
    const retrogradeAlertContainer = document.getElementById('retrogradeAlert');

    if (!container || !influencesContainer || !retrogradeAlertContainer) {
        console.warn("Planet tracker UI elements not found. (container: 'planetPositions', influences: 'planetaryInfluences', alerts: 'retrogradeAlert')");
        return;
    }
    if (!globalState.ALL_PLANETARY_DATA || !globalState.ALL_ZODIAC_SIGNS_DATA){
         if(container) container.innerHTML = "<p>Planetary or Zodiac data not loaded yet. Please wait.</p>";
         return;
    }
    container.innerHTML = "<p>Tracking celestial movements...</p>";
    influencesContainer.innerHTML = "<h3>Current Planetary Influences</h3><ul><li>Loading...</li></ul>";
    retrogradeAlertContainer.innerHTML = "";

    try {
        // Use current location (Grants Pass, Oregon) if available, otherwise default
        const currentLat = currentUser?.birth_data?.birth_location?.latitude || 42.44; // Grants Pass Latitude
        const currentLon = currentUser?.birth_data?.birth_location?.longitude || -123.33; // Grants Pass Longitude
        const currentTimezone = currentUser?.birth_data?.birth_location?.timezone_str || 'America/Los_Angeles';
        const currentDateTime = new Date().toISOString();

        const transitData = await apiService.getCurrentTransitsForDaily(currentLat, currentLon, currentDateTime, currentTimezone, 'Placidus'); // Example params

        if(transitData.error || !transitData.points){
             throw new Error(transitData.error || "Planetary points data missing.");
        }

        container.innerHTML = Object.values(transitData.points).map(point => {
            if (point.error || !point.key) return '';
            const planetBase = globalState.ALL_PLANETARY_DATA[point.key] || { name: point.name, symbol: '?', influence: 'General influence.' };
            const signInfo = globalState.ALL_ZODIAC_SIGNS_DATA[point.sign_key] || { name: point.sign_name || 'Unknown Sign', symbol: '?' };
            return `
                <div class="planet-item">
                    <div style="font-size: 1.5rem;">${point.symbol || planetBase.symbol}</div>
                    <strong>${point.name} ${point.is_retrograde ? '(R)' : ''}</strong>
                    <div>in ${signInfo.symbol} ${point.sign_name || signInfo.name}</div>
                    <p style="font-size: 0.8rem; margin-top: 5px;">${(point.degrees_in_sign || 0).toFixed(2)}°</p>
                </div>`;
        }).join('');

        let influencesHTML = '<ul>';
        let retroAlerts = [];
        Object.values(transitData.points).forEach(point => {
            if (point.error || !point.key) return;
            const planetBase = globalState.ALL_PLANETARY_DATA[point.key] || { name: point.name, influence: 'Planetary influence.' };
            const signBase = globalState.ALL_ZODIAC_SIGNS_DATA[point.sign_key] || { name: point.sign_name || 'Unknown Sign', keywords: ['general themes'] };
            influencesHTML += `<li><strong>${point.name} in ${point.sign_name || signBase.name}:</strong> Focus on ${planetBase.influence ? planetBase.influence.split(',')[0] : 'its core themes'} via ${(signBase.keywords[0] || 'general').toLowerCase()} energies.</li>`;
            if (point.is_retrograde) {
                retroAlerts.push(`<strong>${point.name} is currently retrograde in ${point.sign_name || signBase.name}:</strong> A time to review, reflect, and re-evaluate matters related to ${planetBase.influence ? planetBase.influence.split(',')[0].toLowerCase() : 'its domain'} and themes of ${(point.sign_name || signBase.name).toLowerCase()}.`);
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
                <p>Major personal and faster-moving planets appear direct, supporting forward momentum.</p>
            </div>`;
        }

    } catch (error) {
        console.error("Error updating planet tracker:", error);
        if(container) container.innerHTML = `<p>Could not load planetary positions: ${error.message}</p>`;
        if(influencesContainer) influencesContainer.innerHTML = "<h3>Current Planetary Influences</h3><p>Could not load influences.</p>";
    }
}

// Helper for Chakra Element Activities
function getChakraElementActivity(element) {
    if (!element) return 'Engage in mindful practices.';
    switch(element.toLowerCase()) {
        case 'fire': return 'Connect with nature: walk barefoot (earthing), gardening, hiking. Eat grounding root vegetables. Practice stability and routine.'; // Corrected from fire to earth
        case 'earth': return 'Engage with water: swim, take ritual baths with Epsom salts, be near oceans, lakes, or rivers. Creative dance or fluid movements. Honor and express your emotions healthily.'; // Corrected from earth to water
        case 'air': return 'Sunbathe (safely for short periods). Engage in dynamic exercises (cardio, martial arts). Eat warming, spicy foods. Pursue passions with vigor and courage. Sit by a campfire.'; // Corrected from air to fire
        case 'water': return 'Practice deep conscious breathwork (pranayama). Spend time in fresh, open air. Engage in intellectual pursuits, stimulating conversations. Sing, play wind instruments, or listen to wind chimes.'; // Corrected from water to air
        case 'ether (akasha) / sound': case 'ether / sound': case 'sound': return 'Sing, chant mantras, listen to healing music (especially singing bowls, tuning forks, or Solfeggio frequencies). Express your authentic truth. Practice active, mindful listening.';
        case 'light / intuition / mind': case 'light / intuition': case 'light': return 'Meditate in soft natural light or candlelight. Gentle sun/moon gazing (at appropriate, safe times). Visualize pure, healing light. Trust your intuitive hits and insights. Keep a dream journal. Practice scrying or other forms of divination.';
        case 'thought / cosmic energy / consciousness': case 'thought / cosmic energy': case 'consciousness': return 'Practice mindfulness and presence. Engage in spiritual study and contemplation. Connect with higher consciousness through prayer, deep meditation, or periods of silence. Practice being open-minded and receptive to universal wisdom.';
        default: return `Engage in practices that resonate deeply with this chakra's essence (${element}), focusing on its core qualities.`;
    }
}

// --- Affirmation UI ---
export async function generateAffirmationUI() { // Export generateAffirmationUI
    const affirmationEl = document.getElementById('dailyAffirmation');
    if (!affirmationEl) { console.warn("Daily affirmation element 'dailyAffirmation' not found."); return; }

    try {
        const data = await apiService.fetchRandomAffirmation();
        affirmationEl.textContent = data.affirmation || "Embrace the positive energy within and around you.";
        // Only update globalState.ALL_AFFIRMATIONS_DATA if it's new and valid
        if (data.affirmation && (!globalState.ALL_AFFIRMATIONS_DATA || !globalState.ALL_AFFIRMATIONS_DATA.includes(data.affirmation))) {
             // Ensure it's an array and limit its size if it grows too large
             if (!Array.isArray(globalState.ALL_AFFIRMATIONS_DATA)) {
                 globalState.ALL_AFFIRMATIONS_DATA = [];
             }
             globalState.ALL_AFFIRMATIONS_DATA.unshift(data.affirmation); // Add to beginning
             globalState.ALL_AFFIRMATIONS_DATA = globalState.ALL_AFFIRMATIONS_DATA.slice(0, 50); // Keep max 50
        }
    } catch (error) {
        console.error("Error fetching/displaying affirmation:", error);
        affirmationEl.textContent = "Could not load affirmation. Remember: You are resilient and capable.";
    }
}

// --- Rituals UI ---
export async function updateRitualsUI() { // Export updateRitualsUI
    const purpose = document.getElementById('ritualPurpose')?.value;
    const signKey = document.getElementById('ritualSign')?.value;
    const container = document.getElementById('ritualInstructions');

    if (!container) { console.warn("Ritual instructions container 'ritualInstructions' not found."); return; }
    if (!purpose || !signKey) {
        container.innerHTML = '<p>Please select a ritual purpose and your Zodiac sign for personalized guidance.</p>';
        return;
    }
    container.innerHTML = '<p>Crafting your sacred ritual guidance...</p>';

    try {
        const ritualData = await apiService.fetchRitualSuggestion(purpose, signKey);
        if (ritualData.error) throw new Error(ritualData.error);

        let ritualHTML = `<h3>${ritualData.title || 'Sacred Ritual'}</h3>`;
        if (ritualData.description) ritualHTML += `<p>${ritualData.description}</p>`;

        ritualHTML += `<h4>General Preparation:</h4><ul>`;
        (ritualData.general_preparation || []).forEach(prep => ritualHTML += `<li>${prep}</li>`);
        ritualHTML += `</ul>`;

        ritualHTML += `<h4>Ritual Steps:</h4><ol>`;
        (ritualData.steps || ["Focus on your intention.", "Perform a symbolic action.", "Express gratitude."]).forEach(step => ritualHTML += `<li>${step}</li>`);
        ritualHTML += `</ol>`;

        if(ritualData.sign_data && ritualData.elemental_enhancement){
            ritualHTML += `<h4>${ritualData.sign_data.name} (${ritualData.sign_data.element}, ${ritualData.sign_data.quality}) Enhancement:</h4><p>${ritualData.elemental_enhancement}</p>`;
        }

        ritualHTML += `<p><em>${ritualData.safety_note || "Always practice rituals with respect and safety, especially with fire."}</em></p>`;
        if(ritualData.affirmation_template) ritualHTML += `<p><strong>Affirm:</strong> "${ritualData.affirmation_template}"</p>`;

        container.innerHTML = ritualHTML;

    } catch (error) {
        console.error("Error updating rituals UI:", error);
        container.innerHTML = `<p>Could not load ritual guidance: ${error.message}</p>`;
    }
}

// --- Biorhythms UI ---
export async function calculateBiorhythmsUI() { // Export calculateBiorhythmsUI
    const birthDateInput = document.getElementById('biorhythmBirthDateInput');
    const analysisDateInput = document.getElementById('biorhythmAnalysisDateInput');
    const chartContainer = document.getElementById('biorhythmChartDisplay');
    const interpretationEl = document.getElementById('biorhythmInterpretation');

    if (!birthDateInput || !analysisDateInput || !chartContainer || !interpretationEl) {
        console.warn("Biorhythm UI elements not found. Check 'biorhythmBirthDateInput', 'biorhythmAnalysisDateInput', 'biorhythmChartDisplay', 'biorhythmInterpretation'.");
        return;
    }

    const birthDateStr = birthDateInput.value;
    const analysisDateStr = analysisDateInput.value;


    if (!birthDateStr) {
        alert('Please enter your birth date to calculate biorhythms.');
        if(chartContainer) chartContainer.innerHTML = '<p style="text-align:center; padding-top: 80px;">Enter birth date to view chart.</p>';
        ['physical', 'emotional', 'intellectual'].forEach(cycle => updateBiorhythmDisplayUI(cycle, undefined, true)); // Pass undefined for reset
        if (interpretationEl) interpretationEl.innerHTML = '';
        return;
    }
    if (!analysisDateStr) {
        alert('Please select an analysis date.');
        return;
    }

    if(chartContainer) chartContainer.innerHTML = '<p>Calculating your cosmic rhythms...</p>';

    try {
        const biorhythmData = await apiService.fetchBiorhythms(birthDateStr, analysisDateStr);
        if (biorhythmData.error) throw new Error(biorhythmData.error);

        if (biorhythmData.cycles) {
            updateBiorhythmDisplayUI('physical', biorhythmData.cycles.physical?.value_sin);
            updateBiorhythmDisplayUI('emotional', biorhythmData.cycles.emotional?.value_sin);
            updateBiorhythmDisplayUI('intellectual', biorhythmData.cycles.intellectual?.value_sin);
        }

        if(interpretationEl && biorhythmData.cycles){
            interpretationEl.innerHTML = `<h4>Secondary Rhythms for ${biorhythmData.analysis_date || new Date(analysisDateStr).toLocaleDateString()}:</h4><ul>`;
            const secondaryCyclesOrder = ['intuition', 'aesthetic', 'awareness', 'spiritual'];
            secondaryCyclesOrder.forEach(cycleKey => {
                const cycle = biorhythmData.cycles[cycleKey];
                if(cycle){
                    interpretationEl.innerHTML += `<li><strong>${cycle.label || cycleKey.charAt(0).toUpperCase() + cycleKey.slice(1)} (${cycle.length_days || 'N/A'} days):</strong> ${cycle.status || 'N/A'} (${cycle.percentage !== undefined ? `${cycle.percentage}%` : 'N/A'})</li>`;
                }
            });
            interpretationEl.innerHTML += `</ul><p><em>Use this as a guide for self-awareness. Highs = peak energy; Lows = rest/recharge; Critical days (near 50%) = potential instability or heightened sensitivity to the cycle's themes.</em></p>`;
        }

        const chartPlotData = await apiService.fetchBiorhythmChartData(birthDateStr, analysisDateStr);
        if(chartPlotData && !chartPlotData.error){
            drawBiorhythmChartUI(chartPlotData);
        } else if (chartPlotData && chartPlotData.error) {
             if(chartContainer) chartContainer.innerHTML = `<p>Could not load chart: ${chartPlotData.error}</p>`;
        }

    } catch (error) {
        console.error("Error calculating biorhythms:", error);
        if(chartContainer) chartContainer.innerHTML = `<p>Could not calculate biorhythms: ${error.message}</p>`;
        ['physical', 'emotional', 'intellectual'].forEach(cycle => updateBiorhythmDisplayUI(cycle, undefined, true));
        if (interpretationEl) interpretationEl.innerHTML = `<p>Error: ${error.message}</p>`;
    }
}

export function updateBiorhythmDisplayUI(cycleName, valueSin, reset = false) { // Export updateBiorhythmDisplayUI
    const barEl = document.getElementById(`${cycleName}Bar`);
    const statusEl = document.getElementById(`${cycleName}Status`);
    if (!barEl || !statusEl) {
        console.warn(`Biorhythm display elements for '${cycleName}' not found.`);
        return;
    }

    if (reset || typeof valueSin === 'undefined' || valueSin === null) {
        barEl.style.width = `50%`; // Neutral position
        barEl.style.background = `rgba(255, 255, 255, 0.2)`; // Default/neutral color
        statusEl.textContent = `Awaiting calculation...`;
        return;
    }

    const percentage = (valueSin + 1) / 2 * 100; // Convert sin value (-1 to 1) to percentage (0 to 100)
    barEl.style.width = `${Math.max(0, Math.min(100, percentage))}%`; // Clamp percentage

    let statusText = "Neutral";
    let barColor = "linear-gradient(90deg, #ffd700, #ffaa00)"; // Neutral/Transitional color

    if (percentage > 90) { statusText = "Peak Performance"; barColor = "linear-gradient(90deg, #4CAF50, #8BC34A)";} // Green shades for high
    else if (percentage > 70) { statusText = "High Energy"; barColor = "linear-gradient(90deg, #8BC34A, #CDDC39)"; }
    else if (percentage > 55) { statusText = "Positive"; barColor = "linear-gradient(90deg, #CDDC39, #FFEB3B)";} // Yellow shades for positive
    else if (percentage < 10) { statusText = "Deep Recharge"; barColor = "linear-gradient(90deg, #B71C1C, #D32F2F)";} // Dark red for very low
    else if (percentage < 25) { statusText = "Very Low"; barColor = "linear-gradient(90deg, #F44336, #E57373)";} // Red shades for low
    else if (percentage < 45) { statusText = "Low Energy"; barColor = "linear-gradient(90deg, #FF9800, #FFB74D)";} // Orange shades for lower
    else { statusText = "Transitional/Critical"; } // Default yellow/orange for mid-range

    statusEl.textContent = `${statusText} (${Math.round(percentage)}%)`;
    barEl.style.background = barColor;
}

export function drawBiorhythmChartUI(chartData) { // Export drawBiorhythmChartUI
    const chartContainer = document.getElementById('biorhythmChartDisplay');
    if (!chartContainer) { console.warn("Biorhythm chart container 'biorhythmChartDisplay' not found."); return; }
    if (!chartData || !chartData.series) {
        chartContainer.innerHTML = `<p>Chart Error: ${chartData?.error || 'Chart data unavailable.'}</p>`;
        return;
    }
    chartContainer.innerHTML = ''; // Clear previous chart
    const canvas = document.createElement('canvas');
    chartContainer.appendChild(canvas);
    // Ensure dimensions are reasonable, fallback if container is not visible
    canvas.width = chartContainer.offsetWidth > 20 ? chartContainer.offsetWidth - 10 : 280;
    canvas.height = chartContainer.offsetHeight > 20 ? chartContainer.offsetHeight - 10 : 180;


    const ctx = canvas.getContext('2d');
    if (!ctx) {
        chartContainer.innerHTML = '<p>Canvas not supported for chart.</p>';
        return;
    }

    const yZero = canvas.height / 2;
    const numDataPoints = chartData.x_axis_labels?.length || (chartData.series.physical?.points?.length > 0 ? chartData.series.physical.points.length : 31); // Default to 31 if no specific length
    const analysisDateIndex = chartData.analysis_date_index ?? Math.floor(numDataPoints / 2); // Use provided index or calculate

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'rgba(255,255,255,0.2)';
    ctx.fillStyle = 'rgba(255,255,255,0.7)';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';

    // Horizontal center line (0%)
    ctx.beginPath(); ctx.moveTo(0, yZero); ctx.lineTo(canvas.width, yZero); ctx.stroke();
    ctx.fillText("0%", canvas.width - 15, yZero - 2);
    ctx.fillText("+100%", canvas.width - 25, 12);
    ctx.fillText("-100%", canvas.width - 25, canvas.height - 5);

    // Vertical line for analysis date
    const xToday = (analysisDateIndex / (numDataPoints -1)) * canvas.width;
    ctx.beginPath(); ctx.setLineDash([2, 2]); ctx.moveTo(xToday, 0); ctx.lineTo(xToday, canvas.height); ctx.strokeStyle = 'rgba(255,255,0,0.5)'; ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(255,255,0,0.8)';
    if (chartData.x_axis_labels && chartData.x_axis_labels[analysisDateIndex]) {
        ctx.fillText(chartData.x_axis_labels[analysisDateIndex], xToday, canvas.height - 5);
    } else {
        ctx.fillText(new Date(chartData.analysis_date + 'T00:00:00Z').toLocaleDateString('en-US', {month:'short', day:'numeric', timeZone:'UTC'}), xToday, canvas.height - 5);
    }
    ctx.fillStyle = 'rgba(255,255,255,0.7)'; // Reset fillStyle

    // X-axis labels and tick marks
    for (let i = 0; i < numDataPoints; i++) {
        const xPos = (i / (numDataPoints -1)) * canvas.width;
        if (chartData.x_axis_labels && i % Math.max(1, Math.floor(numDataPoints/10)) === 0 && i !== analysisDateIndex) { // Adjust tick frequency
            ctx.fillText(chartData.x_axis_labels[i], xPos, canvas.height - 5);
        }
        ctx.beginPath(); ctx.moveTo(xPos, yZero -3); ctx.lineTo(xPos, yZero+3); ctx.strokeStyle = 'rgba(255,255,255,0.1)'; ctx.stroke();
    }
    ctx.strokeStyle = 'rgba(255,255,255,0.2)'; // Reset strokeStyle

    // Plot each cycle
    Object.values(chartData.series).forEach((cycleData, index) => {
        if(!cycleData.points || cycleData.points.length === 0) return;
        ctx.strokeStyle = cycleData.color || '#FFFFFF'; // Default to white if no color
        ctx.fillStyle = cycleData.color || '#FFFFFF';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        cycleData.points.forEach((point, i) => {
            const x = (i / (cycleData.points.length - 1)) * canvas.width;
            const y = yZero * (1 - (point.value_sin || 0)); // Default to 0 if value_sin is missing
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();

        // Legend
        const legendY = 10 + ( index * 15);
        const cycleInfo = BIORHYTHM_CYCLES[cycleData.label.toLowerCase()]
                         ? BIORHYTHM_CYCLES[cycleData.label.toLowerCase()]
                         : { length: 'N/A' };
        const cycleLength = cycleData.points[analysisDateIndex]?.length_days || cycleInfo.length;

        ctx.fillText(`${cycleData.label.substring(0,1).toUpperCase()}(${cycleLength}d)`, 30, legendY);
        ctx.beginPath(); ctx.moveTo(5, legendY - 4); ctx.lineTo(15, legendY - 4); ctx.stroke(); // Line for legend color
    });
    ctx.lineWidth = 1; // Reset lineWidth
}


// --- Journaling UI ---
export async function saveJournalEntryUI() { // Export saveJournalEntryUI
    const titleInput = document.getElementById('journalTitle');
    const contentInput = document.getElementById('journalText');
    const typeInput = document.getElementById('journalType');

    if (!titleInput || !contentInput || !typeInput) {
        console.warn("Journal form elements not found. Check 'journalTitle', 'journalText', 'journalType'.");
        alert("Journal form elements not found.");
        return;
    }

    const title = titleInput.value;
    const content = contentInput.value;
    const entry_type = typeInput.value;

    if (content.trim() === '') {
        alert('Please write something in your journal entry.');
        return;
    }

    const entryData = { title: title || `Entry for ${new Date().toLocaleDateString()}`, content, entry_type };
    if (entry_type === 'dreams') {
        entryData.dream_date = document.getElementById('dreamDateInput')?.value || new Date().toISOString().split('T')[0];
        entryData.dream_mood = document.getElementById('dreamMoodSelect')?.value;
    }

    try {
        const result = await apiService.createJournalEntry(entryData);
        alert(result.message || 'Journal entry saved successfully!');
        contentInput.value = '';
        titleInput.value = '';
        loadUserJournalEntriesUI();
    } catch (error) {
        console.error("Error saving journal entry:", error);
        alert(`Failed to save entry: ${error.message || 'Please try again.'}`);
    }
}

export async function loadUserJournalEntriesUI() { // Export loadUserJournalEntriesUI
    const container = document.getElementById('savedEntries');
    if (!container) { console.warn("Saved entries container 'savedEntries' not found."); return; }
    if (!currentUser) {
        container.innerHTML = "<h4>Your Saved Journal Entries:</h4><p>Login to view your saved readings.</p>";
        return;
    }
    container.innerHTML = '<h4>Your Saved Journal Entries:</h4><p>Loading entries...</p>';

    try {
        const data = await apiService.fetchJournalEntries();
        if (data.error) throw new Error(data.error);

        if (data.entries && data.entries.length > 0) {
            container.innerHTML = '<h4>Your Saved Journal Entries:</h4>';
            // Sort entries by creation date, newest first
            data.entries.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

            data.entries.forEach(entry => {
                const entryDiv = document.createElement('div');
                entryDiv.className = 'journal-entry';
                let entryHTML = `<p><strong>${entry.title || new Date(entry.created_at).toLocaleString([], {year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'})} - ${entry.entry_type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</strong></p>
                                 <p>${entry.content.replace(/\n/g, '<br>')}</p>`;
                if (entry.entry_type === 'dreams' && entry.dream_date) {
                    entryHTML += `<p><small>Dream Date: ${new Date(entry.dream_date + 'T00:00:00Z').toLocaleDateString([],{timeZone:'UTC', month: 'short', day: 'numeric', year: 'numeric'})} | Mood: ${entry.dream_mood || 'N/A'}</small></p>`;
                }
                entryHTML += `<button onclick="deleteJournalEntryUI(${entry.id})" style="background: #c0392b; color: white; border: none; padding: 5px 10px; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 5px; font-size: 0.8em;">Delete</button>`;
                entryDiv.innerHTML = entryHTML;
                container.appendChild(entryDiv);
            });
        } else {
            container.innerHTML = '<h4>Your Saved Journal Entries:</h4><p>No saved journal entries yet. Start writing!</p>';
        }
    } catch (error) {
        console.error("Error loading journal entries:", error);
        container.innerHTML = `<h4>Your Saved Journal Entries:</h4><p>Could not load entries: ${error.message}</p>`;
    }
}

export async function deleteJournalEntryUI(entryId) { // Export deleteJournalEntryUI
    if (!confirm('Are you sure you want to permanently delete this journal entry?')) return;
    try {
        const result = await apiService.deleteJournalEntry(entryId);
        alert(result.message || "Entry deleted.");
        loadUserJournalEntriesUI();
    } catch (error) {
        console.error("Error deleting entry:", error);
        alert(`Failed to delete entry: ${error.message || 'Please try again.'}`);
    }
}
// Make deleteJournalEntryUI globally accessible if called from inline HTML
// This is redundant if you're using ES Modules for everything, but harmless for onclick.
window.deleteJournalEntryUI = deleteJournalEntryUI;


// --- Dream Analysis UI ---
export function analyzeDreamUI() { // Export analyzeDreamUI
    const descriptionInput = document.getElementById('dreamDescription');
    const moodInput = document.getElementById('dreamMoodSelect');
    const dreamDateInput = document.getElementById('dreamDateInput');
    const analysisContainer = document.getElementById('dreamAnalysisResult');

    if (!descriptionInput || !moodInput || !dreamDateInput || !analysisContainer) {
        console.warn("Dream analysis form elements not found. Check 'dreamDescription', 'dreamMoodSelect', 'dreamDateInput', 'dreamAnalysisResult'.");
        return;
    }
    const description = descriptionInput.value;
    const mood = moodInput.value;
    const dreamDate = dreamDateInput.value || new Date().toISOString().split('T')[0];

    if (!globalState.ALL_DREAM_SYMBOLS_DATA) {
        analysisContainer.innerHTML = "<p>Dream symbol data not ready. Please wait or refresh.</p>";
        return;
    }
    if (description.trim() === '') {
        analysisContainer.innerHTML = '<p>Please describe your dream in detail for analysis.</p>';
        return;
    }

    let identifiedSymbols = [];
    let interpretationText = `<h4>Dream Analysis for ${new Date(dreamDate+'T00:00:00Z').toLocaleDateString([],{timeZone:'UTC', month: 'short', day: 'numeric', year: 'numeric'})} (Mood: ${mood})</h4>`;
    interpretationText += `<p><strong>Your Dream:</strong><br> "<em>${description.replace(/\n/g, '<br>')}</em>"</p>`;

    // Ensure globalState.ALL_DREAM_SYMBOLS_DATA is an object to iterate over
    if (globalState.ALL_DREAM_SYMBOLS_DATA && typeof globalState.ALL_DREAM_SYMBOLS_DATA === 'object') {
        Object.entries(globalState.ALL_DREAM_SYMBOLS_DATA).forEach(([symbolKey, symbolData]) => {
            const regex = new RegExp(`\\b${symbolKey.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')}\\b`, 'gi'); // Escape regex special chars
            if (description.match(regex) && symbolData && symbolData.general_meaning) {
                identifiedSymbols.push({ symbol: symbolKey.charAt(0).toUpperCase() + symbolKey.slice(1), meaning: symbolData.general_meaning });
            }
        });
    } else {
        console.warn("globalState.ALL_DREAM_SYMBOLS_DATA is not in expected format (object). Cannot process symbols.");
    }

    if (identifiedSymbols.length > 0) {
        interpretationText += '<p><strong>Potential Symbols & General Meanings:</strong></p><ul>';
        identifiedSymbols.forEach(item => {
            interpretationText += `<li><strong>${item.symbol}:</strong> ${item.meaning}</li>`;
        });
        interpretationText += '</ul>';
    } else {
        interpretationText += '<p>No specific common symbols matched from our database based on exact keywords. Consider the overall narrative and feelings.</p>';
    }

    let moodInterp = "";
    if (globalState.ALL_HOROSCOPE_INTERPRETATIONS && globalState.ALL_HOROSCOPE_INTERPRETATIONS.dream_mood_interpretations && globalState.ALL_HOROSCOPE_INTERPRETATIONS.dream_mood_interpretations[mood.toLowerCase()]) {
        moodInterp = globalState.ALL_HOROSCOPE_INTERPRETATIONS.dream_mood_interpretations[mood.toLowerCase()];
    } else {
        moodInterp = `A dream with a ${mood} mood often reflects current emotional states influencing your subconscious processing.`;
        if (!globalState.ALL_HOROSCOPE_INTERPRETATIONS || !globalState.ALL_HOROSCOPE_INTERPRETATIONS.dream_mood_interpretations) {
            console.warn("Dream mood interpretations data is not available in globalState.ALL_HOROSCOPE_INTERPRETATIONS.dream_mood_interpretations.");
        }
    }
    interpretationText += `<p><strong>Reflection considering Mood (${mood}):</strong> ${moodInterp}</p>`;
    interpretationText += `<p><em>Remember, your personal associations are key. Use this as a starting point for deeper reflection.</em></p>`;
    analysisContainer.innerHTML = interpretationText;

    // Auto-save dream analysis to journal if user is logged in and API is available
    if (currentUser && typeof apiService?.createJournalEntry === 'function') {
        const entryData = {
            title: `Dream Analysis: ${new Date(dreamDate+'T00:00:00Z').toLocaleDateString([],{timeZone:'UTC', month: 'short', day: 'numeric'})} - ${mood}`,
            content: `Dream: ${description}\n\nIdentified Symbols: ${identifiedSymbols.map(s=>s.symbol).join(', ') || 'None specific'}\n\nInitial Interpretation: ${moodInterp}`,
            entry_type: 'dreams',
            dream_date: dreamDate,
            dream_mood: mood
        };
        apiService.createJournalEntry(entryData)
            .then(() => {
                console.log("Dream analysis auto-saved to journal.");
                loadUserJournalEntriesUI(); // Optionally refresh journal list
            })
            .catch(err => console.error("Failed to auto-save dream analysis:", err));
    } else if (!currentUser) {
        console.info("Dream analysis not auto-saved: User not logged in.");
    } else {
        console.warn("Dream analysis not auto-saved: apiService.createJournalEntry not available.");
    }
}

// --- Meditation UI ---
export function updateMeditationUI() { // Export updateMeditationUI
    const type = document.getElementById('meditationType')?.value;
    const guidanceContainer = document.getElementById('meditationGuidance');
    if (!guidanceContainer) { console.warn("Meditation guidance container 'meditationGuidance' not found."); return; }

    let guidanceText = `<h4>${type ? type.charAt(0).toUpperCase() + type.slice(1) : "General"} Meditation Guidance</h4>`;
    const medGuidanceSource = globalState.ALL_RITUAL_DATA?.meditation_guidance || {};

    switch(type) {
        case 'mindfulness': guidanceText += `<p>${medGuidanceSource.mindfulness || "Focus on your breath. Observe thoughts without judgment. Be present in this moment."}</p>`; break;
        case 'chakra':
             const chakraKeys = globalState.ALL_CHAKRA_DATA ? Object.keys(globalState.ALL_CHAKRA_DATA) : [];
             const randomChakraKey = chakraKeys.length > 0 ? chakraKeys[Math.floor(Math.random() * chakraKeys.length)] : null;
             const chakraForMed = randomChakraKey ? globalState.ALL_CHAKRA_DATA?.[randomChakraKey] : {name: "Root", color: "red", bija_mantra: "LAM", location: "base of spine", affirmation: "I am grounded."};
             guidanceText += `<p>${medGuidanceSource.chakra?.replace('{chakraName}', chakraForMed.name).replace('{chakraColor}', chakraForMed.color).replace('{chakraLocation}', chakraForMed.location).replace('{chakraMantra}', chakraForMed.bija_mantra).replace('{chakraAffirmation}', chakraForMed.affirmation) || `Focus on your ${chakraForMed.name}. Visualize its ${chakraForMed.color} light at its ${chakraForMed.location}. Chant ${chakraForMed.bija_mantra}. Affirm: "${chakraForMed.affirmation}"`}</p>`;
             break;
        case 'manifestation': guidanceText += `<p>${medGuidanceSource.manifestation || "Clearly visualize your desire as fulfilled. Feel the emotions of success and gratitude. Release attachment to the outcome."}</p>`; break;
        case 'healing': guidanceText += `<p>${medGuidanceSource.healing || "Visualize healing light filling your body. Direct it to areas needing care. Affirm your wholeness and vitality."}</p>`; break;
        case 'zodiac':
            const signKeys = globalState.ALL_ZODIAC_SIGNS_DATA ? Object.keys(globalState.ALL_ZODIAC_SIGNS_DATA) : [];
            const randomSignKey = signKeys.length > 0 ? signKeys[Math.floor(Math.random() * signKeys.length)] : null;
            const signForMed = randomSignKey ? globalState.ALL_ZODIAC_SIGNS_DATA?.[randomSignKey] : {name: "Aries", keywords: ["courage"], mantra: "I am courageous."};
            guidanceText += `<p>${medGuidanceSource.zodiac?.replace('{signName}', signForMed.name).replace('{signKeywords}', (signForMed.keywords || []).join(', ')).replace('{signMantra}', signForMed.mantra) || `Connect with the energy of ${signForMed.name}. Meditate on its qualities: ${(signForMed.keywords || []).join(', ')}. Affirm: "${signForMed.mantra}"`}</p>`;
            break;
        default: guidanceText += "<p>Find a comfortable position, close your eyes gently, and focus on your natural breath, allowing thoughts to pass without judgment.</p>";
    }
    guidanceContainer.innerHTML = guidanceText;
}

// --- Numerology UI ---
export async function prefillAndCalculateNumerology(userData) { // Export prefillAndCalculateNumerology
    const nameInput = document.getElementById('numerologyFullName');
    const dateInput = document.getElementById('numerologyBirthDate');

    if (!nameInput || !dateInput) {
        console.warn("Numerology input fields not found for prefilling. Check 'numerologyFullName', 'numerologyBirthDate'.");
        return;
    }

    if (userData.full_name_for_numerology) {
        nameInput.value = userData.full_name_for_numerology;
    }

    if (userData.birth_data && userData.birth_data.birth_datetime_utc) {
        const birthDateTime = new Date(userData.birth_data.birth_datetime_utc);
        // Ensure date is formatted correctly for input type="date" (YYYY-MM-DD)
        const year = birthDateTime.getUTCFullYear();
        const month = (birthDateTime.getUTCMonth() + 1).toString().padStart(2, '0');
        const day = birthDateTime.getUTCDate().toString().padStart(2, '0');
        dateInput.value = `${year}-${month}-${day}`;
    }

    if (nameInput.value && dateInput.value) { // Check if both have values after prefill
        await calculateNumerologyUI();
    }
}

export async function calculateNumerologyUI() { // Export calculateNumerologyUI
    const fullName = document.getElementById('numerologyFullName')?.value;
    const birthDateStr = document.getElementById('numerologyBirthDate')?.value;
    const resultsContainer = document.getElementById('numerologyResults');
    const interpretationContainer = document.getElementById('numerologyInterpretation');

    if (!resultsContainer || !interpretationContainer) {
        console.warn("Numerology results containers not found. Check 'numerologyResults', 'numerologyInterpretation'.");
        return;
    }

    if (!fullName || !birthDateStr) {
        resultsContainer.innerHTML = '';
        interpretationContainer.innerHTML = '<p>Please enter your full birth name and birth date.</p>';
        return;
    }
    resultsContainer.innerHTML = ''; // Clear previous results
    interpretationContainer.innerHTML = '<p>Calculating your sacred numbers...</p>';

    try {
        const reportData = await apiService.calculateAndMaybeSaveNumerology(fullName, birthDateStr, !!currentUser);

        await displayNumerologyUI(reportData);

    } catch (error) {
        console.error("Error calculating numerology:", error);
        interpretationContainer.innerHTML = `<p>Could not calculate numerology: ${error.message}</p>`;
    }
}

export async function loadSavedNumerologyReportsUI() { // Export loadSavedNumerologyReportsUI
    const container = document.getElementById('savedNumerologyReportsContainer');
    if (!container) { console.warn("Saved numerology reports container 'savedNumerologyReportsContainer' not found."); return; }
    if (!currentUser) {
        container.innerHTML = "<h4>Your Saved Numerology Reports:</h4><p>Login to view saved reports.</p>";
        return;
    }
    container.innerHTML = '<h4>Your Saved Numerology Reports:</h4><p>Loading reports...</p>';

    try {
        const reports = await apiService.fetchSavedNumerologyReports();
        if (reports && reports.length > 0) {
            container.innerHTML = '<h4>Your Saved Numerology Reports:</h4>';
            // Sort reports by creation date, newest first
            reports.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

            reports.forEach(report => {
                const reportDiv = document.createElement('div');
                reportDiv.className = 'journal-entry'; // Re-using class
                let reportHTML = `<p><strong>Report for: ${report.full_name_used} (Born: ${new Date(report.birth_date_used + 'T00:00:00Z').toLocaleDateString([],{timeZone:'UTC', month: 'short', day: 'numeric', year: 'numeric'})})</strong> - Saved: ${new Date(report.created_at).toLocaleDateString([],{month: 'short', day: 'numeric', year: 'numeric'})}</p>`;
                reportHTML += '<ul>';
                // Iterate over expected numerology number keys if known, or all keys
                const numberKeys = ['life_path_number', 'expression_number', 'soul_urge_number', 'personality_number', 'birth_day_number']; // Add other relevant keys
                numberKeys.forEach(key => {
                     if (report[key] && typeof report[key] === 'object' && report[key].number !== undefined) {
                         const displayName = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                         reportHTML += `<li><strong>${displayName}: ${report[key].number}</strong> - ${report[key].keyword || 'N/A'}.</li>`; // Removed summary for brevity in list
                    }
                });
                // Fallback for other numbers not in numberKeys, if any
                for (const key in report) {
                    if (key.endsWith("_number") && !numberKeys.includes(key) && report[key] && typeof report[key] === 'object' && report[key].number !== undefined) {
                         const displayName = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                         reportHTML += `<li><strong>${displayName}: ${report[key].number}</strong> - ${report[key].keyword || 'N/A'}.</li>`;
                    }
                }

                reportHTML += `</ul>`;
                reportHTML += `<button onclick="viewFullNumerologyReportUI('${report.id}')" class="tab-button" style="margin-right:5px;font-size:0.8em; padding: 4px 8px;">View</button>`;
                reportHTML += `<button onclick="deleteNumerologyReportUI(${report.id})" style="background: #c0392b; color: white; border: none; padding: 4px 8px; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 5px; font-size: 0.8em;">Delete</button>`;
                reportDiv.innerHTML = reportHTML;
                container.appendChild(reportDiv);
            });
        } else {
            container.innerHTML = '<h4>Your Saved Numerology Reports:</h4><p>No saved reports found.</p>';
        }
    } catch (error) {
        console.error("Error loading saved numerology reports:", error);
        container.innerHTML = `<h4>Your Saved Numerology Reports:</h4><p>Could not load reports: ${error.message}</p>`;
    }
}
export async function viewFullNumerologyReportUI(reportId) { // Export viewFullNumerologyReportUI
    try {
        const reportData = await apiService.fetchSpecificNumerologyReport(reportId);
        if (reportData.error) throw new Error(reportData.error);

        const nameInput = document.getElementById('numerologyFullName');
        const dateInput = document.getElementById('numerologyBirthDate');
        if(nameInput) nameInput.value = reportData.full_name_used;
        if(dateInput) dateInput.value = reportData.birth_date_used; // Ensure this isYYYY-MM-DD

        await displayNumerologyUI(reportData);
        // alert("Loaded saved report. Details are displayed in the main calculation area.");
        const numerologySection = document.getElementById('numerologyCalculator') || document.getElementById('numerologyResults');
        if(numerologySection) numerologySection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        alert(`Could not load report: ${error.message}`);
    }
}
window.viewFullNumerologyReportUI = viewFullNumerologyReportUI; // Expose to global if called from inline HTML

export async function deleteNumerologyReportUI(reportId) { // Export deleteNumerologyReportUI
    if (!confirm('Are you sure you want to delete this numerology report?')) return;
    try {
        const result = await apiService.deleteNumerologyReport(reportId);
        alert(result.message || "Report deleted successfully.");
        loadSavedNumerologyReportsUI(); // Refresh list
        // Also clear main display if the deleted report was shown
        const nameInput = document.getElementById('numerologyFullName');
        const dateInput = document.getElementById('numerologyBirthDate');
        const resultsContainer = document.getElementById('numerologyResults');
        const interpretationContainer = document.getElementById('numerologyInterpretation');
        if (nameInput) nameInput.value = '';
        if (dateInput) dateInput.value = '';
        if (resultsContainer) resultsContainer.innerHTML = '';
        if (interpretationContainer) interpretationContainer.innerHTML = '<p>Please enter your full birth name and birth date.</p>';

    } catch (error) {
        console.error("Error deleting numerology report:", error);
        alert(`Failed to delete report: ${error.message || 'Please try again.'}`);
    }
}
window.deleteNumerologyReportUI = deleteNumerologyReportUI; // Expose to global if called from inline HTML


// --- Combination and Compatibility ---
export function updateCombinationUI() { // Export updateCombinationUI
    const sunKey = document.getElementById('sunSign')?.value;
    const moonKey = document.getElementById('moonSign')?.value;
    const risingKey = document.getElementById('risingSign')?.value;
    const resultContainer = document.getElementById('combinationResult');
    if (!resultContainer) { console.warn("Combination result container 'combinationResult' not found."); return; }
    if (!globalState.ALL_ZODIAC_SIGNS_DATA) {
        resultContainer.innerHTML = "<p>Zodiac data not yet loaded for combinations.</p>";
        return;
    }

    if (sunKey && moonKey && risingKey) {
        const sunData = globalState.ALL_ZODIAC_SIGNS_DATA[sunKey];
        const moonData = globalState.ALL_ZODIAC_SIGNS_DATA[moonKey];
        const risingData = globalState.ALL_ZODIAC_SIGNS_DATA[risingKey];

        if (!sunData || !moonData || !risingData) {
            resultContainer.innerHTML = '<p>Invalid sign selection. Please try again.</p>';
            return;
        }

        let profileText = `Your core identity (Sun in ${sunData.name}) is driven by ${sunData.element} energy, seeking to express ${(sunData.keywords?.[0] || 'its essence').toLowerCase()} and ${(sunData.keywords?.[1] || 'its nature').toLowerCase()}.
                           This is filtered through your emotional landscape (Moon in ${moonData.name}), which needs ${(moonData.keywords?.[0] || 'comfort').toLowerCase()} and processes the world with ${moonData.element} sensitivity.
                           Your outward persona (Rising in ${risingData.name}) is how you meet the world, often appearing ${(risingData.keywords?.[0] || 'distinctive').toLowerCase()} and utilizing ${risingData.element} qualities.`;

        const combinedKeywords = [...(sunData.keywords || []), ...(moonData.keywords || []), ...(risingData.keywords || [])]
                                 .filter((v,i,a)=>a.indexOf(v)===i).slice(0,10).join(', ');

        resultContainer.innerHTML = `
            <h3>${sunData.name} Sun, ${moonData.name} Moon, ${risingData.name} Rising</h3>
            <p><strong>Profile:</strong> ${profileText}</p>
            <p><strong>Combined Keywords:</strong> ${combinedKeywords || 'A unique blend of energies.'}</p>
            <p><em>This combination highlights a personality that is typically ${(sunData.strengths?.[0] || 'strong').toLowerCase()}, emotionally needs ${(moonData.strengths?.[1] || 'security').toLowerCase()}, and approaches the world by being ${(risingData.strengths?.[0] || 'adaptable').toLowerCase()}. The interplay of these energies defines your unique astrological signature.</em></p>
        `;
    } else {
        resultContainer.innerHTML = '<p>Select your sun, moon, and rising signs for an analysis.</p>';
    }
}

export function updateCompatibilityUI() { // Export updateCompatibilityUI
    const sign1Key = document.getElementById('compatSign1')?.value;
    const sign2Key = document.getElementById('compatSign2')?.value;
    const resultsContainer = document.getElementById('compatibilityResults');
    if (!resultsContainer) { console.warn("Compatibility results container 'compatibilityResults' not found."); return; }
    if (!globalState.ALL_COMPATIBILITY_MATRIX || !globalState.ALL_ZODIAC_SIGNS_DATA) {
        resultsContainer.innerHTML = "<p>Compatibility or Zodiac data not yet loaded.</p>";
        return;
    }

    if (sign1Key && sign2Key) {
        const sign1Data = globalState.ALL_ZODIAC_SIGNS_DATA[sign1Key];
        const sign2Data = globalState.ALL_ZODIAC_SIGNS_DATA[sign2Key];

        if(!sign1Data || !sign2Data) {
            resultsContainer.innerHTML = "<p>Invalid sign selection.</p>";
            return;
        }

        const compatibilityData = globalState.ALL_COMPATIBILITY_MATRIX[sign1Key]?.[sign2Key] || globalState.ALL_COMPATIBILITY_MATRIX[sign2Key]?.[sign1Key];

        if (compatibilityData) {
            resultsContainer.innerHTML = `
                <div class="compatibility-item" style="grid-column: 1 / -1; background: rgba(255,255,255,0.15); padding: 10px; border-radius: 8px; text-align: center;">
                    <div class="compatibility-score" style="color: ${getScoreColor(compatibilityData.overall_score)}; font-size: 2rem; font-weight: bold;">${compatibilityData.overall_score}%</div>
                    <div>Overall Compatibility: ${sign1Data.name} & ${sign2Data.name}</div>
                </div>
                <div class="interpretation" style="grid-column: 1 / -1; margin-top: 20px;">
                    <h4>${compatibilityData.interaction_type || 'Interaction Analysis'}:</h4><p>${compatibilityData.summary || 'A unique dynamic defines this pairing.'}</p>
                    <h4 style="margin-top: 10px;">Elemental Interaction (${compatibilityData.elemental_interaction_type || 'N/A'}):</h4><p>${compatibilityData.elemental_interaction_text || 'The elements blend in a distinct way.'}</p>
                    <h4 style="margin-top: 10px;">Quality Interaction (${compatibilityData.quality_interaction_type || 'N/A'}):</h4><p>${compatibilityData.quality_interaction_text || 'Their qualities interact to create a specific dynamic.'}</p>
                    <h4 style="margin-top: 10px;">Key Strengths:</h4><ul>${(compatibilityData.key_strengths || ['Unique dynamic']).map(s => `<li>${s}</li>`).join('')}</ul>
                    <h4 style="margin-top: 10px;">Potential Challenges:</h4><ul>${(compatibilityData.potential_challenges || ['Standard relationship growth areas']).map(c => `<li>${c}</li>`).join('')}</ul>
                    <h4 style="margin-top: 10px;">Relationship Guidance:</h4><p>${compatibilityData.love_compatibility?.advice || 'Focus on understanding, communication, and mutual respect for a thriving connection.'}</p>
                </div>`;
        } else {
            resultsContainer.innerHTML = `<p>Detailed compatibility data not found for ${sign1Data.name} and ${sign2Data.name}. Generally, signs of the same element (Fire, Earth, Air, Water) or complementary elements (Fire-Air, Earth-Water) tend to harmonize well. Opposite signs can offer balance and attraction through differences.</p>`;
        }
    } else {
        resultsContainer.innerHTML = '<p>Select two signs to see their compatibility analysis.</p>';
    }
}

export function updateMoonSunAnalysisUI() { // Export updateMoonSunAnalysisUI
    const sunKey = document.getElementById('sunAnalysis')?.value;
    const moonKey = document.getElementById('moonAnalysis')?.value;
    const resultContainer = document.getElementById('moonSunResult');
    if (!resultContainer) { console.warn("Moon-Sun analysis result container 'moonSunResult' not found."); return; }
    if (!globalState.ALL_ZODIAC_SIGNS_DATA) {
        resultContainer.innerHTML = "<p>Zodiac data not yet loaded for Moon-Sun analysis.</p>";
        return;
    }

    if (sunKey && moonKey) {
        const sunData = globalState.ALL_ZODIAC_SIGNS_DATA[sunKey];
        const moonData = globalState.ALL_ZODIAC_SIGNS_DATA[moonKey];
        if(!sunData || !moonData) {
             resultContainer.innerHTML = "<p>Invalid sign selection for Moon-Sun analysis.</p>";
            return;
        }

        let analysis = `<h3>${sunData.symbol || '?'} ${sunData.name} Sun with ${moonData.symbol || '?'} ${moonData.name} Moon</h3>`;
        analysis += `<p>Your <strong>${sunData.element} Sun in ${sunData.name}</strong> represents your core identity, vitality, and conscious drive, seeking expression through qualities like ${(sunData.keywords?.[0] || 'its core nature').toLowerCase()} and ${(sunData.strengths?.[0] || 'its key characteristics').toLowerCase()}.</p>`;
        analysis += `<p>Your <strong>${moonData.element} Moon in ${moonData.name}</strong> shapes your emotional nature, subconscious needs, and how you seek comfort, often through themes of ${(moonData.keywords?.[0] || 'emotional security').toLowerCase()} and ${(moonData.keywords?.[1] || 'inner feelings').toLowerCase()}.</p>`;

        if (sunData.element === moonData.element) {
            analysis += `<p>The shared <strong>${sunData.element}</strong> element between your Sun and Moon creates a harmonious internal landscape. Your conscious desires and emotional needs are naturally aligned, leading to a strong and coherent expression of your personality. You "walk your talk" with inner congruence.</p>`;
        } else if ( (sunData.element === "Fire" && moonData.element === "Air") || (sunData.element === "Air" && moonData.element === "Fire") ) {
            analysis += `<p>Your Fire Sun and Air Moon (or vice-versa) is a highly compatible and stimulating blend. Your actions and ideas feed each other, creating an expressive, communicative, and enthusiastic approach to life. Your head and your passions work well together.</p>`;
        } else if ( (sunData.element === "Earth" && moonData.element === "Water") || (sunData.element === "Water" && moonData.element === "Earth") ) {
            analysis += `<p>Your Earth Sun and Water Moon (or vice-versa) create a nurturing and grounded combination. Your practical drive finds emotional support, and your feelings are expressed with stability and care. This blend fosters deep empathy and reliable strength.</p>`;
        } else { // Square or Quincunx by element (e.g., Fire/Earth, Fire/Water, Air/Earth, Air/Water)
            analysis += `<p>The interplay between your ${sunData.element} Sun and ${moonData.element} Moon creates a dynamic tension. Your conscious drive (${sunData.name}) may sometimes operate differently from your emotional needs (${moonData.name}), presenting opportunities for significant personal growth as you learn to integrate these powerful forces. For example, your ${sunData.name} Sun's desire for ${(sunData.keywords?.[1] || 'expression').toLowerCase()} needs to harmonize with your ${moonData.name} Moon's quest for ${(moonData.keywords?.[1] || 'comfort').toLowerCase()}. This requires awareness and effort but can lead to a very well-rounded personality.</p>`;
        }
        analysis += `<p>Understanding this Sun-Moon blend is key to aligning your actions with your feelings, leading to greater fulfillment and inner peace.</p>`;
        resultContainer.innerHTML = analysis;
    } else {
        resultContainer.innerHTML = '<p>Select your sun and moon signs to understand their interaction.</p>';
    }
}

function getScoreColor(score) {
    if (score === undefined || score === null) return '#CCCCCC'; // Default for no score
    if (score >= 80) return '#4CAF50'; // Excellent - Green
    if (score >= 65) return '#8BC34A'; // Good - Light Green
    if (score >= 50) return '#FFC107'; // Average - Yellow
    if (score >= 35) return '#FF9800'; // Challenging - Orange
    return '#F44336'; // Difficult - Red
}

export function populateMantraListUI() { // Export populateMantraListUI
    const container = document.getElementById('mantraList');
    if (!container) { console.warn("Mantra list container 'mantraList' not found."); return; }

    const mantrasData = [ // This could be fetched from globalState.ALL_MANTRAS_DATA if available
        { name: "Om (AUM)", chantText: "Om", description: "Primordial sound, representing creation, preservation, dissolution. Calming, centering, connects to universal consciousness." },
        { name: "Om Mani Padme Hum", chantText: "Om Mani Padme Hum", description: "Tibetan Buddhist mantra for compassion, wisdom, and liberation." },
        { name: "Gayatri Mantra", chantText: "Om Bhur Bhuvah Swaha, Tat Savitur Varenyam, Bhargo Devasya Dhimahi, Dhiyo Yo Nah Prachodayat", description: "Vedic mantra for illumination of intellect, spiritual wisdom, and dispelling ignorance." },
        { name: "So Hum", chantText: "So Hum", description: "Breath mantra: \"I am That.\" Connects individual consciousness with universal consciousness." },
        { name: "Aham Prema", chantText: "Aham Prema", description: "Sanskrit for \"I am Divine Love.\" Cultivates self-love, compassion, and loving-kindness towards all." }
    ];

    container.innerHTML = mantrasData.map(mantra => `
        <div class="ritual-card">
            <h4>${mantra.name}</h4>
            <p>${mantra.description}</p>
            <button onclick="playMantra('${(mantra.chantText || mantra.name).replace(/'/g, "\\'")}', '${mantra.name.replace(/'/g, "\\'")}')" class="tab-button">Chant</button>
        </div>
    `).join('');
}
window.playMantra = playMantra; // Expose to global if called from inline HTML

export function playMantra(chantText, mantraName) { // Export playMantra
    const statusArea = document.getElementById('meditationGuidance') || document.getElementById('ritualInstructions') || document.getElementById('mantraList');

    if ('speechSynthesis' in window) {
        if (currentSpeechUtterance && speechSynthesis.speaking) {
            speechSynthesis.cancel(); // Stop any current speech
        }

        currentSpeechUtterance = new SpeechSynthesisUtterance(chantText);
        // Voice selection can be OS/browser dependent. Default is often fine.
        const englishVoice = speechVoices.find(v => v.lang.startsWith('en'));
        if (englishVoice) {
            currentSpeechUtterance.voice = englishVoice;
        } else if (speechVoices.length > 0) {
            currentSpeechUtterance.voice = speechVoices[0]; // Fallback to first available voice
        }

        currentSpeechUtterance.lang = 'en-US'; // Default to US English
        currentSpeechUtterance.rate = 0.7; // Slower for chanting
        currentSpeechUtterance.pitch = 1;

        const updateStatus = (message, color) => {
            if (statusArea) {
                const existingStatus = statusArea.querySelector('p[data-chant-status="true"]');
                if (existingStatus) existingStatus.remove();

                const statusMsgElement = document.createElement('p');
                statusMsgElement.setAttribute('data-chant-status', 'true');
                statusMsgElement.style.fontStyle = 'italic';
                statusMsgElement.style.color = color;
                statusMsgElement.textContent = message;

                if (statusArea.id === 'mantraList') {
                    statusArea.insertBefore(statusMsgElement, statusArea.firstChild);
                } else { // For meditationGuidance or ritualInstructions, replace content
                    statusArea.innerHTML = statusMsgElement.outerHTML;
                }
            }
        };

        currentSpeechUtterance.onstart = () => {
            updateStatus(`Now chanting: ${mantraName}. Focus and breathe...`, '#ffd700');
        };
        currentSpeechUtterance.onend = () => {
            updateStatus(`Chant for ${mantraName} complete. Carry its peace.`, '#a8e063');
            currentSpeechUtterance = null;
        };
        currentSpeechUtterance.onerror = (event) => {
            console.error("Speech synthesis error:", event.error);
            updateStatus(`Could not play chant for ${mantraName}. Error: ${event.error}`, '#ff6b6b');
            currentSpeechUtterance = null;
        };

        speechSynthesis.speak(currentSpeechUtterance);

    } else {
        alert(`Web Speech API not supported by your browser. Conceptual Chant for: ${mantraName}\n\n${chantText}\n\nFind a quiet space. Repeat the mantra with focused intention. Allow its vibrations to resonate within you, calming your mind and uplifting your spirit.`);
        if(statusArea) {
            const noSupportMsg = `<p style="color: #ffcc00;" data-chant-status="true">Web Speech API not supported. Please chant ${mantraName} manually: "${chantText}"</p>`;
            if (statusArea.id === 'mantraList') {
                 const existingStatus = statusArea.querySelector('p[data-chant-status="true"]');
                if (existingStatus) existingStatus.remove();
                statusArea.insertAdjacentHTML('afterbegin', noSupportMsg);
            } else {
                statusArea.innerHTML = noSupportMsg;
            }
        }
    }
}