// Filename: calendarEventsManager.js

/**
 * Manages the Cosmic Calendar feature:
 * - Renders the calendar grid.
 * - Fetches and displays cosmic events for the current month.
 * - Handles user interaction with calendar dates.
 * - Displays detailed astrological information for a selected date.
 */

// Store for fetched monthly events to avoid re-fetching on simple re-renders
let monthlyCosmicEventsCache = {};
let currentDisplayedYearMonth = ""; // To track if cache is for current view

/**
 * Initializes the Calendar feature.
 * Sets up event listeners and renders the initial calendar view.
 */
async function initCalendarFeature() {
    const prevMonthButton = document.getElementById('prevMonth');
    const nextMonthButton = document.getElementById('nextMonth');

    if (prevMonthButton) {
        prevMonthButton.addEventListener('click', () => changeDisplayMonth(-1));
    }
    if (nextMonthButton) {
        nextMonthButton.addEventListener('click', () => changeDisplayMonth(1));
    }

    // Initialize global date variables if not already set by script.js
    if (typeof currentDateForCalendar === 'undefined') {
        currentDateForCalendar = new Date();
    }
    if (typeof selectedCalendarDate === 'undefined') {
        selectedCalendarDate = new Date(currentDateForCalendar.getFullYear(), currentDateForCalendar.getMonth(), currentDateForCalendar.getDate());
    }

    await renderCalendar();
    // Initial display for the selected date (which defaults to today or first of month)
    await displaySelectedDateDetails();
    // Display current moon phase for the main calendar view (usually today's)
    await displayCurrentMoonPhaseForCalendarHeader();
}

/**
 * Changes the displayed month and re-renders the calendar.
 * @param {number} direction - -1 for previous month, 1 for next month.
 */
async function changeDisplayMonth(direction) {
    currentDateForCalendar.setDate(1); // Avoid issues with days not existing in next/prev month
    currentDateForCalendar.setMonth(currentDateForCalendar.getMonth() + direction);
    // Update selectedCalendarDate to the first of the new month to avoid invalid dates
    selectedCalendarDate = new Date(currentDateForCalendar.getFullYear(), currentDateForCalendar.getMonth(), 1);
    await renderCalendar();
    await displaySelectedDateDetails(); // Update details for the new default selected date
    await displayCurrentMoonPhaseForCalendarHeader(); // Update moon phase for the new month's general view
}

/**
 * Fetches cosmic events for the given month and year if not already cached.
 * @param {number} year - The year.
 * @param {number} month - The month (0-indexed).
 */
async function fetchAndCacheMonthlyEvents(year, month) {
    const yearMonthKey = `${year}-${month}`;
    if (currentDisplayedYearMonth === yearMonthKey && monthlyCosmicEventsCache[yearMonthKey]) {
        return monthlyCosmicEventsCache[yearMonthKey]; // Use cached data
    }

    const firstDayOfMonth = new Date(Date.UTC(year, month, 1));
    const lastDayOfMonth = new Date(Date.UTC(year, month + 1, 0)); // Day 0 of next month is last day of current

    try {
        const events = await getCosmicEventsForMonth(firstDayOfMonth, lastDayOfMonth); // from apiService.js
        monthlyCosmicEventsCache[yearMonthKey] = events.filter(event => {
            // Ensure events are within the correct month, as API might return broader range
            const eventDate = new Date(event.date + "T00:00:00Z"); // Assume event.date is YYYY-MM-DD
            return eventDate.getUTCFullYear() === year && eventDate.getUTCMonth() === month;
        });
        currentDisplayedYearMonth = yearMonthKey;
        return monthlyCosmicEventsCache[yearMonthKey];
    } catch (error) {
        console.error("Error fetching monthly cosmic events:", error);
        monthlyCosmicEventsCache[yearMonthKey] = []; // Cache empty array on error
        return [];
    }
}

/**
 * Renders the calendar grid for the month defined by `currentDateForCalendar`.
 */
async function renderCalendar() {
    const calendarGrid = document.getElementById('calendarGrid');
    const monthHeader = document.getElementById('currentMonth');

    if (!calendarGrid || !monthHeader) {
        console.error("Calendar grid or month header element not found.");
        return;
    }

    const year = currentDateForCalendar.getFullYear();
    const month = currentDateForCalendar.getMonth(); // 0-indexed

    monthHeader.textContent = new Date(year, month).toLocaleDateString(undefined, {
        month: 'long',
        year: 'numeric'
    });
    calendarGrid.innerHTML = ''; // Clear previous grid

    // Add day headers (Sun, Mon, ...)
    const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayHeaders.forEach(day => {
        const dayHeaderEl = document.createElement('div');
        dayHeaderEl.className = 'day-of-week';
        dayHeaderEl.textContent = day;
        calendarGrid.appendChild(dayHeaderEl);
    });

    const monthlyEvents = await fetchAndCacheMonthlyEvents(year, month);
    const monthlyEventsOverviewContainer = document.getElementById('cosmicEvents');
    if (monthlyEventsOverviewContainer) {
        let overviewHTML = '<ul>';
        if (monthlyEvents && monthlyEvents.length > 0) {
            monthlyEvents.sort((a,b) => new Date(a.date) - new Date(b.date)).forEach(event => {
                overviewHTML += `<li><strong>${new Date(event.date + "T00:00:00Z").toLocaleDateString([], {month: 'short', day: 'numeric', timeZone: 'UTC'})}: ${event.title}</strong> - ${event.description}</li>`;
            });
        } else {
            overviewHTML += '<li>No major cosmic events highlighted for this month.</li>';
        }
        overviewHTML += '</ul>';
        monthlyEventsOverviewContainer.innerHTML = overviewHTML;
    }


    const firstDayOfMonth = new Date(year, month, 1).getDay(); // 0 for Sunday, 1 for Monday...
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const today = new Date();

    // Create empty cells for days before the first of the month
    for (let i = 0; i < firstDayOfMonth; i++) {
        const emptyDayEl = document.createElement('div');
        emptyDayEl.className = 'calendar-day';
        calendarGrid.appendChild(emptyDayEl);
    }

    // Create cells for each day of the month
    for (let day = 1; day <= daysInMonth; day++) {
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day';
        dayEl.textContent = day;

        const currentIterationDate = new Date(year, month, day);

        if (year === today.getFullYear() && month === today.getMonth() && day === today.getDate()) {
            dayEl.classList.add('today');
        }
        if (year === selectedCalendarDate.getFullYear() && month === selectedCalendarDate.getMonth() && day === selectedCalendarDate.getDate()) {
            dayEl.classList.add('selected-date');
        }

        // Check for events on this day
        const eventsOnThisDay = monthlyEvents.filter(event => {
            const eventDate = new Date(event.date + "T00:00:00Z"); // Ensure consistent comparison
            return eventDate.getUTCDate() === day;
        });

        if (eventsOnThisDay.length > 0) {
            dayEl.classList.add('has-event');
            dayEl.title = eventsOnThisDay.map(e => e.title).join('; ');
            // Store event details for quick access if needed, or rely on displaySelectedDateDetails
            dayEl.dataset.eventDetails = JSON.stringify(eventsOnThisDay);
        }

        dayEl.addEventListener('click', () => selectDate(year, month, day, dayEl));
        calendarGrid.appendChild(dayEl);
    }
}

/**
 * Handles the selection of a date on the calendar.
 * @param {number} year
 * @param {number} month (0-indexed)
 * @param {number} day
 * @param {HTMLElement} dayElement - The clicked day element.
 */
async function selectDate(year, month, day, dayElement) {
    selectedCalendarDate = new Date(year, month, day);

    // Update visual selection
    document.querySelectorAll('#calendarGrid .calendar-day.selected-date').forEach(el => {
        el.classList.remove('selected-date');
    });
    if (dayElement) {
        dayElement.classList.add('selected-date');
    }

    await displaySelectedDateDetails();
}

/**
 * Fetches and displays detailed astrological info for the selectedCalendarDate.
 */
async function displaySelectedDateDetails() {
    const infoContainer = document.getElementById('selectedDateInfo');
    if (!infoContainer) {
        console.error("Selected date info container not found.");
        return;
    }
    infoContainer.innerHTML = `<p>Loading details for ${selectedCalendarDate.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}...</p>`;

    try {
        // Fetch Moon Details (phase, illumination, sign)
        const moonData = await fetchMoonDetailsAPI(selectedCalendarDate.toISOString().split('T')[0]); // from apiService.js

        // Fetch Planetary Positions (sign and degree for major planets)
        // Assuming getPlanetaryPositions from apiService.js fetches current transits for the date
        // and the backend astrology_service.py provides this.
        const planetaryData = await getPlanetaryPositions(selectedCalendarDate); // from apiService.js

        // Fetch specific events for THIS day from the monthly cache or re-fetch if necessary
        const year = selectedCalendarDate.getFullYear();
        const month = selectedCalendarDate.getMonth();
        const day = selectedCalendarDate.getDate();
        const yearMonthKey = `${year}-${month}`;

        let dailyEvents = [];
        if (monthlyCosmicEventsCache[yearMonthKey]) {
            dailyEvents = monthlyCosmicEventsCache[yearMonthKey].filter(event => {
                const eventDate = new Date(event.date + "T00:00:00Z");
                return eventDate.getUTCDate() === day;
            });
        } else {
            // Fallback: fetch again if cache missed (should ideally not happen if renderCalendar ran)
            const eventsForMonth = await fetchAndCacheMonthlyEvents(year, month);
            dailyEvents = eventsForMonth.filter(event => {
                const eventDate = new Date(event.date + "T00:00:00Z");
                return eventDate.getUTCDate() === day;
            });
        }


        let html = `<h4>Influences for ${selectedCalendarDate.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}:</h4>`;

        // Moon Phase Info
        if (moonData && !moonData.error) {
            html += `<div class="moon-phase-info" style="margin-bottom:15px;">
                        <p><strong>Moon:</strong> ${moonData.phase_name} (${moonData.illumination_percent}% full) in ${moonData.moon_sign?.name || 'Unknown Sign'} ${moonData.moon_sign?.symbol || ''}</p>
                        <p><em>Influence: ${moonData.influence_text || 'General lunar energies prevail.'}</em></p>
                     </div>`;
        } else {
            html += `<p>Moon phase data currently unavailable.</p>`;
        }

        // Planetary Positions
        if (planetaryData && !planetaryData.error && planetaryData.points) {
            html += `<div class="planetary-positions" style="margin-bottom:15px;"><h5>Key Planetary Positions:</h5><ul>`;
            // Display a few key planets for brevity, or all if desired
            const planetsToShow = ['Sun', 'Mercury', 'Venus', 'Mars'];
            planetsToShow.forEach(pName => {
                const pData = planetaryData.points[pName];
                if (pData && !pData.error) {
                    const planetSymbol = (ALL_PLANETARY_DATA && ALL_PLANETARY_DATA[pData.key]) ? ALL_PLANETARY_DATA[pData.key].symbol : pName.substring(0,2);
                    const signSymbol = (ALL_ZODIAC_SIGNS_DATA && ALL_ZODIAC_SIGNS_DATA[pData.sign_key]) ? ALL_ZODIAC_SIGNS_DATA[pData.sign_key].symbol : '';
                    html += `<li>${planetSymbol} ${pData.name} in ${signSymbol} ${pData.sign_name} ${pData.is_retrograde ? '(R)' : ''}</li>`;
                }
            });
            html += `</ul></div>`;
        } else {
            html += `<p>Planetary positions data currently unavailable.</p>`;
        }

        // Cosmic Events for the Day
        if (dailyEvents.length > 0) {
            html += `<div class="cosmic-events-today"><h5>Cosmic Events Today:</h5><ul>`;
            dailyEvents.forEach(event => {
                html += `<li><strong>${event.title}:</strong> ${event.description}</li>`;
            });
            html += `</ul></div>`;
        } else {
            html += `<p>No specific major cosmic events highlighted for this particular day.</p>`;
        }

        infoContainer.innerHTML = html;

    } catch (error) {
        console.error("Error displaying selected date details:", error);
        infoContainer.innerHTML = `<p style="color: red;">Could not load details for ${selectedCalendarDate.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}: ${error.message}</p>`;
    }
}


/**
 * Displays the current moon phase in the calendar header section.
 * This is separate from displaySelectedDateDetails which is for the clicked date.
 */
async function displayCurrentMoonPhaseForCalendarHeader() {
    const moonPhaseTextEl = document.getElementById('moonPhaseText');
    const moonInfluenceEl = document.getElementById('moonInfluence');
    const moonVisualEl = document.getElementById('moonPhaseVisual');

    if (!moonPhaseTextEl || !moonInfluenceEl || !moonVisualEl) {
        console.warn("Moon phase display elements for calendar header not found.");
        return;
    }

    moonPhaseTextEl.textContent = "Loading moon phase...";
    moonInfluenceEl.textContent = "";

    try {
        // Use today's date for the header moon phase, regardless of selectedCalendarDate
        const todayForHeader = new Date();
        const moonDetails = await fetchMoonDetailsAPI(todayForHeader.toISOString().split('T')[0]); // from apiService.js

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
            } else if (phaseName && phaseName.toLowerCase().includes("waxing")) {
                 moonVisualEl.style.background = `linear-gradient(to left, #f0f0f0 ${illumination}%, #333333 ${illumination}%)`;
                 moonVisualEl.style.boxShadow = `inset ${-5 + (illumination/20)}px 0px 10px rgba(0,0,0,0.3)`;
            } else { // Waning
                 moonVisualEl.style.background = `linear-gradient(to right, #f0f0f0 ${illumination}%, #333333 ${illumination}%)`;
                 moonVisualEl.style.boxShadow = `inset ${5 - (illumination/20)}px 0px 10px rgba(0,0,0,0.3)`;
            }
        } else {
            moonPhaseTextEl.textContent = `Error: ${moonDetails.error || 'Could not load moon phase.'}`;
        }
    } catch (error) {
        console.error("Error updating current moon phase display for header:", error);
        moonPhaseTextEl.textContent = "Error loading moon phase.";
        moonInfluenceEl.textContent = `Details: ${error.message}`;
    }
}


// Expose functions to be callable from script.js or HTML
window.initCalendarFeature = initCalendarFeature;
window.changeDisplayMonth = changeDisplayMonth; // If called directly from HTML, otherwise internal
window.selectDate = selectDate; // If called directly from HTML, otherwise internal
window.renderCalendar = renderCalendar; // Expose if script.js needs to trigger re-render
