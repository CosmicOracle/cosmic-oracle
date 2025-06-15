# app/tests/test_04_divination_services.py
import pytest
import allure
import json # Used for allure.attach, response.json is preferred for data
from datetime import date # Keep datetime for test data

# IMPORTANT: Do NOT define the 'client' fixture here if it's already in conftest.py.
# Pytest will automatically discover and use the 'client' fixture from conftest.py.
# Also, do not import 'fastapi.testclient.TestClient'. Your project uses Flask.
# The 'client' fixture provided by conftest.py will be a FlaskClient.
# Also, no need to import 'app.main' directly here, as 'client' fixture handles app setup.


@allure.epic("Divination & Insights")
@allure.feature("Tarot Readings")
class TestTarotService:
    """Test cases for the Tarot API endpoints."""

    @allure.story("Perform a New Reading")
    @allure.title("Test Tarot API for a Three-Card Spread")
    @allure.description("This test verifies that the Tarot API successfully returns a three-card reading with expected structure.")
    def test_tarot_three_card_spread(self, client):
        """Test a valid request for a three-card tarot spread."""
        with allure.step("Make POST request to perform a 'three' card spread"):
            # Your API endpoint likely requires a POST with a specific spread type or number of cards.
            # Adjust the URL and payload to match your actual API endpoint for tarot readings.
            # Example assuming a generic /reading endpoint that takes 'spread_type' and 'num_cards' in JSON:
            test_data = {"spread_type": "past_present_future", "num_cards": 3}
            response = client.post("/api/v1/divination/tarot/reading", json=test_data)
        
        with allure.step("Verify the response structure and content"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json # Flask test client provides .json property
            allure.attach(
                json.dumps(data, indent=2), # Use json.dumps for structured JSON attachment
                name="Three-Card Spread Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "spread_type" in data, "Response missing 'spread_type' key"
            assert data["spread_type"] == test_data["spread_type"], "Spread type mismatch in response"
            assert "cards_drawn" in data, "Response missing 'cards_drawn' key"
            assert len(data["cards_drawn"]) == test_data["num_cards"], "Incorrect number of cards drawn"
            
            # Assert on card structure (adjust keys based on your TarotService output)
            assert "name" in data["cards_drawn"][0], "Card missing 'name'"
            assert "orientation" in data["cards_drawn"][0], "Card missing 'orientation'"
            assert "meaning" in data["cards_drawn"][0], "Card missing 'meaning'"
            # Example: check for a specific position if your API assigns them
            # assert data["cards_drawn"][0]["position_name"] == "Past" # If your service outputs this

    @allure.story("Invalid Spread Type")
    @allure.title("Test Tarot API with an Invalid Spread Name")
    @allure.description("This test verifies that the Tarot API returns a 400 Bad Request error for an invalid spread type.")
    def test_tarot_invalid_spread(self, client):
        """Test that an invalid spread type returns an appropriate error."""
        with allure.step("Make POST request with an invalid spread type"):
            # Assuming your API validates spread types
            test_data = {"spread_type": "invalid_spread_type", "num_cards": 3}
            response = client.post("/api/v1/divination/tarot/reading", json=test_data)

        with allure.step("Verify the 400 Bad Request error"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Invalid spread type" in data["error"] or "Unsupported spread type" in data["error"], "Specific error message for invalid spread mismatch"

    @allure.story("Edge Case: Zero Cards")
    @allure.title("Test Tarot API with Zero Cards Requested")
    @allure.description("This test ensures that requesting zero cards results in a 400 Bad Request error.")
    def test_tarot_zero_cards(self, client):
        """Test requesting zero cards returns an error."""
        with allure.step("Make POST request for zero cards"):
            test_data = {"spread_type": "daily", "num_cards": 0}
            response = client.post("/api/v1/divination/tarot/reading", json=test_data)

        with allure.step("Verify the 400 Bad Request error"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data
            assert "Number of cards must be positive" in data["error"]


@allure.epic("Divination & Insights")
@allure.feature("Biorhythms")
class TestBiorhythmService:
    """Test cases for the Biorhythm API endpoint."""

    @allure.story("Current Biorhythm Values")
    @allure.title("Test Biorhythm API for current values")
    @allure.description("This test verifies that the Biorhythm API successfully returns current biorhythm values for a given birth date.")
    def test_biorhythm_current_values(self, client):
        with allure.step("Define request payload"):
            test_data = {
                "birth_date_str": "1990-05-15",
                "analysis_date_str": date.today().isoformat() # Use today's date for current values
            }
        with allure.step("Make POST request to get current biorhythms"):
            # Adjust the URL to match your Biorhythm API endpoint
            response = client.post("/api/v1/insights/biorhythm/current", json=test_data)

        with allure.step("Verify the response structure"):
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Biorhythm Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "days_alive" in data, "Response missing 'days_alive'"
            assert "cycles" in data, "Response missing 'cycles'"
            assert "physical" in data["cycles"], "Cycles missing 'physical'"
            assert "emotional" in data["cycles"], "Cycles missing 'emotional'"
            assert "intellectual" in data["cycles"], "Cycles missing 'intellectual'"
            assert "status" in data["cycles"]["physical"], "Physical cycle missing 'status'"
            # Add more specific assertions about the values or expected phases if desired

    @allure.story("Invalid Birth Date")
    @allure.title("Test Biorhythm API with Invalid Birth Date")
    @allure.description("This test ensures that an invalid birth date format for biorhythm calculation returns a 400 Bad Request status.")
    def test_biorhythm_invalid_birth_date(self, client):
        with allure.step("Define request payload with invalid birth_date_str"):
            test_data = {
                "birth_date_str": "1990/05/15", # Invalid format
                "analysis_date_str": date.today().isoformat()
            }
        with allure.step("Make POST request to get current biorhythms"):
            response = client.post("/api/v1/insights/biorhythm/current", json=test_data)

        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Invalid birth date format" in data["error"]

    @allure.story("Invalid Analysis Date")
    @allure.title("Test Biorhythm API with Invalid Analysis Date")
    @allure.description("This test ensures that an invalid analysis date format for biorhythm calculation returns a 400 Bad Request status.")
    def test_biorhythm_invalid_analysis_date(self, client):
        with allure.step("Define request payload with invalid analysis_date_str"):
            test_data = {
                "birth_date_str": "1990-05-15",
                "analysis_date_str": "not-a-date" # Invalid format
            }
        with allure.step("Make POST request to get current biorhythms"):
            response = client.post("/api/v1/insights/biorhythm/current", json=test_data)

        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data, "Error message missing from response"
            assert "Invalid analysis date format" in data["error"]