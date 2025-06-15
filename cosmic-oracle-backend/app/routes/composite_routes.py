# app/routes/composite_routes.py
"""
Flask Blueprint for the Composite Chart feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.composite_controller import composite_ns

composite_bp = Blueprint('composite_api', __name__, url_prefix='/api/v1')

api = Api(composite_bp,
          title='Composite Chart API',
          version='1.0',
          description='Endpoints for creating and analyzing composite relationship charts.')

api.add_namespace(composite_ns)