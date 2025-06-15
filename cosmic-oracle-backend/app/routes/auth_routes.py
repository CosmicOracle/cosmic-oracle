# app/routes/auth_routes.py
"""
Flask Blueprint for the Authentication and User Management features.
"""
from flask import Blueprint
from flask_restx import Api
from app.controllers.auth_controller import auth_ns, users_ns

auth_bp = Blueprint('auth_api', __name__, url_prefix='/api/v1')
api = Api(auth_bp, title='Authentication & Users API', version='1.0')

api.add_namespace(auth_ns)
api.add_namespace(users_ns)