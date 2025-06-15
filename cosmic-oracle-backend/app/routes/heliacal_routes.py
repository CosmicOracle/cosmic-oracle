# app/routes/heliacal_routes.py
"""
Flask Blueprint for the Heliacal Events feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.heliacal_controller import heliacal_ns

heliacal_bp = Blueprint('heliacal_api', __name__, url_prefix='/api/v1')

api = Api(heliacal_bp,
          title='Heliacal Events API',
          version='1.0',
          description='Endpoints for calculating traditional heliacal phenomena.')

api.add_namespace(heliacal_ns)