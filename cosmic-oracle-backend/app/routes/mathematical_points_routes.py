# app/routes/mathematical_points_routes.py
"""
Flask Blueprint for the Mathematical Points feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.mathematical_points_controller import math_points_ns

math_points_bp = Blueprint('math_points_api', __name__, url_prefix='/api/v1')

api = Api(math_points_bp,
          title='Mathematical Points API',
          version='1.0',
          description='Endpoints for calculating sensitive points like the Vertex, East Point, and Syzygy.')

api.add_namespace(math_points_ns)