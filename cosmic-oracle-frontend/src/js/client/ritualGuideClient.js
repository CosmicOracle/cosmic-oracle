// Filename: ritualGuide.js

/**
 * Manages the Sacred Rituals & Ceremonies feature:
 * - Initializes UI elements and event listeners.
 * - Fetches and displays ritual suggestions based on purpose and zodiac sign.
 * - Handles daily affirmation generation.
 */

/**
 * Initializes the Sacred Rituals feature.
 */
function initRitualGuideFeature() {
    const purposeSelect = document.getElementById('ritualPurpose');
    const signSelect = document.getElementById('ritualSign');
    const affirmationButton = document.getElementById('generateAffirmationBtn'); // Assuming this ID for the button

    if (purposeSelect) {
        purposeSelect.addEventListener('change', handleRitualSelectionChange);
    } else {
        console.error("Ritual purpose selector 'ritualPurpose' not found.");
    }

    if (signSelect) {
        populateRitualZodiacSelector(); // Populate with zodiac signs
        signSelect.addEventListener('change', handleRitualSelectionChange);
    } else {
        console.error("Ritual zodiac sign selector 'ritualSign' not found.");
    }

    if (affirmationButton) {
        affirmationButton.addEventListener('click', displayDailyAffirmation);
    } else {
        // If using onclick="generateAffirmationUI()" in HTML from oracle.html
        console.warn("Generate Affirmation button 'generateAffirmationBtn' not found. Ensure HTML is updated or use direct onclick for displayDailyAffirmation.");
    }

    // Initial call to display default or empty state for rituals
    handleRitualSelectionChange();
    // Initial call for daily affirmation
    displayDailyAffirmation();
}

/**
 * Populates the zodiac sign selector in the Rituals tab.
 */
function populateRitualZodiacSelector() {
    const selector = document.getElementById('ritualSign');
    if (!selector) return;

    if (ALL_ZODIAC_SIGNS_DATA && typeof ALL_ZODIAC_SIGNS_DATA === 'object') {
        // Preserve the "Select Sign" option if it exists, or add it
        let firstOptionHTML = '<option value="">Select Sign (Optional)</option>';
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
        console.warn("ALL_ZODIAC_SIGNS_DATA not available for ritual zodiac selector.");
    }
}

/**
 * Handles changes in ritual purpose or sign selectors and fetches ritual guidance.
 */
async function handleRitualSelectionChange() {
    const purpose = document.getElementById('ritualPurpose')?.value;
    const signKey = document.getElementById('ritualSign')?.value; // Can be empty if "Select Sign (Optional)"
    const container = document.getElementById('ritualInstructions');

    if (!container) {
        console.error("Ritual instructions container 'ritualInstructions' not found.");
        return;
    }

    if (!purpose) { // Purpose is mandatory for a meaningful ritual suggestion
        container.innerHTML = '<p>Please select a ritual purpose to receive guidance.</p>';
        return;
    }
    // If signKey is empty, the backend should ideally handle providing a general ritual for the purpose.
    // The current backend `ritual_service.py` requires a zodiac_sign_key.
    // We'll proceed, and the backend will return an error if the sign is missing and it needs one.
    // Or, we can make signKey mandatory here if the backend strictly requires it.
    // For now, let's allow it to be optional and see if backend handles it.
    // If your backend requires a sign, uncomment the next block:
    /*
    if (!signKey) {
        container.innerHTML = '<p>Please select your Zodiac sign along with the ritual purpose for personalized guidance.</p>';
        return;
    }
    */


    container.innerHTML = '<p>Crafting your sacred ritual guidance...</p>';

    try {
        const ritualData = await fetchRitualSuggestionAPI(purpose, signKey || "general"); // Pass "general" or handle null in backend if sign is optional

        if (ritualData.error) {
            // If the error is due to missing sign, and sign is optional, provide a gentler message.
            if (ritualData.error.toLowerCase().includes("invalid zodiac sign key") && !signKey) {
                 container.innerHTML = `<p>Please select your Zodiac sign for a more personalized ${purpose.replace('-', ' ')} ritual, or a general version will be shown if available.</p><p style="color:orange;">Note: Currently, a sign selection might be required for this purpose.</p>`;
            } else {
                throw new Error(ritualData.error);
            }
        } else {
            let ritualHTML = `<h3>${ritualData.title || 'Sacred Ritual'}</h3>`;
            if (ritualData.description) {
                ritualHTML += `<p>${ritualData.description}</p>`;
            }

            if (ritualData.general_preparation && Array.isArray(ritualData.general_preparation)) {
                ritualHTML += `<h4>General Preparation:</h4><ul>`;
                ritualData.general_preparation.forEach(prep => ritualHTML += `<li>${prep}</li>`);
                ritualHTML += `</ul>`;
            }

            if (ritualData.steps && Array.isArray(ritualData.steps)) {
                ritualHTML += `<h4>Ritual Steps:</h4><ol>`;
                ritualData.steps.forEach(step => ritualHTML += `<li>${step}</li>`);
                ritualHTML += `</ol>`;
            }

            if (ritualData.sign_data && ritualData.elemental_enhancement) {
                ritualHTML += `<h4>${ritualData.sign_data.name || 'Zodiac'} (${ritualData.sign_data.element || ''}, ${ritualData.sign_data.quality || ''}) Enhancement:</h4><p>${ritualData.elemental_enhancement}</p>`;
            }

            if (ritualData.affirmation_template) {
                ritualHTML += `<p style="margin-top:10px;"><strong>Affirm:</strong> "<em>${ritualData.affirmation_template}</em>"</p>`;
            }

            if (ritualData.safety_note) {
                ritualHTML += `<p style="margin-top:15px; font-size:0.9em;"><em>${ritualData.safety_note}</em></p>`;
            }
            container.innerHTML = ritualHTML;
        }

    } catch (error) {
        console.error("Error updating rituals UI:", error);
        container.innerHTML = `<p style="color: red;">Could not load ritual guidance: ${error.message}</p>`;
    }
}

/**
 * Fetches and displays a new daily affirmation.
 */
async function displayDailyAffirmation() {
    const affirmationEl = document.getElementById('dailyAffirmation');
    if (!affirmationEl) {
        console.error("Daily affirmation display element 'dailyAffirmation' not found.");
        return;
    }
    affirmationEl.textContent = "Summoning cosmic wisdom...";

    try {
        const data = await fetchRandomAffirmation(); // from apiService.js
        affirmationEl.textContent = data.affirmation || "Embrace the positive energy within and around you today.";
    } catch (error) {
        console.error("Error fetching/displaying affirmation:", error);
        affirmationEl.textContent = "Could not load affirmation. Remember: You are resilient and capable.";
    }
}

// Expose main function to be callable from script.js or HTML
window.initRitualGuideFeature = initRitualGuideFeature;
window.displayDailyAffirmation = displayDailyAffirmation; // If called by onclick in HTML
// handleRitualSelectionChange is called by event listeners, no need to expose if button ID is used.
