from flask import Blueprint, request, jsonify, current_app
import swisseph as swe
import sys
import os
from datetime import datetime

# Initialize Swiss Ephemeris with path from config
def init_ephemeris():
    try:
        ephe_path = current_app.config['SWEPH_PATH']
        
        # Verify SwissEph directory exists
        if not os.path.exists(ephe_path):
            raise FileNotFoundError(f"Swiss Ephemeris directory not found at {ephe_path}")
            
        # Check for essential files (sepl*.se1, semo*.se1, etc.)
        essential_files = ['sepl_20.se1', 'semo_20.se1']
        missing_files = [f for f in essential_files if not os.path.exists(os.path.join(ephe_path, f))]
        if missing_files:
            raise FileNotFoundError(f"Missing essential Swiss Ephemeris files: {', '.join(missing_files)}")
        
        swe.set_ephe_path(ephe_path)
        current_app.logger.info(f"Swiss Ephemeris initialized with path: {ephe_path}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to initialize Swiss Ephemeris: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to initialize Swiss Ephemeris: {str(e)}")

from app.controllers.astrology_controller import (
    get_daily_horoscope,
    get_natal_chart,
    get_moon_phase,
    get_planetary_positions,
    get_cosmic_events,
    get_compatibility_report
)
from app.services.skyfield_astronomy_service import get_moon_phase_data
from app.services.content_fetch_service import get_cosmic_events_for_date_range
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import swisseph as swe

bp = Blueprint('astrology', __name__, url_prefix='/api/astrology')

@bp.route('/daily_horoscope/<sign>', methods=['GET'])
def daily_horoscope(sign):
    try:
        horoscope = get_daily_horoscope(sign)
        return jsonify(horoscope)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/moon_phase', methods=['GET'])
def moon_phase():
    date_str = request.args.get('date')
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        phase_data = get_moon_phase_data(date)
        return jsonify(phase_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/planetary_positions', methods=['GET'])
def planetary_positions():
    date_str = request.args.get('date')
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        positions = get_planetary_positions(date)
        return jsonify(positions)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/cosmic_events', methods=['GET'])
def cosmic_events():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        events = get_cosmic_events_for_date_range(start, end)
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/natal_chart', methods=['POST'])
@jwt_required()
def create_natal_chart():
    current_user_id = get_jwt_identity()
    try:
        chart_data = get_natal_chart(request.get_json(), current_user_id)
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/natal_chart', methods=['GET'])
@jwt_required()
def get_saved_natal_chart():
    current_user_id = get_jwt_identity()
    try:
        chart_data = get_natal_chart(None, current_user_id)
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 404 if "No chart found" in str(e) else 400

@bp.route('/compatibility', methods=['POST'])
def get_compatibility():
    try:
        data = request.get_json()
        report = get_compatibility_report(data['person1'], data['person2'])
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/test_ephemeris', methods=['GET'])
def test_ephemeris():
    try:
        if not init_ephemeris():
            return jsonify({
                'success': False,
                'error': 'Failed to initialize Swiss Ephemeris'
            }), 500

        # Get current time
        now = datetime.utcnow()
        jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
        
        # Calculate Sun's position
        flags = swe.FLG_SWIEPH
        sun_pos = swe.calc_ut(jd, swe.SUN, flags)
        
        # Get position in zodiac
        sign_num = int(sun_pos[0][0] / 30)
        zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                       'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        return jsonify({
            'success': True,
            'message': 'Swiss Ephemeris is working correctly',
            'time': now.isoformat(),
            'sun_position': {
                'longitude': sun_pos[0][0],
                'latitude': sun_pos[0][1],
                'speed': sun_pos[0][2],
                'zodiac_sign': zodiac_signs[sign_num],
                'degrees_in_sign': sun_pos[0][0] % 30
            }
        })
    except Exception as e:
        current_app.logger.error(f"Swiss Ephemeris test failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500