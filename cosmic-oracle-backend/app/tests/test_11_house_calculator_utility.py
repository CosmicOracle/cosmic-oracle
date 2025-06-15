# app/tests/test_11_house_calculator_utility.py
import pytest
import allure
import json # Used for allure.attach, response.json is preferred for data

# IMPORTANT: Do NOT import 'fastapi.testclient.TestClient'. Your project uses Flask.
# The 'client' fixture from conftest.py will provide the correct Flask test client.
# No need to import 'app.main' directly here, as 'client' fixture handles app setup.

@allure.epic("Astrological Tools & Utilities")
@allure.feature("House Calculator")
class TestHouseCalculator:
    """Test cases for the House Calculator API endpoint."""

    @allure.story("Calculate with Different Systems")
    @allure.title("Test House Calculator API with Placidus and Whole Sign systems")
    @allure.description("This test verifies the house calculator API returns correct house cusps for different house systems (Placidus and Whole Sign) based on specific astrological rules.")
    @pytest.mark.parametrize("system, expected_asc_diff", [
        ("placidus", 0.0),      # In Placidus, Cusp 1 is the Ascendant
        ("whole_sign", 0.0)      # In Whole Sign, Cusp 1 is 0° of the Ascendant's sign
    ])
    def test_house_calculator_systems(self, client, system, expected_asc_diff):
        with allure.step(f"Define payload for {system.title()} system"):
            test_data = {
                "datetime_utc_str": "2024-01-01T12:00:00Z", # Example UTC datetime
                "latitude": 51.5074, # London
                "longitude": -0.1278, # London
                "house_system_key": system
            }
        
        with allure.step("Make POST request to the house calculator endpoint"):
            # Assuming your house calculator endpoint is `/api/v1/tools/house-calculator`
            response = client.post("/api/v1/tools/house-calculator/", json=test_data)

        with allure.step("Verify the response and key calculations"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json # Flask test client provides .json property
            allure.attach(
                json.dumps(data, indent=2),
                name=f"{system.title()} Response",
                attachment_type=allure.attachment_type.JSON
            )
            
            results = data.get("results")
            assert results is not None, "Response missing 'results' key"
            assert "house_cusps" in results, "'results' missing 'house_cusps'"
            assert len(results["house_cusps"]) == 12, "Expected 12 house cusps"
            assert "angles" in results, "'results' missing 'angles'"
            
            # For approximate floating-point comparisons
            if system == "placidus":
                # For Placidus, the 1st cusp (Ascendant) should be very close to the Ascendant angle
                # `pytest.approx` is great for float comparisons
                assert results["house_cusps"]["1"] == pytest.approx(results["angles"]["ascendant"], abs=1e-4)
            elif system == "whole_sign":
                # For Whole Sign, the 1st cusp is 0° of the sign the Ascendant is in
                ascendant_degree = results["angles"]["ascendant"]
                # Calculate the start of the sign (e.g., 25° Aries is in Aries, start is 0° Aries)
                ascendant_sign_start_degree = (int(ascendant_degree) // 30) * 30
                assert results["house_cusps"]["1"] == pytest.approx(ascendant_sign_start_degree, abs=1e-4)

    @allure.story("Invalid Input Handling")
    @allure.title("Test House Calculator API with Invalid House System")
    @allure.description("This test ensures that providing an invalid house system key results in a 400 Bad Request status.")
    def test_house_calculator_invalid_system(self, client):
        with allure.step("Define payload with an invalid house system"):
            test_data = {
                "datetime_utc_str": "2024-01-01T12:00:00Z",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "house_system_key": "invalid_system" # Invalid house system
            }
        
        with allure.step("Make POST request to the house calculator endpoint"):
            response = client.post("/api/v1/tools/house-calculator/", json=test_data)

        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Unsupported house system" in data["error"] or "Invalid house system key" in data["error"]

    @allure.story("Missing Data")
    @allure.title("Test House Calculator API with Missing Latitude")
    @allure.description("This test ensures that a missing latitude in the request results in a 400 Bad Request status.")
    def test_house_calculator_missing_latitude(self, client):
        with allure.step("Define payload with missing latitude"):
            test_data = {
                "datetime_utc_str": "2024-01-01T12:00:00Z",
                # "latitude": 51.5074, # Missing latitude
                "longitude": -0.1278,
                "house_system_key": "placidus"
            }
        
        with allure.step("Make POST request to the house calculator endpoint"):
            response = client.post("/api/v1/tools/house-calculator/", json=test_data)

        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Missing required field 'latitude'" in data["error"] or "validation error" in data["error"]