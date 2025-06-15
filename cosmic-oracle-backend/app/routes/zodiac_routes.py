# app/routes/zodiac_routes.py
"""
Flask Blueprint for the Zodiac information and User Preferences features.
"""
from flask import Blueprint
from flask_restx import Api
from app.controllers.zodiac_controller import zodiac_ns, prefs_ns

zodiac_bp = Blueprint('zodiac_api', __name__, url_prefix='/api/v1')
api = Api(zodiac_bp, title='Zodiac & Preferences API', version='1.0')

api.add_namespace(zodiac_ns)
api.add_namespace(prefs_ns)