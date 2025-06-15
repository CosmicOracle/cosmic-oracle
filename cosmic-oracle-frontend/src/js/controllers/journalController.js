// Filename: journalController.js

/**
 * Manages the Cosmic Journal feature:
 * - Initializes UI and event listeners.
 * - Handles saving, loading, and deleting journal entries.
 * - Relies on uiUpdate.js for prompt display.
 */

/**
 * Initializes the Cosmic Journal feature.
 */
function initJournalFeature() {
    const saveButton = document.getElementById('saveJournalEntryBtn'); // Assuming this ID for the save button
    const journalTypeSelect = document.getElementById('journalType');

    if (saveButton) {
        saveButton.addEventListener('click', handleSaveJournalEntry);
    } else {
        // If using onclick="saveJournalEntryUI()" in HTML, ensure handleSaveJournalEntry is global.
        // For this controller, we'll make handleSaveJournalEntry available globally.
        console.warn("Save Journal Entry button 'saveJournalEntryBtn' not found. Ensure HTML is updated or use direct onclick for handleSaveJournalEntry.");
    }

    if (journalTypeSelect) {
        journalTypeSelect.addEventListener('change', () => {
            // Toggle dream-specific fields visibility based on journal type
            const dreamFieldsDiv = document.getElementById('dreamJournalSpecificFields'); // Assuming a wrapper div
            if (dreamFieldsDiv) {
                dreamFieldsDiv.style.display = journalTypeSelect.value === 'dreams' ? 'block' : 'none';
            }
            // Call the existing prompt updater from uiUpdate.js or script.js
            if (typeof updateJournalPromptsUI === 'function') {
                updateJournalPromptsUI();
            } else if (typeof updateJournalPrompts === 'function') { // Fallback for older naming
                updateJournalPrompts();
            }
        });
        // Initial check for dream fields visibility
        const dreamFieldsDiv = document.getElementById('dreamJournalSpecificFields');
        if (dreamFieldsDiv) {
            dreamFieldsDiv.style.display = journalTypeSelect.value === 'dreams' ? 'block' : 'none';
        }
    }


    if (currentUser && currentUser.id) {
        displayUserJournalEntries();
    } else {
        const savedEntriesContainer = document.getElementById('savedEntries');
        if (savedEntriesContainer) {
            savedEntriesContainer.innerHTML = "<h4>Your Saved Journal Entries:</h4><p>Login to save and view your entries.</p>";
        }
    }

    // Call the prompt updater on initial load as well
    if (typeof updateJournalPromptsUI === 'function') {
        updateJournalPromptsUI();
    } else if (typeof updateJournalPrompts === 'function') {
        updateJournalPrompts();
    }
}

/**
 * Handles saving a new journal entry.
 */
async function handleSaveJournalEntry() {
    if (!currentUser || !currentUser.id) {
        alert("Please login to save your journal entry.");
        if (typeof showLoginForm === 'function') showLoginForm();
        return;
    }

    const titleInput = document.getElementById('journalTitle');
    const contentInput = document.getElementById('journalText');
    const typeInput = document.getElementById('journalType');

    if (!contentInput || !typeInput) {
        alert("Journal form elements (content or type) are missing.");
        return;
    }

    const title = titleInput ? titleInput.value.trim() : ""; // Title is optional
    const content = contentInput.value.trim();
    const entry_type = typeInput.value;

    if (content === '') {
        alert('Please write something in your journal entry before saving.');
        return;
    }

    const entryData = { title, content, entry_type };

    if (entry_type === 'dreams') {
        const dreamDateValue = document.getElementById('dreamDateInput')?.value; // ID from dreamAnalyzer.js
        const dreamMoodValue = document.getElementById('dreamMoodSelect')?.value; // ID from dreamAnalyzer.js

        if (dreamDateValue) {
            entryData.dream_date = dreamDateValue;
        } else {
            // Default dream_date to today if not provided, backend might also do this
            entryData.dream_date = new Date().toISOString().split('T')[0];
        }
        if (dreamMoodValue) {
            entryData.dream_mood = dreamMoodValue;
        }
    }

    try {
        const result = await createJournalEntryAPI(entryData); // from apiService.js
        alert(result.message || 'Journal entry saved successfully!');
        if (contentInput) contentInput.value = ''; // Clear textarea
        if (titleInput) titleInput.value = '';   // Clear title
        displayUserJournalEntries(); // Refresh the list of saved entries
    } catch (error) {
        console.error("Error saving journal entry:", error);
        alert(`Failed to save journal entry: ${error.message || 'Please try again.'}`);
    }
}

/**
 * Fetches and displays the user's saved journal entries.
 */
async function displayUserJournalEntries() {
    const container = document.getElementById('savedEntries');
    if (!container) {
        console.error("Saved entries container 'savedEntries' not found.");
        return;
    }

    if (!currentUser || !currentUser.id) {
        container.innerHTML = "<h4>Your Saved Journal Entries:</h4><p>Login to view and save your entries.</p>";
        return;
    }

    container.innerHTML = '<h4>Your Saved Journal Entries:</h4><p>Loading your entries...</p>';

    try {
        const journalData = await fetchJournalEntriesAPI(); // Fetches paginated entries (default page 1, 10 per page)
        if (journalData.error) {
            throw new Error(journalData.error);
        }

        if (journalData.entries && journalData.entries.length > 0) {
            container.innerHTML = '<h4>Your Saved Journal Entries:</h4>'; // Clear loading message
            journalData.entries.forEach(entry => {
                const entryDiv = document.createElement('div');
                entryDiv.className = 'journal-entry'; // Re-use styling

                let entryHTML = `
                    <p>
                        <strong>${entry.title || new Date(entry.created_at).toLocaleString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</strong> 
                        - ${entry.entry_type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </p>
                    <p>${entry.content.replace(/\n/g, '<br>')}</p>`;

                if (entry.entry_type === 'dreams' && entry.dream_date) {
                    const dreamDateObj = new Date(entry.dream_date + 'T00:00:00Z'); // Treat as UTC
                    entryHTML += `<p><small>Dream Date: ${dreamDateObj.toLocaleDateString(undefined, {timeZone:'UTC'})} | Mood: ${entry.dream_mood || 'N/A'}</small></p>`;
                }
                 entryHTML += `
                    <p><small>Created: ${new Date(entry.created_at).toLocaleString()}</small></p>
                    <button onclick="handleDeleteJournalEntry(${entry.id})"
                            style="background: #c0392b; color: white; border: none; padding: 5px 10px; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 5px; font-size: 0.8em;">
                        Delete
                    </button>`;
                entryDiv.innerHTML = entryHTML;
                container.appendChild(entryDiv);
            });
            // Basic pagination info (can be expanded)
            if (journalData.total_pages > 1) {
                container.innerHTML += `<p style="text-align:center; font-size:0.9em; margin-top:10px;">Page ${journalData.current_page} of ${journalData.total_pages}. Total Entries: ${journalData.total_entries}</p>`;
                // Add pagination buttons if desired
            }

        } else {
            container.innerHTML = '<h4>Your Saved Journal Entries:</h4><p>No saved journal entries yet. Start writing!</p>';
        }
    } catch (error) {
        console.error("Error loading journal entries:", error);
        container.innerHTML = `<h4>Your Saved Journal Entries:</h4><p style="color: red;">Could not load entries: ${error.message}</p>`;
    }
}

/**
 * Handles deleting a saved journal entry.
 * @param {number} entryId - The ID of the journal entry to delete.
 */
async function handleDeleteJournalEntry(entryId) {
    if (!confirm('Are you sure you want to permanently delete this journal entry?')) {
        return;
    }
    try {
        const result = await deleteJournalEntryAPI(entryId); // from apiService.js
        alert(result.message || "Journal entry deleted successfully.");
        displayUserJournalEntries(); // Refresh the list
    } catch (error) {
        console.error("Error deleting journal entry:", error);
        alert(`Failed to delete entry: ${error.message || 'Please try again.'}`);
    }
}

// Expose main function to be callable from script.js or HTML
window.initJournalFeature = initJournalFeature;
window.handleSaveJournalEntry = handleSaveJournalEntry; // If called by onclick in HTML (e.g. saveJournalEntryUI)
window.handleDeleteJournalEntry = handleDeleteJournalEntry; // For onclick in dynamically generated buttons

// Ensure dream-specific fields are shown/hidden based on initial journal type
document.addEventListener('DOMContentLoaded', () => {
    const journalTypeSelect = document.getElementById('journalType');
    const dreamFieldsDiv = document.getElementById('dreamJournalSpecificFields'); // Assuming a wrapper div
    if (journalTypeSelect && dreamFieldsDiv) {
        dreamFieldsDiv.style.display = journalTypeSelect.value === 'dreams' ? 'block' : 'none';
    }
});
