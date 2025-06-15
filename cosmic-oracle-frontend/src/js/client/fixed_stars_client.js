// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\fixed_stars_client.js
document.addEventListener('DOMContentLoaded', () => {
    const fixedStarsForm = document.getElementById('fixedStarsForm');
    const fixedStarsResultsDiv = document.getElementById('fixedStarsResults');

    if (fixedStarsForm) {
        const fsBirthDatetimeInput = document.getElementById('fsBirthDatetime');
        const fsBirthTimezoneInput = document.getElementById('fsBirthTimezone');
        const fsLatitudeInput = document.getElementById('fsLatitude');
        const fsLongitudeInput = document.getElementById('fsLongitude');

        if(document.getElementById('birthDatetime')) fsBirthDatetimeInput.value = document.getElementById('birthDatetime').value;
        if(document.getElementById('birthTimezone')) fsBirthTimezoneInput.value = document.getElementById('birthTimezone').value;
        if(document.getElementById('latitude')) fsLatitudeInput.value = document.getElementById('latitude').value;
        if(document.getElementById('longitude')) fsLongitudeInput.value = document.getElementById('longitude').value;


        fixedStarsForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            fixedStarsResultsDiv.innerHTML = '<p class="calculating">Calculating Fixed Star aspects...</p>';

            const birth_datetime_str = fsBirthDatetimeInput.value;
            const birth_timezone_str = fsBirthTimezoneInput.value;
            const latitude = parseFloat(fsLatitudeInput.value);
            const longitude = parseFloat(fsLongitudeInput.value);
            const orb_longitude = parseFloat(document.getElementById('fsOrbLongitude').value || '1.0');
            const orb_declination_parallel = parseFloat(document.getElementById('fsOrbDeclination').value || '0.5');


            if (isNaN(latitude) || isNaN(longitude) || isNaN(orb_longitude) || isNaN(orb_declination_parallel)) {
                fixedStarsResultsDiv.innerHTML = '<p class="error">Invalid latitude, longitude, or orb values.</p>';
                return;
            }
             if (!birth_datetime_str || !birth_timezone_str) {
                fixedStarsResultsDiv.innerHTML = '<p class="error">Birth date/time and timezone are required.</p>';
                return;
            }

            try {
                const response = await fetch('/api/v1/fixed-stars/aspects', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        birth_datetime_str: birth_datetime_str,
                        birth_timezone_str,
                        latitude,
                        longitude,
                        orb_longitude,
                        orb_declination_parallel
                    }),
                });
                const responseData = await response.json(); 
                if (!response.ok || responseData.error) {
                    fixedStarsResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p><pre>${responseData.details ? JSON.stringify(responseData.details, null, 2) : ''}</pre>`;
                } else {
                    displayFixedStarAspects(responseData.data); // Pass the 'data' array
                }
            } catch (error) {
                console.error('Fixed Stars Fetch Error:', error);
                fixedStarsResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayFixedStarAspects(aspects) {
        let html = `<h3>Fixed Star Aspects</h3>`;
        if (!aspects) { // Check if aspects itself is undefined or null
            html += `<p class="error">No fixed star aspect data received.</p>`;
        } else if (!Array.isArray(aspects)) {
             html += `<p class="error">${aspects.error || 'Unexpected data format for fixed star aspects.'}</p>`;
        } else if (aspects.length === 0) {
            html += `<p>No significant fixed star aspects found within the specified orbs.</p>`;
        } else {
            html += `<ul>`;
            aspects.forEach(asp => {
                if (asp.error) {
                    html += `<li>Error processing an aspect: ${asp.error}</li>`;
                    return;
                }
                html += `<li><strong>${asp.star_name}</strong> (Mag: ${asp.magnitude || 'N/A'}) ${asp.aspect_type} <strong>${asp.planet_name}</strong> (Orb: ${asp.orb_degrees?.toFixed(2)}°)`;
                if (asp.influence) {
                    html += `<br/><em>Influence: ${asp.influence}</em>`;
                }
                 if (asp.nature) {
                    html += `<br/><small>Nature: ${Array.isArray(asp.nature) ? asp.nature.join('/') : asp.nature}</small>`;
                }
                if (asp.aspect_type.includes("Longitude")) {
                    html += `<br/><small>Star Lon: ${asp.star_longitude?.toFixed(2)}°, Planet Lon: ${asp.planet_longitude?.toFixed(2)}°</small>`;
                } else if (asp.aspect_type.includes("Declination")) {
                     html += `<br/><small>Star Dec: ${asp.star_declination?.toFixed(2)}°, Planet Dec: ${asp.planet_declination?.toFixed(2)}°</small>`;
                }
                html += `</li>`;
            });
            html += `</ul>`;
        }
        fixedStarsResultsDiv.innerHTML = html;
    }
});