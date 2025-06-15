// Filename: script.js

// Import only what's needed
// Ensure these paths are correct relative to script.js
import { loadInitialContentData, showTab as uiUpdateShowTab, globalState as uiUpdateGlobalState, displayDailyHoroscopeUI, updateMoonPhaseDisplayUI, updateMoonSunAnalysisUI, updateCrystalGuidanceUI, updateRitualsUI } from './uiUpdate.js'; //
import { zodiacFeaturesController } from './zodiacFeaturesController.js'; //
import { astralCalendarUI } from './astralCalendar.js'; //

// --- Constants ---
const API_BASE_URL = 'http://localhost:5000/api/v1'; //
const DEBUG_MODE = true; // Set to false in production

// --- State Management ---
const appState = {
    currentDate: new Date(), //
    selectedDate: new Date(), //
    activeTab: 'daily-horoscope-tab', // Corrected default tab ID to match uiUpdate.js and HTML structure
    isLoading: false, //
    controllers: new Map() //
};

// --- Utility Functions ---
function logDebug(...args) {
    if (DEBUG_MODE) { //
        console.debug('[DEBUG]', ...args); //
    }
}

// Renamed to `displayAppError` to avoid conflict with `uiUpdate.js`'s `showError` if both were global
function displayAppError(message, elementId = 'errorContainerGeneral') {
    const errorEl = document.getElementById(elementId); //
    if (errorEl) { //
        errorEl.innerHTML = `
            <div class="error-message">
                ${message}
                <button onclick="this.parentElement.style.display='none'">Dismiss</button>
            </div>
        `;
        errorEl.style.display = 'block'; //
    }
    console.error(message); //
}

// --- Tab Management ---
// This showTab function is now explicitly for script.js to manage its own tab logic,
// and it will call uiUpdate's showTab for the actual UI rendering.
export function showTab(tabId, event) { //
    if (event) event.preventDefault(); //

    logDebug(`Attempting to show tab: ${tabId}`); //

    // Update internal app state
    appState.activeTab = tabId; //

    // Call uiUpdate's showTab function to handle actual DOM manipulation and globalState update
    // Pass the event object as uiUpdate's showTab also expects it for activating button
    uiUpdateShowTab(tabId, event); //

    // Load tab-specific data (if not already handled by uiUpdate's tabChanged listener)
    loadDataForActiveTab(tabId).catch(error => { //
        displayAppError(`Failed to load tab ${tabId}: ${error.message}`); //
    });
}

// --- Controller Management ---
async function initializeController(name, initFn) { //
    if (!initFn || typeof initFn !== 'function') { //
        logDebug(`Skipping ${name} - no init function`); //
        return; //
    }

    try {
        logDebug(`Initializing ${name}...`); //
        await Promise.resolve(initFn()); //
        appState.controllers.set(name, true); //
    } catch (error) {
        console.error(`Error initializing ${name}:`, error); //
        throw error; // Re-throw to propagate to Promise.allSettled and catch block in initializeApp
    }
}

// --- Core Initialization ---
async function initializeApp() {
    try {
        appState.isLoading = true; //
        logDebug('Starting app initialization...'); //

        // 1. Initialize authentication (if `window.initializeAuth` exists and is a function)
        if (typeof window.initializeAuth === 'function') {
            await window.initializeAuth().catch(error => { // Use window.initializeAuth explicitly
                console.warn('Auth initialization warning:', error); //
            });
        }

        // 2. Load initial content data from backend
        // This is now called via uiUpdate.js's loadInitialContentData
        // which sets globalState.ALL_... data.
        if (typeof loadInitialContentData === 'function') { //
            await loadInitialContentData().catch(error => { //
                throw new Error(`Content load failed: ${error.message}`); //
            });
        }

        // 3. Initialize core controllers
        const controllers = {
            zodiac: () => zodiacFeaturesController?.initialize?.(), //
            calendar: () => astralCalendarUI?.initialize?.('astral-calendar-container'), // Pass the ID here
            // Add other controllers here if they have a separate initialize method
        };

        // Use Promise.allSettled to ensure all controller initializations run
        // even if one fails, and to catch errors gracefully.
        const results = await Promise.allSettled( //
            Object.entries(controllers).map(([name, initFn]) =>
                initializeController(name, initFn)
            )
        );

        results.forEach(result => {
            if (result.status === 'rejected') {
                console.error('Controller initialization failed:', result.reason);
                // Optionally, show a more specific error for failed controllers
                displayAppError(`Some features could not be initialized: ${result.reason.message || result.reason}`);
            }
        });


        // 4. Setup UI specific to script.js
        updateDateTime(); //
        setInterval(updateDateTime, 1000); //
        setupEventListeners(); //

        // 5. Show default tab
        // Use the new showTab for internal consistency, passing `null` for event
        showTab(appState.activeTab, null); //

        logDebug('App initialized successfully'); //
    } catch (error) {
        displayAppError(`Initialization failed: ${error.message}`); //
    } finally {
        appState.isLoading = false; //
    }
}

// --- Event Listeners ---
function setupEventListeners() { //
    // Tab click handlers
    document.querySelectorAll('.tab-button').forEach(button => { //
        button.addEventListener('click', (e) => { //
            const tabId = e.currentTarget.getAttribute('data-target'); //
            if (tabId) showTab(tabId, e); //
        });
    });

    // Add other global event listeners here if needed,
    // otherwise, module-specific event listeners should be in their respective files.
}

// --- Tab Content Loading (DEPRECATED: Now handled by uiUpdate.js's tabChanged event) ---
// This function will now simply call the respective rendering functions
// that are likely already being triggered by uiUpdate.js's tabChanged listener.
// This layer might be redundant if uiUpdate.js handles all rendering directly.
async function loadDataForActiveTab(tabId) {
    // Check if the uiUpdateGlobalState is available and has the necessary data
    // This function can serve as a trigger for data refresh if needed for a tab
    // that uiUpdate.js doesn't auto-refresh.

    logDebug(`Attempting to load data for tab: ${tabId}`); //

    switch (tabId) {
        case 'daily-horoscope-tab':
            // The displayDailyHoroscopeUI in uiUpdate.js already fetches data if needed
            // You might want to get the selected sign from the UI here.
            const selectedSign = document.getElementById('zodiacSignSelect')?.value || (uiUpdateGlobalState.ALL_ZODIAC_SIGNS_DATA ? Object.keys(uiUpdateGlobalState.ALL_ZODIAC_SIGNS_DATA)[0] : 'aries');
            if (selectedSign) {
                await displayDailyHoroscopeUI(selectedSign); //
            }
            break;
        case 'natal-chart-tab':
            // uiUpdate.js already has renderNatalChartInputForm() which is triggered by uiUpdateShowTab
            // If you have a specific "re-load" logic for this tab, put it here.
            break;
        case 'moon-sun-tab':
            await updateMoonPhaseDisplayUI(); //
            await updateMoonSunAnalysisUI(); //
            break;
        case 'planetary-hours-tab':
            if (typeof window.uiUpdate?.renderPlanetaryHoursUI === 'function') {
                await window.uiUpdate.renderPlanetaryHoursUI();
            }
            break;
        case 'dignities-tab':
            if (typeof window.uiUpdate?.renderDignitiesUI === 'function') {
                await window.uiUpdate.renderDignitiesUI();
            }
            break;
        case 'arabic-parts-tab':
            if (typeof window.uiUpdate?.renderArabicPartsUI === 'function') {
                await window.uiUpdate.renderArabicPartsUI();
            }
            break;
        case 'fixed-stars-tab':
            if (typeof window.uiUpdate?.renderFixedStarsUI === 'function') {
                await window.uiUpdate.renderFixedStarsUI();
            }
            break;
        case 'midpoints-tab':
            if (typeof window.uiUpdate?.renderMidpointsUI === 'function') {
                await window.uiUpdate.renderMidpointsUI();
            }
            break;
        case 'lunar-mansions-tab':
            if (typeof window.uiUpdate?.renderLunarMansionsUI === 'function') {
                await window.uiUpdate.renderLunarMansionsUI();
            }
            break;
        case 'antiscia-tab':
            if (typeof window.uiUpdate?.renderAntisciaUI === 'function') {
                await window.uiUpdate.renderAntisciaUI();
            }
            break;
        case 'declination-tab':
            if (typeof window.uiUpdate?.renderDeclinationUI === 'function') {
                await window.uiUpdate.renderDeclinationUI();
            }
            break;
        case 'heliacal-tab':
            if (typeof window.uiUpdate?.renderHeliacalUI === 'function') {
                await window.uiUpdate.renderHeliacalUI();
            }
            break;
        case 'cosmic-calendar-tab':
            if (typeof window.uiUpdate?.generateCosmicEventsUI === 'function') {
                await window.uiUpdate.generateCosmicEventsUI();
            }
            break;
        case 'personal-sky-tab':
            if (typeof window.uiUpdate?.renderPersonalSkyUI === 'function') {
                await window.uiUpdate.renderPersonalSkyUI();
            }
            break;
        case 'year-ahead-tab':
            if (typeof window.uiUpdate?.renderYearAheadUI === 'function') {
                await window.uiUpdate.renderYearAheadUI();
            }
            break;
        case 'sign-combinations-tab':
            if (typeof updateCombinationUI === 'function') { // Assuming this is now in uiUpdate.js or globally available
                await updateCombinationUI();
            } else if (typeof zodiacFeaturesController?.handleCombinationUpdate === 'function') {
                await zodiacFeaturesController.handleCombinationUpdate();
            }
            break;
        case 'compatibility-tab':
            if (typeof updateCompatibilityUI === 'function') {
                await updateCompatibilityUI();
            } else if (typeof zodiacFeaturesController?.handleCompatibilityUpdate === 'function') {
                await zodiacFeaturesController.handleCompatibilityUpdate();
            }
            break;
        case 'zodiac-knowledge-tab':
            if (typeof window.uiUpdate?.populateKnowledgeUI === 'function') {
                await window.uiUpdate.populateKnowledgeUI();
            } else if (typeof zodiacFeaturesController?.populateKnowledgeBase === 'function') {
                await zodiacFeaturesController.populateKnowledgeBase(); //
            }
            break;
        case 'tarot-reading-tab':
            if (typeof window.uiUpdate?.setupTarotReadingUI === 'function') {
                await window.uiUpdate.setupTarotReadingUI();
            }
            if (typeof window.uiUpdate?.loadSavedTarotReadingsUI === 'function') {
                await window.uiUpdate.loadSavedTarotReadingsUI();
            }
            break;
        case 'numerology-tab':
            if (typeof window.uiUpdate?.prefillAndCalculateNumerology === 'function' && uiUpdateGlobalState.currentUser) { // Assuming currentUser is set on globalState
                await window.uiUpdate.prefillAndCalculateNumerology(uiUpdateGlobalState.currentUser);
            }
            if (typeof window.uiUpdate?.loadSavedNumerologyReportsUI === 'function') {
                await window.uiUpdate.loadSavedNumerologyReportsUI();
            }
            break;
        case 'crystal-guide-tab':
            if (typeof updateCrystalGuidanceUI === 'function') {
                await updateCrystalGuidanceUI(); //
            }
            break;
        case 'planet-tracker-tab':
            if (typeof window.uiUpdate?.updatePlanetTrackerUI === 'function') {
                await window.uiUpdate.updatePlanetTrackerUI();
            }
            break;
        case 'chakra-analysis-tab':
            if (typeof window.uiUpdate?.updateChakraInfoUI === 'function') {
                await window.uiUpdate.updateChakraInfoUI();
            }
            break;
        case 'meditation-tab':
            if (typeof window.uiUpdate?.updateMeditationUI === 'function') {
                await window.uiUpdate.updateMeditationUI();
            }
            if (typeof window.uiUpdate?.populateMantraListUI === 'function') {
                await window.uiUpdate.populateMantraListUI();
            }
            break;
        case 'cosmic-journal-tab':
            if (typeof window.uiUpdate?.loadUserJournalEntriesUI === 'function') {
                await window.uiUpdate.loadUserJournalEntriesUI();
            }
            break;
        case 'dream-analysis-tab':
            if (typeof window.uiUpdate?.populateDreamSymbolGridUI === 'function') {
                await window.uiUpdate.populateDreamSymbolGridUI();
            }
            break;
        case 'sacred-rituals-tab':
            if (typeof updateRitualsUI === 'function') {
                await updateRitualsUI(); //
            }
            break;
        case 'biorhythms-tab':
            if (typeof window.uiUpdate?.calculateBiorhythmsUI === 'function') {
                // Ensure date inputs are correctly set for biorhythms before calling
                const today = new Date();
                const todayStr = today.toISOString().split('T')[0];
                const birthDateInput = document.getElementById('biorhythmBirthDateInput');
                const analysisDateInput = document.getElementById('biorhythmAnalysisDateInput');

                if (birthDateInput && !birthDateInput.value && uiUpdateGlobalState.currentUser?.birth_data?.birth_datetime_utc) {
                    const birthDate = new Date(uiUpdateGlobalState.currentUser.birth_data.birth_datetime_utc);
                    birthDateInput.value = birthDate.toISOString().split('T')[0];
                }
                if (analysisDateInput) {
                    analysisDateInput.value = todayStr;
                }
                await window.uiUpdate.calculateBiorhythmsUI();
            }
            break;
        default:
            logDebug(`No specific data load handler for tab: ${tabId}`); //
            break;
    }
}

// --- Date/Time ---
function updateDateTime() { //
    const now = new Date(); //
    const dtEl = document.getElementById('currentDateTime'); //
    if (dtEl) { //
        dtEl.textContent = now.toLocaleString(undefined, { //
            weekday: 'long', //
            year: 'numeric', //
            month: 'long', //
            day: 'numeric', //
            hour: '2-digit', //
            minute: '2-digit', //
            second: '2-digit' //
        });
    }
}

// --- Error Handling ---
function setupGlobalErrorHandling() { //
    window.addEventListener('error', (event) => { //
        console.error('Global error:', event.error || event.message); //
        displayAppError('An unexpected error occurred. Please try refreshing the page.'); // Using `displayAppError`
    });

    window.addEventListener('unhandledrejection', (event) => { //
        console.error('Unhandled rejection:', event.reason); //
        displayAppError('An asynchronous operation failed. Please try again.'); // Using `displayAppError`
    });
}

// --- Initialize ---
// Export the init function so it can be imported by init.js
export function init() { // Added `export` keyword here
    setupGlobalErrorHandling(); //
    if (document.readyState === 'loading') { //
        document.addEventListener('DOMContentLoaded', initializeApp); //
    } else {
        initializeApp(); //
    }
}

// Export public API (for global access if other scripts need it)
// showTab is already exported above, so no need for `window.showTab = showTab;` here.
// But if you rely on `window.showTab` being globally available *before* this module executes,
// you might keep `window.showTab = showTab;` or adjust load order.
// For now, assuming it's imported via ES Modules.

// Start the application
// This function will be called by init.js if it imports `init` from here.
// If script.js is the main entry point (type="module"), then this init() call is needed.
// Given the error `init.js` trying to import `init` from here, this `init()` call should NOT be here.
// `init.js` will call it.
// init(); // REMOVED: `init.js` will import and call this.