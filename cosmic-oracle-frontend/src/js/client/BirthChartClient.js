// cosmic-oracle-frontend/public/js/birthchart.js

/**
 * Handles birth chart functionality including form submission and chart display.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check if the birth chart form exists on the page
    const birthChartForm = document.getElementById('birth-chart-form');
    if (birthChartForm) {
        birthChartForm.addEventListener('submit', function(event) {
            event.preventDefault();
            submitBirthChartForm();
        });
    }

    // Check if the user already has a birth chart (fetch on page load if applicable)
    fetchBirthChart();
});

function submitBirthChartForm() {
    const form = document.getElementById('birth-chart-form');
    const formData = new FormData(form);
    const birthData = {
        birth_date: formData.get('birth_date'),
        birth_location: formData.get('birth_location'),
        latitude: parseFloat(formData.get('latitude')),
        longitude: parseFloat(formData.get('longitude'))
    };

    // Validate input
    if (!birthData.birth_date || !birthData.birth_location || isNaN(birthData.latitude) || isNaN(birthData.longitude)) {
        displayErrorMessage('Please fill in all fields correctly.');
        return;
    }

    // Get the JWT token from local storage or wherever it's stored
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        displayErrorMessage('You must be logged in to generate a birth chart.');
        window.location.href = '/login.html';
        return;
    }

    fetch('/api/v1/birth-chart/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(birthData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to generate birth chart');
        }
        return response.json();
    })
    .then(data => {
        displayBirthChart(data);
        // Hide the form after successful submission
        form.style.display = 'none';
    })
    .catch(error => {
        console.error('Error generating birth chart:', error);
        displayErrorMessage('Failed to generate birth chart. Please try again.');
    });
}

function fetchBirthChart() {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        return; // Don't attempt to fetch if not logged in
    }

    fetch('/api/v1/birth-chart/my-chart', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 404) {
                // Birth chart not found, show the form to create one
                const form = document.getElementById('birth-chart-form');
                if (form) {
                    form.style.display = 'block';
                }
                return null;
            }
            throw new Error('Failed to fetch birth chart');
        }
        return response.json();
    })
    .then(data => {
        if (data) {
            displayBirthChart(data);
            // Hide the form if chart exists
            const form = document.getElementById('birth-chart-form');
            if (form) {
                form.style.display = 'none';
            }
        }
    })
    .catch(error => {
        console.error('Error fetching birth chart:', error);
        displayErrorMessage('Failed to load your birth chart. Please refresh the page.');
    });
}

function displayBirthChart(chartData) {
    const chartContainer = document.getElementById('birth-chart-container');
    if (!chartContainer) {
        console.error('Birth chart container not found on the page.');
        return;
    }

    // Clear any existing content
    chartContainer.innerHTML = '';

    // Create a title
    const title = document.createElement('h2');
    title.textContent = 'Your Birth Chart';
    chartContainer.appendChild(title);

    // Display birth details
    const details = document.createElement('p');
    details.innerHTML = `<strong>Birth Date:</strong> ${chartData.birth_date} <br> <strong>Location:</strong> ${chartData.birth_location}`;
    chartContainer.appendChild(details);

    // Display planetary positions
    const planetsTitle = document.createElement('h3');
    planetsTitle.textContent = 'Planetary Positions';
    chartContainer.appendChild(planetsTitle);

    const planetsTable = document.createElement('table');
    planetsTable.className = 'birth-chart-table';
    planetsTable.innerHTML = '<tr><th>Planet</th><th>Position</th><th>Zodiac Sign</th></tr>';
    
    for (const [planet, position] of Object.entries(chartData.planet_positions)) {
        const row = document.createElement('tr');
        let positionText = 'Unknown';
        if (typeof position === 'object' && position !== null && 'ecliptic_longitude' in position) {
            positionText = position.ecliptic_longitude.toFixed(2) + '°';
        }
        const sign = chartData.zodiac_signs[planet] || 'Unknown';
        row.innerHTML = `<td>${planet.charAt(0).toUpperCase() + planet.slice(1)}</td><td>${positionText}</td><td>${sign}</td>`;
        planetsTable.appendChild(row);
    }
    chartContainer.appendChild(planetsTable);

    // Display major aspects
    const aspectsTitle = document.createElement('h3');
    aspectsTitle.textContent = 'Major Aspects';
    chartContainer.appendChild(aspectsTitle);

    const aspectsTable = document.createElement('table');
    aspectsTable.className = 'birth-chart-table';
    aspectsTable.innerHTML = '<tr><th>Planets</th><th>Aspect</th><th>Angle</th><th>Orb</th></tr>';
    
    for (const [pair, aspect] of Object.entries(chartData.aspects)) {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${pair.replace('-', ' - ')}</td><td>${aspect.aspect.charAt(0).toUpperCase() + aspect.aspect.slice(1)}</td><td>${aspect.angle.toFixed(2)}°</td><td>${aspect.orb.toFixed(2)}°</td>`;
        aspectsTable.appendChild(row);
    }
    if (Object.keys(chartData.aspects).length === 0) {
        const noAspectsMsg = document.createElement('p');
        noAspectsMsg.textContent = 'No major aspects calculated.';
        chartContainer.appendChild(noAspectsMsg);
    } else {
        chartContainer.appendChild(aspectsTable);
    }

    // Add a button to edit/update birth chart
    const editButton = document.createElement('button');
    editButton.textContent = 'Update Birth Data';
    editButton.onclick = function() {
        const form = document.getElementById('birth-chart-form');
        if (form) {
            // Pre-fill form with existing data
            form.elements['birth_date'].value = chartData.birth_date.split('.')[0]; // Remove milliseconds if any
            form.elements['birth_location'].value = chartData.birth_location;
            form.elements['latitude'].value = chartData.latitude;
            form.elements['longitude'].value = chartData.longitude;
            form.style.display = 'block';
        }
        // Hide the chart display
        chartContainer.style.display = 'none';
    };
    chartContainer.appendChild(editButton);

    // Make container visible
    chartContainer.style.display = 'block';
}

function displayErrorMessage(message) {
    const errorContainer = document.getElementById('birth-chart-error');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    } else {
        alert(message);
    }
}
