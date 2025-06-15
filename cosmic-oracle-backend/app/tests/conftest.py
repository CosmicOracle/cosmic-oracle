# app/tests/conftest.py
import pytest
from flask import current_app # Import current_app
from app import create_app, db # Import create_app and db

# IMPORTANT: Do NOT import specific service instances directly here (e.g., no `from app import astrology_service`)
# They are accessed via the 'app' fixture and `app.<service_name>`.

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for the test session."""
    test_app = create_app() # Your app factory
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Use in-memory DB for tests
        "WTF_CSRF_ENABLED": False, # Disable CSRF for testing
        # Ensure test config has necessary paths and other values for service initialization
        "SWEPH_PATH": "C:\\SWEPH\\EPHE\\swisseph",
        "SKYFIELD_EPHEMERIS_PATH": "D:\\my_projects\\cosmic_oracle\\cosmic-oracle-backend\\instance\\skyfield-data\\de440.bsp",
        "LOG_LEVEL": "DEBUG", # Set logging to DEBUG for tests
        # Add any other config variables needed for services to initialize
    })

    # Push an application context for the session fixture
    # This is critical because services are attached to `app` and often accessed via `current_app`.
    with test_app.app_context():
        db.create_all() # Create tables for tests
        # Optionally, seed database with test data here if needed for all tests
        yield test_app
        db.session.remove() # Clean up session
        db.drop_all() # Clean up database after tests

@pytest.fixture()
def client(app):
    """A test client for the app."""
    # This client operates within an app context for each request it makes
    return app.test_client()

@pytest.fixture()
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

# Fixtures to provide specific service instances from the test app context
# Using function scope is generally safer for services in tests to ensure isolation.
@pytest.fixture(scope='function')
def astrology_service_fixture(app):
    """Provides the instantiated astrology_service for tests."""
    return app.astrology_service

@pytest.fixture(scope='function')
def horoscope_service_fixture(app):
    """Provides the instantiated horoscope_service for tests."""
    return app.horoscope_service

@pytest.fixture(scope='function')
def numerology_service_fixture(app):
    """Provides the instantiated numerology_service for tests."""
    return app.numerology_service

@pytest.fixture(scope='function')
def content_fetch_service_fixture(app):
    """Provides the instantiated content_fetch_service for tests."""
    return app.content_fetch_service

@pytest.fixture(scope='function')
def ai_synthesis_service_fixture(app):
    """Provides the instantiated ai_synthesis_service for tests."""
    return app.ai_synthesis_service

@pytest.fixture(scope='function')
def user_service_fixture(app):
    """Provides the instantiated user_service for tests."""
    return app.user_service

@pytest.fixture(scope='function')
def auth_service_fixture(app):
    """Provides the instantiated auth_service for tests."""
    return app.auth_service

@pytest.fixture(scope='function')
def tarot_service_fixture(app):
    """Provides the instantiated tarot_service for tests."""
    return app.tarot_service

# Add fixtures for all other services if you need to access them directly in tests