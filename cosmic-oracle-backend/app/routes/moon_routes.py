# app/routes/moon_routes.py
"""
Flask Blueprint for the Moon Service feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.moon_controller import moon_ns

moon_bp = Blueprint('moon_api', __name__, url_prefix='/api/v1')

api = Api(moon_bp,
          title='Moon API',
          version='1.0',
          description='Endpoints for getting detailed information about the Moon.')

api.add_namespace(moon_ns)