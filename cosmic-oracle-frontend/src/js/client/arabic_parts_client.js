// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\arabic_parts_client.js
document.addEventListener('DOMContentLoaded', () => {
    const arabicPartsForm = document.getElementById('arabicPartsForm');
    const arabicPartsResultsDiv = document.getElementById('arabicPartsResults');
    
    if (arabicPartsForm) {
        const apBirthDatetimeInput = document.getElementById('apBirthDatetime');
        const apBirthTimezoneInput = document.getElementById('apBirthTimezone');
        const apLatitudeInput = document.getElementById('apLatitude');
        const apLongitudeInput = document.getElementById('apLongitude');
        const partNameSelect = document.getElementById('arabicPartName'); // Make sure this select exists in HTML

        // Pre-fill from natal chart form
        if(document.getElementById('birthDatetime')) apBirthDatetimeInput.value = document.getElementById('birthDatetime').value;
        if(document.getElementById('birthTimezone')) apBirthTimezoneInput.value = document.getElementById('birthTimezone').value;
        if(document.getElementById('latitude')) apLatitudeInput.value = document.getElementById('latitude').value;
        if(document.getElementById('longitude')) apLongitudeInput.value = document.getElementById('longitude').value;


        arabicPartsForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            arabicPartsResultsDiv.innerHTML = '<p class="calculating">Calculating Arabic Part...</p>';

            const birth_datetime_str = apBirthDatetimeInput.value;
            const birth_timezone_str = apBirthTimezoneInput.value;
            const latitude = parseFloat(apLatitudeInput.value);
            const longitude = parseFloat(apLongitudeInput.value);
            const part_name = partNameSelect ? partNameSelect.value : 'Part of Fortune';
            const house_system_name = document.getElementById('apHouseSystem').value;


            if (isNaN(latitude) || isNaN(longitude)) {
                arabicPartsResultsDiv.innerHTML = '<p class="error">Invalid latitude or longitude.</p>';
                return;
            }
            if (!birth_datetime_str || !birth_timezone_str) {
                arabicPartsResultsDiv.innerHTML = '<p class="error">Birth date/time and timezone are required.</p>';
                return;
            }
            if (!part_name) {
                 arabicPartsResultsDiv.innerHTML = '<p class="error">Please select an Arabic Part.</p>';
                 return;
            }

            try {
                const response = await fetch('/api/v1/arabic-parts/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        birth_datetime_str: birth_datetime_str,
                        birth_timezone_str,
                        latitude,
                        longitude,
                        part_name,
                        house_system_name
                    }),
                });
                const responseData = await response.json();
                if (!response.ok || responseData.error) {
                    arabicPartsResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p><pre>${responseData.details ? JSON.stringify(responseData.details, null, 2) : ''}</pre>`;
                } else {
                    displayArabicPart(responseData.data); // Pass the 'data' object from response
                }
            } catch (error) {
                console.error('Arabic Parts Fetch Error:', error);
                arabicPartsResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayArabicPart(data) {
        if (!data) {
            arabicPartsResultsDiv.innerHTML = `<p class="error">No Arabic Part data received.</p>`;
            return;
        }
        let html = `<h3>${data.name || 'Arabic Part'} Calculation</h3>`;
        html += `<p><strong>Position ${data.symbol || ''}:</strong> ${data.longitude?.toFixed(2)}° (${data.display_dms || data.display_short || ''})</p>`;
        html += `<p><strong>Sign:</strong> ${data.sign_name || 'N/A'} ${data.sign_symbol || ''}</p>`;
        html += `<p><strong>House:</strong> ${data.house ?? 'N/A'}</p>`;
        if (data.sign_interpretation) {
            html += `<p><strong>Sign Interpretation:</strong> ${data.sign_interpretation}</p>`;
        }
        if (data.house_interpretation) {
            html += `<p><strong>House Interpretation:</strong> ${data.house_interpretation}</p>`;
        }
        if (data.calculated_as_day_chart !== undefined) {
            html += `<p><small>Calculated as ${data.calculated_as_day_chart ? 'Day' : 'Night'} chart.</small></p>`;
        }
        if(data.formula_used) {
            html += `<p><small>Formula: ${data.formula_used}</small></p>`;
        }
        arabicPartsResultsDiv.innerHTML = html;
    }
});