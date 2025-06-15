# app/routes/fixed_star_routes.py
"""
Flask Blueprint for the Fixed Star Astrology feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.fixed_star_controller import fixed_star_ns

fixed_star_bp = Blueprint('fixed_star_api', __name__, url_prefix='/api/v1')

api = Api(fixed_star_bp,
          title='Fixed Star Astrology API',
          version='1.0',
          description='Endpoints for analyzing fixed star conjunctions and parans.')

api.add_namespace(fixed_star_ns)