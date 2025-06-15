# app/routes/horary_routes.py
"""
Flask Blueprint for the Horary Astrology feature.
"""

from flask import Blueprint
from flask_restx import Api

from app.controllers.horary_controller import horary_ns

horary_bp = Blueprint('horary_api', __name__, url_prefix='/api/v1')

api = Api(horary_bp,
          title='Horary Astrology API',
          version='1.0',
          description='Endpoints for asking and judging horary questions.')

api.add_namespace(horary_ns)