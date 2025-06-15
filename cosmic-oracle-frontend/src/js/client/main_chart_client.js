// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\main_chart_client.js
document.addEventListener('DOMContentLoaded', () => {
    // --- Natal Chart ---
    const natalChartForm = document.getElementById('natalChartForm');
    const natalChartResultsDiv = document.getElementById('natalChartResults');

    if (natalChartForm) {
        const birthDatetimeInput = document.getElementById('birthDatetime');
        const birthTimezoneInput = document.getElementById('birthTimezone');

        if (birthDatetimeInput) {
            const now = new Date();
            const localIsoDateTime = new Date(now.getTime() - (now.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
            birthDatetimeInput.value = localIsoDateTime;
        }
        if (birthTimezoneInput) {
            try {
                birthTimezoneInput.value = Intl.DateTimeFormat().resolvedOptions().timeZone;
            } catch(e) { console.warn("Could not auto-detect timezone."); }
        }

        natalChartForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            natalChartResultsDiv.innerHTML = '<p class="calculating">Calculating natal chart...</p>';

            const birth_datetime_str = birthDatetimeInput.value;
            const birth_timezone_str = birthTimezoneInput.value;
            const latitude = parseFloat(document.getElementById('latitude').value);
            const longitude = parseFloat(document.getElementById('longitude').value);
            const altitude = parseFloat(document.getElementById('altitude').value || '0');
            const house_system_name = document.getElementById('houseSystem').value;

            if (isNaN(latitude) || isNaN(longitude) || isNaN(altitude)) {
                natalChartResultsDiv.innerHTML = '<p class="error">Invalid latitude, longitude, or altitude.</p>';
                return;
            }
            if (!birth_datetime_str || !birth_timezone_str) {
                natalChartResultsDiv.innerHTML = '<p class="error">Birth date/time and timezone are required.</p>';
                return;
            }

            try {
                // CORRECTED API ENDPOINT: from /chart/natal-chart to /astrology/natal-chart
                const response = await fetch('/api/v1/astrology/natal-chart', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        birth_datetime_str: birth_datetime_str, // Backend expects string
                        birth_timezone_str,
                        latitude,
                        longitude,
                        altitude,
                        house_system_name
                    }),
                });
                const responseData = await response.json();
                if (!response.ok || responseData.error) {
                    natalChartResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p><pre>${responseData.details ? JSON.stringify(responseData.details, null, 2) : ''}</pre>`;
                } else {
                    displayNatalChart(responseData.data, responseData.birth_data_input); // Pass data and input context
                }
            } catch (error) {
                console.error('Natal Chart Fetch Error:', error);
                natalChartResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayNatalChart(chartData, birthInput) {
        if (!chartData) {
            natalChartResultsDiv.innerHTML = `<p class="error">No chart data received.</p>`;
            return;
        }
        let html = `<h3>Natal Chart Results</h3>`;
        if (birthInput) {
            html += `<p><small>Input: ${birthInput.datetime_local_str} (${birthInput.timezone_str})</small></p>`;
        }
        html += `<p>Calculated for: ${new Date(chartData.datetime_utc).toLocaleString()} (UTC)</p>`;
        html += `<p>Location: Lat ${chartData.latitude}, Lon ${chartData.longitude}, House System: ${chartData.house_system}</p>`;

        html += `<h4>Planets:</h4><ul>`;
        for (const name in chartData.planets) {
            const p = chartData.planets[name];
            if (p.error) {
                html += `<li><strong>${p.name} ${p.symbol || ''}:</strong> Error - ${p.error}</li>`;
            } else {
                html += `<li><strong>${p.name} ${p.symbol || ''}:</strong> ${p.longitude?.toFixed(2)}° (${p.display_dms || p.display_short}) in House ${p.house ?? 'N/A'} ${p.is_retrograde ? '(R)' : ''}</li>`;
                if (p.dignities && p.dignities.status !== 'N/A') {
                    html += `<ul><li>Dignity: ${p.dignities.status} - ${p.dignities.interpretation || ''}</li></ul>`;
                }
            }
        }
        html += `</ul>`;

        html += `<h4>Angles:</h4><ul>`;
        for (const name in chartData.angles) {
            const angle = chartData.angles[name];
            if (angle.error) {
                html += `<li><strong>${angle.name} ${angle.symbol || ''}:</strong> Error - ${angle.error}</li>`;
            } else {
                html += `<li><strong>${angle.name} ${angle.symbol || ''}:</strong> ${angle.longitude?.toFixed(2)}° (${angle.display_dms || angle.display_short}) - House: ${angle.house ?? 'N/A'}</li>`;
            }
        }
        html += `</ul>`;

        html += `<h4>House Cusps:</h4><ol>`;
        for (let i = 1; i <= 12; i++) {
            const cusp = chartData.houses[i.toString()]; // Ensure key is string if data is keyed by string "1"
            if (cusp && !cusp.error) {
                html += `<li>House ${i}: ${cusp.longitude?.toFixed(2)}° (${cusp.display_dms || cusp.display_short})</li>`;
            } else {
                html += `<li>House ${i}: Error or N/A</li>`;
            }
        }
        html += `</ol>`;
        
        if (chartData.part_of_fortune && !chartData.part_of_fortune.error) {
            const pof = chartData.part_of_fortune;
            html += `<h4>Part of Fortune ${pof.symbol || ''}:</h4>`;
            html += `<p>${pof.longitude?.toFixed(2)}° (${pof.display_dms || pof.display_short}) in House ${pof.house ?? 'N/A'}</p>`;
            if (pof.sign_interpretation) html += `<p>Sign: ${pof.sign_interpretation}</p>`;
            if (pof.house_interpretation) html += `<p>House: ${pof.house_interpretation}</p>`;
        }

        if (chartData.aspects && chartData.aspects.length > 0) {
            html += `<h4>Aspects:</h4><ul>`;
            chartData.aspects.forEach(asp => {
                html += `<li>${asp.point1_name} ${asp.aspect_symbol} ${asp.point2_name} (Orb: ${asp.orb_degrees}° - ${asp.aspect_type_category}) ${asp.applying === true ? 'Applying' : asp.applying === false ? 'Separating' : ''}</li>`;
            });
            html += `</ul>`;
        } else {
            html += `<h4>Aspects:</h4><p>No aspects calculated or found.</p>`;
        }
        natalChartResultsDiv.innerHTML = html;
    }

    // --- Daily Horoscope ---
    const horoscopeForm = document.getElementById('horoscopeForm');
    const horoscopeResultsDiv = document.getElementById('horoscopeResults');

    if (horoscopeForm) {
        horoscopeForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            horoscopeResultsDiv.innerHTML = '<p class="calculating">Fetching horoscope...</p>';
            const zodiacSign = horoscopeForm.querySelector('#zodiacSignSelect').value;
            const horoscopeDate = horoscopeForm.querySelector('#horoscopeDate').value; // Optional

            let url = `/api/v1/astrology/daily-horoscope?sign_key=${encodeURIComponent(zodiacSign)}`; // CORRECTED URL
            if (horoscopeDate) {
                url += `&target_date=${encodeURIComponent(horoscopeDate)}`;
            }

            try {
                const response = await fetch(url);
                const responseData = await response.json();
                if (!response.ok || responseData.error) {
                    horoscopeResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p>`;
                } else {
                    displayHoroscope(responseData.data);
                }
            } catch (error) {
                console.error('Horoscope Fetch Error:', error);
                horoscopeResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayHoroscope(data) {
        if (!data) {
            horoscopeResultsDiv.innerHTML = `<p class="error">No horoscope data received.</p>`;
            return;
        }
        let html = `<h3>${data.title}</h3>`;
        html += `<p>Date: ${data.date}</p>`;
        html += `<p><strong>Overview:</strong> ${data.overview}</p>`;
        if (data.moon_phase) html += `<p>Moon Phase: ${data.moon_phase}</p>`;

        data.sections.forEach(section => {
            html += `<h4>${section.title}</h4><p>${section.content}</p>`;
        });
        html += `<p><strong>Affirmation:</strong> ${data.affirmation}</p>`;
        if(data.lucky_number) html += `<p>Lucky Number: ${data.lucky_number}, Lucky Color: ${data.lucky_color || 'N/A'}</p>`;
        horoscopeResultsDiv.innerHTML = html;
    }

    // --- Moon Phase ---
    const moonPhaseForm = document.getElementById('moonPhaseForm');
    const moonPhaseResultsDiv = document.getElementById('moonPhaseResults');

    if (moonPhaseForm) {
        const moonPhaseDatetimeInput = document.getElementById('moonPhaseDatetime');
        if (moonPhaseDatetimeInput) {
            const now = new Date();
            const localIsoDateTime = new Date(now.getTime() - (now.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
            moonPhaseDatetimeInput.value = localIsoDateTime; // Default to current local time
        }


        moonPhaseForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            moonPhaseResultsDiv.innerHTML = '<p class="calculating">Fetching moon phase...</p>';
            const datetimeLocalStr = moonPhaseDatetimeInput.value;
            let datetimeUtcStr = '';
            if (datetimeLocalStr) { // If user provided a date/time
                try {
                    datetimeUtcStr = new Date(datetimeLocalStr).toISOString();
                } catch (e) {
                    moonPhaseResultsDiv.innerHTML = '<p class="error">Invalid date/time format for Moon Phase.</p>';
                    return;
                }
            } // If blank, backend will use current UTC time

            // CORRECTED API ENDPOINT: from /chart/moon-phase to /astrology/moon-phase
            let url = `/api/v1/astrology/moon-phase`; 
            if (datetimeUtcStr) {
                url += `?datetime_utc=${encodeURIComponent(datetimeUtcStr)}`;
            }

            try {
                const response = await fetch(url);
                const responseData = await response.json();
                if (!response.ok || responseData.error) {
                    moonPhaseResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p>`;
                } else {
                    displayMoonPhase(responseData.data);
                }
            } catch (error) {
                console.error('Moon Phase Fetch Error:', error);
                moonPhaseResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayMoonPhase(data) {
        if (!data) {
            moonPhaseResultsDiv.innerHTML = `<p class="error">No moon phase data received.</p>`;
            return;
        }
        let html = `<h3>Moon Phase Details</h3>`;
        html += `<p>For: ${new Date(data.datetime_utc).toLocaleString()}</p>`;
        html += `<p>Phase: <strong>${data.phase_name}</strong></p>`;
        html += `<p>Illumination: ${data.illumination_percent?.toFixed(1)}%</p>`;
        html += `<p>Elongation: ${data.elongation_degrees?.toFixed(2)}°</p>`;
        html += `<p>Sun Longitude: ${data.sun_longitude?.toFixed(2)}°, Moon Longitude: ${data.moon_longitude?.toFixed(2)}°</p>`;
        html += `<p>${data.is_waxing ? 'Waxing' : data.is_waning ? 'Waning' : 'Exact Phase (New/Full)'}</p>`;
        moonPhaseResultsDiv.innerHTML = html;
    }
});