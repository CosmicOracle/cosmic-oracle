// Filename: numerologyController.js

/**
 * Manages the Sacred Numerology Analysis feature:
 * - Initializes UI elements and event listeners.
 * - Handles calculation, display, saving, loading, and deletion of numerology reports.
 */

/**
 * Initializes the Numerology feature.
 */
async function initNumerologyFeature() {
    const calculateButton = document.getElementById('calculateNumerologyBtn');
    const fullNameInput = document.getElementById('numerologyFullName');
    const birthDateInput = document.getElementById('numerologyBirthDate');

    if (calculateButton) {
        calculateButton.addEventListener('click', handleCalculateNumerologyReport);
    }

    if (window.currentUser?.id) {
        // Prefill form if user data is available
        if (fullNameInput && window.currentUser.full_name_for_numerology) {
            fullNameInput.value = window.currentUser.full_name_for_numerology;
        }
        if (birthDateInput && window.currentUser.birth_data?.birth_date_local) {
            birthDateInput.value = window.currentUser.birth_data.birth_date_local;
        }

        // Automatically calculate if both fields are prefilled
        if (fullNameInput?.value && birthDateInput?.value) {
            await handleCalculateNumerologyReport();
        }
        await displaySavedNumerologyReports();
    } else {
        const resultsContainer = document.getElementById('numerologyResults');
        const interpretationContainer = document.getElementById('numerologyInterpretation');
        const savedReportsContainer = document.getElementById('savedNumerologyReportsContainer');

        if (resultsContainer) resultsContainer.innerHTML = '';
        if (interpretationContainer) {
            interpretationContainer.innerHTML = '<p>Enter your full birth name and birth date to discover your sacred numbers. Login to save and view past reports.</p>';
        }
        if (savedReportsContainer) {
            savedReportsContainer.innerHTML = "<h4>Your Saved Reports:</h4><p>Login to view saved reports.</p>";
        }
    }
}

/**
 * Handles the "Calculate My Numbers" button click.
 */
async function handleCalculateNumerologyReport() {
    const fullNameInput = document.getElementById('numerologyFullName');
    const birthDateInput = document.getElementById('numerologyBirthDate');
    const resultsContainer = document.getElementById('numerologyResults');
    const interpretationContainer = document.getElementById('numerologyInterpretation');

    if (!fullNameInput || !birthDateInput || !resultsContainer || !interpretationContainer) {
        console.error("Required UI elements missing");
        return;
    }

    const fullName = fullNameInput.value.trim();
    const birthDateStr = birthDateInput.value;

    if (!fullName || !birthDateStr) {
        interpretationContainer.innerHTML = '<p>Please enter your full birth name and birth date.</p>';
        resultsContainer.innerHTML = '';
        return;
    }

    interpretationContainer.innerHTML = '<p>Calculating your sacred numbers and their meanings...</p>';
    resultsContainer.innerHTML = '';

    try {
        const response = await fetch('/api/v1/numerology/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                full_name: fullName,
                birth_date: birthDateStr
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Failed to calculate numerology: ${response.statusText}`);
        }

        const data = await response.json();
        displayFullNumerologyReport(data.calculations);

        if (window.currentUser?.id) {
            await displaySavedNumerologyReports();
        }

    } catch (error) {
        console.error("Error calculating numerology report:", error);
        interpretationContainer.innerHTML = `<p style="color: red;">Could not calculate numerology report: ${error.message}</p><p>Please ensure the birth date is valid and the name is entered correctly.</p>`;
    }
}

/**
 * Displays the full numerology report (numbers and interpretations).
 * @param {object} numerologyData - The numerology report data from the API.
 */
function displayFullNumerologyReport(numerologyData) {
    const resultsContainer = document.getElementById('numerologyResults');
    const interpretationContainer = document.getElementById('numerologyInterpretation');

    if (!resultsContainer || !interpretationContainer) return;

    resultsContainer.innerHTML = '';
    interpretationContainer.innerHTML = `<h3>Your Sacred Numerology Analysis</h3>`;

    Object.entries(numerologyData).forEach(([key, data]) => {
        const displayName = key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        
        const itemDiv = document.createElement('div');
        itemDiv.className = 'numerology-item';
        itemDiv.innerHTML = `
            <h4>${displayName}</h4>
            <div style="font-size: 2rem; color: var(--cosmic-purple-600);">${data.number}</div>
            <div class="interpretation">
                <strong>${data.keyword || 'N/A'}</strong>
                <p>${data.summary || 'Interpretation not available.'}</p>
                ${data.calculation ? `<p class="calculation-details">${data.calculation}</p>` : ''}
            </div>
        `;
        resultsContainer.appendChild(itemDiv);
    });
}

/**
 * Fetches and displays the user's saved numerology reports.
 */
async function displaySavedNumerologyReports() {
    const container = document.getElementById('savedNumerologyReportsContainer');
    if (!container) return;

    try {
        const response = await fetch('/api/v1/numerology/reports', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch saved reports');
        }

        const data = await response.json();
        
        container.innerHTML = '<h4>Your Saved Reports:</h4>';
        
        if (data.reports && data.reports.length > 0) {
            data.reports.forEach(report => {
                const reportDiv = document.createElement('div');
                reportDiv.className = 'saved-report-item';
                reportDiv.innerHTML = `
                    <p>
                        <strong>Report for: ${report.full_name}</strong><br>
                        (Born: ${new Date(report.birth_date + 'T00:00:00Z').toLocaleDateString()})
                        <br>
                        <small>Life Path: ${report.life_path_number}, Expression: ${report.expression_number}</small>
                    </p>
                    <div class="report-actions">
                        <button onclick="handleViewSavedNumerologyReport('${report.id}')" 
                                class="view-report-btn">View Full Report</button>
                        <button onclick="handleDeleteNumerologyReport(${report.id})"
                                class="delete-report-btn">Delete</button>
                    </div>
                `;
                container.appendChild(reportDiv);
            });
        } else {
            container.innerHTML += '<p>No saved numerology reports found.</p>';
        }
    } catch (error) {
        console.error("Error loading saved reports:", error);
        container.innerHTML = `<h4>Your Saved Reports:</h4><p style="color: red;">Could not load reports: ${error.message}</p>`;
    }
}

/**
 * Handles viewing a specific saved numerology report.
 * @param {string} reportId - The ID of the report to view.
 */
async function handleViewSavedNumerologyReport(reportId) {
    try {
        const response = await fetch(`/api/v1/numerology/report/${reportId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch report');
        }

        const reportData = await response.json();
        
        // Prefill the form with the saved data
        const fullNameInput = document.getElementById('numerologyFullName');
        const birthDateInput = document.getElementById('numerologyBirthDate');
        if (fullNameInput) fullNameInput.value = reportData.full_name;
        if (birthDateInput) birthDateInput.value = reportData.birth_date;

        // Display the report
        displayFullNumerologyReport(reportData.calculations);

    } catch (error) {
        console.error("Error viewing saved report:", error);
        const interpretationContainer = document.getElementById('numerologyInterpretation');
        if (interpretationContainer) {
            interpretationContainer.innerHTML = `<p style="color: red;">Could not load report: ${error.message}</p>`;
        }
    }
}

/**
 * Handles deleting a saved numerology report.
 * @param {string} reportId - The ID of the report to delete.
 */
async function handleDeleteNumerologyReport(reportId) {
    if (!confirm('Are you sure you want to delete this numerology report?')) return;

    try {
        const response = await fetch(`/api/v1/numerology/report/${reportId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete report');
        }

        await displaySavedNumerologyReports();
        alert('Report deleted successfully.');

    } catch (error) {
        console.error("Error deleting report:", error);
        alert(`Failed to delete report: ${error.message}`);
    }
}

// Expose functions needed by HTML
window.initNumerologyFeature = initNumerologyFeature;
window.handleCalculateNumerologyReport = handleCalculateNumerologyReport;
window.handleViewSavedNumerologyReport = handleViewSavedNumerologyReport;
window.handleDeleteNumerologyReport = handleDeleteNumerologyReport;