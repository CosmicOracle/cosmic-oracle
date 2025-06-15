# app/tests/test_05_insight_services.py
import pytest
import allure
import json # Used for allure.attach, response.json is preferred for data
from datetime import date # Keep date for test data

# IMPORTANT: Do NOT import 'fastapi.testclient.TestClient'. Your project uses Flask.
# The 'client' fixture from conftest.py will provide the correct Flask test client.
# No need to import 'app.main' directly here, as 'client' fixture handles app setup.

@allure.epic("Personalized Insights")
@allure.feature("Dynamic Horoscopes")
class TestHoroscopeService:
    """Test cases for the Daily Horoscope API endpoint."""

    @allure.story("Get Daily Horoscope")
    @allure.title("Test Daily Horoscope endpoint for a valid sign")
    @allure.description("This test verifies that the daily horoscope API successfully returns content for various valid zodiac signs.")
    @pytest.mark.parametrize("sign", ["aries", "leo", "pisces"])
    def test_daily_horoscope_success(self, client, sign):
        with allure.step(f"Make GET request for {sign.capitalize()} horoscope"):
            # Assuming your daily horoscope endpoint is `/api/v1/insights/horoscope/daily/<sign_key>`
            response = client.get(f"/api/v1/insights/horoscope/daily/{sign}")

        with allure.step("Verify the successful response"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json # Flask test client provides .json property
            allure.attach(
                json.dumps(data, indent=2),
                name=f"Daily Horoscope Response for {sign.capitalize()}",
                attachment_type=allure.attachment_type.JSON
            )
            assert "zodiac_sign" in data, "Response missing 'zodiac_sign' key"
            assert data["zodiac_sign"].lower() == sign.lower(), "Zodiac sign mismatch in response"
            assert "horoscope_text" in data, "Response missing 'horoscope_text' key"
            assert len(data["horoscope_text"]) > 50, "Horoscope text is too short, possibly empty or error message"
            assert "influences" in data, "Response missing 'influences' key"
            assert isinstance(data["influences"], list), "'influences' should be a list"

    @allure.story("Invalid Sign Handling")
    @allure.title("Test Daily Horoscope endpoint with Invalid Sign")
    @allure.description("This test verifies that the daily horoscope API returns a 400 Bad Request for an invalid zodiac sign key.")
    def test_daily_horoscope_invalid_sign(self, client):
        with allure.step("Make GET request for an invalid sign"):
            response = client.get("/api/v1/insights/horoscope/daily/invalid_sign")

        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Invalid zodiac sign" in data["error"] or "not found" in data["error"], "Specific error message for invalid sign mismatch"


@allure.epic("Personalized Insights")
@allure.feature("Ritual Suggestions")
class TestRitualService:
    """Test cases for the Ritual Suggestion API endpoint."""
    
    @allure.story("Get Ritual Suggestion")
    @allure.title("Test Ritual Suggestion endpoint for New Moon")
    @allure.description("This test ensures that a POST request for a new moon ritual for a specific sign returns a successful response with ritual details.")
    def test_ritual_suggestion_new_moon(self, client):
        with allure.step("Define request payload for a New Moon ritual for Leo"):
            # Your API endpoint likely requires a specific structure for ritual requests.
            test_data = {
                "purpose": "new-moon-manifestation", # Ensure this matches your backend enum/logic
                "zodiac_sign_key": "leo"
            }
        with allure.step("Make POST request to get ritual suggestion"):
            # Adjust the URL to match your actual Ritual API endpoint
            response = client.post("/api/v1/personal-growth/rituals/suggestion", json=test_data)
        
        with allure.step("Verify the successful response"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Ritual Suggestion Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "title" in data, "Response missing 'title'"
            assert "New Moon Manifestation Ritual for Leo" in data["title"], "Ritual title mismatch"
            assert "general_preparation" in data, "Response missing 'general_preparation'"
            assert "steps" in data, "Response missing 'steps'"
            assert len(data["steps"]) > 3, "Not enough steps in the ritual"
            assert "elemental_enhancement" in data, "Response missing 'elemental_enhancement'"
            assert "Fire sign" in data["elemental_enhancement"], "Elemental enhancement mismatch"

    @allure.story("Invalid Ritual Purpose")
    @allure.title("Test Ritual Suggestion endpoint with Invalid Purpose")
    @allure.description("This test checks that an invalid ritual purpose returns a 400 Bad Request status.")
    def test_ritual_suggestion_invalid_purpose(self, client):
        with allure.step("Define request payload with an invalid purpose"):
            test_data = {
                "purpose": "invalid_purpose",
                "zodiac_sign_key": "aries"
            }
        with allure.step("Make POST request to get ritual suggestion"):
            response = client.post("/api/v1/personal-growth/rituals/suggestion", json=test_data)
        
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Invalid ritual purpose" in data["error"] or "Unsupported ritual" in data["error"]

    @allure.story("Missing Zodiac Sign")
    @allure.title("Test Ritual Suggestion endpoint with Missing Zodiac Sign")
    @allure.description("This test ensures that a missing zodiac sign in the request returns a 400 Bad Request status.")
    def test_ritual_suggestion_missing_sign(self, client):
        with allure.step("Define request payload with missing zodiac_sign_key"):
            test_data = {
                "purpose": "full-moon-release",
                # "zodiac_sign_key": "taurus" # Missing
            }
        with allure.step("Make POST request to get ritual suggestion"):
            response = client.post("/api/v1/personal-growth/rituals/suggestion", json=test_data)
        
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Missing required field" in data["error"] or "zodiac_sign_key is required" in data["error"]