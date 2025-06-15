// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\antiscia_client.js
document.addEventListener('DOMContentLoaded', () => {
    const antisciaForm = document.getElementById('antisciaForm');
    const antisciaResultsDiv = document.getElementById('antisciaResults');

    if (antisciaForm) {
        const anBirthDatetimeInput = document.getElementById('anBirthDatetime');
        const anBirthTimezoneInput = document.getElementById('anBirthTimezone');
        const anLatitudeInput = document.getElementById('anLatitude');
        const anLongitudeInput = document.getElementById('anLongitude');

        if(document.getElementById('birthDatetime')) anBirthDatetimeInput.value = document.getElementById('birthDatetime').value;
        if(document.getElementById('birthTimezone')) anBirthTimezoneInput.value = document.getElementById('birthTimezone').value;
        if(document.getElementById('latitude')) anLatitudeInput.value = document.getElementById('latitude').value;
        if(document.getElementById('longitude')) anLongitudeInput.value = document.getElementById('longitude').value;

        antisciaForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            antisciaResultsDiv.innerHTML = '<p class="calculating">Calculating Antiscia/Contra-Antiscia...</p>';

            const birth_datetime_str = anBirthDatetimeInput.value;
            const birth_timezone_str = anBirthTimezoneInput.value;
            const latitude = parseFloat(anLatitudeInput.value);
            const longitude = parseFloat(anLongitudeInput.value);
            const house_system_name = document.getElementById('anHouseSystem').value;
            const include_contra_antiscia = document.getElementById('anIncludeContra').checked;

            if (isNaN(latitude) || isNaN(longitude)) {
                antisciaResultsDiv.innerHTML = '<p class="error">Invalid latitude or longitude.</p>';
                return;
            }
             if (!birth_datetime_str || !birth_timezone_str) {
                antisciaResultsDiv.innerHTML = '<p class="error">Birth date/time and timezone are required.</p>';
                return;
            }

            try {
                const response = await fetch('/api/v1/antiscia/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        birth_datetime_str: birth_datetime_str,
                        birth_timezone_str,
                        latitude,
                        longitude,
                        house_system_name,
                        include_contra_antiscia
                    }),
                });
                const responseData = await response.json();
                if (!response.ok || responseData.error) {
                     antisciaResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p><pre>${responseData.details ? JSON.stringify(responseData.details, null, 2) : ''}</pre>`;
                } else {
                    displayAntiscia(responseData); // Pass the whole response object
                }
            } catch (error) {
                console.error('Antiscia Fetch Error:', error);
                antisciaResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displaySingleAntisciaSet(pointData, type) {
        // pointData is expected to be like AntisciaPointDetail Pydantic model
        if (!pointData || !pointData.longitude) return 'N/A';
        return `${pointData.longitude?.toFixed(2)}° (${pointData.display_dms || pointData.display_short || ''}), Lat: ${pointData.ecliptic_latitude?.toFixed(2) ?? 'N/A'}`;
    }

    function displayAntiscia(responseData) {
        let html = ``;
        if (responseData.error) {
            html += `<p class="error">${responseData.error}</p>`;
            antisciaResultsDiv.innerHTML = html;
            return;
        }

        if (responseData.antiscia && responseData.antiscia.length > 0) {
            html += `<h3>Antiscia Points</h3><ul>`;
            responseData.antiscia.forEach(item => { // item is AntisciaData
                html += `<li><strong>${item.planet_name}:</strong> `;
                if (item.antiscia_details) {
                    html += `Antiscia at ${displaySingleAntisciaSet(item.antiscia_details, 'Antiscia')}`;
                } else {
                    html += `Antiscia: Error or N/A`;
                }
                html += ` (Original: ${item.original_longitude?.toFixed(2)}°, Lat: ${item.original_latitude?.toFixed(2)})</li>`;
            });
            html += `</ul>`;
        } else if (!responseData.error) { // Only show "no points" if there wasn't a top-level error
            html += `<p>No antiscia points calculated.</p>`;
        }

        if (responseData.contra_antiscia && responseData.contra_antiscia.length > 0) {
            html += `<h3>Contra-Antiscia Points</h3><ul>`;
            responseData.contra_antiscia.forEach(item => { // item is AntisciaData
                html += `<li><strong>${item.planet_name}:</strong> `;
                if (item.contra_antiscia_details) {
                     html += `Contra-Antiscia at ${displaySingleAntisciaSet(item.contra_antiscia_details, 'Contra-Antiscia')}`;
                } else {
                    html += `Contra-Antiscia: Error or N/A`;
                }
                html += ` (Original: ${item.original_longitude?.toFixed(2)}°, Lat: ${item.original_latitude?.toFixed(2)})</li>`;
            });
            html += `</ul>`;
        } else if (document.getElementById('anIncludeContra')?.checked && !responseData.error) {
            html += `<p>No contra-antiscia points calculated.</p>`;
        }
        antisciaResultsDiv.innerHTML = html;
    }
});