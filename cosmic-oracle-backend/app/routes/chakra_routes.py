# app/routes/chakra_routes.py
"""
Flask Blueprint for the Chakra feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.chakra_controller import chakra_ns

chakra_bp = Blueprint('chakra_api', __name__, url_prefix='/api/v1')

api = Api(chakra_bp,
          title='Chakra Healing API',
          version='1.0',
          description='Endpoints for personal chakra assessment and healing recommendations.')

api.add_namespace(chakra_ns)