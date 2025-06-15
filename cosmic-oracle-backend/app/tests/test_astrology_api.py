# app/tests/test_astrology_api.py
import json
from datetime import datetime, timezone, timedelta

def test_natal_chart_creation(client):
    """Test creating a natal chart with valid data"""
    test_data = {
        "profile_name": "Test User",
        "birth_datetime_str": "1990-01-15T16:45:00",
        "birth_timezone_offset_hours": -8.0,
        "latitude": 34.0522,
        "longitude": -118.2437,
        "house_system_name": "Placidus"
    }
    response = client.post('/api/v1/astrology/natal-chart', json=test_data)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert data["status"] == "success"
    assert "chart_data" in data
    assert "profile_id" in data

def test_get_geocentric_positions(client):
    """Test getting geocentric planetary positions"""
    response = client.get('/api/v1/skyfield/positions/geocentric')
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert "positions" in data
    assert "Sun" in data["positions"]
    assert "Moon" in data["positions"]
    assert "datetime_utc" in data

def test_get_topocentric_positions(client):
    """Test getting topocentric planetary positions"""
    test_data = {
        "latitude": 34.0522,
        "longitude": -118.2437,
        "elevation_m": 86.0
    }
    response = client.post('/api/v1/skyfield/positions/topocentric', json=test_data)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert "positions" in data
    assert "Sun" in data["positions"]
    assert "observer_location" in data

def test_invalid_input_validation(client):
    """Test input validation with invalid data"""
    test_data = {
        "birth_datetime_str": "not-a-datetime",
        "latitude": "not-a-float",
        "longitude": -118.2437
    }
    response = client.post('/api/v1/astrology/natal-chart', json=test_data)
    assert response.status_code == 422, "Expected 422 for invalid input"
    data = response.json()
    assert "detail" in data

def test_satellite_passes(client):
    """Test getting satellite pass predictions"""
    test_data = {
        "tle_line1": "1 25544U 98067A   23300.06319827  .00012211  00000+0  22557-3 0  9993",
        "tle_line2": "2 25544  51.6422 264.4759 0007818  63.3854  73.9789 15.49386769419958",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "elevation_m": 86.0,
        "duration_hours": 24
    }
    response = client.post('/api/v1/skyfield/satellite/passes', json=test_data)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert isinstance(data, list), "Expected a list of satellite passes"