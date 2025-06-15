# app/routes/solar_return_routes.py
"""
Flask Blueprint for the Solar Return Astrology feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.solar_return_controller import solar_return_ns

solar_return_bp = Blueprint('solar_return_api', __name__, url_prefix='/api/v1')

api = Api(solar_return_bp,
          title='Solar Return API',
          version='1.0',
          description='Endpoints for creating yearly forecast charts (Solar Returns).')

api.add_namespace(solar_return_ns)