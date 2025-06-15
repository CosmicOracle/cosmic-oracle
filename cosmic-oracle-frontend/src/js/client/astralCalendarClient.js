/**
 * Astral Calendar Feature
 * Displays cosmic events and personal events in a calendar view
 */

// Global variables
let astralCalendar = {
    events: [],
    settings: {},
    currentView: 'month', // 'day', 'week', 'month'
    selectedDate: new Date(),
    isInitialized: false
};

// API Service functions (as provided by you)
const astralCalendarService = {
    /**
     * Fetch cosmic events for a date range
     * @param {Date} startDate - Start date
     * @param {Date} endDate - End date
     * @param {string} timezone - User's timezone
     * @returns {Promise} - Promise resolving to events array
     */
    fetchCosmicEvents: async function(startDate, endDate, timezone = Intl.DateTimeFormat().resolvedOptions().timeZone) {
        try {
            const startDateStr = startDate.toISOString();
            const endDateStr = endDate.toISOString();
            
            const response = await fetch(`/api/astral-calendar/cosmic-events?start_date=${startDateStr}&end_date=${endDateStr}&timezone=${timezone}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                return data.data.events;
            } else {
                throw new Error(data.message || 'Failed to fetch cosmic events');
            }
        } catch (error) {
            console.error('Error fetching cosmic events:', error);
            // Try to load from local fallback data if available
            return await this.fetchLocalCosmicEvents(startDate, endDate);
        }
    },
    
    /**
     * Fetch local cosmic events data (fallback)
     * @param {Date} startDate - Start date
     * @param {Date} endDate - End date
     * @returns {Promise} - Promise resolving to events array
     */
    fetchLocalCosmicEvents: async function(startDate, endDate) {
        try {
            // Assuming your local data is at this path, adjust if necessary
            const response = await fetch('/data/cosmic_events_calendar.json'); 
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Filter events within the date range
            return data.filter(event => {
                const eventStartDate = new Date(event.start_date);
                const eventEndDate = event.end_date ? new Date(event.end_date) : eventStartDate;
                
                return (eventStartDate >= startDate && eventStartDate <= endDate) ||
                       (eventEndDate >= startDate && eventEndDate <= endDate) ||
                       (eventStartDate <= startDate && eventEndDate >= endDate);
            });
        } catch (error) {
            console.error('Error fetching local cosmic events:', error);
            return [];
        }
    },
    
    /**
     * Fetch personal events for a date range
     * @param {Date} startDate - Start date
     * @param {Date} endDate - End date
     * @returns {Promise} - Promise resolving to events array
     */
    fetchPersonalEvents: async function(startDate, endDate) {
        try {
            // Check if user is authenticated
            const token = localStorage.getItem('token');
            if (!token) {
                return [];
            }
            
            const startDateStr = startDate.toISOString();
            const endDateStr = endDate.toISOString();
            
            const response = await fetch(`/api/astral-calendar/personal-events?start_date=${startDateStr}&end_date=${endDateStr}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                return data.data.events;
            } else {
                throw new Error(data.message || 'Failed to fetch personal events');
            }
        } catch (error) {
            console.error('Error fetching personal events:', error);
            return [];
        }
    },
    
    /**
     * Create a new personal event
     * @param {Object} eventData - Event data
     * @returns {Promise} - Promise resolving to created event
     */
    createPersonalEvent: async function(eventData) {
        try {
            // Check if user is authenticated
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch('/api/astral-calendar/personal-events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(eventData)
            });
            
            if (!response.ok) {
                 const errorData = await response.json().catch(() => ({ message: `HTTP error! Status: ${response.status}` }));
                throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                return data.data.event;
            } else {
                throw new Error(data.message || 'Failed to create personal event');
            }
        } catch (error) {
            console.error('Error creating personal event:', error);
            throw error;
        }
    },
    
    /**
     * Update a personal event
     * @param {string} eventId - Event ID
     * @param {Object} eventData - Updated event data
     * @returns {Promise} - Promise resolving to updated event
     */
    updatePersonalEvent: async function(eventId, eventData) {
        try {
            // Check if user is authenticated
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch(`/api/astral-calendar/personal-events/${eventId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(eventData)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: `HTTP error! Status: ${response.status}` }));
                throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                return data.data.event;
            } else {
                throw new Error(data.message || 'Failed to update personal event');
            }
        } catch (error) {
            console.error('Error updating personal event:', error);
            throw error;
        }
    },
    
    /**
     * Delete a personal event
     * @param {string} eventId - Event ID
     * @returns {Promise} - Promise resolving to success message
     */
    deletePersonalEvent: async function(eventId) {
        try {
            // Check if user is authenticated
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch(`/api/astral-calendar/personal-events/${eventId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: `HTTP error! Status: ${response.status}` }));
                throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                return data.message;
            } else {
                throw new Error(data.message || 'Failed to delete personal event');
            }
        } catch (error) {
            console.error('Error deleting personal event:', error);
            throw error;
        }
    },
    
    /**
     * Fetch calendar settings
     * @returns {Promise} - Promise resolving to settings object
     */
    fetchCalendarSettings: async function() {
        try {
            // Check if user is authenticated
            const token = localStorage.getItem('token');
            if (!token) {
                return this.getDefaultSettings();
            }
            
            const response = await fetch('/api/astral-calendar/settings', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                // If settings not found for user, or other error, fallback to defaults
                if (response.status === 404) {
                    console.warn('No user settings found, using defaults.');
                    return this.getDefaultSettings();
                }
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success' && data.data.settings) {
                // Merge with defaults to ensure all keys are present
                return { ...this.getDefaultSettings(), ...data.data.settings };
            } else {
                 console.warn('Failed to fetch calendar settings or settings data is empty, using defaults.');
                return this.getDefaultSettings();
            }
        } catch (error) {
            console.error('Error fetching calendar settings:', error);
            return this.getDefaultSettings();
        }
    },
    
    /**
     * Update calendar settings
     * @param {Object} settingsData - Updated settings data
     * @returns {Promise} - Promise resolving to updated settings
     */
    updateCalendarSettings: async function(settingsData) {
        try {
            // Check if user is authenticated
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('User not authenticated');
            }
            
            const response = await fetch('/api/astral-calendar/settings', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(settingsData)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: `HTTP error! Status: ${response.status}` }));
                throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                return data.data.settings;
            } else {
                throw new Error(data.message || 'Failed to update calendar settings');
            }
        } catch (error) {
            console.error('Error updating calendar settings:', error);
            throw error;
        }
    },
    
    /**
     * Get default calendar settings
     * @returns {Object} - Default settings object
     */
    getDefaultSettings: function() {
        return {
            display_moon_phases: true,
            display_planetary_transits: true,
            display_meteor_showers: true,
            display_eclipses: true,
            display_retrogrades: true,
            notification_enabled: false, // Default to false for privacy unless user enables
            notification_days_before: 1,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };
    },
    
    /**
     * Get all events for a date range
     * @param {Date} startDate - Start date
     * @param {Date} endDate - End date
     * @param {string} timezone - User's timezone
     * @returns {Promise} - Promise resolving to combined events array
     */
    getAllEvents: async function(startDate, endDate, timezone = Intl.DateTimeFormat().resolvedOptions().timeZone) {
        try {
            // Get settings
            // Ensure astralCalendar.settings is populated, if not, fetch them.
            if (Object.keys(astralCalendar.settings).length === 0 && astralCalendar.isInitialized) { // Check if settings are empty but calendar is init
                 astralCalendar.settings = await this.fetchCalendarSettings();
            } else if (Object.keys(astralCalendar.settings).length === 0) { // Initial load or not yet initialized
                 astralCalendar.settings = await this.fetchCalendarSettings();
            }
            const settings = astralCalendar.settings;

            // Get cosmic events based on settings
            const cosmicEvents = await this.fetchCosmicEvents(startDate, endDate, timezone);
            
            // Filter cosmic events based on settings
            const filteredCosmicEvents = cosmicEvents.filter(event => {
                switch (event.event_type) {
                    case 'moon_phase':
                        return settings.display_moon_phases;
                    case 'planetary_transit':
                        return settings.display_planetary_transits;
                    case 'meteor_shower':
                        return settings.display_meteor_showers;
                    case 'solar_eclipse':
                    case 'lunar_eclipse':
                        return settings.display_eclipses;
                    case 'retrograde': // This might be a sub-type of planetary_transit
                        return settings.display_retrogrades;
                    default: // For other cosmic events not explicitly listed in settings
                        return true; 
                }
            });
            
            // Get personal events
            const personalEvents = await this.fetchPersonalEvents(startDate, endDate);
            
            // Combine events
            const allEvents = [...filteredCosmicEvents, ...personalEvents];
            
            // Sort events by date
            allEvents.sort((a, b) => {
                const dateA = new Date(a.start_date);
                const dateB = new Date(b.start_date);
                return dateA - dateB;
            });
            
            return allEvents;
        } catch (error) {
            console.error('Error getting all events:', error);
            return [];
        }
    }
};

// UI functions
export const astralCalendarUI = { // Added export keyword
    /**
     * Initialize the calendar
     * @param {string} containerId - ID of the container element
     */
    initialize: async function(containerId) {
        if (astralCalendar.isInitialized) {
            return;
        }
        
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container element with ID '${containerId}' not found`);
            return;
        }
        
        this.createCalendarUI(container);
        
        // Load settings first, so getAllEvents in loadEvents can use them
        astralCalendar.settings = await astralCalendarService.fetchCalendarSettings();
        
        await this.loadEvents();
        this.renderCalendar();
        this.addEventListeners(); // Add event listeners after UI is created and initial data loaded
        
        astralCalendar.isInitialized = true;
    },
    
    /**
     * Create calendar UI elements
     * @param {HTMLElement} container - Container element
     */
    createCalendarUI: function(container) {
        // (Code as provided by user - no changes here)
        // Create calendar header
        const header = document.createElement('div');
        header.className = 'astral-calendar-header';
        header.innerHTML = `
            <div class="calendar-title">
                <h2>Astral Calendar</h2>
                <p class="current-date"></p>
            </div>
            <div class="calendar-controls">
                <button id="prev-btn" class="calendar-btn"><i class="fas fa-chevron-left"></i></button>
                <div class="view-controls">
                    <button id="day-view-btn" class="view-btn">Day</button>
                    <button id="week-view-btn" class="view-btn">Week</button>
                    <button id="month-view-btn" class="view-btn active">Month</button>
                </div>
                <button id="next-btn" class="calendar-btn"><i class="fas fa-chevron-right"></i></button>
                <button id="today-btn" class="calendar-btn">Today</button>
                <button id="settings-btn" class="calendar-btn"><i class="fas fa-cog"></i></button>
            </div>
        `;
        
        // Create calendar body
        const body = document.createElement('div');
        body.className = 'astral-calendar-body';
        
        // Create calendar grid
        const grid = document.createElement('div');
        grid.className = 'calendar-grid';
        grid.id = 'calendar-grid';
        body.appendChild(grid);
        
        // Create event details panel
        const detailsPanel = document.createElement('div');
        detailsPanel.className = 'event-details-panel'; // Add 'panel' class for common styling
        detailsPanel.id = 'event-details-panel';
        detailsPanel.innerHTML = `
            <div class="panel-header">
                <h3>Event Details</h3>
                <button id="close-details-btn" class="close-btn"><i class="fas fa-times"></i></button>
            </div>
            <div class="panel-body" id="event-details-content">
                <p>Select an event to view details</p>
            </div>
        `;
        
        // Create settings panel
        const settingsPanel = document.createElement('div');
        settingsPanel.className = 'settings-panel'; // Add 'panel' class
        settingsPanel.id = 'settings-panel';
        settingsPanel.innerHTML = `
            <div class="panel-header">
                <h3>Calendar Settings</h3>
                <button id="close-settings-btn" class="close-btn"><i class="fas fa-times"></i></button>
            </div>
            <div class="panel-body">
                <form id="settings-form">
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="display-moon-phases" name="display_moon_phases">
                            Display Moon Phases
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="display-planetary-transits" name="display_planetary_transits">
                            Display Planetary Transits
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="display-meteor-showers" name="display_meteor_showers">
                            Display Meteor Showers
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="display-eclipses" name="display_eclipses">
                            Display Eclipses
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="display-retrogrades" name="display_retrogrades">
                            Display Retrogrades
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="notification-enabled" name="notification_enabled">
                            Enable Notifications (Future Feature)
                        </label>
                    </div>
                    <div class="form-group">
                        <label for="notification-days">Days Before Event (Future Feature):</label>
                        <input type="number" id="notification-days" name="notification_days_before" min="0" max="30" value="1">
                    </div>
                    <div class="form-group">
                        <button type="submit" class="btn-save">Save Settings</button>
                    </div>
                </form>
            </div>
        `;
        
        // Create add event button
        const addEventBtn = document.createElement('button');
        addEventBtn.className = 'add-event-btn';
        addEventBtn.id = 'add-event-btn';
        addEventBtn.innerHTML = '<i class="fas fa-plus"></i> Add Event';
        
        // Create add event panel
        const addEventPanel = document.createElement('div');
        addEventPanel.className = 'add-event-panel'; // Add 'panel' class
        addEventPanel.id = 'add-event-panel';
        addEventPanel.innerHTML = `
            <div class="panel-header">
                <h3>Add Personal Event</h3>
                <button id="close-add-event-btn" class="close-btn"><i class="fas fa-times"></i></button>
            </div>
            <div class="panel-body">
                <form id="add-event-form">
                    <input type="hidden" id="event-id" name="event_id"> <div class="form-group">
                        <label for="event-title">Title:</label>
                        <input type="text" id="event-title" name="title" required>
                    </div>
                    <div class="form-group">
                        <label for="event-date">Date:</label>
                        <input type="date" id="event-date" name="start_date_date" required>
                    </div>
                    <div class="form-group">
                        <label for="event-time">Time (optional, for all-day leave blank):</label>
                        <input type="time" id="event-time" name="start_date_time">
                    </div>
                     <div class="form-group">
                        <label for="event-end-date">End Date (optional):</label>
                        <input type="date" id="event-end-date" name="end_date_date">
                    </div>
                    <div class="form-group">
                        <label for="event-end-time">End Time (optional):</label>
                        <input type="time" id="event-end-time" name="end_date_time">
                    </div>
                    <div class="form-group">
                        <label for="event-personal-type">Event Type:</label>
                        <select id="event-personal-type" name="event_type" required>
                            <option value="personal_event">Personal Event</option>
                            <option value="birthday">Birthday</option>
                            <option value="anniversary">Anniversary</option>
                            <option value="personal_milestone">Personal Milestone</option>
                            <option value="reminder">Reminder</option>
                            <option value="other_personal">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="event-description">Description:</label>
                        <textarea id="event-description" name="description"></textarea>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="event-all-day" name="all_day">
                            All-day event
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="event-recurring" name="is_recurring">
                            Recurring Event
                        </label>
                    </div>
                    <div class="form-group recurring-options" style="display: none;">
                        <label for="recurrence-pattern">Recurrence:</label>
                        <select id="recurrence-pattern" name="recurrence_pattern">
                            <option value="yearly">Yearly</option>
                            <option value="monthly">Monthly</option>
                            <option value="weekly">Weekly</option> 
                        </select>
                    </div>
                    <div class="form-group">
                        <button type="submit" class="btn-save">Save Event</button>
                    </div>
                </form>
            </div>
        `;
        
        container.appendChild(header);
        container.appendChild(body);
        container.appendChild(detailsPanel);
        container.appendChild(settingsPanel);
        container.appendChild(addEventBtn); // Add this button to the main container
        container.appendChild(addEventPanel);
    },
    
    /**
     * Load events for the current view
     */
    loadEvents: async function() {
        const { startDate, endDate } = this.getDateRange();
        astralCalendar.events = await astralCalendarService.getAllEvents(startDate, endDate);
    },
    
    /**
     * Get date range for the current view
     * @returns {Object} - Object with startDate and endDate
     */
    getDateRange: function() {
        // (Code as provided by user - no changes here)
        const date = astralCalendar.selectedDate;
        let startDate, endDate;
        
        switch (astralCalendar.currentView) {
            case 'day':
                startDate = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0, 0);
                endDate = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999);
                break;
            case 'week':
                const dayOfWeek = date.getDay(); // 0 (Sun) - 6 (Sat)
                startDate = new Date(date.getFullYear(), date.getMonth(), date.getDate() - dayOfWeek, 0, 0, 0, 0);
                endDate = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate() + 6, 23, 59, 59, 999);
                break;
            case 'month':
            default:
                startDate = new Date(date.getFullYear(), date.getMonth(), 1, 0, 0, 0, 0);
                endDate = new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999); // Day 0 of next month is last day of current
                break;
        }
        return { startDate, endDate };
    },
    
    /**
     * Render the calendar based on the current view
     */
    renderCalendar: function() {
        // (Code as provided by user, with slight modifications for clarity)
        const currentDateElem = document.querySelector('.current-date');
        const options = { year: 'numeric', month: 'long' };
        if (astralCalendar.currentView === 'day' || astralCalendar.currentView === 'week') { // Week also benefits from specific date
            options.day = 'numeric';
             if (astralCalendar.currentView === 'week') {
                const { startDate, endDate } = this.getDateRange();
                currentDateElem.textContent = `${startDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} - ${endDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
            } else {
                 currentDateElem.textContent = astralCalendar.selectedDate.toLocaleDateString(undefined, options);
            }
        } else {
            currentDateElem.textContent = astralCalendar.selectedDate.toLocaleDateString(undefined, options);
        }
        
        const grid = document.getElementById('calendar-grid');
        grid.innerHTML = '';
        grid.className = `calendar-grid ${astralCalendar.currentView}-view`;
        
        switch (astralCalendar.currentView) {
            case 'day':
                this.renderDayView(grid);
                break;
            case 'week':
                this.renderWeekView(grid);
                break;
            case 'month':
            default:
                this.renderMonthView(grid);
                break;
        }
        
        const viewBtns = document.querySelectorAll('.view-btn');
        viewBtns.forEach(btn => {
            btn.classList.remove('active');
            if (btn.id === `${astralCalendar.currentView}-view-btn`) {
                btn.classList.add('active');
            }
        });
    },
    
    /**
     * Render day view
     * @param {HTMLElement} grid - Grid element
     */
    renderDayView: function(grid) {
        // (Code as provided by user - calls this.createEventElement)
        const date = astralCalendar.selectedDate;
        const dayStart = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0);
        const dayEnd = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59);
        
        // Create header
        const header = document.createElement('div');
        header.className = 'day-header';
        header.textContent = date.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
        grid.appendChild(header);

        const allDayContainer = document.createElement('div');
        allDayContainer.className = 'all-day-events-container';
        grid.appendChild(allDayContainer); // Add container for all-day events
        
        const timeSlotsContainer = document.createElement('div');
        timeSlotsContainer.className = 'time-slots-container';
        grid.appendChild(timeSlotsContainer);

        // Add all-day events at the top
        const allDayEvents = astralCalendar.events.filter(event => {
            const eventStart = new Date(event.start_date);
            return event.all_day || (eventStart.getHours() === 0 && eventStart.getMinutes() === 0 && eventStart.getDate() === date.getDate() && eventStart.getMonth() === date.getMonth() && eventStart.getFullYear() === date.getFullYear());
        });
        
        if (allDayEvents.length > 0) {
            const allDayCell = document.createElement('div');
            allDayCell.className = 'all-day-cell-dayview'; // Specific class for day view
            
            const allDayLabel = document.createElement('div');
            allDayLabel.className = 'all-day-label';
            allDayLabel.textContent = 'All Day';
            allDayCell.appendChild(allDayLabel);
            
            const allDayContent = document.createElement('div');
            allDayContent.className = 'all-day-content';
            
            allDayEvents.forEach(event => {
                const eventElem = this.createEventElement(event); // isMonthViewCompact defaults to false
                allDayContent.appendChild(eventElem);
            });
            allDayCell.appendChild(allDayContent);
            allDayContainer.appendChild(allDayCell);
        }
        
        // Create hour cells
        for (let hour = 0; hour < 24; hour++) {
            const hourCell = document.createElement('div');
            hourCell.className = 'hour-cell';
            
            const hourLabel = document.createElement('div');
            hourLabel.className = 'hour-label';
            hourLabel.textContent = `${hour.toString().padStart(2, '0')}:00`; // Format hour
            
            const hourContent = document.createElement('div');
            hourContent.className = 'hour-content';
            
            // Filter events for this hour (that are not all-day)
            const hourEvents = astralCalendar.events.filter(event => {
                if (event.all_day) return false;
                const eventDate = new Date(event.start_date);
                return eventDate.getDate() === date.getDate() && 
                       eventDate.getMonth() === date.getMonth() && 
                       eventDate.getFullYear() === date.getFullYear() && 
                       eventDate.getHours() === hour;
            });
            
            hourEvents.forEach(event => {
                const eventElem = this.createEventElement(event);
                hourContent.appendChild(eventElem);
            });
            
            hourCell.appendChild(hourLabel);
            hourCell.appendChild(hourContent);
            timeSlotsContainer.appendChild(hourCell);
        }
    },
    
    /**
     * Render week view
     * @param {HTMLElement} grid - Grid element
     */
    renderWeekView: function(grid) {
        // (Code as provided by user - calls this.createEventElement)
        const date = astralCalendar.selectedDate;
        const dayOfWeek = date.getDay();
        const weekStart = new Date(date.getFullYear(), date.getMonth(), date.getDate() - dayOfWeek);
        
        // Create header row
        const headerRow = document.createElement('div');
        headerRow.className = 'week-header-row'; // Changed class for better targeting
        
        const emptyHeader = document.createElement('div');
        emptyHeader.className = 'week-header-cell time-label-header'; // Class for time column header
        headerRow.appendChild(emptyHeader);
        
        for (let i = 0; i < 7; i++) {
            const dayDate = new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate() + i);
            const dayHeader = document.createElement('div');
            dayHeader.className = 'week-header-cell';
            
            if (dayDate.toDateString() === new Date().toDateString()) dayHeader.classList.add('current-day');
            if (dayDate.toDateString() === astralCalendar.selectedDate.toDateString()) dayHeader.classList.add('selected-day');
            
            const dayName = document.createElement('div');
            dayName.className = 'day-name';
            dayName.textContent = dayDate.toLocaleDateString(undefined, { weekday: 'short' });
            
            const dayNum = document.createElement('div');
            dayNum.className = 'day-num';
            dayNum.textContent = dayDate.getDate();
            
            dayHeader.appendChild(dayName);
            dayHeader.appendChild(dayNum);
            dayHeader.dataset.date = dayDate.toISOString();
            
            dayHeader.addEventListener('click', () => {
                astralCalendar.selectedDate = new Date(dayDate);
                this.renderCalendar(); // Re-render to update selection
            });
            headerRow.appendChild(dayHeader);
        }
        grid.appendChild(headerRow);
        
        // Create all-day row
        const allDayRow = document.createElement('div');
        allDayRow.className = 'all-day-row-weekview';
        
        const allDayLabelCell = document.createElement('div'); // Cell for "All Day" label
        allDayLabelCell.className = 'all-day-label-cell';
        allDayLabelCell.textContent = 'All Day';
        allDayRow.appendChild(allDayLabelCell);
        
        for (let i = 0; i < 7; i++) {
            const dayDate = new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate() + i);
            const allDayCellContent = document.createElement('div');
            allDayCellContent.className = 'all-day-cell-content'; // Content within each day's all-day slot
            
            const dayEvents = astralCalendar.events.filter(event => {
                const eventStart = new Date(event.start_date);
                // Check if event is all_day or starts at midnight on this day
                return (event.all_day || (eventStart.getHours() === 0 && eventStart.getMinutes() === 0)) &&
                       eventStart.toDateString() === dayDate.toDateString();
            });
            
            dayEvents.forEach(event => {
                allDayCellContent.appendChild(this.createEventElement(event, true)); // Compact for all-day week view
            });
            allDayRow.appendChild(allDayCellContent);
        }
        grid.appendChild(allDayRow);
        
        // Create time grid
        const timeGridContainer = document.createElement('div');
        timeGridContainer.className = 'time-grid-container-weekview';
        
        const timeLabelsColumn = document.createElement('div');
        timeLabelsColumn.className = 'time-labels-column';
        for (let hour = 0; hour < 24; hour++) {
            const timeLabel = document.createElement('div');
            timeLabel.className = 'time-label-week';
            timeLabel.textContent = `${hour.toString().padStart(2, '0')}:00`;
            timeLabelsColumn.appendChild(timeLabel);
        }
        timeGridContainer.appendChild(timeLabelsColumn);
        
        const daysContainer = document.createElement('div');
        daysContainer.className = 'days-container-weekview';

        for (let i = 0; i < 7; i++) {
            const dayDate = new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate() + i);
            const dayColumn = document.createElement('div');
            dayColumn.className = 'day-column-week';
             if (dayDate.toDateString() === new Date().toDateString()) dayColumn.classList.add('current-day');
            if (dayDate.toDateString() === astralCalendar.selectedDate.toDateString()) dayColumn.classList.add('selected-day');

            for (let hour = 0; hour < 24; hour++) {
                const hourCell = document.createElement('div');
                hourCell.className = 'hour-cell-week';
                
                const hourEvents = astralCalendar.events.filter(event => {
                    if (event.all_day) return false;
                    const eventDate = new Date(event.start_date);
                    return eventDate.toDateString() === dayDate.toDateString() && eventDate.getHours() === hour;
                });
                
                hourEvents.forEach(event => {
                    hourCell.appendChild(this.createEventElement(event));
                });
                dayColumn.appendChild(hourCell);
            }
            daysContainer.appendChild(dayColumn);
        }
        timeGridContainer.appendChild(daysContainer);
        grid.appendChild(timeGridContainer);
    },
    
    /**
     * Render month view
     * @param {HTMLElement} grid - Grid element
     */
    renderMonthView: function(grid) {
        // (Code as provided by user - calls this.createEventElement with isMonthViewCompact = true)
        const date = astralCalendar.selectedDate;
        const firstDayOfMonth = new Date(date.getFullYear(), date.getMonth(), 1);
        const lastDayOfMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        
        const firstDayOfWeek = firstDayOfMonth.getDay(); // 0 (Sun) to 6 (Sat)
        
        const weekdayHeader = document.createElement('div');
        weekdayHeader.className = 'weekday-header-month';
        const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        weekdays.forEach(day => {
            const dayHeaderCell = document.createElement('div');
            dayHeaderCell.className = 'weekday-cell-month';
            dayHeaderCell.textContent = day;
            weekdayHeader.appendChild(dayHeaderCell);
        });
        grid.appendChild(weekdayHeader);
        
        const monthGridCells = document.createElement('div');
        monthGridCells.className = 'month-grid-cells';
        
        // Days from previous month
        const prevMonthLastDate = new Date(date.getFullYear(), date.getMonth(), 0);
        for (let i = 0; i < firstDayOfWeek; i++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'day-cell-month prev-month-day';
            const dayNum = document.createElement('div');
            dayNum.className = 'day-num-month';
            dayNum.textContent = prevMonthLastDate.getDate() - firstDayOfWeek + i + 1;
            dayCell.appendChild(dayNum);
            monthGridCells.appendChild(dayCell);
        }
        
        // Days of current month
        for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
            const dayDate = new Date(date.getFullYear(), date.getMonth(), i);
            const dayCell = document.createElement('div');
            dayCell.className = 'day-cell-month current-month-day';
            if (dayDate.toDateString() === new Date().toDateString()) dayCell.classList.add('current-day');
            if (dayDate.toDateString() === astralCalendar.selectedDate.toDateString()) dayCell.classList.add('selected-day');
            
            const dayNum = document.createElement('div');
            dayNum.className = 'day-num-month';
            dayNum.textContent = i;
            dayCell.appendChild(dayNum);
            
            const eventsContainer = document.createElement('div');
            eventsContainer.className = 'day-events-month';
            
            const dayEvents = astralCalendar.events.filter(event => {
                const eventStart = new Date(event.start_date);
                const eventEnd = event.end_date ? new Date(event.end_date) : eventStart;
                // Check if event falls on this day
                return (eventStart.getFullYear() === dayDate.getFullYear() &&
                        eventStart.getMonth() === dayDate.getMonth() &&
                        eventStart.getDate() === dayDate.getDate()) ||
                       (eventEnd.getFullYear() === dayDate.getFullYear() &&
                        eventEnd.getMonth() === dayDate.getMonth() &&
                        eventEnd.getDate() === dayDate.getDate()) ||
                       (eventStart < dayDate && eventEnd > dayDate);
            });
            
            dayEvents.forEach(event => {
                eventsContainer.appendChild(this.createEventElement(event, true)); // Compact for month view
            });
            dayCell.appendChild(eventsContainer);
            
            dayCell.addEventListener('click', () => {
                astralCalendar.selectedDate = new Date(dayDate);
                this.renderCalendar(); // Re-render to update selection
                // Optionally, switch to day view: this.handleChangeView('day');
            });
            monthGridCells.appendChild(dayCell);
        }
        
        // Days from next month
        const totalCells = firstDayOfWeek + lastDayOfMonth.getDate();
        const nextMonthDaysCount = (totalCells % 7 === 0) ? 0 : 7 - (totalCells % 7);
        for (let i = 1; i <= nextMonthDaysCount; i++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'day-cell-month next-month-day';
            const dayNum = document.createElement('div');
            dayNum.className = 'day-num-month';
            dayNum.textContent = i;
            dayCell.appendChild(dayNum);
            monthGridCells.appendChild(dayCell);
        }
        grid.appendChild(monthGridCells);
    },

    // --- NEWLY ADDED/COMPLETED FUNCTIONS ---

    /**
     * Create an HTML element for an event
     * @param {Object} event - Event object
     * @param {boolean} isMonthViewCompact - Whether to render a compact version for month view
     * @returns {HTMLElement} - Event element
     */
    createEventElement: function(event, isMonthViewCompact = false) {
        const eventElem = document.createElement('div');
        eventElem.className = 'calendar-event';
        eventElem.classList.add(this.getEventTypeClass(event.event_type));
        eventElem.dataset.eventId = event.id || event.title + event.start_date; // Use a more stable unique key if ID is not always present

        const eventDate = new Date(event.start_date);
        const timeOptions = { hour: 'numeric', minute: '2-digit', hour12: true };

        if (isMonthViewCompact) {
            const eventDot = document.createElement('span');
            eventDot.className = 'event-dot';
            eventElem.appendChild(eventDot);
            const eventTitleCompact = document.createElement('span');
            eventTitleCompact.className = 'event-title-compact';
            eventTitleCompact.textContent = event.title;
            eventElem.appendChild(eventTitleCompact);
        } else {
            const eventIcon = document.createElement('i');
            eventIcon.className = `fas ${this.getEventIcon(event.event_type)} event-icon`;
            eventElem.appendChild(eventIcon);

            const eventTitle = document.createElement('span');
            eventTitle.className = 'event-title';
            eventTitle.textContent = event.title;
            eventElem.appendChild(eventTitle);

            if (!event.all_day && !(eventDate.getHours() === 0 && eventDate.getMinutes() === 0 && (!event.end_date || new Date(event.end_date).getHours() === 23 ))) {
                const eventTime = document.createElement('span');
                eventTime.className = 'event-time';
                eventTime.textContent = ` ${eventDate.toLocaleTimeString(undefined, timeOptions)}`;
                eventElem.appendChild(eventTime);
            }
        }

        eventElem.addEventListener('click', (e) => {
            e.stopPropagation();
            this.displayEventDetails(event);
        });
        return eventElem;
    },

    /**
     * Display event details in the panel
     * @param {Object} event - Event object
     */
    displayEventDetails: function(event) {
        const detailsContent = document.getElementById('event-details-content');
        if (!detailsContent) return;

        const startDate = new Date(event.start_date);
        const endDate = event.end_date ? new Date(event.end_date) : null;
        const timeFormatOptions = { hour: 'numeric', minute: '2-digit', hour12: true };
        const dateFormatOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };

        let html = `
            <h4>${event.title}</h4>
            <p><strong>Type:</strong> ${this.formatEventType(event.event_type || 'N/A')}</p>
            <p><strong>Date:</strong> ${startDate.toLocaleDateString(undefined, dateFormatOptions)}</p>
        `;

        if (event.all_day) {
            html += `<p><strong>Time:</strong> All-day</p>`;
            if (endDate && endDate.toDateString() !== startDate.toDateString()) {
                 html += `<p><strong>Ends:</strong> ${endDate.toLocaleDateString(undefined, dateFormatOptions)}</p>`;
            }
        } else {
             html += `<p><strong>Time:</strong> ${startDate.toLocaleTimeString(undefined, timeFormatOptions)}`;
             if (endDate && (endDate.toISOString() !== startDate.toISOString())) {
                 html += ` - ${endDate.toLocaleTimeString(undefined, timeFormatOptions)}`;
                 if (endDate.toDateString() !== startDate.toDateString()) {
                     html += ` (ends ${endDate.toLocaleDateString(undefined, {month: 'short', day: 'numeric'})})`;
                 }
             }
             html += `</p>`;
        }
        
        if (event.description) html += `<p><strong>Description:</strong> ${event.description}</p>`;
        if (event.location) html += `<p><strong>Location:</strong> ${event.location}</p>`;
        if (event.category) html += `<p><strong>Category:</strong> ${event.category}</p>`;
        if (event.sign) html += `<p><strong>Sign:</strong> ${event.sign}</p>`;
        if (event.related_planet) html += `<p><strong>Planet:</strong> ${event.related_planet}</p>`;
        if (event.is_recurring) html += `<p><strong>Recurring:</strong> ${event.recurrence_pattern ? this.formatEventType(event.recurrence_pattern) : 'Yes'}</p>`;


        const knownCosmicTypes = ['moon_phase', 'planetary_transit', 'meteor_shower', 'solar_eclipse', 'lunar_eclipse', 'retrograde', 'cosmic_general'];
        // Check if it's a personal event (has an ID and not a known cosmic type OR has a specific personal type)
        const isPersonalEvent = event.id && 
            (!knownCosmicTypes.includes(event.event_type) || 
             ['birthday', 'anniversary', 'personal_milestone', 'reminder', 'other_personal', 'personal_event'].includes(event.event_type));

        if (isPersonalEvent) {
            html += `
                <div class="event-actions">
                    <button class="btn-edit-event" data-event-id="${event.id}"><i class="fas fa-edit"></i> Edit</button>
                    <button class="btn-delete-event" data-event-id="${event.id}"><i class="fas fa-trash"></i> Delete</button>
                </div>
            `;
        }
        detailsContent.innerHTML = html;

        detailsContent.querySelector('.btn-edit-event')?.addEventListener('click', () => this.handleEditEvent(event));
        detailsContent.querySelector('.btn-delete-event')?.addEventListener('click', () => this.handleDeleteEvent(event.id));
        
        this.openPanel('event-details-panel');
    },

    /**
     * Add all necessary event listeners for calendar controls and interactions
     */
    addEventListeners: function() {
        document.getElementById('prev-btn')?.addEventListener('click', () => this.handlePrevNext(-1));
        document.getElementById('next-btn')?.addEventListener('click', () => this.handlePrevNext(1));
        document.getElementById('today-btn')?.addEventListener('click', () => this.handleToday());

        document.getElementById('day-view-btn')?.addEventListener('click', () => this.handleChangeView('day'));
        document.getElementById('week-view-btn')?.addEventListener('click', () => this.handleChangeView('week'));
        document.getElementById('month-view-btn')?.addEventListener('click', () => this.handleChangeView('month'));

        document.getElementById('settings-btn')?.addEventListener('click', () => {
            this.populateSettingsForm();
            this.openPanel('settings-panel');
        });
        document.getElementById('close-settings-btn')?.addEventListener('click', () => this.closePanel('settings-panel'));
        document.getElementById('close-details-btn')?.addEventListener('click', () => this.closePanel('event-details-panel'));
        
        document.getElementById('add-event-btn')?.addEventListener('click', () => {
            this.resetAddEventForm(); // Clear form for new event
            this.openPanel('add-event-panel');
        });
        document.getElementById('close-add-event-btn')?.addEventListener('click', () => this.closePanel('add-event-panel'));

        document.getElementById('settings-form')?.addEventListener('submit', (e) => this.handleSettingsFormSubmit(e));
        document.getElementById('add-event-form')?.addEventListener('submit', (e) => this.handleAddEventFormSubmit(e));
        
        const recurringCheckbox = document.getElementById('event-recurring');
        const recurringOptionsDiv = document.querySelector('#add-event-form .recurring-options');
        recurringCheckbox?.addEventListener('change', function() {
            if (recurringOptionsDiv) recurringOptionsDiv.style.display = this.checked ? 'block' : 'none';
        });

        const allDayCheckbox = document.getElementById('event-all-day');
        const timeInput = document.getElementById('event-time');
        const endTimeInput = document.getElementById('event-end-time');
        allDayCheckbox?.addEventListener('change', function() {
            if (timeInput) timeInput.disabled = this.checked;
            if (endTimeInput) endTimeInput.disabled = this.checked;
            if (this.checked) {
                if (timeInput) timeInput.value = '';
                if (endTimeInput) endTimeInput.value = '';
            }
        });
    },

    // --- HELPER FUNCTIONS ---

    handlePrevNext: async function(direction) {
        const current = astralCalendar.selectedDate;
        switch (astralCalendar.currentView) {
            case 'day':
                astralCalendar.selectedDate = new Date(current.setDate(current.getDate() + direction));
                break;
            case 'week':
                astralCalendar.selectedDate = new Date(current.setDate(current.getDate() + (7 * direction)));
                break;
            case 'month':
            default:
                astralCalendar.selectedDate = new Date(current.setMonth(current.getMonth() + direction, 1)); // Set day to 1 to avoid month skips
                break;
        }
        await this.loadEvents();
        this.renderCalendar();
    },

    handleToday: async function() {
        astralCalendar.selectedDate = new Date();
        await this.loadEvents();
        this.renderCalendar();
    },

    handleChangeView: async function(view) {
        if (astralCalendar.currentView === view) return;
        astralCalendar.currentView = view;
        await this.loadEvents(); // Reload events for the new view's date range
        this.renderCalendar();
    },

    openPanel: function(panelId) {
        const panel = document.getElementById(panelId);
        if (panel) {
            ['event-details-panel', 'settings-panel', 'add-event-panel'].forEach(id => {
                const p = document.getElementById(id);
                if (p && id !== panelId) p.classList.remove('active');
            });
            panel.classList.add('active');
        }
    },

    closePanel: function(panelId) {
        document.getElementById(panelId)?.classList.remove('active');
    },

    populateSettingsForm: function() {
        const settings = astralCalendar.settings || astralCalendarService.getDefaultSettings();
        const form = document.getElementById('settings-form');
        if (!form) return;

        form.querySelector('#display-moon-phases').checked = !!settings.display_moon_phases;
        form.querySelector('#display-planetary-transits').checked = !!settings.display_planetary_transits;
        form.querySelector('#display-meteor-showers').checked = !!settings.display_meteor_showers;
        form.querySelector('#display-eclipses').checked = !!settings.display_eclipses;
        form.querySelector('#display-retrogrades').checked = !!settings.display_retrogrades;
        form.querySelector('#notification-enabled').checked = !!settings.notification_enabled;
        form.querySelector('#notification-days').value = settings.notification_days_before || 1;
    },

    handleSettingsFormSubmit: async function(e) {
        e.preventDefault();
        const form = e.target;
        const newSettings = {
            display_moon_phases: form.querySelector('#display-moon-phases').checked,
            display_planetary_transits: form.querySelector('#display-planetary-transits').checked,
            display_meteor_showers: form.querySelector('#display-meteor-showers').checked,
            display_eclipses: form.querySelector('#display-eclipses').checked,
            display_retrogrades: form.querySelector('#display-retrogrades').checked,
            notification_enabled: form.querySelector('#notification-enabled').checked,
            notification_days_before: parseInt(form.querySelector('#notification-days').value, 10),
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        };

        try {
            const updatedSettings = await astralCalendarService.updateCalendarSettings(newSettings);
            astralCalendar.settings = updatedSettings;
            await this.loadEvents();
            this.renderCalendar();
            this.closePanel('settings-panel');
            // Import dynamically since this is not a module
            import('../utils/notifications.js').then(({ showSuccess }) => {
                showSuccess('Settings updated successfully!');
            });
            console.log('Settings updated.');
        } catch (error) {
            console.error('Failed to update settings:', error);
            // Import dynamically since this is not a module
            import('../utils/notifications.js').then(({ showError }) => {
                showError('Failed to update settings. Please try again.');
            });
        }
    },

    resetAddEventForm: function(event = null) {
        const form = document.getElementById('add-event-form');
        if (!form) return;
        form.reset(); // Clears form fields

        document.getElementById('event-id').value = event ? event.id : '';
        document.getElementById('event-title').value = event ? event.title : '';
        
        const startDate = event ? new Date(event.start_date) : new Date();
        document.getElementById('event-date').value = startDate.toISOString().split('T')[0];

        const allDayCheckbox = document.getElementById('event-all-day');
        const timeInput = document.getElementById('event-time');
        if (event && !event.all_day && event.start_date) {
             allDayCheckbox.checked = false;
             timeInput.value = `${String(startDate.getHours()).padStart(2, '0')}:${String(startDate.getMinutes()).padStart(2, '0')}`;
             timeInput.disabled = false;
        } else if (event && event.all_day) {
            allDayCheckbox.checked = true;
            timeInput.value = '';
            timeInput.disabled = true;
        } else { // New event
            allDayCheckbox.checked = false; // Default to not all-day
            timeInput.value = '';
            timeInput.disabled = false;
        }

        const endDateInput = document.getElementById('event-end-date');
        const endTimeInput = document.getElementById('event-end-time');
        if (event && event.end_date) {
            const endDateObj = new Date(event.end_date);
            endDateInput.value = endDateObj.toISOString().split('T')[0];
            if (!event.all_day) {
                 endTimeInput.value = `${String(endDateObj.getHours()).padStart(2, '0')}:${String(endDateObj.getMinutes()).padStart(2, '0')}`;
                 endTimeInput.disabled = false;
            } else {
                endTimeInput.value = '';
                endTimeInput.disabled = true;
            }
        } else {
            endDateInput.value = '';
            endTimeInput.value = '';
            endTimeInput.disabled = allDayCheckbox.checked;
        }


        document.getElementById('event-personal-type').value = event ? (event.event_type || 'personal_event') : 'personal_event';
        document.getElementById('event-description').value = event ? (event.description || '') : '';
        
        const recurringCheckbox = document.getElementById('event-recurring');
        const recurringOptionsDiv = form.querySelector('.recurring-options');
        recurringCheckbox.checked = event ? !!event.is_recurring : false;
        recurringOptionsDiv.style.display = recurringCheckbox.checked ? 'block' : 'none';
        document.getElementById('recurrence-pattern').value = event && event.recurrence_pattern ? event.recurrence_pattern : 'yearly';

        const panelTitle = document.querySelector('#add-event-panel .panel-header h3');
        panelTitle.textContent = event ? 'Edit Personal Event' : 'Add Personal Event';
        form.querySelector('button[type="submit"]').textContent = event ? 'Update Event' : 'Save Event';
    },

    handleAddEventFormSubmit: async function(e) {
        e.preventDefault();
        const form = e.target;
        const eventId = form.querySelector('#event-id').value;

        const title = form.querySelector('#event-title').value;
        const dateStr = form.querySelector('#event-date').value;
        const timeStr = form.querySelector('#event-time').value;
        const endDateStr = form.querySelector('#event-end-date').value;
        const endTimeStr = form.querySelector('#event-end-time').value;
        const isAllDay = form.querySelector('#event-all-day').checked;

        let startDateTime;
        if (isAllDay || !timeStr) {
            startDateTime = new Date(`${dateStr}T00:00:00`); // Treat as local start of day
        } else {
            startDateTime = new Date(`${dateStr}T${timeStr}`);
        }

        let endDateTime = null;
        if (endDateStr) {
            if (isAllDay || !endTimeStr) {
                endDateTime = new Date(`${endDateStr}T23:59:59`); // Local end of day
            } else {
                endDateTime = new Date(`${endDateStr}T${endTimeStr}`);
            }
        }


        const eventData = {
            title: title,
            start_date: startDateTime.toISOString(),
            end_date: endDateTime ? endDateTime.toISOString() : null,
            event_type: form.querySelector('#event-personal-type').value,
            description: form.querySelector('#event-description').value,
            all_day: isAllDay,
            is_recurring: form.querySelector('#event-recurring').checked,
            recurrence_pattern: form.querySelector('#event-recurring').checked ? form.querySelector('#recurrence-pattern').value : null,
        };
        
        try {
            if (eventId) {
                await astralCalendarService.updatePersonalEvent(eventId, eventData);
                import('../utils/notifications.js').then(({ showSuccess }) => {
                    showSuccess('Event updated successfully!');
                });
                console.log('Event updated.');
            } else {
                await astralCalendarService.createPersonalEvent(eventData);
                import('../utils/notifications.js').then(({ showSuccess }) => {
                    showSuccess('Event created successfully!');
                });
                console.log('Event created.');
            }
            await this.loadEvents();
            this.renderCalendar();
            this.closePanel('add-event-panel');
        } catch (error) {
            console.error(`Failed to ${eventId ? 'update' : 'create'} event:`, error);
            import('../utils/notifications.js').then(({ showError }) => {
                showError(`Failed to ${eventId ? 'update' : 'create'} event. Please try again.`);
            });
        }
    },

    handleEditEvent: function(event) {
        this.resetAddEventForm(event);
        this.openPanel('add-event-panel');
    },

    handleDeleteEvent: async function(eventId) {
        if (!eventId) return;
        if (confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
            try {
                await astralCalendarService.deletePersonalEvent(eventId);
                import('../utils/notifications.js').then(({ showSuccess }) => {
                    showSuccess('Event deleted successfully!');
                });
                console.log('Event deleted.');
                astralCalendar.events = astralCalendar.events.filter(ev => ev.id !== eventId); // Optimistic UI update
                this.renderCalendar(); // Re-render immediately
                this.closePanel('event-details-panel'); 
                // For safety, you might want to reload all events from server:
                // await this.loadEvents(); this.renderCalendar();
            } catch (error) {
                console.error('Failed to delete event:', error);
                import('../utils/notifications.js').then(({ showError }) => {
                    showError('Failed to delete event. Please try again.');
                });
            }
        }
    },

    getEventTypeClass: function(eventType) {
        if (!eventType) return 'event-default';
        return `event-${eventType.toLowerCase().replace(/_/g, '-')}`;
    },

    getEventIcon: function(eventType) {
        // Maps event types to Font Awesome icons
        switch (eventType) {
            case 'moon_phase': return 'fa-moon';
            case 'planetary_transit': return 'fa-satellite-dish'; // fa-globe-americas before
            case 'meteor_shower': return 'fa-meteor';
            case 'solar_eclipse': return 'fa-sun'; 
            case 'lunar_eclipse': return 'fa-moon'; 
            case 'retrograde': return 'fa-undo-alt'; // fa-undo before
            case 'birthday': return 'fa-birthday-cake';
            case 'anniversary': return 'fa-gifts'; // fa-gift before
            case 'personal_milestone': return 'fa-award';
            case 'reminder': return 'fa-bell';
            case 'personal_event': return 'fa-calendar-check';
            case 'other_personal': return 'fa-user-astronaut'; // Fun icon for other personal
            default: return 'fa-star'; // Generic cosmic or unknown
        }
    },

    formatEventType: function(eventType) {
        if (!eventType) return 'Event';
        return eventType.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
};

// Initialize when the DOM is ready
// document.addEventListener('DOMContentLoaded', () => {
//     const calendarContainer = document.getElementById('astral-calendar-container'); // Adjust ID if needed
//     if (calendarContainer) {
//         astralCalendarUI.initialize('astral-calendar-container');
//     } else {
//         console.warn('Astral Calendar container not found. Calendar will not initialize.');
//     }
// });