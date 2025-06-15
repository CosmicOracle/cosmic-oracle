// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\dignities_client.js
document.addEventListener('DOMContentLoaded', () => {
    const dignitiesForm = document.getElementById('dignitiesForm');
    const dignitiesResultsDiv = document.getElementById('dignitiesResults');

    if (dignitiesForm) {
        // Attempt to pre-fill from natal chart form for convenience
        const commonDatetime = document.getElementById('birthDatetime')?.value;
        const commonTimezone = document.getElementById('birthTimezone')?.value;
        const commonLat = document.getElementById('latitude')?.value;
        const commonLon = document.getElementById('longitude')?.value;

        if(commonDatetime) document.getElementById('dignityBirthDatetime').value = commonDatetime;
        if(commonTimezone) document.getElementById('dignityBirthTimezone').value = commonTimezone;
        if(commonLat) document.getElementById('dignityLatitude').value = commonLat;
        if(commonLon) document.getElementById('dignityLongitude').value = commonLon;


        dignitiesForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            dignitiesResultsDiv.innerHTML = '<p class="calculating">Calculating dignities...</p>';

            const birth_datetime_str = document.getElementById('dignityBirthDatetime').value;
            const birth_timezone_str = document.getElementById('dignityBirthTimezone').value;
            const latitude = parseFloat(document.getElementById('dignityLatitude').value);
            const longitude = parseFloat(document.getElementById('dignityLongitude').value);
            const house_system_name = document.getElementById('dignityHouseSystem').value;
            // Example: Allow selecting points, or backend defaults
            // const points_to_assess_nodes = document.querySelectorAll('#dignityPointsSelect input:checked');
            // const points_to_assess = Array.from(points_to_assess_nodes).map(el => el.value);

            if (isNaN(latitude) || isNaN(longitude)) {
                dignitiesResultsDiv.innerHTML = '<p class="error">Invalid latitude or longitude.</p>';
                return;
            }
             if (!birth_datetime_str || !birth_timezone_str) {
                dignitiesResultsDiv.innerHTML = '<p class="error">Birth date/time and timezone are required.</p>';
                return;
            }

            const payload = {
                birth_datetime_str: birth_datetime_str,
                birth_timezone_str,
                latitude,
                longitude,
                house_system_name,
                // points_to_assess: points_to_assess.length > 0 ? points_to_assess : null
            };

            try {
                const response = await fetch('/api/v1/dignities/chart-dignities', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                const responseData = await response.json();
                if (!response.ok || responseData.error) {
                     dignitiesResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p><pre>${responseData.details ? JSON.stringify(responseData.details, null, 2) : ''}</pre>`;
                } else {
                    displayDignities(responseData.data);
                }
            } catch (error) {
                console.error('Dignities Fetch Error:', error);
                dignitiesResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayDignities(data) {
        if (!data) {
            dignitiesResultsDiv.innerHTML = `<p class="error">No dignity data received.</p>`;
            return;
        }
        let html = `<h3>Planetary Dignities</h3>`;
        if (Object.keys(data).length === 0) {
            html += `<p>No dignities calculated or available for the selected points.</p>`;
        } else {
            html += `<ul>`;
            for (const pointName in data) {
                const dignityInfo = data[pointName];
                if (dignityInfo && dignityInfo.error) {
                    html += `<li><strong>${pointName}</strong>: Error - ${dignityInfo.error}</li>`;
                } else if (dignityInfo && dignityInfo.status) {
                     html += `<li><strong>${pointName}</strong>: ${dignityInfo.status}`;
                    if (dignityInfo.interpretation) {
                        html += ` - <em>${dignityInfo.interpretation}</em>`;
                    }
                    // Optionally display detailed flags like ruler:true, exaltation:true
                    let details = [];
                    if(dignityInfo.ruler) details.push("Ruler");
                    if(dignityInfo.exaltation) details.push("Exaltation");
                    if(dignityInfo.detriment) details.push("Detriment");
                    if(dignityInfo.fall) details.push("Fall");
                    // Add other dignities like triplicity, term, face if your backend provides them.
                    if (details.length > 0) {
                        html += ` (${details.join(', ')})`;
                    }
                    html += `</li>`;
                }
            }
            html += `</ul>`;
        }
        dignitiesResultsDiv.innerHTML = html;
    }
});