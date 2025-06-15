# app/tests/test_astrology_engine.py
import pytest
from datetime import datetime, timezone
# NO MORE: from app import create_app, astrology_service
# You can still import the class if you're testing it directly, not via the service facade
from app.services.astrology_service import AstrologyEngine

# Define fixtures as they come from conftest.py implicitly when pytest runs
# (or you can explicitly import them from conftest if you prefer, but not usually needed)

def test_astrology_engine_basic_calculation(app): # Use the 'app' fixture directly for config or context
    # When testing AstrologyEngine directly, you still instantiate it as before
    dt_utc = datetime(1990, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    latitude = 34.0522
    longitude = -118.2437
    house_system = "Placidus"
    altitude = 0.0

    with app.app_context(): # Ensure app context is active if Engine relies on global singletons
        engine = AstrologyEngine(dt_utc, latitude, longitude, altitude, house_system)
        chart = engine.generate_full_chart()

        assert "chart_info" in chart
        assert "points" in chart
        assert "error" not in chart
        assert chart['points']['Sun']['sign_name'] == 'Capricorn'
        assert chart['angles']['Ascendant']['sign_name']


def test_astrology_service_natal_chart_details(astrology_service_fixture): # Use the service fixture
    chart = astrology_service_fixture.get_natal_chart_details(
        datetime_str="1990-01-01T12:00:00",
        timezone_str="America/New_York",
        latitude=34.0522,
        longitude=-118.2437,
        house_system="Placidus"
    )
    assert "chart_info" in chart
    assert "points" in chart
    assert "error" not in chart
    assert chart['points']['Sun']['sign_name'] == 'Capricorn'
    assert chart['angles']['Ascendant']['sign_name']

# Apply similar changes to all other test files listed in the error.
# For example, in test_01_natal_chart.py, if it uses app.main, you might change it to use the `client` fixture or `astrology_service_fixture`.