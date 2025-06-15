// D:\my_projects\cosmic-oracle\cosmic-oracle-backend\public\js\lunar_mansions_client.js
document.addEventListener('DOMContentLoaded', () => {
    const lunarMansionsForm = document.getElementById('lunarMansionsForm');
    const lunarMansionsResultsDiv = document.getElementById('lunarMansionsResults');

    if (lunarMansionsForm) {
        const lmBirthDatetimeInput = document.getElementById('lmBirthDatetime');
        const lmBirthTimezoneInput = document.getElementById('lmBirthTimezone');

        if(document.getElementById('birthDatetime')) lmBirthDatetimeInput.value = document.getElementById('birthDatetime').value;
        // Timezone for lunar mansion date is important
        if(lmBirthTimezoneInput && document.getElementById('birthTimezone')) {
            lmBirthTimezoneInput.value = document.getElementById('birthTimezone').value;
        } else if (lmBirthTimezoneInput) {
            try {
                lmBirthTimezoneInput.value = Intl.DateTimeFormat().resolvedOptions().timeZone;
            } catch(e) { console.warn("Could not auto-detect timezone for lunar mansions.");}
        }


        lunarMansionsForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            lunarMansionsResultsDiv.innerHTML = '<p class="calculating">Calculating Lunar Mansion...</p>';

            const birth_datetime_str = lmBirthDatetimeInput.value; // For mansion at a specific time
            const birth_timezone_str = lmBirthTimezoneInput.value;
            const system = document.getElementById('lmSystemSelect').value || 'tropical_28_mansions';
            const ayanamsa_name = document.getElementById('lmAyanamsaSelect') ? document.getElementById('lmAyanamsaSelect').value : 'lahiri';


            if (!birth_datetime_str || !birth_timezone_str) {
                lunarMansionsResultsDiv.innerHTML = '<p class="error">Date/time and timezone are required.</p>';
                return;
            }

            try {
                const response = await fetch('/api/v1/lunar-mansions/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        birth_datetime_str: birth_datetime_str,
                        birth_timezone_str,
                        system_type: system.startsWith('sidereal') ? 'sidereal' : 'tropical',
                        ayanamsa_name: system.startsWith('sidereal') ? ayanamsa_name : null
                    }),
                });
                const responseData = await response.json();
                if (!response.ok || responseData.error) {
                    lunarMansionsResultsDiv.innerHTML = `<p class="error">Error: ${responseData.error || response.statusText}</p><pre>${responseData.details ? JSON.stringify(responseData.details, null, 2) : ''}</pre>`;
                } else {
                    displayLunarMansion(responseData.data);
                }
            } catch (error) {
                console.error('Lunar Mansions Fetch Error:', error);
                lunarMansionsResultsDiv.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
            }
        });
    }

    function displayLunarMansion(data) {
        if (!data) {
            lunarMansionsResultsDiv.innerHTML = `<p class="error">No lunar mansion data received.</p>`;
            return;
        }
        let html = `<h3>Lunar Mansion</h3>`;
        html += `<p>For: ${new Date(data.datetime_utc).toLocaleString()}</p>`;
        html += `<p>System: ${data.system_used || 'N/A'}</p>`;
        html += `<p>Moon's Longitude: ${data.moon_longitude?.toFixed(2)}°</p>`;
        if(data.moon_zodiac_position) {
            html += `<p>Moon in Zodiac: ${data.moon_zodiac_position.display_dms || data.moon_zodiac_position.display_short}</p>`;
        }
        html += `<h4>Mansion #${data.mansion_number || 'N/A'}: ${data.name || 'Unknown Name'}</h4>`;
        if(data.arabic_name) html += `<p>Arabic Name: ${data.arabic_name}</p>`;
        if(data.sanskrit_name) html += `<p>Sanskrit Name: ${data.sanskrit_name}</p>`;
        if(data.ruler_traditional || data.ruler_vedic) html += `<p>Ruler: ${data.ruler_traditional || data.ruler_vedic}</p>`;
        if(data.deity) html += `<p>Deity: ${data.deity}</p>`;
        if(data.symbol) html += `<p>Symbol: ${data.symbol}</p>`;
        if(data.nature) html += `<p>Nature/Influence: ${data.nature}</p>`;
        if(data.keywords && Array.isArray(data.keywords)) html += `<p>Keywords: ${data.keywords.join(', ')}</p>`;
        if(data.start_deg !== undefined && data.end_deg !== undefined) {
            html += `<p><small>Boundaries: ${data.start_deg?.toFixed(2)}° - ${data.end_deg?.toFixed(2)}°</small></p>`;
        }
        if(data.interpretation) html += `<p>Interpretation: ${data.interpretation}</p>`;

        lunarMansionsResultsDiv.innerHTML = html;
    }
});