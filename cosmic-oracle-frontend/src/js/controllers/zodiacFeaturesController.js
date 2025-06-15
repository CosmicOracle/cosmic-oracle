// D:\my_projects\cosmic-oracle\cosmic-oracle-frontend\public\js\zodiacFeaturesController.js

import { apiService } from './apiService.js';
// It's good practice to import uiUpdate, but ensure its functions are correctly used
// uiUpdate functions like showLoading, hideLoading, displayError are globally available via window.uiHelpers
// The uiUpdate module also exports them.
import { displayError, showLoading, hideLoading } from './uiUpdate.js';

export const zodiacFeaturesController = {
    cachedData: {
        signs: null,
        compatibility: null,
        dailyHoroscopes: {},
        knowledgeBaseContent: [] // Store parsed knowledge base content here
    },

    // These selectors are used to populate dropdowns with zodiac signs or other related data.
    selectors: [
        'zodiacSignSelect', // For daily horoscope
        'sunSign',          // For sign combinations
        'moonSign',         // For sign combinations
        'risingSign',       // For sign combinations
        'compatSign1',      // For compatibility
        'compatSign2',      // For compatibility
        'crystalSign',      // For crystal guide (optional)
        'ritualSign'        // For rituals (optional)
    ],

    async initialize() {
        console.log("Initializing zodiac features...");

        // Ensure COSMIC_ORACLE is initialized globally (if other parts of your app rely on it)
        window.COSMIC_ORACLE = window.COSMIC_ORACLE || {};

        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve));
        }

        // Initialize ALL_ZODIAC_SIGNS_DATA if it doesn't exist
        if (!window.COSMIC_ORACLE.ALL_ZODIAC_SIGNS_DATA) {
            console.warn("Zodiac data not yet loaded. Attempting to load from API...");
            try {
                // Try to load the data from the API
                const response = await fetch('/api/v1/data/zodiac-signs');
                if (response.ok) {
                    window.COSMIC_ORACLE.ALL_ZODIAC_SIGNS_DATA = await response.json();
                    this.cachedData.signs = window.COSMIC_ORACLE.ALL_ZODIAC_SIGNS_DATA; // Cache it
                    console.log("Zodiac data loaded successfully from API.");
                } else {
                    console.error("Failed to load zodiac data:", response.status);
                    window.COSMIC_ORACLE.ALL_ZODIAC_SIGNS_DATA = {}; // Fallback to empty object
                    this.cachedData.signs = {};
                }
            } catch (error) {
                console.error("Error loading zodiac data:", error);
                window.COSMIC_ORACLE.ALL_ZODIAC_SIGNS_DATA = {}; // Fallback to empty object
                this.cachedData.signs = {};
            }
        } else {
            this.cachedData.signs = window.COSMIC_ORACLE.ALL_ZODIAC_SIGNS_DATA; // Use existing global data
            console.log("Zodiac data already available globally.");
        }

        // Set up a timeout in case the data is never loaded
        setTimeout(() => {
            if (!this.cachedData.signs || Object.keys(this.cachedData.signs).length === 0) {
                console.warn("Timed out waiting for zodiac data or data is empty.");
            }
        }, 5000);

        // Initialize the UI components
        this.setupZodiacSelectors();
        this.setupEventListeners();
        this.populateKnowledgeBase(); // Populate knowledge base on init
    },

    setupZodiacSelectors() {
        const zodiacSigns = this.cachedData.signs;

        if (!zodiacSigns || Object.keys(zodiacSigns).length === 0) {
            console.error("Zodiac data is empty or not loaded, cannot populate selectors.");
            const errorMessage = "Error loading zodiac signs. Please refresh the page.";
            displayError(errorMessage); // Use imported uiUpdate function

            const errorOptionHtml = '<option value="">' + errorMessage + '</option>';
            this.selectors.forEach(selectorId => {
                const selectElement = document.getElementById(selectorId);
                if (selectElement) {
                    selectElement.innerHTML = errorOptionHtml;
                }
            });
            return;
        }

        this.selectors.forEach(selectorId => {
            const selectElement = document.getElementById(selectorId);
            if (selectElement) {
                const currentSelection = selectElement.value; // Preserve current selection
                selectElement.innerHTML = ''; // Clear existing options

                // Add a default blank option if it's not a required selection
                if (!['zodiacSignSelect', 'sunSign', 'moonSign', 'risingSign', 'compatSign1', 'compatSign2'].includes(selectorId)) {
                    selectElement.add(new Option('Any Sign', ''));
                } else {
                    selectElement.add(new Option('Select Sign', '')); // For required fields
                }

                const sortedZodiacs = Object.entries(zodiacSigns).sort(([, a], [, b]) => (a.number || 0) - (b.number || 0));

                sortedZodiacs.forEach(([key, value]) => {
                    const option = document.createElement('option');
                    option.value = key;
                    option.textContent = value.name;
                    selectElement.appendChild(option);
                });

                // Restore previous selection
                if (currentSelection && Array.from(selectElement.options).some(opt => opt.value === currentSelection)) {
                    selectElement.value = currentSelection;
                } else if (!currentSelection && selectElement.options.length > 1 && ['zodiacSignSelect', 'sunSign', 'moonSign', 'risingSign', 'compatSign1', 'compatSign2'].includes(selectorId)) {
                    // Automatically select the first valid zodiac sign if no value is set for required selectors
                    selectElement.value = sortedZodiacs[0][0];
                }
            }
        });
        console.log("Zodiac selectors populated.");
    },

    setupEventListeners() {
        // Event listener for horoscope form
        const horoscopeForm = document.getElementById('horoscopeForm');
        if (horoscopeForm) {
            horoscopeForm.addEventListener('submit', this.handleHoroscopeFormSubmit.bind(this));
            // Also trigger update on select change for daily horoscope
            document.getElementById('zodiacSignSelect')?.addEventListener('change', this.handleHoroscopeFormSubmit.bind(this));
            document.getElementById('horoscopeDate')?.addEventListener('change', this.handleHoroscopeFormSubmit.bind(this));
        }

        // Event listener for combinations form (assuming there's one)
        const combinationForm = document.getElementById('combinationForm');
        if (combinationForm) {
            combinationForm.addEventListener('change', this.handleCombinationUpdate.bind(this));
        }

        // Event listener for compatibility form (assuming there's one)
        const compatibilityForm = document.getElementById('compatibilityForm');
        if (compatibilityForm) {
            compatibilityForm.addEventListener('change', this.handleCompatibilityUpdate.bind(this));
        }

        // Event listener for moon-sun form (assuming there's one)
        const moonSunForm = document.getElementById('moonPhaseForm');
        if (moonSunForm) {
            moonSunForm.addEventListener('submit', this.handleMoonSunAnalysisUpdate.bind(this));
            document.getElementById('moonPhaseDatetime')?.addEventListener('change', this.handleMoonSunAnalysisUpdate.bind(this));
        }

        // Event listener for crystal guide changes
        document.getElementById('crystalSign')?.addEventListener('change', () => {
            // Assuming uiUpdate.updateCrystalGuidanceUI exists and takes no args or gets from DOM
            if (typeof window.uiUpdate?.updateCrystalGuidanceUI === 'function') {
                window.uiUpdate.updateCrystalGuidanceUI();
            } else {
                console.warn("window.uiUpdate.updateCrystalGuidanceUI not found. Ensure uiUpdate is loaded and exports this function.");
            }
        });
        document.getElementById('crystalNeed')?.addEventListener('change', () => {
            if (typeof window.uiUpdate?.updateCrystalGuidanceUI === 'function') {
                window.uiUpdate.updateCrystalGuidanceUI();
            }
        });

        // Event listener for ritual changes
        document.getElementById('ritualPurpose')?.addEventListener('change', () => {
            if (typeof window.uiUpdate?.updateRitualsUI === 'function') {
                window.uiUpdate.updateRitualsUI();
            }
        });
        document.getElementById('ritualSign')?.addEventListener('change', () => {
            if (typeof window.uiUpdate?.updateRitualsUI === 'function') {
                window.uiUpdate.updateRitualsUI();
            }
        });


        // Event listener for knowledge search bar
        const knowledgeSearchBar = document.getElementById('knowledgeSearchBar');
        if (knowledgeSearchBar) {
            knowledgeSearchBar.addEventListener('input', this.filterKnowledgeBase.bind(this));
        }
    },

    async handleHoroscopeFormSubmit(event) {
        if (event) event.preventDefault(); // Only prevent default if it's a form submission directly
        const zodiacSignSelect = document.getElementById('zodiacSignSelect');
        const horoscopeDateInput = document.getElementById('horoscopeDate');
        const horoscopeResults = document.getElementById('horoscopeResults');

        if (!zodiacSignSelect || !horoscopeResults) return;

        const signKey = zodiacSignSelect.value;
        const targetDate = horoscopeDateInput.value;

        if (!signKey) {
            horoscopeResults.innerHTML = '<p class="info-message">Please select a zodiac sign for your daily horoscope.</p>';
            return;
        }

        showLoading('Getting your horoscope...'); // Use imported uiUpdate function
        try {
            // Assuming uiUpdate.displayDailyHoroscopeUI exists and can take signKey and data
            // Or that apiService.fetchDailyHoroscope updates globalState and uiUpdate renders.
            // If uiUpdate.displayDailyHoroscopeUI already fetches, avoid double fetch.
            // For now, let uiUpdate handle the display after fetching.
            await window.uiUpdate.displayDailyHoroscopeUI(signKey, targetDate); // Assuming uiUpdate has this

        } catch (error) {
            console.error('Error fetching daily horoscope:', error);
            displayError('Error fetching horoscope. Please try again.', horoscopeResults); // Use imported uiUpdate function
        } finally {
            hideLoading(); // Use imported uiUpdate function
        }
    },

    // Handles updates for sign combinations
    handleCombinationUpdate() {
        const sunSign = document.getElementById('sunSign')?.value;
        const moonSign = document.getElementById('moonSign')?.value;
        const risingSign = document.getElementById('risingSign')?.value;
        const combinationResultDiv = document.getElementById('combinationResult');

        if (!combinationResultDiv) return;

        if (!sunSign || !moonSign || !risingSign) {
            combinationResultDiv.innerHTML = '<p class="info-message">Select all three signs for analysis.</p>';
            return;
        }

        showLoading('Analyzing combinations...');
        // Directly call uiUpdate's function if it's designed to handle this
        // It's assumed uiUpdate has a function named updateCombinationUI
        if (typeof window.uiUpdate?.updateCombinationUI === 'function') {
            window.uiUpdate.updateCombinationUI();
        } else {
            // Fallback for direct DOM manipulation if uiUpdate function is not found
            const zodiacSigns = this.cachedData.signs;
            let resultHtml = `<h3>Your Cosmic Blueprint</h3>`;
            if (zodiacSigns) {
                resultHtml += `<p><strong>Sun in ${zodiacSigns[sunSign]?.name || sunSign}:</strong> Your core identity and ego.</p>`;
                resultHtml += `<p><strong>Moon in ${zodiacSigns[moonSign]?.name || moonSign}:</strong> Your emotional nature and inner world.</p>`;
                resultHtml += `<p><strong>Rising in ${zodiacSigns[risingSign]?.name || risingSign}:</strong> Your outer personality and how you appear to the world.</p>`;
                resultHtml += `<h4>Combined Energies:</h4><p>The combination of ${zodiacSigns[sunSign]?.name} Sun, ${zodiacSigns[moonSign]?.name} Moon, and ${zodiacSigns[risingSign]?.name} Rising creates a unique astrological signature influencing your personality and destiny.</p>`;
            } else {
                resultHtml += `<p>Zodiac data not loaded, cannot provide detailed combinations.</p>`;
            }
            combinationResultDiv.innerHTML = resultHtml;
        }
        hideLoading();
    },

    // Handles updates for zodiac compatibility
    async handleCompatibilityUpdate() {
        const compatSign1 = document.getElementById('compatSign1')?.value;
        const compatSign2 = document.getElementById('compatSign2')?.value;
        const compatibilityResultsDiv = document.getElementById('compatibilityResults');

        if (!compatibilityResultsDiv) return;

        if (!compatSign1 || !compatSign2) {
            compatibilityResultsDiv.innerHTML = '<p class="info-message">Select two signs for compatibility analysis.</p>';
            return;
        }

        showLoading('Calculating compatibility...');
        try {
            // Directly call uiUpdate's function if it's designed to handle this
            if (typeof window.uiUpdate?.updateCompatibilityUI === 'function') {
                await window.uiUpdate.updateCompatibilityUI();
            } else {
                // Fallback direct update
                const data = this.cachedData.compatibility || await apiService.fetchCompatibilityMatrix();
                if (!this.cachedData.compatibility) this.cachedData.compatibility = data; // Cache if not already

                if (data && data[compatSign1] && data[compatSign1][compatSign2]) {
                    const score = data[compatSign1][compatSign2].overall_score;
                    const advice = data[compatSign1][compatSign2].summary;
                    compatibilityResultsDiv.innerHTML = `<p><strong>Compatibility Score:</strong> ${score}%</p><p><strong>Advice:</strong> ${advice}</p>`;
                } else {
                    compatibilityResultsDiv.innerHTML = '<p>Compatibility data not found for selected signs.</p>';
                }
            }
        } catch (error) {
            console.error('Error fetching compatibility data:', error);
            displayError('Error loading compatibility data. Please try again.', compatibilityResultsDiv);
        } finally {
            hideLoading();
        }
    },

    // Handles Moon & Sun Analysis updates
    async handleMoonSunAnalysisUpdate(event) {
        if (event) event.preventDefault();
        const moonPhaseDatetimeInput = document.getElementById('moonPhaseDatetime');
        const moonPhaseResults = document.getElementById('moonPhaseResults');

        if (!moonPhaseDatetimeInput || !moonPhaseResults) return;

        const datetimeUtcStr = moonPhaseDatetimeInput.value;

        if (!datetimeUtcStr) {
             moonPhaseResults.innerHTML = '<p class="info-message">Please select a date and time for Moon Phase calculation.</p>';
             return;
        }

        showLoading('Calculating moon phase...');
        try {
            // Assuming uiUpdate handles the update of moon phase display based on date
            // The uiUpdate.js provided already has updateMoonPhaseDisplayUI
            window.globalState.selectedCalendarDate = new Date(datetimeUtcStr); // Update globalState for uiUpdate
            await window.uiUpdate.updateMoonPhaseDisplayUI(); // This function will use globalState.selectedCalendarDate
            await window.uiUpdate.updateMoonSunAnalysisUI(); // If this is separate from moon phase

        } catch (error) {
            console.error('Error fetching moon phase:', error);
            displayError('Error calculating moon phase. Please try again.', moonPhaseResults);
        } finally {
            hideLoading();
        }
    },

    // Populates and filters knowledge base
    async populateKnowledgeBase() {
        const knowledgeContentDiv = document.getElementById('knowledgeContent');
        if (!knowledgeContentDiv) {
            console.warn("Knowledge content div 'knowledgeContent' not found.");
            return;
        }

        if (this.cachedData.knowledgeBaseContent.length === 0) {
            // Populate cache if empty
            const zodiacSigns = this.cachedData.signs || window.COSMIC_ORACLE.ALL_ZODIAC_SIGNS_DATA;
            if (!zodiacSigns || Object.keys(zodiacSigns).length === 0) {
                knowledgeContentDiv.innerHTML = '<p>Error loading zodiac knowledge data. Please refresh.</p>';
                return;
            }

            this.cachedData.knowledgeBaseContent = Object.values(zodiacSigns).map(sign => {
                const elementHtml = sign.element ? `<p><strong>Element:</strong> ${sign.element}</p>` : '';
                const qualityHtml = sign.quality ? `<p><strong>Quality (Modality):</strong> ${sign.quality}</p>` : '';
                const rulerHtml = sign.ruler ? `<p><strong>Ruling Planet:</strong> ${sign.ruler}</p>` : '';
                const keywordsHtml = (sign.keywords && sign.keywords.length > 0) ? `<p><strong>Keywords:</strong> ${sign.keywords.join(', ')}</p>` : '';
                const descriptionHtml = sign.description ? `<p>${sign.description}</p>` : '<p>No description available.</p>';
                const strengthsHtml = (sign.strengths && sign.strengths.length > 0) ? `<h4>Strengths:</h4><p>${sign.strengths.join(', ')}.</p>` : '';
                const weaknessesHtml = (sign.weaknesses && sign.weaknesses.length > 0) ? `<h4>Weaknesses (Areas for Awareness & Growth):</h4><p>${sign.weaknesses.join(', ')}.</p>` : '';
                const crystalsHtml = (sign.crystals && sign.crystals.length > 0) ? `<h4>Harmonizing Crystals:</h4><p>${sign.crystals.join(', ')}.</p>` : '';
                const mantraHtml = sign.mantra ? `<h4>Affirmation/Mantra:</h4><p>"<em>${sign.mantra}</em>"</p>` : '';

                // Combine all content into a single string for keyword searching
                const fullText = `${sign.name} ${sign.element} ${sign.quality} ${sign.ruler} ${sign.keywords?.join(' ')} ${sign.description} ${sign.strengths?.join(' ')} ${sign.weaknesses?.join(' ')} ${sign.crystals?.join(' ')} ${sign.mantra}`.toLowerCase();

                return {
                    id: sign.name.toLowerCase().replace(/\s/g, '-'), // Unique ID for later DOM manipulation
                    html: `
                        <div class="knowledge-section" data-sign-id="${sign.name.toLowerCase().replace(/\s/g, '-')}" style="display: block;">
                            <h3 class="knowledge-title">${sign.symbol || '?'} ${sign.name} (${sign.dates || 'N/A'})</h3>
                            <div class="element-card">
                                ${elementHtml}${qualityHtml}${rulerHtml}${keywordsHtml}
                            </div>
                            <div class="interpretation" style="margin-top:15px;">
                                ${descriptionHtml}${strengthsHtml}${weaknessesHtml}${crystalsHtml}${mantraHtml}
                            </div>
                        </div>
                    `,
                    searchableText: fullText // For filtering
                };
            });
        }

        // Render all content from cache initially
        knowledgeContentDiv.innerHTML = this.cachedData.knowledgeBaseContent.map(item => item.html).join('');
        this.filterKnowledgeBase(); // Apply any existing filter
        console.log("Knowledge base populated/refreshed.");
    },

    filterKnowledgeBase() {
        const searchBar = document.getElementById('knowledgeSearchBar');
        const knowledgeContentDiv = document.getElementById('knowledgeContent');
        if (!searchBar || !knowledgeContentDiv) return;

        const searchTerm = searchBar.value.toLowerCase().trim();
        const knowledgeSections = knowledgeContentDiv.querySelectorAll('.knowledge-section');

        if (!this.cachedData.knowledgeBaseContent || this.cachedData.knowledgeBaseContent.length === 0) {
            // If cache is empty, try to populate it, then re-filter
            this.populateKnowledgeBase(); // THIS LINE NO LONGER CAUSES SYNTAX ERROR
            return; // Exit to avoid double processing before populateKnowledgeBase finishes
        }

        // If there's a search term, filter by showing/hiding elements
        if (searchTerm) {
            let foundMatch = false;
            knowledgeSections.forEach(section => {
                const signId = section.getAttribute('data-sign-id');
                const cachedItem = this.cachedData.knowledgeBaseContent.find(item => item.id === signId);

                if (cachedItem && cachedItem.searchableText.includes(searchTerm)) {
                    section.style.display = 'block';
                    foundMatch = true;
                } else {
                    section.style.display = 'none';
                }
            });

            if (!foundMatch) {
                // If no direct matches, check if any section is already showing and make sure the message is not duplicated.
                const noMatchMsg = knowledgeContentDiv.querySelector('.no-match-message');
                if (!noMatchMsg) {
                    knowledgeContentDiv.innerHTML += '<p class="no-match-message">No matching knowledge found.</p>';
                }
            } else {
                // If matches are found, remove the "no match" message if it exists
                const noMatchMsg = knowledgeContentDiv.querySelector('.no-match-message');
                if (noMatchMsg) noMatchMsg.remove();
            }

        } else {
            // If search term is empty, show all content
            knowledgeSections.forEach(section => {
                section.style.display = 'block';
            });
            const noMatchMsg = knowledgeContentDiv.querySelector('.no-match-message');
            if (noMatchMsg) noMatchMsg.remove();
        }
    }
};