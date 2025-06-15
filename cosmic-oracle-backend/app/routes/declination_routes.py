# app/routes/declination_routes.py
"""
Flask Blueprint for the Declination Analysis feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.declination_controller import declination_ns

declination_bp = Blueprint('declination_api', __name__, url_prefix='/api/v1')

api = Api(declination_bp,
          title='Declination API',
          version='1.0',
          description='Endpoints for advanced declination analysis.')

api.add_namespace(declination_ns)