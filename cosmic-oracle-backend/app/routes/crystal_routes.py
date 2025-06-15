# app/routes/crystal_routes.py
"""
Flask Blueprint for the Crystal Recommendation feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.crystal_controller import crystal_ns

crystal_bp = Blueprint('crystal_api', __name__, url_prefix='/api/v1')

api = Api(crystal_bp,
          title='Crystal API',
          version='1.0',
          description='Endpoints for getting personalized crystal recommendations.')

api.add_namespace(crystal_ns)