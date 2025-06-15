// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\declination_client.js
document.addEventListener('DOMContentLoaded', () => {
    const declinationForm = document.getElementById('declinationForm');
    const declinationResultsDiv = document.getElementById('declinationResults');

    if (declinationForm) {
        const decBirthDatetimeInput = document.getElementById('decBirthDatetime');
        const decBirthTimezoneInput = document.getElementById('decBirthTimezone');
        // Latitude/Longitude for declination service are observer's location if topocentric matters,
        // but declination itself is geocentric unless topocentric transformation is explicitly done.
        // For chart-based declination aspects, usually geocentric is fine.
        const decLatitudeInput = document.getElementById('decLatitude');
        const decLongitudeInput = document.getElementById('decLongitude');


        if(document.getElementById('birthDatetime')) decBirthDatetimeInput.value = document.getElementById('birthDatetime').value;
        if(document.getElementById('birthTimezone')) decBirthTimezoneInput.value = document.getElementById('birthTimezone').value;
        if(document.getElementById('latitude')) decLatitudeInput.value = document.getElementById('latitude').value;
        if(document.getElementById('longitude')) decLongitudeInput.value = document.getElementById('longitude').value;

        declinationForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            declinationResultsDiv.innerHTML = '<p class="calculating">Calculating Declination Aspects...</p>';

            const birth_datetime_str = decBirthDatetimeInput.value;
            const birth_timezone_str = decBirthTimezoneInput.value;
            // Pass lat/lon as they are in the Pydantic model, service can decide if/how to use them.
            const latitude = parseFloat(decLatitudeInput.value);
            const longitude = parseFloat(decLongitudeInput.value);
            const orb = parseFloat(document.getElementById('decOrb').value || '1.0');

            if (isNaN(latitude) || isNaN(longitude) || isNaN(orb)) {
                declinationResultsDiv.innerHTML = '<p class="error">Invalid latitude, longitude, or orb.</p>';
                return;
            }
            if (!birth_datetime_str || !birth_timezone_str) {
                declinationResultsDiv.innerHTML = '<p class="error">Birth date/time and timezone are required.</p>';
                return;
            }

            try {
                const response = await fetch('/api/v1/declination/aspects', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        birth_datetime_str: birth_datetime_str,
                        birth_timezone_str,
                        latitude, // Service might use these for topocentric adjustments if designed for it
                        longitude,
                        orb
                    }),
                });
                const responseData = await response.json();
                if (!response.ok || responseData.error) {
                    declinationResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p><pre>${responseData.details ? JSON.stringify(responseData.details, null, 2) : ''}</pre>`;
                } else {
                    displayDeclinationAspects(responseData.data);
                }
            } catch (error) {
                console.error('Declination Aspects Fetch Error:', error);
                declinationResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayDeclinationAspects(aspects) {
        let html = `<h3>Declination Aspects (Parallel/Contra-Parallel)</h3>`;
        if (!aspects) {
            html += `<p class="error">No declination aspect data received.</p>`;
        } else if (!Array.isArray(aspects)) {
             html += `<p class="error">${aspects.error || 'Unexpected data format for declination aspects.'}</p>`;
        } else if (aspects.length === 0) {
            html += `<p>No declination aspects found within the specified orb.</p>`;
        } else {
            html += `<ul>`;
            aspects.forEach(asp => {
                if (asp.error) {
                    html += `<li>Error processing aspect: ${asp.error}</li>`;
                    return;
                }
                html += `<li><strong>${asp.planet1_name}</strong> (Dec: ${asp.declination1?.toFixed(2)}°) ${asp.aspect_type} <strong>${asp.planet2_name}</strong> (Dec: ${asp.declination2?.toFixed(2)}°) (Orb: ${asp.orb_degrees?.toFixed(2)}°)</li>`;
            });
            html += `</ul>`;
        }
        declinationResultsDiv.innerHTML = html;
    }
});