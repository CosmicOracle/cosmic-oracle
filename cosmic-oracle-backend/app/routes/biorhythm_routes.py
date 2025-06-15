# app/routes/biorhythm_routes.py
"""
Flask Blueprint for the Biorhythm feature.

This script groups all biorhythm-related endpoints under a single
blueprint for easy registration with the main Flask application.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.biorhythm_controller import biorhythm_ns

# Note the new URL prefix for this category of feature.
biorhythm_bp = Blueprint('biorhythm_api', __name__, url_prefix='/api/v1')

api = Api(biorhythm_bp,
          title='Biorhythm API',
          version='1.0',
          description='Endpoints for calculating and charting personal biorhythm cycles.')

api.add_namespace(biorhythm_ns)