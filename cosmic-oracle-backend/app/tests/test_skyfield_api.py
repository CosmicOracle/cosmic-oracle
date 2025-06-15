# app/tests/test_skyfield_api.py
"""
Integration tests for the Skyfield API endpoints.

These tests use a test client to make real HTTP requests to the Skyfield
endpoints, verifying that the routes are correctly configured and that they
interact with the Skyfield service as expected.
"""

import json
import pytest
import os
from datetime import datetime

# The `client` fixture is automatically provided by conftest.py

# Skip these tests if the Skyfield ephemeris file is missing.
from app.core.config import settings
EPHEMERIS_FULL_PATH = os.path.join(settings.skyfield_data_path, settings.skyfield_ephemeris)

skip_if_no_skyfield_ephem = pytest.mark.skipif(
    not os.path.exists(EPHEMERIS_FULL_PATH),
    reason=f"Skyfield ephemeris file not found at {EPHEMERIS_FULL_PATH}, skipping Skyfield API tests."
)


@skip_if_no_skyfield_ephem
def test_when_getting_position_of_valid_body_then_returns_200_and_data(client):
    """
    GIVEN a running FastAPI application with Skyfield service initialized.
    WHEN a GET request is made to the /position/{body_name} endpoint with a valid body.
    THEN the server should respond with a 200 OK status and correct position data.
    """
    body_name = "mars"
    # This URL must exactly match the one defined in the controller.
    response = client.get(f'/astrology/skyfield/position/{body_name}')
    
    # 1. Assert the HTTP status code is correct.
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Response: {response.text}"
    
    # 2. Assert the response is valid JSON and has the expected structure.
    data = response.json()
    assert data["status"] == "success"
    assert "body" in data
    assert data["body"].lower() == body_name
    assert "position" in data
    position = data["position"]
    assert "altitude_deg" in position
    assert "azimuth_deg" in position
    assert "distance_au" in position
    assert "right_ascension_hours" in position
    assert "declination_deg" in position
    assert isinstance(position["altitude_deg"], float)
    assert isinstance(position["azimuth_deg"], float)
    assert isinstance(position["distance_au"], float)

@skip_if_no_skyfield_ephem
def test_when_getting_position_of_invalid_body_then_returns_400(client):
    """
    GIVEN a running FastAPI application.
    WHEN a GET request is made to the /position/{body_name} endpoint with an invalid body name.
    THEN the server should respond with a 400 Bad Request status and a clear error message.
    """
    invalid_body_name = "invalidplanet"
    response = client.get(f'/astrology/skyfield/position/{invalid_body_name}')
    
    # Assert the status code indicates a client error.
    assert response.status_code == 400
    
    data = response.json()
    assert "detail" in data
    assert "Unknown celestial body" in data["detail"]

@skip_if_no_skyfield_ephem
def test_skyfield_endpoint_returns_different_positions_over_time(client):
    """
    GIVEN a running FastAPI application.
    WHEN two requests are made to the same endpoint a short time apart.
    THEN the positional data should be different, proving it's a real-time calculation.
    """
    import time

    # First request
    response1 = client.get('/astrology/skyfield/position/moon')
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Wait for a moment to ensure the time has changed
    time.sleep(1.1)
    
    # Second request
    response2 = client.get('/astrology/skyfield/position/moon')
    assert response2.status_code == 200
    data2 = response2.json()
    
    # The Moon moves quickly, its altitude and azimuth should have changed.
    position1 = data1["position"]
    position2 = data2["position"]
    assert position1["altitude_deg"] != position2["altitude_deg"]
    assert position1["azimuth_deg"] != position2["azimuth_deg"]