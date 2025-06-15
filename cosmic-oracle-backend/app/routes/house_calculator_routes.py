# app/routes/house_calculator_routes.py
"""
Flask Blueprint for the House Calculator tool.
"""
from flask import Blueprint
from flask_restx import Api
from app.controllers.house_calculator_controller import house_calculator_ns

house_calculator_bp = Blueprint('house_calculator_api', __name__, url_prefix='/api/v1')
api = Api(house_calculator_bp, title='House Calculator API', version='1.0', description='A utility for astrological house calculations.')
api.add_namespace(house_calculator_ns)