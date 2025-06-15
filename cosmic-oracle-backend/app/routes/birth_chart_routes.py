# app/routes/birth_chart_routes.py
"""
Flask Blueprint for the user's primary Birth Chart feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.birth_chart_controller import birth_chart_ns

birth_chart_bp = Blueprint('birth_chart_api', __name__, url_prefix='/api/v1')

api = Api(birth_chart_bp,
          title='User Birth Chart API',
          version='1.0',
          description='Endpoints for managing a user\'s personal birth chart.')

api.add_namespace(birth_chart_ns)