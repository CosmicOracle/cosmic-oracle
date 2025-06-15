// Filename: dreamAnalyzer.js

/**
 * Manages the Dream Analysis feature:
 * - Populates common dream symbols.
 * - Analyzes dream descriptions based on symbols and mood.
 * - Saves dream analysis to journal if user is logged in.
 */

/**
 * Initializes the Dream Analysis feature.
 * Sets up event listeners and populates the symbol grid.
 */
function initDreamAnalysisFeature() {
    const analyzeButton = document.getElementById('analyzeDreamBtn'); // Recommended ID
    const dreamDescriptionInput = document.getElementById('dreamDescription');
    const dreamDateInput = document.getElementById('dreamDateInput');

    if (analyzeButton) {
        analyzeButton.addEventListener('click', handleDreamAnalysis);
    } else {
        // If using onclick="analyzeDreamUI()" in HTML, ensure handleDreamAnalysis is global
        // For this controller, we'll make handleDreamAnalysis available globally.
        console.log("Dream Analyze button 'analyzeDreamBtn' not found. Ensure HTML is updated or use direct onclick for handleDreamAnalysis.");
    }

    if (dreamDescriptionInput) {
        // Optional: Add any specific listeners to dreamDescriptionInput if needed
    }

    if (dreamDateInput && !dreamDateInput.value) {
        dreamDateInput.value = new Date().toISOString().split('T')[0]; // Default to today
    }

    populateDreamSymbolsForSelection();
    clearDreamAnalysisDisplay(); // Clear previous analysis on tab load
}

/**
 * Populates the grid with clickable dream symbols.
 */
function populateDreamSymbolsForSelection() {
    const container = document.getElementById('dreamSymbolsGrid');
    if (!container) {
        console.error("Dream symbols grid container 'dreamSymbolsGrid' not found.");
        return;
    }

    if (!ALL_DREAM_SYMBOLS_DATA || typeof ALL_DREAM_SYMBOLS_DATA !== 'object') {
        container.innerHTML = '<h4>Common Dream Symbols:</h4><p>Dream symbol data not available. Please try refreshing.</p>';
        return;
    }

    let headerHTML = '<h4>Common Dream Symbols (click to add to description):</h4>';
    container.innerHTML = headerHTML; // Clear previous symbols but keep header

    Object.keys(ALL_DREAM_SYMBOLS_DATA).sort().forEach(symbolKey => {
        const symbolData = ALL_DREAM_SYMBOLS_DATA[symbolKey];
        const card = document.createElement('div');
        card.className = 'symbol-card'; // From style.css
        card.textContent = symbolKey.charAt(0).toUpperCase() + symbolKey.slice(1);
        card.title = symbolData?.general_meaning ? `Click to add '${symbolKey}'. Meaning: ${symbolData.general_meaning.substring(0, 100)}...` : `Click to add '${symbolKey}'`;
        card.onclick = () => {
            const dreamDescTextarea = document.getElementById('dreamDescription');
            if (dreamDescTextarea) {
                const currentText = dreamDescTextarea.value;
                const selectionStart = dreamDescTextarea.selectionStart || currentText.length; // Default to end if no selection
                const selectionEnd = dreamDescTextarea.selectionEnd || currentText.length;
                const spaceBefore = (selectionStart > 0 && currentText[selectionStart - 1] !== ' ' && currentText[selectionStart -1] !== '\n') ? ' ' : '';
                const textToInsert = spaceBefore + symbolKey + ' ';

                dreamDescTextarea.value = currentText.substring(0, selectionStart) + textToInsert + currentText.substring(selectionEnd);
                dreamDescTextarea.focus();
                // Move cursor to after the inserted text
                const newCursorPosition = selectionStart + textToInsert.length;
                dreamDescTextarea.setSelectionRange(newCursorPosition, newCursorPosition);
            }
        };
        container.appendChild(card);
    });
}

/**
 * Clears the dream analysis display area.
 */
function clearDreamAnalysisDisplay() {
    const analysisContainer = document.getElementById('dreamAnalysisResult');
    if (analysisContainer) {
        analysisContainer.innerHTML = "<p>Enter your dream details above and click \"Analyze Dream\" to receive a comprehensive symbolic interpretation.</p>";
    }
}

/**
 * Handles the dream analysis process.
 */
async function handleDreamAnalysis() {
    const descriptionInput = document.getElementById('dreamDescription');
    const moodInput = document.getElementById('dreamMoodSelect');
    const dreamDateInput = document.getElementById('dreamDateInput');
    const analysisContainer = document.getElementById('dreamAnalysisResult');

    if (!descriptionInput || !moodInput || !dreamDateInput || !analysisContainer) {
        console.error("One or more dream analysis form elements are missing.");
        if(analysisContainer) analysisContainer.innerHTML = "<p style='color:red;'>Error: UI elements missing for analysis.</p>";
        return;
    }

    const description = descriptionInput.value.trim();
    const mood = moodInput.value;
    const dreamDate = dreamDateInput.value || new Date().toISOString().split('T')[0];

    if (!ALL_DREAM_SYMBOLS_DATA) {
        analysisContainer.innerHTML = "<p style='color:red;'>Dream symbol data is not loaded. Cannot perform analysis. Please refresh.</p>";
        return;
    }
    if (description === '') {
        analysisContainer.innerHTML = '<p>Please describe your dream in detail for analysis.</p>';
        return;
    }

    analysisContainer.innerHTML = '<p>Analyzing your dream\'s cosmic whispers...</p>';

    let identifiedSymbols = [];
    let interpretationText = `<h4>Dream Analysis for ${new Date(dreamDate + 'T00:00:00Z').toLocaleDateString(undefined, {timeZone:'UTC'})} (Mood: ${mood})</h4>`;
    interpretationText += `<p><strong>Your Dream:</strong><br> "<em>${description.replace(/\n/g, '<br>')}</em>"</p>`;

    Object.entries(ALL_DREAM_SYMBOLS_DATA).forEach(([symbolKey, symbolData]) => {
        // Use a regex that matches whole words only, case-insensitive
        const regex = new RegExp(`\\b${symbolKey.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')}\\b`, 'gi');
        if (description.match(regex) && symbolData && symbolData.general_meaning) {
            identifiedSymbols.push({
                symbol: symbolKey.charAt(0).toUpperCase() + symbolKey.slice(1),
                meaning: symbolData.general_meaning,
                positive: symbolData.positive_connotations || [],
                negative: symbolData.negative_connotations || [],
                questions: symbolData.questions_for_reflection || []
            });
        }
    });

    if (identifiedSymbols.length > 0) {
        interpretationText += '<p><strong>Potential Symbols Identified & General Meanings:</strong></p><ul>';
        identifiedSymbols.forEach(item => {
            interpretationText += `<li><strong>${item.symbol}:</strong> ${item.meaning}</li>`;
            if (item.positive.length > 0 && mood === 'positive') { // Show positive if mood matches
                interpretationText += `<small><em>Positive aspects might involve: ${item.positive.slice(0,2).join('; ')}.</em></small><br/>`;
            }
            if (item.negative.length > 0 && mood === 'negative') { // Show negative if mood matches
                interpretationText += `<small><em>Negative aspects could relate to: ${item.negative.slice(0,2).join('; ')}.</em></small><br/>`;
            }
        });
        interpretationText += '</ul>';
    } else {
        interpretationText += '<p>No specific common symbols matched from our database based on exact keywords. Consider the overall narrative and feelings of the dream.</p>';
    }

    let moodInterpretationText = "Your emotional state during the dream significantly colors its meaning.";
    if (ALL_HOROSCOPE_INTERPRETATIONS && ALL_HOROSCOPE_INTERPRETATIONS.dream_mood_interpretations && ALL_HOROSCOPE_INTERPRETATIONS.dream_mood_interpretations[mood.toLowerCase()]) {
        moodInterpretationText = ALL_HOROSCOPE_INTERPRETATIONS.dream_mood_interpretations[mood.toLowerCase()];
    } else {
        // Fallback mood interpretation
        switch (mood.toLowerCase()) {
            case 'positive': moodInterpretationText = "A positive dream mood often reflects inner harmony, wish fulfillment, or subconscious encouragement. The symbols encountered are likely pointing towards growth, joy, or resolution."; break;
            case 'negative': moodInterpretationText = "A negative dream mood usually highlights anxieties, fears, or unresolved conflicts. The symbols may represent challenges or aspects of yourself needing attention and healing."; break;
            case 'confusing': moodInterpretationText = "A confusing dream mood suggests your subconscious is processing complex information or conflicting emotions. The symbols might seem disjointed, indicating a period of uncertainty or transition."; break;
            case 'neutral': moodInterpretationText = "A neutral dream mood might indicate objective processing of information or a more detached observation of subconscious content. The symbols could be straightforward reflections of daily thoughts or subtle insights."; break;
            case 'prophetic': moodInterpretationText = "If you felt the dream was prophetic, its symbols and mood take on a heightened significance, potentially offering glimpses into future possibilities or important intuitive messages. Journaling and reflection are key."; break;
        }
    }
    interpretationText += `<p><strong>Reflection considering Mood (${mood}):</strong> ${moodInterpretationText}</p>`;

    if (identifiedSymbols.length > 0 && identifiedSymbols[0].questions && identifiedSymbols[0].questions.length > 0) {
        interpretationText += `<p><strong>Questions for Deeper Reflection (related to '${identifiedSymbols[0].symbol}'):</strong></p><ul>`;
        identifiedSymbols[0].questions.slice(0,3).forEach(q => interpretationText += `<li>${q}</li>`);
        interpretationText += `</ul>`;
    }

    interpretationText += `<p style="margin-top:15px;"><em>Remember, your personal associations with dream elements are paramount. This analysis provides general symbolic meanings to guide your own introspection. Consider how these symbols and themes resonate with your current waking life experiences and feelings.</em></p>`;
    analysisContainer.innerHTML = interpretationText;

    // Auto-save to journal if user is logged in
    if (currentUser && currentUser.id && typeof createJournalEntryAPI === 'function') {
        const journalContent = `Dream on ${dreamDate} (Mood: ${mood}):\n${description}\n\n--- Analysis Summary ---\nIdentified Symbols: ${identifiedSymbols.map(s => s.symbol).join(', ') || 'None specific'}\nMood Reflection: ${moodInterpretationText}`;
        const entryData = {
            title: `Dream: ${description.substring(0, 30)}${description.length > 30 ? '...' : ''} - ${dreamDate}`,
            content: journalContent,
            entry_type: 'dreams', // Ensure this matches backend expectations
            dream_date: dreamDate,
            dream_mood: mood
        };
        try {
            await createJournalEntryAPI(entryData);
            console.log("Dream analysis automatically saved to journal.");
            // Optionally, refresh the journal entries display if visible
            if (document.getElementById('journal') && document.getElementById('journal').classList.contains('active') && typeof loadUserJournalEntriesUI === 'function') {
                loadUserJournalEntriesUI();
            }
        } catch (error) {
            console.error("Failed to auto-save dream analysis to journal:", error);
            // Optionally, inform the user with a non-blocking message
        }
    }
}

// Expose main function to be callable from script.js or HTML
window.initDreamAnalysisFeature = initDreamAnalysisFeature;
window.handleDreamAnalysis = handleDreamAnalysis; // If called by onclick in HTML
