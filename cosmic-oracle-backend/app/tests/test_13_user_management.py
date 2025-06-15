# app/tests/test_13_user_management.py
import pytest
import allure
import json # Used for allure.attach, response.json is preferred for data

# IMPORTANT: Do NOT import 'fastapi.testclient.TestClient'. Your project uses Flask.
# The 'client' fixture from conftest.py will provide the correct Flask test client.
# No need to import 'app.main' directly here, as 'client' fixture handles app setup.

# You might need to import specific services or models if your tests
# directly interact with them to set up test data or verify database state.
# from app import db # Example, if you need direct DB access
# from app.models.user import User # Example, if you need to query User model

@allure.epic("User Management & Authentication")
@allure.feature("User Account Lifecycle")
# Removed global skip, as we'll implement basic tests.
# You can add pytest.mark.skip(reason="...") to individual tests if needed.
class TestUserManagement:
    """Test cases for the User Management and Authentication API endpoints."""

    # Fixture to provide a clean user for tests, ensuring isolation.
    @pytest.fixture(autouse=True) # autouse=True means it runs for every test in this class
    def setup_teardown_user(self, app, db, user_service_fixture):
        with app.app_context(): # Ensure app context for DB operations
            # Clear users table before each test to ensure clean state
            # Assuming you have a User model and can delete all records
            # This is a simple way; for complex setups, use transaction rollbacks.
            # db.session.query(User).delete()
            # db.session.commit()
            
            # Yield to the test function
            yield
            
            # Teardown: Clean up users created during the test
            # db.session.query(User).delete()
            # db.session.commit()

    @allure.story("User Registration")
    @allure.title("Test successful user registration")
    @allure.description("Verifies that a new user can successfully register with valid credentials.")
    def test_user_registration(self, client):
        """
        1. POST to /auth/register with new credentials.
        2. Assert 201 Created.
        3. Assert response contains user data (without password).
        """
        with allure.step("Define registration payload"):
            registration_data = {
                "username": "testuser_reg",
                "email": "register@example.com",
                "password": "password123"
            }
        
        with allure.step("Make POST request to register endpoint"):
            # Assuming your registration endpoint is /api/v1/auth/register
            response = client.post("/api/v1/auth/register", json=registration_data)
        
        with allure.step("Verify 201 Created status and response data"):
            assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.json}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Registration Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "message" in data and "User registered successfully" in data["message"]
            assert "user" in data
            assert data["user"]["username"] == registration_data["username"]
            assert data["user"]["email"] == registration_data["email"]
            assert "password" not in data["user"], "Password should not be returned"

    @allure.story("User Login and Token Generation")
    @allure.title("Test successful user login and JWT token generation")
    @allure.description("Verifies that a registered user can log in with correct credentials and receive an access token.")
    def test_user_login(self, client):
        """
        1. Create a user first (or use a pre-registered one).
        2. POST to /auth/login with correct credentials.
        3. Assert 200 OK.
        4. Assert response contains an access_token.
        """
        # First, register a user to ensure one exists for login
        register_data = {
            "username": "testuser_login",
            "email": "login@example.com",
            "password": "loginpassword"
        }
        client.post("/api/v1/auth/register", json=register_data) # Register user

        with allure.step("Define login payload"):
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
        
        with allure.step("Make POST request to login endpoint"):
            # Assuming your login endpoint is /api/v1/auth/login
            response = client.post("/api/v1/auth/login", json=login_data)
        
        with allure.step("Verify 200 OK status and token presence"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Login Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "access_token" in data, "Access token missing from response"
            assert data["access_token"] is not None

    @allure.story("Authenticated Endpoint Access")
    @allure.title("Test access to a protected route with a valid JWT token")
    @allure.description("Verifies that a user can access a JWT-protected endpoint by providing a valid access token in the Authorization header.")
    def test_access_protected_route_with_token(self, client):
        """
        1. Login to get a token.
        2. Make a GET request to a protected endpoint (e.g., /users/me) with the
           'Authorization: Bearer <token>' header.
        3. Assert 200 OK.
        4. Assert the response contains the correct user's data.
        """
        # Login to get a token
        register_data = {
            "username": "testuser_protected",
            "email": "protected@example.com",
            "password": "protectedpassword"
        }
        client.post("/api/v1/auth/register", json=register_data)
        
        login_data = {"email": register_data["email"], "password": register_data["password"]}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        access_token = login_response.json["access_token"]

        with allure.step("Make GET request to a protected endpoint with token"):
            # Assuming /api/v1/users/me is a protected endpoint that returns current user info
            response = client.get(
                "/api/v1/users/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        with allure.step("Verify 200 OK status and user data"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json}"
            data = response.json
            allure.attach(
                json.dumps(data, indent=2),
                name="Protected Route Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert "username" in data and data["username"] == register_data["username"]
            assert "email" in data and data["email"] == register_data["email"]

    @allure.story("Unauthenticated Access")
    @allure.title("Test access to a protected route without a token")
    @allure.description("Verifies that a protected endpoint returns a 401 Unauthorized status when no token is provided.")
    def test_access_protected_route_without_token(self, client):
        with allure.step("Make GET request to a protected endpoint without a token"):
            response = client.get("/api/v1/users/me") # Assuming /api/v1/users/me is protected
        
        with allure.step("Verify 401 Unauthorized status"):
            assert response.status_code == 401, f"Expected 401, got {response.status_code}. Response: {response.json}"
            data = response.json
            assert "msg" in data # Flask-JWT-Extended default unauthorized message key
            assert "Missing" in data["msg"] or "Unauthorized" in data["msg"]