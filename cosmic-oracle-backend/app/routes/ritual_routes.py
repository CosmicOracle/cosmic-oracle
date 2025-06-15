# app/routes/ritual_routes.py
"""
Flask Blueprint for the Personalized Ritual feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.ritual_controller import ritual_ns

ritual_bp = Blueprint('ritual_api', __name__, url_prefix='/api/v1')

api = Api(ritual_bp,
          title='Personalized Rituals API',
          version='1.0',
          description='Endpoints for generating dynamic, personalized ritual guides.')

api.add_namespace(ritual_ns)