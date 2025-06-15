# app/tests/test_07_advanced_techniques.py
import pytest
import allure
import json # Used for allure.attach, response.json is preferred for data
from datetime import datetime # Keep datetime for test data

# IMPORTANT: Do NOT import 'fastapi.testclient.TestClient'. Your project uses Flask.
# The 'client' fixture from conftest.py will provide the correct Flask test client.
# No need to import 'app.main' directly here, as 'client' fixture handles app setup.

@allure.epic("Advanced Astrological Techniques")
@allure.feature("Midpoints")
class TestMidpointsService:
    """Test cases for the Midpoints API endpoint."""

    @allure.story("Midpoint Tree Calculation")
    @allure.title("Test Midpoint Tree API with Valid Data")
    @allure.description("This test ensures that a POST request with valid natal data to the midpoint tree endpoint returns a 200 OK status and a complete midpoint tree structure.")
    def test_midpoint_tree_api(self, client):
        with allure.step("Define natal data payload"):
            test_data = {
                "datetime_str": "1971-06-28T09:44:00",
                "timezone_str": "Africa/Johannesburg",
                "latitude": -26.20,
                "longitude": 28.04,
                "house_system": "Placidus",
                "aspect_orb": 2.0 # Assuming your API can take an aspect orb
            }
        with allure.step("Make POST request to midpoint tree endpoint"):
            # Use json=test_data for Flask test clients to automatically set content_type
            response = client.post(
                "/api/v1/astrology/midpoints/tree", # Assuming this is your midpoint tree endpoint
                json=test_data
            )
        
        with allure.step("Verify successful response"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json # Flask test client provides .json property
            allure.attach(
                json.dumps(data, indent=2),
                name="Midpoint Tree Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "midpoint_tree" in data, "Response missing 'midpoint_tree' key"
            assert isinstance(data["midpoint_tree"], list), "'midpoint_tree' should be a list"
            assert len(data["midpoint_tree"]) > 0, "Expected at least one midpoint"
            assert "direct_midpoint" in data["midpoint_tree"][0], "Midpoint entry missing 'direct_midpoint'"
            assert "aspects" in data["midpoint_tree"][0]["direct_midpoint"], "Direct midpoint missing 'aspects'"
            assert isinstance(data["midpoint_tree"][0]["direct_midpoint"]["aspects"], list), "Midpoint aspects should be a list"

    @allure.story("Invalid Input Handling")
    @allure.title("Test Midpoint Tree API with Invalid Natal Data")
    @allure.description("This test ensures that a POST request with invalid or incomplete natal data returns a 400 Bad Request status.")
    def test_midpoint_tree_api_invalid_data(self, client):
        with allure.step("Define test payload with missing latitude"):
            test_data = {
                "datetime_str": "1971-06-28T09:44:00",
                "timezone_str": "Africa/Johannesburg",
                # "latitude": -26.20, # Missing
                "longitude": 28.04,
                "house_system": "Placidus",
                "aspect_orb": 2.0
            }
        with allure.step("Make POST request to midpoint tree endpoint"):
            response = client.post("/api/v1/astrology/midpoints/tree", json=test_data)
        
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Missing required field" in data["error"] or "Invalid data" in data["error"]