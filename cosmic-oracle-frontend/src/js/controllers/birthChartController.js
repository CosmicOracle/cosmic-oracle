// Filename: birthChartController.js

/**
 * Manages the Birth Chart feature:
 * - Handles user input for birth details.
 * - Geocodes location to get latitude, longitude, and timezone.
 * - Calls the backend API to calculate and save/retrieve the natal chart.
 * - Uses uiUpdate.js to display the chart and analysis.
 * - Pre-fills form from saved user data if available.
 */

// Store geocoded latitude and longitude temporarily
let geocodedChartLatitude = null;
let geocodedChartLongitude = null;

/**
 * Initializes the Birth Chart feature.
 * Sets up event listeners and attempts to load/prefill data for logged-in users.
 */
async function initBirthChartFeature() {
    const generateButton = document.getElementById('generateBirthChartBtn'); // Assuming this button ID will be used
    const locationInput = document.getElementById('birthLocationInput');

    if (generateButton) {
        generateButton.addEventListener('click', handleGenerateBirthChartFromButton);
    } else {
        // If using onclick in HTML like in oracle.html: <button onclick="handleBirthChartGeneration()" ...>
        // Ensure handleBirthChartGeneration is globally available or refactor HTML to use event listener.
        // For this script, we'll make handleBirthChartGeneration available globally later.
        console.log("Birth chart generate button not found by ID 'generateBirthChartBtn'. Ensure HTML is updated or use direct onclick.");
    }

    if (locationInput) {
        locationInput.addEventListener('blur', handleLocationGeocode); // Geocode on losing focus
    }

    // Attempt to load saved chart or prefill from user profile for logged-in user
    if (currentUser && currentUser.id) {
        try {
            const savedChartData = await fetchSavedNatalChart(); // from apiService.js
            if (savedChartData && savedChartData.points) { // Check for actual chart data
                console.log("Loaded saved natal chart:", savedChartData);
                prefillBirthChartForm(savedChartData.birth_data || savedChartData.chart_info);
                displayBirthChartUI(savedChartData); // from uiUpdate.js
            } else if (currentUser.birth_data) {
                console.log("No saved chart, prefilling from user profile birth_data.");
                prefillBirthChartForm(currentUser.birth_data);
                // Optionally, you could automatically generate the chart if all data is present
                // if (document.getElementById('birthDateInput').value && document.getElementById('birthTimeInput').value && document.getElementById('birthLocationInput').value && document.getElementById('birthTimezoneInput').value) {
                //     handleGenerateBirthChartFromButton();
                // }
            } else {
                 console.log("No saved natal chart or prefillable birth data in user profile.");
            }
        } catch (error) {
            console.warn("Could not automatically load saved birth chart or prefill from profile:", error.message);
             if (currentUser.birth_data) {
                prefillBirthChartForm(currentUser.birth_data);
             }
        }
    } else {
        const analysisContainer = document.getElementById('birthChartAnalysis');
        const wheelContainer = document.getElementById('birthChartWheel');
        if(analysisContainer) analysisContainer.innerHTML = "<p>Login to save and automatically load your birth chart details. Otherwise, please enter your birth details to generate your natal chart.</p>";
        if(wheelContainer) wheelContainer.innerHTML = '';
    }
}

/**
 * Prefills the birth chart form with provided birth data.
 * @param {object} birthData - Object containing birth details (e.g., from user profile or saved chart).
 */
function prefillBirthChartForm(birthData) {
    if (!birthData) return;

    const dateInput = document.getElementById('birthDateInput');
    const timeInput = document.getElementById('birthTimeInput');
    const locationInput = document.getElementById('birthLocationInput');
    const timezoneInput = document.getElementById('birthTimezoneInput');

    // Prioritize specific local date/time strings if available
    if (dateInput) {
        if (birthData.birth_date_local) { // From GET /me
            dateInput.value = birthData.birth_date_local;
        } else if (birthData.datetime_local && typeof birthData.datetime_local === 'string') { // From saved chart format
             dateInput.value = birthData.datetime_local.split(' ')[0];
        } else if (birthData.birth_datetime_str && typeof birthData.birth_datetime_str === 'string') { // From astrology_controller POST response
             dateInput.value = birthData.birth_datetime_str.split(' ')[0];
        } else if (birthData.birth_datetime_utc) { // Fallback to UTC, user might need to adjust
            const utcDate = new Date(birthData.birth_datetime_utc);
            dateInput.value = utcDate.toISOString().split('T')[0];
            console.warn("Prefilling date from UTC. User may need to verify for local date.");
        }
    }

    if (timeInput) {
        if (birthData.birth_time_local) { // From GET /me
            timeInput.value = birthData.birth_time_local;
        } else if (birthData.datetime_local && typeof birthData.datetime_local === 'string') { // From saved chart format
             const parts = birthData.datetime_local.split(' ');
             if (parts.length > 1) timeInput.value = parts[1].substring(0,5); // HH:MM
        } else if (birthData.birth_datetime_str && typeof birthData.birth_datetime_str === 'string') { // From astrology_controller POST response
             const parts = birthData.birth_datetime_str.split(' ');
             if (parts.length > 1) timeInput.value = parts[1].substring(0,5);
        } else if (birthData.birth_datetime_utc) { // Fallback to UTC
            const utcDate = new Date(birthData.birth_datetime_utc);
            const hours = utcDate.getUTCHours().toString().padStart(2, '0');
            const minutes = utcDate.getUTCMinutes().toString().padStart(2, '0');
            timeInput.value = `${hours}:${minutes}`;
            console.warn("Prefilling time from UTC. User may need to verify for local time.");
        }
    }

    if (locationInput && birthData.birth_location_name) {
        locationInput.value = birthData.birth_location_name;
    } else if (locationInput && birthData.location_name) { // For consistency with chart_info
        locationInput.value = birthData.location_name;
    }

    if (timezoneInput && birthData.timezone_str) {
        timezoneInput.value = birthData.timezone_str;
    } else if (timezoneInput && birthData.timezone) { // For consistency
        timezoneInput.value = birthData.timezone;
    }

    // Store lat/lon if available from birthData (e.g., from saved chart or user profile)
    if (birthData.latitude !== undefined && birthData.longitude !== undefined) {
        geocodedChartLatitude = parseFloat(birthData.latitude);
        geocodedChartLongitude = parseFloat(birthData.longitude);
    }
}

/**
 * Handles the geocoding of the entered location.
 */
async function handleLocationGeocode() {
    const locationInput = document.getElementById('birthLocationInput');
    const timezoneInput = document.getElementById('birthTimezoneInput');
    if (!locationInput || !locationInput.value.trim() || !timezoneInput) return;

    const locationQuery = locationInput.value;

    try {
        console.log(`Geocoding: ${locationQuery}`);
        const geocodedData = await geocodeLocation(locationQuery); // from apiService.js
        if (geocodedData && geocodedData.latitude !== undefined && geocodedData.longitude !== undefined) {
            geocodedChartLatitude = parseFloat(geocodedData.latitude);
            geocodedChartLongitude = parseFloat(geocodedData.longitude);
            if (geocodedData.timezone) {
                timezoneInput.value = geocodedData.timezone;
                timezoneInput.dispatchEvent(new Event('change')); // Trigger change for any listeners
            } else {
                // timezoneInput.value = ""; // Clear if not found by geocoder
                console.warn("Geocoding successful but no timezone returned by service for:", locationQuery);
                alert("Location found, but timezone could not be automatically determined. Please verify or enter it manually.");
            }
            console.log("Geocoded Data:", geocodedData);
            // Update a status message or log
            const statusEl = document.getElementById('birthChartAnalysis'); // Or a dedicated status element
            if(statusEl) statusEl.innerHTML = `<p style="color: green;">Location geocoded: ${geocodedData.display_name || locationQuery}. Lat: ${geocodedChartLatitude.toFixed(4)}, Lon: ${geocodedChartLongitude.toFixed(4)}. ${geocodedData.timezone ? 'Timezone found: ' + geocodedData.timezone : 'Timezone not auto-detected.'}</p>`;

        } else if (geocodedData && geocodedData.error) {
            alert(`Geocoding issue: ${geocodedData.error}`);
            geocodedChartLatitude = null;
            geocodedChartLongitude = null;
        } else {
            console.warn("Geocoding returned no results for:", locationQuery);
            alert(`Could not find coordinates for "${locationQuery}". Please try a more specific location or enter coordinates and timezone manually.`);
            geocodedChartLatitude = null;
            geocodedChartLongitude = null;
        }
    } catch (error) {
        console.error("Geocoding process failed:", error);
        alert(`Geocoding failed: ${error.message}. Please enter latitude, longitude, and timezone manually if known.`);
        geocodedChartLatitude = null;
        geocodedChartLongitude = null;
    }
}

/**
 * Handles the "Generate Chart" button click.
 * Gathers form data, calls the API, and displays the result.
 */
async function handleGenerateBirthChartFromButton() {
    const birthDate = document.getElementById('birthDateInput').value;
    const birthTime = document.getElementById('birthTimeInput').value;
    const birthLocation = document.getElementById('birthLocationInput').value;
    let timezoneStr = document.getElementById('birthTimezoneInput').value;

    const analysisContainer = document.getElementById('birthChartAnalysis');
    const wheelContainer = document.getElementById('birthChartWheel');

    if (!analysisContainer || !wheelContainer) {
        console.error("Birth chart display containers not found.");
        return;
    }

    analysisContainer.innerHTML = "<p>Gathering celestial data...</p>";
    wheelContainer.innerHTML = ""; // Clear previous wheel

    if (!birthDate || !birthTime || !birthLocation) {
        alert("Please fill in all birth details: Date, Time, and Location.");
        analysisContainer.innerHTML = "<p>Birth details incomplete. Please fill all fields.</p>";
        return;
    }

    if (!timezoneStr) {
        alert("Timezone is required. If unsure, try re-entering the location to geocode the timezone, or enter it manually (e.g., 'America/New_York').");
        analysisContainer.innerHTML = "<p>Timezone missing. Please provide a timezone.</p>";
        return;
    }

    // Use geocoded lat/lon if available, otherwise prompt (or handle error)
    if (geocodedChartLatitude === null || geocodedChartLongitude === null) {
        // If geocoding hasn't run or failed, try to geocode now based on current input
        // Or, if you want to be strict, alert and return.
        // For now, let's try to geocode if location input has value and lat/lon are null.
        if (birthLocation.trim()) {
            console.log("Latitude/Longitude not available from previous geocoding. Attempting geocode now...");
            await handleLocationGeocode(); // This will update geocodedChartLatitude/Longitude
            if (geocodedChartLatitude === null || geocodedChartLongitude === null) {
                 alert("Could not determine coordinates for the location. Please enter a more specific location or ensure it can be geocoded.");
                 analysisContainer.innerHTML = "<p>Location coordinates could not be determined. Chart generation failed.</p>";
                 return;
            }
        } else {
            alert("Location is empty. Cannot geocode.");
            analysisContainer.innerHTML = "<p>Location is empty. Chart generation failed.</p>";
            return;
        }
    }

    const birthDetails = {
        birth_datetime_str: `${birthDate} ${birthTime}`,
        birth_timezone_str: timezoneStr,
        latitude: geocodedChartLatitude,
        longitude: geocodedChartLongitude,
        location_name: birthLocation,
        house_system_name: document.getElementById('birthChartHouseSystem')?.value || "Placidus" // Assuming a selector might exist
    };

    try {
        const chartData = await calculateAndSaveNatalChart(birthDetails); // from apiService.js
        displayBirthChartUI(chartData); // from uiUpdate.js
    } catch (error) {
        console.error("Error generating birth chart:", error);
        let errorMessage = error.message || "An unknown error occurred.";
        if (error.errors) { // Check if backend validation errors are present
            errorMessage = Object.values(error.errors).flat().join(' ');
        }
        analysisContainer.innerHTML = `<p style="color: red;">Chart Generation Error: ${errorMessage}</p><p>Please double-check your input, especially the timezone format (e.g., "America/New_York", "Europe/London"). Ensure date and time are valid for the selected timezone.</p>`;
    }
}

// Expose main function to be callable from script.js or HTML (if current structure demands it)
window.handleBirthChartGeneration = handleGenerateBirthChartFromButton; // For oracle.html's onclick
window.initBirthChartFeature = initBirthChartFeature;
