# app/routes/personal_forecast_routes.py
"""
Flask Blueprint for the Personal Sky & Forecast feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.personal_forecast_controller import personal_sky_ns

personal_forecast_bp = Blueprint('personal_forecast_api', __name__, url_prefix='/api/v1')

api = Api(personal_forecast_bp,
          title='Personal Forecast API',
          version='1.0',
          description='Endpoints for generating personalized astrological forecasts.')

api.add_namespace(personal_sky_ns)