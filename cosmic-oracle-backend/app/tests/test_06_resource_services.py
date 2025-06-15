# app/tests/test_06_resource_services.py
import pytest
import allure
import json # Used for allure.attach, response.json is preferred for data

# IMPORTANT: Do NOT import 'fastapi.testclient.TestClient'. Your project uses Flask.
# The 'client' fixture from conftest.py will provide the correct Flask test client.
# No need to import 'app.main' directly here, as 'client' fixture handles app setup.

@allure.epic("Resource Libraries")
@allure.feature("Crystal Recommendations")
class TestCrystalService:
    """Test cases for the Crystal Recommendation API endpoint."""

    @allure.story("Get Recommendation by Need")
    @allure.title("Test Crystal API for 'love' crystals")
    @allure.description("This test verifies that the Crystal API successfully returns crystal recommendations for a given need (e.g., 'love').")
    def test_crystal_rec_by_need(self, client):
        with allure.step("Make GET request for 'love' crystals"):
            # Assuming your crystal recommendations endpoint is `/api/v1/resources/crystals/recommendations`
            # and takes `need_key` as a query parameter.
            response = client.get("/api/v1/resources/crystals/recommendations?need_key=love")

        with allure.step("Verify the response"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json # Flask test client provides .json property
            allure.attach(
                json.dumps(data, indent=2),
                name="Crystal Recommendations Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "recommendations" in data, "Response missing 'recommendations' key"
            assert isinstance(data["recommendations"], list), "Recommendations should be a list"
            assert len(data["recommendations"]) > 0, "Expected at least one crystal recommendation"
            
            # Check if Rose Quartz is in the recommendations for love (assuming your data has it)
            assert any(rec.get("name") == "Rose Quartz" for rec in data["recommendations"]), "Rose Quartz not found in 'love' recommendations"
            assert any("properties" in rec for rec in data["recommendations"]), "Crystal recommendation missing 'properties'"

    @allure.story("Invalid Need Key")
    @allure.title("Test Crystal API with Invalid Need Key")
    @allure.description("This test ensures that an invalid need key for crystal recommendations returns a 400 Bad Request status.")
    def test_crystal_rec_invalid_need_key(self, client):
        with allure.step("Make GET request for an invalid need key"):
            response = client.get("/api/v1/resources/crystals/recommendations?need_key=invalid_need")

        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "No crystals found for need" in data["error"] or "Invalid need key" in data["error"], "Specific error message for invalid need key mismatch"

    @allure.story("Missing Need Key")
    @allure.title("Test Crystal API with Missing Need Key")
    @allure.description("This test ensures that a missing 'need_key' query parameter returns a 400 Bad Request status.")
    def test_crystal_rec_missing_need_key(self, client):
        with allure.step("Make GET request with missing need_key"):
            response = client.get("/api/v1/resources/crystals/recommendations") # No query param

        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "need_key parameter is required" in data["error"] or "missing parameter" in data["error"], "Specific error message for missing parameter mismatch"


@allure.epic("Resource Libraries")
@allure.feature("Star Catalog")
class TestStarCatalogService:
    """Test cases for the Star Catalog API endpoint."""

    @allure.story("Get Specific Star Details")
    @allure.title("Test Star Catalog endpoint for 'Sirius'")
    @allure.description("This test verifies that the Star Catalog API successfully returns details for a known star (Sirius).")
    def test_get_star_details_sirius(self, client):
        with allure.step("Make GET request for star 'Sirius'"):
            # Assuming your star catalog endpoint is `/api/v1/resources/star-catalog/<star_name>`
            response = client.get("/api/v1/resources/star-catalog/Sirius")
        
        with allure.step("Verify the response"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Star Details Response for Sirius",
                attachment_type=allure.attachment_type.JSON
            )
            assert "name" in data, "Response missing 'name'"
            assert data["name"] == "Sirius", "Star name mismatch"
            # Assuming your star data has an 'hr_number' and 'lore' field
            assert "hr_number" in data, "Response missing 'hr_number'"
            assert data["hr_number"] == 2491, "HR number mismatch for Sirius"
            assert "lore" in data, "Response missing 'lore'"
            assert "constellation" in data["lore"], "Lore missing 'constellation'"
            assert "Canis Major" in data["lore"]["constellation"], "Constellation mismatch"

    @allure.story("Star Not Found")
    @allure.title("Test Star Catalog endpoint for Non-Existent Star")
    @allure.description("This test ensures that requesting details for a non-existent star returns a 404 Not Found status.")
    def test_get_star_details_not_found(self, client):
        with allure.step("Make GET request for a non-existent star"):
            response = client.get("/api/v1/resources/star-catalog/NonExistentStar")
        
        with allure.step("Verify the error response"):
            assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Star 'NonExistentStar' not found" in data["error"]