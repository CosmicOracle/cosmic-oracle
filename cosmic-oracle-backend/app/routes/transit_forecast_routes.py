# app/routes/transit_forecast_routes.py
"""
Flask Blueprint for the Transit Forecasting feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.transit_forecast_controller import forecast_ns

transit_forecast_bp = Blueprint('transit_forecast_api', __name__, url_prefix='/api/v1')

api = Api(transit_forecast_bp,
          title='Transit Forecast API',
          version='1.0',
          description='Endpoints for generating personalized transit reports.')

api.add_namespace(forecast_ns)