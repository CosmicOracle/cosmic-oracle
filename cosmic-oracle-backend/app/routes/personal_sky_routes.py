# app/routes/personal_sky_routes.py
"""
Flask Blueprint for the Personal Sky & Forecast feature.
"""
from flask import Blueprint
from flask_restx import Api
from app.controllers.personal_sky_controller import personal_sky_ns

personal_sky_bp = Blueprint('personal_sky_api', __name__, url_prefix='/api/v1')
api = Api(personal_sky_bp, title='Personal Sky API', version='1.0', description='Endpoints for the personalized user dashboard.')
api.add_namespace(personal_sky_ns)