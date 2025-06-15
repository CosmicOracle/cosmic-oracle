# app/routes/astrology_routes.py
"""
This module defines the Flask Blueprint for astrology-related routes
and registers the Flask-RESTX API namespaces from the astrology controller.
It also includes a utility route for testing the Swiss Ephemeris setup.
"""
from flask import Blueprint, request, jsonify, current_app
import os
from datetime import datetime
import swisseph as swe

# Important: Import your Flask-RESTX Api instance.
# This assumes 'api' is the name of your Flask-RESTX Api object initialized in app/__init__.py.
from app import api

# Import the Flask-RESTX Namespaces defined in your astrology_controller.
# These namespaces (swisseph_ns, skyfield_ns) contain your actual API endpoint definitions (Resources).
from app.controllers.astrology_controller import swisseph_ns, skyfield_ns

# Define a Flask Blueprint for general astrology routes.
# This Blueprint's `url_prefix` will apply to any *traditional* Flask routes defined below it.
# It does NOT apply to Flask-RESTX namespaces, which manage their own prefixes.
astrology_bp = Blueprint('astrology', __name__, url_prefix='/api/astrology')

# Register the Flask-RESTX namespaces with the main API instance.
# This is the CRUCIAL STEP that makes all the endpoints defined within
# 'swisseph_ns' and 'skyfield_ns' (e.g., /daily-horoscope, /natal-chart)
# accessible via your Flask application's API.
api.add_namespace(swisseph_ns)
api.add_namespace(skyfield_ns)

# --- Utility Functions and Routes (Non-Flask-RESTX) ---

def init_ephemeris():
    """
    Initializes the Swiss Ephemeris library by setting the path to its ephemeris files.
    This function should be called before performing any Swiss Ephemeris calculations.
    """
    try:
        ephe_path = current_app.config.get('SWEPH_PATH')
        if not ephe_path:
            raise RuntimeError("SWEPH_PATH is not configured in Flask app.")

        if not os.path.exists(ephe_path):
            raise FileNotFoundError(f"Swiss Ephemeris directory not found at: {ephe_path}")

        # Basic check for essential ephemeris files.
        # These are common files, adjust if your setup requires others.
        essential_files = ['sepl_20.se1', 'semo_20.se1']
        missing_files = [f for f in essential_files if not os.path.exists(os.path.join(ephe_path, f))]
        if missing_files:
            current_app.logger.warning(
                f"Missing some recommended Swiss Ephemeris files in {ephe_path}: {', '.join(missing_files)}. "
                "Calculations might be incomplete or fall back to internal data."
            )

        swe.set_ephe_path(ephe_path)
        current_app.logger.info(f"Swiss Ephemeris initialized with path: {ephe_path}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to initialize Swiss Ephemeris: {str(e)}", exc_info=True)
        # Re-raise as a more general RuntimeError for upstream error handling
        raise RuntimeError(f"Failed to initialize Swiss Ephemeris: {str(e)}")


@astrology_bp.route('/test_ephemeris', methods=['GET'])
def test_ephemeris():
    """
    Tests the Swiss Ephemeris setup by calculating the Sun's position for the current UTC time.
    This route demonstrates direct interaction with the swe library.
    It is accessible via `/api/astrology/test_ephemeris`.
    """
    try:
        # Ensure Swiss Ephemeris is initialized. In a larger app, this might be done once on app startup.
        init_ephemeris()

        # Get current UTC time for calculation
        now_utc = datetime.utcnow()
        # Convert datetime to Julian Day (UT) for Swiss Ephemeris calculations
        jd_ut = swe.julday(now_utc.year, now_utc.month, now_utc.day,
                           now_utc.hour + now_utc.minute/60.0 + now_utc.second/3600.0)

        # Calculate Sun's position
        # swe.FLG_SWIEPH: Use standard ephemeris files.
        # swe.FLG_SPEED: Calculate and return instantaneous speed.
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED

        # swe.calc_ut returns (xx, ret), where xx is a tuple of (longitude, latitude, speed)
        xx, ret = swe.calc_ut(jd_ut, swe.SUN, flags)

        sun_longitude = xx[0]
        sun_latitude = xx[1]
        sun_speed = xx[2] # Speed in degrees per day

        # Determine Zodiac Sign
        sign_num = int(sun_longitude / 30)
        zodiac_signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]

        # Longitude within its sign
        degrees_in_sign = sun_longitude % 30

        return jsonify({
            'success': True,
            'message': 'Swiss Ephemeris is working correctly and calculated Sun\'s position.',
            'current_utc_time': now_utc.isoformat(),
            'sun_position': {
                'longitude': sun_longitude,
                'latitude': sun_latitude,
                'speed_degrees_per_day': sun_speed,
                'zodiac_sign': zodiac_signs[sign_num],
                'degrees_in_sign': degrees_in_sign
            }
        })
    except Exception as e:
        current_app.logger.error(f"Swiss Ephemeris test failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500