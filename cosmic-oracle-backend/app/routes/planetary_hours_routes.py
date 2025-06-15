app/routes/planetary_hours_routes.py
from flask import Blueprint
from flask_restx import Api
from app.controllers.planetary_hours_controller import planetary_hours_ns

planetary_hours_bp = Blueprint('planetary_hours_api', __name__, url_prefix='/api/v1')
api = Api(planetary_hours_bp, title='Planetary Hours API', version='1.0')
api.add_namespace(planetary_hours_ns)