# app/routes/horoscope_routes.py
"""
Flask Blueprint for the Dynamic Horoscope feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.horoscope_controller import horoscope_ns

horoscope_bp = Blueprint('horoscope_api', __name__, url_prefix='/api/v1')

api = Api(horoscope_bp,
          title='Dynamic Horoscope API',
          version='1.0',
          description='Endpoints for generating real-time, transit-based horoscopes.')

api.add_namespace(horoscope_ns)