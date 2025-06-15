# app/routes/__init__.py
from flask import Blueprint

from .numerology_routes import numerology_bp
from .auth import auth_bp
from .user_data_routes import user_data_bp
from .astrology_routes import astrology_bp

# List all blueprints to be registered
blueprints = [
    numerology_bp,
    auth_bp,
    user_data_bp,
    astrology_bp
]