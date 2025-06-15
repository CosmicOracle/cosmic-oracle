# app/tests/test_01_natal_chart.py
import pytest
import allure
import json
# Import common typing hints for consistency in test files
from typing import Optional, Dict, Any, List, Tuple

# Assuming your Flask app is here; often it's `from app import create_app`
# For a test setup, you usually create the app within a fixture.
# If app.main is truly your main app instance, this should work.
from app.main import app # Assuming app.main is the entry point/instance

@pytest.fixture(scope="module")
def client():
    """A client to make requests to the app."""
    # Ensure the app is in testing mode for the fixture
    app.config['TESTING'] = True
    # Establish an application context for the duration of the tests in this module
    with app.app_context():
        # Then, get a test client
        with app.test_client() as c:
            yield c

@allure.epic("Core Astrology Services")
@allure.feature("Natal Chart Calculation")
class TestNatalChart:
    """Test cases for the Natal Chart API endpoints."""

    @allure.story("Successful Chart Generation")
    @allure.title("Test Natal Chart API with Valid Data")
    @allure.description("This test ensures that a POST request with valid birth data to the natal chart endpoint returns a 200 OK status and a complete chart object.")
    def test_natal_chart_api_success(self, client):
        """Test that a valid request returns a successful response with chart data."""
        with allure.step("Define test payload for a known chart (David Bowie)"):
            test_data = {
                "datetime_str": "1947-01-08T09:00:00",
                "timezone_str": "Europe/London",
                "latitude": 51.4613,
                "longitude": -0.1156,
                "house_system": "Placidus",
                "full_name": "David Bowie"  # Needed for numerology etc.
            }
        
        with allure.step("Make POST request to the API"):
            # Use json=test_data for Flask clients to automatically set content_type
            response = client.post(
                "/api/v1/astrology/swisseph/natal-chart",
                json=test_data # Automatically handles JSON serialization and content-type
            )
        
        with allure.step("Verify the response"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            # Use response.json for automatic deserialization
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="API Response JSON",
                attachment_type=allure.attachment_type.JSON
            )
            assert "chart_info" in data, "Response missing 'chart_info'"
            assert "points" in data, "Response missing 'points'"
            assert "angles" in data, "Response missing 'angles'"
            assert data['points']['Sun']['sign_name'] == "Capricorn", "Sun sign mismatch"
            # Add more specific assertions based on David Bowie's known chart
            assert data['angles']['Ascendant']['sign_name'] == "Libra", "Ascendant sign mismatch"
            assert data['angles']['Midheaven']['sign_name'] == "Cancer", "Midheaven sign mismatch"


    @allure.story("Invalid Input Handling")
    @allure.title("Test Natal Chart API with Invalid Timezone")
    @allure.description("This test verifies that the natal chart endpoint gracefully handles requests with an invalid timezone string, returning a 400 Bad Request status.")
    def test_natal_chart_api_invalid_timezone(self, client):
        """Test that an invalid timezone returns an appropriate error."""
        with allure.step("Define test payload with an invalid timezone"):
            test_data = {
                "datetime_str": "1990-01-01T12:00:00",
                "timezone_str": "Invalid/Timezone",
                "latitude": 34.05,
                "longitude": -118.24,
                "house_system": "Placidus",
                "full_name": "Test User"
            }
        
        with allure.step("Make POST request to the API"):
            response = client.post("/api/v1/astrology/swisseph/natal-chart", json=test_data)
            
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Invalid or unparseable datetime or timezone string provided." in data["error"], "Specific error message for timezone mismatch"

    @allure.story("Missing Required Fields")
    @allure.title("Test Natal Chart API with Missing Data")
    @allure.description("This test checks that a POST request with missing required fields returns a 400 Bad Request status.")
    def test_natal_chart_api_missing_data(self, client):
        """Test that a request with missing data returns an appropriate error."""
        with allure.step("Define test payload with missing latitude"):
            test_data = {
                "datetime_str": "1990-01-01T12:00:00",
                "timezone_str": "America/New_York",
                "longitude": -118.24,
                "house_system": "Placidus",
                "full_name": "Test User"
            }
        
        with allure.step("Make POST request to the API"):
            response = client.post("/api/v1/astrology/swisseph/natal-chart", json=test_data)
            
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Missing required field 'latitude'" in data["error"], "Specific error message for missing field"

    @allure.story("Invalid House System")
    @allure.title("Test Natal Chart API with Unsupported House System")
    @allure.description("This test ensures that providing an unsupported house system results in a 400 Bad Request status.")
    def test_natal_chart_api_unsupported_house_system(self, client):
        """Test that an unsupported house system returns an appropriate error."""
        with allure.step("Define test payload with an unsupported house system"):
            test_data = {
                "datetime_str": "1990-01-01T12:00:00",
                "timezone_str": "America/New_York",
                "latitude": 34.05,
                "longitude": -118.24,
                "house_system": "Unsupported", # Invalid house system
                "full_name": "Test User"
            }
        
        with allure.step("Make POST request to the API"):
            response = client.post("/api/v1/astrology/swisseph/natal-chart", json=test_data)
            
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Unsupported house system" in data["error"], "Specific error message for unsupported house system"