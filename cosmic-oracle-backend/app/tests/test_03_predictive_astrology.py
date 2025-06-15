# app/tests/test_03_predictive_astrology.py
import pytest
import allure
import json # Used for allure.attach, response.json is preferred for data
from datetime import datetime, timezone # Keep datetime for test data

# IMPORTANT: Do NOT define the 'client' fixture here if it's already in conftest.py.
# Pytest will automatically discover and use the 'client' fixture from conftest.py.
# Also, do not import 'fastapi.testclient.TestClient'. Your project uses Flask.
# The 'client' fixture provided by conftest.py will be a FlaskClient.

@allure.epic("Predictive Astrology")
@allure.feature("Solar Return Charts")
class TestSolarReturn:
    """Test cases for the Solar Return API endpoint."""

    @allure.story("Successful Solar Return Calculation")
    @allure.title("Test Solar Return API with Valid Data")
    @allure.description("This test ensures that a POST request with valid natal data and return year/location returns a 200 OK status and a complete solar return chart.")
    def test_solar_return_api_success(self, client):
        """Test that a valid request returns a successful response with solar return chart data."""
        with allure.step("Define test payload for Solar Return chart"):
            # Example natal data for testing
            test_data = {
                "natal_data": {
                    "datetime_str": "1980-01-01T12:00:00",
                    "timezone_str": "America/New_York",
                    "latitude": 40.71,
                    "longitude": -74.00,
                    "house_system": "Placidus"
                },
                "return_year": 2024,
                "return_location": {"latitude": 34.05, "longitude": -118.24} # Los Angeles, for example
            }
        
        with allure.step("Make POST request to Solar Return endpoint"):
            # Use json=test_data for Flask test clients to automatically set content_type
            response = client.post(
                "/api/v1/astrology/solar-return/chart", # Assuming this is your endpoint
                json=test_data
            )
        
        with allure.step("Verify the response"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json # For Flask test client, .json property directly deserializes JSON response
            allure.attach(
                json.dumps(data, indent=2),
                name="API Response JSON",
                attachment_type=allure.attachment_type.JSON
            )
            assert "solar_return_chart" in data, "Response missing 'solar_return_chart' key"
            assert "metadata" in data, "Response missing 'metadata' key"
            assert data["metadata"]["return_year"] == 2024, "Return year in metadata mismatch"
            assert "points" in data["solar_return_chart"], "Solar return chart missing 'points'"
            assert "angles" in data["solar_return_chart"], "Solar return chart missing 'angles'"
            assert data['solar_return_chart']['points']['Sun']['sign_name'] == 'Capricorn', "Sun sign mismatch in solar return"
            # Add more specific assertions relevant to solar return properties if desired

    @allure.story("Invalid Input Handling")
    @allure.title("Test Solar Return API with Missing Natal Data")
    @allure.description("This test verifies that a POST request with missing or incomplete natal data returns a 400 Bad Request status.")
    def test_solar_return_api_missing_natal_data(self, client):
        """Test that missing natal data returns an appropriate error."""
        with allure.step("Define test payload with incomplete natal_data"):
            test_data = {
                "natal_data": { # Missing datetime_str, timezone_str
                    "latitude": 40.71, "longitude": -74.00, "house_system": "Placidus"
                },
                "return_year": 2024,
                "return_location": {"latitude": 34.05, "longitude": -118.24}
            }
        
        with allure.step("Make POST request to Solar Return endpoint"):
            response = client.post("/api/v1/astrology/solar-return/chart", json=test_data)
            
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            # Specific error message might vary based on your validation logic
            assert "Missing required field" in data["error"] or "Invalid data for natal chart" in data["error"]

    @allure.story("Invalid Return Year")
    @allure.title("Test Solar Return API with Invalid Return Year")
    @allure.description("This test ensures that providing an invalid return year (e.g., in the past) returns a 400 Bad Request status.")
    def test_solar_return_api_invalid_return_year(self, client):
        """Test that an invalid return year returns an appropriate error."""
        with allure.step("Define test payload with an invalid return year (before natal year)"):
            test_data = {
                "natal_data": {
                    "datetime_str": "1980-01-01T12:00:00", "timezone_str": "America/New_York",
                    "latitude": 40.71, "longitude": -74.00, "house_system": "Placidus"
                },
                "return_year": 1979, # Invalid return year
                "return_location": {"latitude": 34.05, "longitude": -118.24}
            }
        
        with allure.step("Make POST request to Solar Return endpoint"):
            response = client.post("/api/v1/astrology/solar-return/chart", json=test_data)
            
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Return year must be equal to or after natal year" in data["error"] # Adjust message to match your actual validation