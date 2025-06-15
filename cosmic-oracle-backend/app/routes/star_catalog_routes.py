# app/routes/star_catalog_routes.py
"""
Flask Blueprint for the Star Catalog feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.star_catalog_controller import star_catalog_ns

star_catalog_bp = Blueprint('star_catalog_api', __name__, url_prefix='/api/v1')

api = Api(star_catalog_bp,
          title='Star Catalog API',
          version='1.0',
          description='Endpoints for querying a high-precision fixed star catalog.')

api.add_namespace(star_catalog_ns)