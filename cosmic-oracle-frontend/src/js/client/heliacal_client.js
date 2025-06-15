// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\heliacal_client.js
document.addEventListener('DOMContentLoaded', () => {
    const heliacalForm = document.getElementById('heliacalForm');
    const heliacalResultsDiv = document.getElementById('heliacalResults');
    
    if (heliacalForm) {
        const helDatetimeInput = document.getElementById('helDatetime'); // Renamed for uniqueness
        const helLatitudeInput = document.getElementById('helLatitude');
        const helLongitudeInput = document.getElementById('helLongitude');
        const bodyNameSelect = document.getElementById('heliacalBodyName');


        if(helDatetimeInput && document.getElementById('birthDatetime')) helDatetimeInput.value = document.getElementById('birthDatetime').value;
        if(helLatitudeInput && document.getElementById('latitude')) helLatitudeInput.value = document.getElementById('latitude').value;
        if(helLongitudeInput && document.getElementById('longitude')) helLongitudeInput.value = document.getElementById('longitude').value;


        heliacalForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            heliacalResultsDiv.innerHTML = '<p class="calculating">Calculating Heliacal Phenomena...</p>';

            const datetimeLocalStr = helDatetimeInput.value; // Using helDatetime
            const latitude = parseFloat(helLatitudeInput.value);
            const longitude = parseFloat(helLongitudeInput.value);
            const altitude_observer = parseFloat(document.getElementById('helAltitudeObserver').value || '0');
            const body_name = bodyNameSelect ? bodyNameSelect.value : 'Mercury';

            let datetimeUtcStr;
            if (!datetimeLocalStr) {
                 heliacalResultsDiv.innerHTML = '<p class="error">Date/Time is required.</p>';
                 return;
            }
            try {
                datetimeUtcStr = new Date(datetimeLocalStr).toISOString();
            } catch(e) {
                heliacalResultsDiv.innerHTML = '<p class="error">Invalid Date/Time format.</p>';
                return;
            }


            if (isNaN(latitude) || isNaN(longitude) || isNaN(altitude_observer)) {
                heliacalResultsDiv.innerHTML = '<p class="error">Invalid latitude, longitude, or observer altitude.</p>';
                return;
            }
            if (!body_name) {
                heliacalResultsDiv.innerHTML = '<p class="error">Please select a celestial body.</p>';
                return;
            }


            try {
                const response = await fetch('/api/v1/heliacal/phenomena', { // Matches route path
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        datetime_utc_str: datetimeUtcStr, // Sending UTC ISO string
                        latitude,
                        longitude,
                        altitude_observer,
                        body_name
                    }),
                });
                const responseData = await response.json();
                if (!response.ok || responseData.error) {
                    heliacalResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p><pre>${responseData.details ? JSON.stringify(responseData.details, null, 2) : ''}</pre>`;
                } else {
                    displayHeliacalPhenomena(responseData.data);
                }
            } catch (error) {
                console.error('Heliacal Phenomena Fetch Error:', error);
                heliacalResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayHeliacalPhenomena(data) {
        if (!data) {
            heliacalResultsDiv.innerHTML = `<p class="error">No heliacal phenomena data received.</p>`;
            return;
        }
        let html = `<h3>Heliacal Phenomena for ${data.body_name || 'Selected Body'}</h3>`;
        html += `<p>Date Assessed: ${new Date(data.datetime_utc).toLocaleString()}</p>`;
        html += `<p><strong>Status (Approximate):</strong> ${data.status_description_approx || 'N/A'}</p>`;
        if (data.is_potentially_visible_heliacally_approx !== undefined) {
             html += `<p>Potentially Visible (heliacally): ${data.is_potentially_visible_heliacally_approx ? 'Yes' : 'No'}</p>`;
        }
        html += `<p>Approx. Elongation from Sun: ${data.elongation_from_sun_deg_approx?.toFixed(2)}°</p>`;
        if(data.simplified_arcus_visionis_deg_approx) {
             html += `<p><small>Simplified Arcus Visionis Used (Approx): ${data.simplified_arcus_visionis_deg_approx?.toFixed(1)}°</small></p>`;
        }
        
        if(data.phenomena_details_sweph) {
            const sweph = data.phenomena_details_sweph;
            html += `<h4>Sweph Details:</h4><ul>`;
            if(sweph.elongation_from_sun_deg_swe !== undefined) html += `<li>Sweph Elongation: ${sweph.elongation_from_sun_deg_swe?.toFixed(2)}°</li>`;
            if(sweph.apparent_magnitude !== undefined) html += `<li>Apparent Magnitude: ${sweph.apparent_magnitude?.toFixed(2)}</li>`;
            if(sweph.illumination_percent !== undefined) html += `<li>Illumination: ${sweph.illumination_percent?.toFixed(1)}%</li>`;
            if(sweph.phase_angle_deg !== undefined) html += `<li>Phase Angle: ${sweph.phase_angle_deg?.toFixed(2)}°</li>`;
            html += `</ul>`;
        }

        html += `<p>Sunrise Today (Approx UTC): ${data.sun_rise_today_utc_approx || 'N/A'}</p>`;
        html += `<p>Sunset Today (Approx UTC): ${data.sun_set_today_utc_approx || 'N/A'}</p>`;
        
        if(data.next_heliacal_rising_utc) {
            html += `<p>Predicted Next Heliacal Rising: ${new Date(data.next_heliacal_rising_utc).toLocaleDateString()}</p>`;
        }
        if(data.next_heliacal_setting_utc) {
            html += `<p>Predicted Next Heliacal Setting: ${new Date(data.next_heliacal_setting_utc).toLocaleDateString()}</p>`;
        }

        heliacalResultsDiv.innerHTML = html;
    }
});