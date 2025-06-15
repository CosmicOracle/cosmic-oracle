// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\midpoints_client.js
document.addEventListener('DOMContentLoaded', () => {
    const midpointsForm = document.getElementById('midpointsForm');
    const midpointsResultsDiv = document.getElementById('midpointsResults');

    if (midpointsForm) {
        const mpBirthDatetimeInput = document.getElementById('mpBirthDatetime');
        const mpBirthTimezoneInput = document.getElementById('mpBirthTimezone');
        const mpLatitudeInput = document.getElementById('mpLatitude');
        const mpLongitudeInput = document.getElementById('mpLongitude');

        if(document.getElementById('birthDatetime')) mpBirthDatetimeInput.value = document.getElementById('birthDatetime').value;
        if(document.getElementById('birthTimezone')) mpBirthTimezoneInput.value = document.getElementById('birthTimezone').value;
        if(document.getElementById('latitude')) mpLatitudeInput.value = document.getElementById('latitude').value;
        if(document.getElementById('longitude')) mpLongitudeInput.value = document.getElementById('longitude').value;

        // Logic for selecting points for midpoints and aspects can be added here
        // e.g., dynamically populating multi-select boxes or using checkboxes

        midpointsForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            midpointsResultsDiv.innerHTML = '<p class="calculating">Calculating Midpoints...</p>';

            const birth_datetime_str = mpBirthDatetimeInput.value;
            const birth_timezone_str = mpBirthTimezoneInput.value;
            const latitude = parseFloat(mpLatitudeInput.value);
            const longitude = parseFloat(mpLongitudeInput.value);
            const house_system_name = document.getElementById('mpHouseSystem').value;
            const aspect_orb = parseFloat(document.getElementById('mpAspectOrb').value || '1.5');

            // Example: Get selected points if you have multi-selects
            // const pointsForMidpointsSelect = document.getElementById('mpPointsForMidpoints');
            // const points_for_midpoints = pointsForMidpointsSelect ? Array.from(pointsForMidpointsSelect.selectedOptions).map(opt => opt.value) : null;
            // const pointsForAspectsSelect = document.getElementById('mpPointsForAspects');
            // const points_for_aspects = pointsForAspectsSelect ? Array.from(pointsForAspectsSelect.selectedOptions).map(opt => opt.value) : null;


            if (isNaN(latitude) || isNaN(longitude) || isNaN(aspect_orb)) {
                midpointsResultsDiv.innerHTML = '<p class="error">Invalid latitude, longitude, or aspect orb.</p>';
                return;
            }
            if (!birth_datetime_str || !birth_timezone_str) {
                midpointsResultsDiv.innerHTML = '<p class="error">Birth date/time and timezone are required.</p>';
                return;
            }

            const payload = {
                birth_datetime_str: birth_datetime_str,
                birth_timezone_str,
                latitude,
                longitude,
                house_system_name,
                aspect_orb,
                // points_for_midpoints: points_for_midpoints && points_for_midpoints.length > 0 ? points_for_midpoints : null,
                // points_for_aspects: points_for_aspects && points_for_aspects.length > 0 ? points_for_aspects : null,
            };

            try {
                const response = await fetch('/api/v1/midpoints/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                const responseData = await response.json();
                if (!response.ok || responseData.error) {
                    midpointsResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p><pre>${responseData.details ? JSON.stringify(responseData.details, null, 2) : ''}</pre>`;
                } else {
                    displayMidpoints(responseData.data);
                }
            } catch (error) {
                console.error('Midpoints Fetch Error:', error);
                midpointsResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayMidpointLocation(mpLocData, type) {
        let locHtml = `<strong>${type}:</strong> ${mpLocData.longitude?.toFixed(2)}° (${mpLocData.display_dms || mpLocData.display_short || ''}) in ${mpLocData.sign_name || ''}`;
        if (mpLocData.house) {
            locHtml += ` (House ${mpLocData.house})`;
        }
        if (mpLocData.aspects_to_point && mpLocData.aspects_to_point.length > 0) {
            locHtml += `<br/>  <em>Aspects to this ${type.toLowerCase().split(' ')[0]} point:</em><ul>`;
            mpLocData.aspects_to_point.forEach(asp => {
                locHtml += `<li>${asp.planet_name} ${asp.aspect_symbol || asp.aspect_name} (Orb: ${asp.orb_degrees?.toFixed(2)}°)</li>`;
            });
            locHtml += `</ul>`;
        } else {
             locHtml += `<br/>  <em>No tight aspects to this ${type.toLowerCase().split(' ')[0]} point.</em>`;
        }
        return locHtml;
    }


    function displayMidpoints(midpointsData) {
        let html = `<h3>Midpoints</h3>`;
        if (!midpointsData) {
             html += `<p class="error">No midpoint data received.</p>`;
        } else if (!Array.isArray(midpointsData)) {
             html += `<p class="error">${midpointsData.error || 'Unexpected data format for midpoints.'}</p>`;
        } else if (midpointsData.length === 0) {
            html += `<p>No midpoints calculated or found for the selected criteria.</p>`;
        } else {
            html += `<ul>`;
            midpointsData.forEach(mp => {
                if (mp.error) {
                    html += `<li>Error calculating midpoint for ${mp.pair?.join('/') || 'unknown pair'}: ${mp.error}</li>`;
                    return;
                }
                html += `<li><h4>Midpoint of ${mp.pair.join(' / ')}</h4>`;
                html += `<ul>`;
                if (mp.direct_midpoint) {
                    html += `<li>${displayMidpointLocation(mp.direct_midpoint, 'Direct Midpoint')}</li>`;
                }
                if (mp.indirect_midpoint) {
                     html += `<li>${displayMidpointLocation(mp.indirect_midpoint, 'Indirect Midpoint')}</li>`;
                }
                html += `</ul></li>`;
            });
            html += `</ul>`;
        }
        midpointsResultsDiv.innerHTML = html;
    }
});