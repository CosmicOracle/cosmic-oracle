// Filename: tarotInteractive.js

/**
 * Manages the Tarot Reading feature:
 * - Initializes UI elements and event listeners.
 * - Handles card drawing and display.
 * - Manages saving and loading user's tarot readings.
 */

// Store the current reading data to be potentially saved
let currentReadingDataForSave = null;

/**
 * Initializes the Tarot Reading feature.
 * Sets up event listeners for spread selection, draw button, save button.
 * Loads saved readings if the user is logged in.
 */
function initTarotFeature() {
    const spreadSelect = document.getElementById('tarotSpread');
    const drawButton = document.getElementById('drawTarotBtnActual'); // Assumes this ID from uiUpdate.js
    const saveButton = document.getElementById('saveTarotReadingBtn');

    if (spreadSelect) {
        spreadSelect.addEventListener('change', setupTarotSpreadLayout);
    } else {
        console.error("Tarot spread selector 'tarotSpread' not found.");
    }

    if (drawButton) {
        drawButton.addEventListener('click', handleDrawAndDisplayReading);
    } else {
        // If the button is dynamically added by uiUpdate.js, this listener might need to be attached there
        // or use event delegation on a parent element.
        // For now, assuming it might exist or be added.
        console.warn("Draw Tarot Button 'drawTarotBtnActual' not found on init. Ensure it exists or is added dynamically with its event listener.");
    }

    if (saveButton) {
        saveButton.addEventListener('click', handleSaveReading);
        saveButton.style.display = 'none'; // Initially hidden
    } else {
        console.error("Save Tarot Reading button 'saveTarotReadingBtn' not found.");
    }

    setupTarotSpreadLayout(); // Initial layout based on default spread
    if (currentUser && currentUser.id) {
        displaySavedReadings();
    } else {
        const savedReadingsContainer = document.getElementById('savedTarotReadingsContainer');
        if (savedReadingsContainer) {
            savedReadingsContainer.innerHTML = "<h4>Your Saved Tarot Readings:</h4><p>Login to save and view your readings.</p>";
        }
    }
}

/**
 * Sets up the visual layout for the selected tarot spread (card placeholders).
 */
function setupTarotSpreadLayout() {
    const spreadType = document.getElementById('tarotSpread')?.value || 'single';
    const cardsContainer = document.getElementById('tarotCards');
    const interpretationContainer = document.getElementById('tarotInterpretation');
    const saveButton = document.getElementById('saveTarotReadingBtn');

    if (!cardsContainer || !interpretationContainer) {
        console.error("Tarot cards or interpretation container not found.");
        return;
    }

    cardsContainer.innerHTML = ''; // Clear previous cards
    currentReadingDataForSave = null; // Reset current reading
    if (saveButton) saveButton.style.display = 'none';

    const spreadConfigs = {
        'single': { cards: 1, positions: ['Guidance for the Moment'] },
        'three': { cards: 3, positions: ['Past Influence', 'Present Situation', 'Future Potential'] },
        'celtic': { cards: 10, positions: ['1. You/Situation', '2. Challenge/Crossing', '3. Foundation/Past', '4. Recent Past/Passing', '5. Crown/Potential Outcome', '6. Near Future/Approaching', '7. Your Attitude/Self', '8. External Influences/Environment', '9. Hopes & Fears', '10. Final Outcome'] },
        'love': { cards: 5, positions: ['1. Your Energy in Love', '2. Partner\'s Energy (or Desired)', '3. Dynamics of Connection', '4. Challenge/Growth Area', '5. Potential Outcome'] },
        'career': { cards: 4, positions: ['1. Current Career Situation', '2. Obstacles/Challenges', '3. Action/Guidance', '4. Potential Outcome'] }
    };

    const config = spreadConfigs[spreadType];
    if (!config) {
        interpretationContainer.innerHTML = '<p>Invalid spread type selected.</p>';
        return;
    }

    for (let i = 0; i < config.cards; i++) {
        const cardWrapper = document.createElement('div');
        cardWrapper.style.textAlign = 'center';
        cardWrapper.style.margin = '5px';
        cardWrapper.style.display = 'inline-block'; // For better layout control

        const cardEl = document.createElement('div');
        cardEl.className = 'tarot-card'; // From style.css
        // Display a generic card back or symbol before revealing
        cardEl.innerHTML = `<div style="font-size: 2.5em; margin: auto;">🎴</div>`;
        cardEl.title = `Click to reveal ${config.positions[i]}`;

        const positionText = document.createElement('p');
        positionText.textContent = config.positions[i];
        positionText.style.fontSize = '0.8rem';
        positionText.style.marginTop = '5px';

        cardWrapper.appendChild(cardEl);
        cardWrapper.appendChild(positionText);
        cardsContainer.appendChild(cardWrapper);
    }
    interpretationContainer.innerHTML = `<p>You've selected the <strong>${spreadType.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</strong> spread. Click "Draw Cards" to begin.</p>`;
}


/**
 * Handles drawing cards, fetching the reading from the API, and displaying it.
 */
async function handleDrawAndDisplayReading() {
    const spreadType = document.getElementById('tarotSpread')?.value || 'single';
    const cardsContainer = document.getElementById('tarotCards');
    const interpretationContainer = document.getElementById('tarotInterpretation');
    const saveButton = document.getElementById('saveTarotReadingBtn');

    if (!cardsContainer || !interpretationContainer) {
        console.error("Tarot cards or interpretation container not found for drawing.");
        return;
    }

    cardsContainer.innerHTML = '<p>Shuffling the cosmic deck and drawing your cards...</p>';
    interpretationContainer.innerHTML = ''; // Clear previous interpretation

    try {
        const readingResult = await performTarotReadingAPI(spreadType); // from apiService.js
        if (readingResult.error) {
            throw new Error(readingResult.error);
        }

        currentReadingDataForSave = readingResult; // Store for potential saving
        cardsContainer.innerHTML = ''; // Clear loading message

        interpretationContainer.innerHTML = `<h3>${readingResult.spread_type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Reading:</h3>`;

        readingResult.cards.forEach(cardDetail => {
            const cardWrapper = document.createElement('div');
            cardWrapper.style.textAlign = 'center';
            cardWrapper.style.margin = '5px';
            cardWrapper.style.display = 'inline-block';

            const cardEl = document.createElement('div');
            cardEl.className = 'tarot-card'; // From style.css
            cardEl.innerHTML = `
                <div style="font-size: 0.9rem; text-align: center; padding: 5px; display: flex; flex-direction: column; justify-content: space-around; height: 100%;">
                    <div style="font-weight: bold; margin-bottom: 5px; font-size: 0.8em;">${cardDetail.card_name}</div>
                    <div style="font-size: 2.5em; margin: 5px 0;">${cardDetail.symbol || '🎴'}</div>
                    ${cardDetail.is_reversed ? '<div style="font-size: 0.7em; color: #ff6b6b;">(Reversed)</div>' : ''}
                </div>`;
            // Style for revealed card
            cardEl.style.background = 'linear-gradient(135deg, #fffacd, #ffe4b5)';
            cardEl.style.color = '#4a148c';
            cardEl.title = `${cardDetail.card_name} - ${cardDetail.position_name}`;

            const positionText = document.createElement('p');
            positionText.textContent = cardDetail.position_name;
            positionText.style.fontSize = '0.8rem';
            positionText.style.marginTop = '5px';

            cardWrapper.appendChild(cardEl);
            cardWrapper.appendChild(positionText);
            cardsContainer.appendChild(cardWrapper);

            // Append interpretation for this card
            interpretationContainer.innerHTML += `
                <div class="interpretation" style="margin-bottom: 10px; padding: 10px; background: rgba(255,255,255,0.08); border-radius: 8px;">
                    <h4>${cardDetail.position_name}: ${cardDetail.card_name} ${cardDetail.is_reversed ? '(R)' : ''} ${cardDetail.symbol || ''}</h4>
                    <p><strong>Meaning:</strong> ${cardDetail.interpretation || 'Interpretation not available.'}</p>
                </div>`;
        });

        if (currentUser && currentUser.id && saveButton) {
            saveButton.style.display = 'block'; // Show save button
            saveButton.style.marginLeft = 'auto';
            saveButton.style.marginRight = 'auto';
        }

    } catch (error) {
        console.error("Error performing tarot reading:", error);
        interpretationContainer.innerHTML = `<p style="color: red;">Could not perform reading: ${error.message}</p>`;
        if (saveButton) saveButton.style.display = 'none';
    }
}

/**
 * Handles saving the current tarot reading.
 */
async function handleSaveReading() {
    if (!currentUser || !currentUser.id) {
        alert("Please login to save your tarot reading.");
        // Optionally, trigger login form display
        if (typeof showLoginForm === 'function') showLoginForm();
        return;
    }

    if (!currentReadingDataForSave || !currentReadingDataForSave.cards || currentReadingDataForSave.cards.length === 0) {
        alert("No reading to save. Please draw cards first.");
        return;
    }

    const questionInput = document.getElementById('tarotQuestion');
    const questionAsked = questionInput ? questionInput.value.trim() : 'General Guidance';

    const userNotes = prompt("Add any personal notes or reflections for this reading (optional):", "");
    if (userNotes === null) return; // User cancelled prompt

    const readingToSave = {
        spread_type: currentReadingDataForSave.spread_type,
        cards: currentReadingDataForSave.cards.map(card => ({ // Ensure only necessary fields are saved
            position_name: card.position_name,
            card_name: card.card_name,
            symbol: card.symbol,
            is_reversed: card.is_reversed,
            interpretation: card.interpretation // Backend might re-interpret or store this
        })),
        question_asked: questionAsked,
        user_notes: userNotes || "" // Ensure it's a string
    };

    try {
        const result = await saveTarotReadingAPI(readingToSave); // from apiService.js
        alert(result.message || "Reading saved successfully!");
        displaySavedReadings(); // Refresh the list of saved readings
    } catch (error) {
        console.error("Error saving tarot reading:", error);
        alert(`Failed to save reading: ${error.message || 'Please try again.'}`);
    }
}

/**
 * Fetches and displays the user's saved tarot readings.
 */
async function displaySavedReadings() {
    const container = document.getElementById('savedTarotReadingsContainer');
    if (!container) {
        console.error("Saved readings container 'savedTarotReadingsContainer' not found.");
        return;
    }

    if (!currentUser || !currentUser.id) {
        container.innerHTML = "<h4>Your Saved Tarot Readings:</h4><p>Login to view and save your readings.</p>";
        return;
    }

    container.innerHTML = '<h4>Your Saved Tarot Readings:</h4><p>Loading your saved readings...</p>';

    try {
        const readings = await fetchSavedTarotReadingsAPI(); // from apiService.js
        if (readings && readings.length > 0) {
            container.innerHTML = '<h4>Your Saved Tarot Readings:</h4>'; // Clear loading message
            readings.forEach(reading => {
                const readingDiv = document.createElement('div');
                readingDiv.className = 'journal-entry'; // Re-use journal entry styling for consistency
                let readingHTML = `
                    <p>
                        <strong>${reading.spread_type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</strong> - 
                        Saved: ${new Date(reading.created_at).toLocaleDateString()}
                    </p>`;
                if (reading.question_asked) {
                    readingHTML += `<p><em>Question: ${reading.question_asked}</em></p>`;
                }
                if (reading.cards_drawn && Array.isArray(reading.cards_drawn)) {
                    readingHTML += '<ul style="list-style-type: none; padding-left: 0;">';
                    reading.cards_drawn.forEach(card => {
                        readingHTML += `
                            <li style="margin-bottom: 5px;">
                                <strong>${card.position_name || 'Card'}: ${card.card_name} ${card.is_reversed ? '(R)' : ''} ${card.symbol || ''}</strong>
                                <br><small>${card.interpretation ? card.interpretation.substring(0, 120) + (card.interpretation.length > 120 ? '...' : '') : 'No interpretation summary.'}</small>
                            </li>`;
                    });
                    readingHTML += '</ul>';
                }
                if (reading.interpretation_notes) { // Changed from user_notes to match backend model
                    readingHTML += `<p><strong>Your Notes:</strong> ${reading.interpretation_notes}</p>`;
                }
                readingHTML += `
                    <button onclick="handleDeleteReading(${reading.id})" 
                            style="background: #c0392b; color: white; border: none; padding: 5px 10px; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 5px; font-size: 0.8em;">
                        Delete
                    </button>`;
                readingDiv.innerHTML = readingHTML;
                container.appendChild(readingDiv);
            });
        } else {
            container.innerHTML = '<h4>Your Saved Tarot Readings:</h4><p>No saved readings found. Perform a reading and click "Save This Reading" to store it here.</p>';
        }
    } catch (error) {
        console.error("Error loading saved tarot readings:", error);
        container.innerHTML = `<h4>Your Saved Tarot Readings:</h4><p style="color: red;">Could not load readings: ${error.message}</p>`;
    }
}

/**
 * Handles deleting a saved tarot reading.
 * @param {number} readingId - The ID of the reading to delete.
 */
async function handleDeleteReading(readingId) {
    if (!confirm('Are you sure you want to delete this tarot reading permanently?')) {
        return;
    }
    try {
        const result = await deleteTarotReadingAPI(readingId); // from apiService.js
        alert(result.message || "Reading deleted successfully.");
        displaySavedReadings(); // Refresh the list
    } catch (error) {
        console.error("Error deleting tarot reading:", error);
        alert(`Failed to delete reading: ${error.message || 'Please try again.'}`);
    }
}

// Make init function globally available if script.js calls it by this name for this feature
window.initTarotFeature = initTarotFeature;
// Expose functions that might be called from HTML onclick attributes if that pattern is used
window.handleDeleteReading = handleDeleteReading;
