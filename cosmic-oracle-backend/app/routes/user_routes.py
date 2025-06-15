# app/routes/user_routes.py
"""
Flask Blueprint for the User Management feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.user_controller import users_ns

# The URL prefix makes all routes in this blueprint start with /api/v1
user_bp = Blueprint('user_api', __name__, url_prefix='/api/v1')

# The `doc` path is where the Swagger UI for this specific blueprint will be available
api = Api(user_bp,
          doc='/docs/users',
          title='User Management API',
          version='1.0',
          description='Endpoints for managing user profiles.')

api.add_namespace(users_ns)