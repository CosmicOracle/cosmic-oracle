// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\planetary_hours_client.js
document.addEventListener('DOMContentLoaded', () => {
    const planetaryHoursForm = document.getElementById('planetaryHoursForm');
    const phResultsDiv = document.getElementById('planetaryHoursResults');
    const phAllHoursTableBody = document.querySelector('#allPlanetaryHoursTable tbody');

    if (planetaryHoursForm) {
        const phDatetimeInput = document.getElementById('phDatetime');
        if (phDatetimeInput) {
            const now = new Date();
            const localIsoDateTime = new Date(now.getTime() - (now.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
            phDatetimeInput.value = localIsoDateTime;
        }

        planetaryHoursForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            phResultsDiv.innerHTML = '<p class="calculating">Calculating planetary hours...</p>';
            if(phAllHoursTableBody) phAllHoursTableBody.innerHTML = '';


            const datetimeLocalStr = phDatetimeInput.value;
            const latitude = parseFloat(document.getElementById('phLatitude').value);
            const longitude = parseFloat(document.getElementById('phLongitude').value);

            if (isNaN(latitude) || isNaN(longitude)) {
                phResultsDiv.innerHTML = '<p class="error">Invalid latitude or longitude.</p>';
                return;
            }
            if (!datetimeLocalStr) {
                 phResultsDiv.innerHTML = '<p class="error">Date/Time is required.</p>';
                 return;
            }

            let datetimeUtcStr;
            try {
                datetimeUtcStr = new Date(datetimeLocalStr).toISOString();
            } catch (e) {
                 phResultsDiv.innerHTML = '<p class="error">Invalid date/time format.</p>';
                return;
            }

            try {
                const response = await fetch('/api/v1/planetary-hours/', { // Endpoint matches route
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        datetime_utc: datetimeUtcStr, // Backend expects UTC ISO string
                        latitude: latitude, 
                        longitude: longitude 
                    }),
                });

                const responseData = await response.json();

                if (!response.ok || responseData.error) {
                    phResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p><pre>${responseData.details ? JSON.stringify(responseData.details, null, 2) : ''}</pre>`;
                } else {
                    displayPlanetaryHours(responseData.data);
                }
            } catch (error) {
                console.error('Planetary Hours Fetch Error:', error);
                phResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayPlanetaryHours(data) {
        if (!data) {
            phResultsDiv.innerHTML = `<p class="error">No planetary hours data received.</p>`;
            return;
        }
        let html = `<h3>Planetary Hours for ${new Date(data.target_datetime_utc).toLocaleString()}</h3>`;
        html += `<p>Location: Lat ${data.latitude?.toFixed(4)}, Lon ${data.longitude?.toFixed(4)}</p>`;
        html += `<p>Sunrise (Day Cycle Start): ${new Date(data.sunrise_of_the_day_utc).toLocaleTimeString()}</p>`;
        html += `<p>Sunset (Night Cycle Start): ${new Date(data.sunset_of_the_day_utc).toLocaleTimeString()}</p>`;
        html += `<p>Ruler of the Day: <strong>${data.ruler_of_the_day}</strong></p>`;
        
        if (data.current_planetary_hour && data.current_planetary_hour.ruler) {
            const current = data.current_planetary_hour;
            html += `<h4>Current Hour</h4>`;
            html += `<p>Type: ${current.type} #${current.number}</p>`;
            html += `<p>Ruler: <strong>${current.ruler}</strong></p>`;
            html += `<p>Starts: ${new Date(current.start_time_utc).toLocaleTimeString()}</p>`;
            html += `<p>Ends: ${new Date(current.end_time_utc).toLocaleTimeString()}</p>`;
        } else {
            html += `<p>Could not determine current planetary hour for the exact time. This might occur if the time is precisely on a cusp or in polar regions with unusual day/night cycles.</p>`;
             if(data.current_planetary_hour && data.current_planetary_hour.error){
                html += `<p class="error">Details: ${data.current_planetary_hour.error}</p>`;
            }
        }
        phResultsDiv.innerHTML = html;

        if (phAllHoursTableBody && data.all_planetary_hours_for_cycle) {
            phAllHoursTableBody.innerHTML = ''; // Clear previous rows
            data.all_planetary_hours_for_cycle.forEach(hour => {
                const row = phAllHoursTableBody.insertRow();
                row.insertCell().textContent = hour.type;
                row.insertCell().textContent = hour.number;
                row.insertCell().textContent = hour.ruler;
                row.insertCell().textContent = new Date(hour.start_time_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
                row.insertCell().textContent = new Date(hour.end_time_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
            });
        }
    }
});