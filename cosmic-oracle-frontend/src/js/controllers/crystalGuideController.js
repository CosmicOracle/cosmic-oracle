// Filename: crystalGuideController.js

/**
 * Manages the Crystal Healing & Guidance feature:
 * - Populates zodiac sign selector.
 * - Fetches and displays crystal recommendations based on sign and/or need.
 */

/**
 * Initializes the Crystal Guide feature.
 * Sets up event listeners for the selection dropdowns.
 */
function initCrystalGuideFeature() {
    const signSelect = document.getElementById('crystalSign');
    const needSelect = document.getElementById('crystalNeed');

    if (signSelect) {
        populateCrystalZodiacSelector(); // Populate with zodiac signs
        signSelect.addEventListener('change', handleCrystalSelectionChange);
    } else {
        console.error("Crystal zodiac sign selector 'crystalSign' not found.");
    }

    if (needSelect) {
        needSelect.addEventListener('change', handleCrystalSelectionChange);
    } else {
        console.error("Crystal need selector 'crystalNeed' not found.");
    }

    // Initial call to display default or empty state
    handleCrystalSelectionChange();
}

/**
 * Populates the zodiac sign selector in the Crystal Guide tab.
 */
function populateCrystalZodiacSelector() {
    const selector = document.getElementById('crystalSign');
    if (!selector) return;

    if (ALL_ZODIAC_SIGNS_DATA && typeof ALL_ZODIAC_SIGNS_DATA === 'object') {
        // Preserve the "Select Sign" option if it exists, or add it
        let firstOptionHTML = '<option value="">Any Sign / No Specific Sign</option>';
        if (selector.options.length > 0 && selector.options[0].value === "") {
            firstOptionHTML = selector.options[0].outerHTML;
        }
        selector.innerHTML = firstOptionHTML;

        Object.entries(ALL_ZODIAC_SIGNS_DATA).forEach(([key, sign]) => {
            if (sign && sign.name) { // Ensure sign object and name exist
                const option = document.createElement('option');
                option.value = key;
                option.textContent = `${sign.symbol || '?'} ${sign.name}`;
                selector.appendChild(option);
            }
        });
    } else {
        selector.innerHTML = '<option value="">Zodiac Data Error</option>';
        console.warn("ALL_ZODIAC_SIGNS_DATA not available for crystal zodiac selector.");
    }
}

/**
 * Handles changes in the crystal sign or need selectors and fetches recommendations.
 */
async function handleCrystalSelectionChange() {
    const signKey = document.getElementById('crystalSign')?.value || ""; // Default to empty string if null
    const needKey = document.getElementById('crystalNeed')?.value || ""; // Default to empty string if null
    const container = document.getElementById('crystalRecommendations');

    if (!container) {
        console.error("Crystal recommendations container not found.");
        return;
    }

    if (!signKey && !needKey) {
        container.innerHTML = '<p>Select your zodiac sign or a current need for crystal recommendations.</p>';
        return;
    }

    container.innerHTML = '<p>Summoning crystal wisdom...</p>';

    try {
        // fetchCrystalRecommendationsAPI expects null if not provided, not empty string.
        const effectiveSignKey = signKey === "" ? null : signKey;
        const effectiveNeedKey = needKey === "" ? null : needKey;

        const data = await fetchCrystalRecommendationsAPI(effectiveSignKey, effectiveNeedKey); // from apiService.js

        if (data.error) {
            throw new Error(data.error);
        }

        if (data.recommendations && data.recommendations.length > 0) {
            container.innerHTML = data.recommendations.map(crystal => {
                // Ensure key_properties is an array before joining
                let propertiesString = 'General harmonizing properties.';
                if (crystal.key_properties) {
                    if (Array.isArray(crystal.key_properties)) {
                        propertiesString = crystal.key_properties.join('; ');
                    } else if (typeof crystal.key_properties === 'string') {
                        propertiesString = crystal.key_properties;
                    }
                }

                let chakraString = 'Varies';
                if (crystal.chakra_association) {
                    if (Array.isArray(crystal.chakra_association)) {
                        chakraString = crystal.chakra_association.join(', ');
                    } else if (typeof crystal.chakra_association === 'string') {
                        chakraString = crystal.chakra_association;
                    }
                }

                return `
                <div class="crystal-card">
                    <h4>${crystal.name || 'Unknown Crystal'} ${crystal.image_placeholder_symbol || ''}</h4>
                    <p style="font-size:0.9em;"><strong>Properties:</strong> ${propertiesString}</p>
                    <p style="font-size:0.9em;"><strong>Chakra(s):</strong> ${chakraString}</p>
                    <p style="font-size:0.9em;"><strong>Reason for Recommendation:</strong> ${crystal.reason || 'Generally beneficial.'}</p>
                    <p style="font-size:0.8em; margin-top:5px;"><em>Affirm: "${crystal.affirmation || 'I am aligned with this crystal\'s healing energy.'}"</em></p>
                </div>`;
            }).join('');
        } else {
            container.innerHTML = '<p>No specific crystal recommendations found for your selection. Consider Clear Quartz or Selenite for general well-being and amplification.</p>';
        }
    } catch (error) {
        console.error("Error fetching crystal recommendations:", error);
        container.innerHTML = `<p style="color: red;">Could not load crystal guidance: ${error.message}</p>`;
    }
}

// Expose init function to be callable from script.js
window.initCrystalGuideFeature = initCrystalGuideFeature;

// Expose handler if it's directly called by onchange in HTML (though event listeners are preferred)
// window.handleCrystalSelectionChange = handleCrystalSelectionChange; // Not strictly needed if using event listeners set in init

