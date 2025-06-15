# app/routes/compatibility_routes.py
"""
Flask Blueprint for the Compatibility feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.compatibility_controller import compat_ns

compat_bp = Blueprint('compatibility_api', __name__, url_prefix='/api/v1')

api = Api(compat_bp,
          title='Compatibility API',
          version='1.0',
          description='Endpoints for generating synastry-based compatibility reports.')

api.add_namespace(compat_ns)