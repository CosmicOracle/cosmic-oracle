# app/routes/lunar_mansion_routes.py
"""
Flask Blueprint for the Lunar Mansions feature.
"""
from flask import Blueprint
from flask_restx import Api
from app.controllers.lunar_mansion_controller import lunar_mansion_ns

lunar_mansion_bp = Blueprint('lunar_mansion_api', __name__, url_prefix='/api/v1')
api = Api(lunar_mansion_bp, title='Lunar Mansions API', version='1.0', description='Endpoints for calculating the current Lunar Mansion.')
api.add_namespace(lunar_mansion_ns)