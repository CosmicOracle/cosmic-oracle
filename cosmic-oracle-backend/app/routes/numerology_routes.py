# app/routes/numerology_routes.py
"""
Flask Blueprint for the Numerology feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.numerology_controller import numerology_ns

numerology_bp = Blueprint('numerology_api', __name__, url_prefix='/api/v1')

api = Api(numerology_bp,
          title='Numerology API',
          version='1.0',
          description='Endpoints for generating personal numerology reports based on name and birth date.')

api.add_namespace(numerology_ns)