# app/routes/electional_routes.py
"""
Flask Blueprint for the Electional Astrology feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.electional_controller import electional_ns

electional_bp = Blueprint('electional_api', __name__, url_prefix='/api/v1')

api = Api(electional_bp,
          title='Electional Astrology API',
          version='1.0',
          description='Endpoints for finding auspicious moments in time.')

api.add_namespace(electional_ns)