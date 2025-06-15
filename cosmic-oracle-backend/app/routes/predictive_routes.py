# app/routes/predictive_routes.py
"""
Flask Blueprint for the Predictive Astrology feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.predictive_controller import predictive_ns

predictive_bp = Blueprint('predictive_api', __name__, url_prefix='/api/v1')

api = Api(predictive_bp,
          title='Predictive Astrology API',
          version='1.0',
          description='Endpoints for calculating transits and progressions.')

api.add_namespace(predictive_ns)