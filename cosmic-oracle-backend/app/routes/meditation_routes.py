# app/routes/meditation_routes.py
"""
Flask Blueprint for the Meditation feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.meditation_controller import meditation_ns

meditation_bp = Blueprint('meditation_api', __name__, url_prefix='/api/v1')

api = Api(meditation_bp,
          title='Meditation API',
          version='1.0',
          description='Endpoints for tracking meditation sessions and getting personalized recommendations.')

api.add_namespace(meditation_ns)