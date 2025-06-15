# app/tests/test_10_personal_growth_services.py
import pytest
import allure
import json # Used for allure.attach, response.json is preferred for data
from datetime import datetime # Keep datetime for test data

# IMPORTANT: Do NOT import 'fastapi.testclient.TestClient'. Your project uses Flask.
# The 'client' fixture from conftest.py will provide the correct Flask test client.
# No need to import 'app.main' directly here, as 'client' fixture handles app setup.

@allure.epic("Personal Growth Features")
@allure.feature("Chakra Analysis")
class TestChakraService:
    """Test cases for the Chakra Analysis API endpoints."""

    @allure.story("Record and Analyze Chakras")
    @allure.title("Test the full flow of assessing a chakra and getting a healing plan")
    @allure.description("This test verifies the process of submitting a chakra assessment and then retrieving a personalized healing plan that reflects the assessment.")
    def test_chakra_assessment_and_healing_plan_flow(self, client):
        with allure.step("1. Submit a new assessment for the Heart chakra"):
            assessment_data = {
                "chakra_key": "heart",
                "balance_score": 3, # A low score indicating imbalance (e.g., 1-5 scale)
                "notes": "Feeling emotionally closed off this week."
            }
            # Assuming your chakra assessment endpoint is `/api/v1/personal/chakras/assessment`
            response = client.post("/api/v1/personal/chakras/assessment", json=assessment_data)
            assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Chakra Assessment Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "message" in data, "Response missing 'message'"
            assert "assessment recorded successfully" in data["message"], "Success message mismatch"
        
        with allure.step("2. Request a personalized healing plan"):
            # Assuming the healing plan endpoint `/api/v1/personal/chakras/healing-plan`
            # uses the most recent assessment for the user/session.
            response = client.get("/api/v1/personal/chakras/healing-plan")
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Healing Plan Response",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("3. Verify the plan addresses the imbalance"):
            assert "recommendations" in data, "Healing plan missing 'recommendations'"
            assert isinstance(data["recommendations"], list), "Recommendations should be a list"
            assert len(data["recommendations"]) > 0, "Expected at least one recommendation"
            
            # Find the recommendation specifically for the Heart chakra based on the assessment
            heart_recommendation = next((rec for rec in data["recommendations"] if rec.get("focus_chakra", "").lower() == "heart"), None)
            
            assert heart_recommendation is not None, "Healing plan should include a recommendation for the imbalanced Heart chakra."
            assert "healing_suggestions" in heart_recommendation, "Heart recommendation missing 'healing_suggestions'"
            assert "affirmation" in heart_recommendation["healing_suggestions"], "Healing suggestions missing 'affirmation'"
            assert "recommended_crystals" in heart_recommendation["healing_suggestions"], "Healing suggestions missing 'recommended_crystals'"
            # Check for a crystal known for heart chakra (e.g., Rose Quartz from your data)
            assert any("Rose Quartz" in crystal_name for crystal_name in heart_recommendation["healing_suggestions"]["recommended_crystals"]), "Rose Quartz not suggested for Heart chakra"

    @allure.story("Invalid Chakra Assessment")
    @allure.title("Test Chakra Assessment with Invalid Data")
    @allure.description("This test verifies that submitting an assessment with an invalid chakra key results in a 400 Bad Request.")
    def test_chakra_assessment_invalid_data(self, client):
        with allure.step("Submit assessment with invalid chakra_key"):
            assessment_data = {
                "chakra_key": "invalid_chakra", # Invalid key
                "balance_score": 1,
                "notes": "Testing invalid chakra."
            }
            response = client.post("/api/v1/personal/chakras/assessment", json=assessment_data)
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data
            assert "Invalid chakra key" in data["error"] or "not found" in data["error"]


@allure.epic("Personal Growth Features")
@allure.feature("Meditation Tracking")
class TestMeditationService:
    """Test cases for the Meditation Tracking API endpoints."""

    @allure.story("Record a Meditation Session")
    @allure.title("Test recording a new mindfulness meditation session")
    @allure.description("This test verifies that a new meditation session can be successfully recorded via the API.")
    def test_record_meditation_session(self, client):
        with allure.step("Define the meditation session payload"):
            session_data = {
                "duration": 20, # in minutes
                "meditation_type": "mindfulness",
                "notes": "Felt very focused today.",
                "quality_rating": 8 # on a scale, e.g., 1-10
            }
        with allure.step("Make POST request to record the session"):
            # Assuming your meditation sessions endpoint is `/api/v1/personal-growth/meditation/sessions`
            response = client.post("/api/v1/personal-growth/meditation/sessions", json=session_data)

        with allure.step("Verify successful creation"):
            assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Meditation Session Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "message" in data, "Response missing 'message'"
            assert "Session recorded successfully" in data["message"], "Success message mismatch"
            assert "session_id" in data, "Response missing 'session_id'"
            # You might also verify that the session is retrievable later if there's a GET endpoint

    @allure.story("Invalid Meditation Session Data")
    @allure.title("Test recording a meditation session with invalid duration")
    @allure.description("This test ensures that providing an invalid duration for a meditation session results in a 400 Bad Request.")
    def test_record_meditation_session_invalid_duration(self, client):
        with allure.step("Define session payload with invalid duration"):
            session_data = {
                "duration": -5, # Invalid duration
                "meditation_type": "mindfulness",
                "notes": "Negative duration test."
            }
        with allure.step("Make POST request to record the session"):
            response = client.post("/api/v1/personal-growth/meditation/sessions", json=session_data)
        
        with allure.step("Verify the error response"):
            assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
            data = response.json
            assert "error" in data
            assert "Duration must be positive" in data["error"]