# app/routes/tarot_routes.py
"""
Flask Blueprint for the Tarot Reading feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.tarot_controller import tarot_ns

tarot_bp = Blueprint('tarot_api', __name__, url_prefix='/api/v1')

api = Api(tarot_bp,
          title='Tarot API',
          version='1.0',
          description='Endpoints for performing, saving, and managing tarot readings.')

api.add_namespace(tarot_ns)