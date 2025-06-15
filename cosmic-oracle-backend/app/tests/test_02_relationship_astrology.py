# app/tests/test_02_relationship_astrology.py
import pytest
import allure
import json # Used for allure.attach, response.json is preferred for data

# IMPORTANT: Do NOT define the 'client' fixture here if it's already in conftest.py.
# Pytest will automatically discover and use the 'client' fixture from conftest.py.
# Also, do not import 'app.main' directly here if your app is built via 'create_app'
# in app/__init__.py and handled by conftest.py's 'app' fixture.

# No specific imports for FlaskClient or TestClient here,
# as the 'client' fixture from conftest.py will provide the correct Flask test client.

@allure.epic("Relationship Astrology")
@allure.feature("Synastry Charts")
class TestSynastry:
    """Test cases for the Synastry API endpoints."""

    @allure.story("Successful Synastry Report")
    @allure.title("Test Synastry API with Valid Data")
    @allure.description("This test ensures that a POST request with valid birth data for two individuals to the synastry endpoint returns a 200 OK status and a complete synastry analysis.")
    def test_synastry_api_success(self, client):
        """Test that a valid request returns a successful response with synastry data."""
        with allure.step("Define test payload for two individuals (David Bowie & Iman)"):
            test_data = {
                "person_a": {
                    "datetime_str": "1947-01-08T09:00:00",
                    "timezone_str": "Europe/London",
                    "latitude": 51.4613,
                    "longitude": -0.1156,
                    "house_system": "Placidus",
                    "full_name": "David Bowie"
                },
                "person_b": {
                    "datetime_str": "1955-07-25T03:00:00", # Example: Iman's birth details
                    "timezone_str": "Africa/Mogadishu",
                    "latitude": 2.0378,
                    "longitude": 45.3432,
                    "house_system": "Placidus",
                    "full_name": "Iman"
                }
            }
        
        with allure.step("Make POST request to Synastry endpoint"):
            # Use json=test_data for Flask test clients to automatically set content_type
            response = client.post(
                "/api/v1/astrology/synastry/chart", # Assuming this is your synastry endpoint
                json=test_data
            )
        
        with allure.step("Verify the response"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json # For Flask test client, .json property directly deserializes
            allure.attach(
                json.dumps(data, indent=2),
                name="API Response JSON",
                attachment_type=allure.attachment_type.JSON
            )
            assert "synastry_analysis" in data, "Response missing 'synastry_analysis' key"
            assert "inter_chart_aspects" in data["synastry_analysis"], "Synastry analysis missing 'inter_chart_aspects'"
            assert isinstance(data["synastry_analysis"]["inter_chart_aspects"], list), "Inter-chart aspects should be a list"
            assert len(data["synastry_analysis"]["inter_chart_aspects"]) > 0, "Expected at least one inter-chart aspect"

            # Example of a specific assertion, if you know what to expect
            # For accurate synastry results, you'd need a mock for swisseph or a known expected output
            # assert any(aspect['aspect_name'] == 'conjunction' for aspect in data["synastry_analysis"]["inter_chart_aspects"])

    @allure.story("Invalid Input Handling")
    @allure.title("Test Synastry API with Invalid Data")
    @allure.description("This test ensures that a POST request with invalid or incomplete data to the synastry endpoint returns a 400 Bad Request status.")
    def test_synastry_api_invalid_data(self, client):
        """Test that an invalid request returns an appropriate error."""
        with allure.step("Define test payload with missing birth_time for person_a"):
            test_data = {
                "person_a": {
                    "datetime_str": "1980-01-01T12:00:00", "timezone_str": "America/New_York",
                    "latitude": 40.71, "longitude": -74.00, "house_system": "Placidus"
                },
                "person_b": { # Missing datetime_str, which is required
                    "timezone_str": "Europe/London",
                    "latitude": 51.50, "longitude": -0.12, "house_system": "Placidus"
                }
            }
        
        with allure.step("Make POST request to Synastry endpoint"):
            response = client.post("/api/v1/astrology/synastry/chart", json=test_data)
            
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            # Specific error message might vary based on your validation logic
            assert "Missing required field" in data["error"] or "Invalid data" in data["error"]