# app/routes/synastry_routes.py
"""
Flask Blueprint for the Synastry feature.

This script gathers all the namespaces from the synastry controller
and groups them under a single blueprint. This allows the main application
to register the entire feature with one line of code.
"""

from flask import Blueprint
from flask_restx import Api

# Import the namespace we defined in the controller.
from app.controllers.synastry_controller import synastry_ns

# Create a blueprint. The url_prefix will be prepended to all routes in this blueprint.
# For example, a route '/chart' in the 'astrology/synastry' namespace will become
# /api/v1/astrology/synastry/chart
synastry_bp = Blueprint('synastry_api', __name__, url_prefix='/api/v1')

# Associate the blueprint with a new Api object to handle the RESTX features.
# This prevents conflicts with other potential Api objects in the app.
api = Api(synastry_bp,
          title='Synastry API',
          version='1.0',
          description='Endpoints for relationship astrology calculations.')

# Add the namespace to our API object.
api.add_namespace(synastry_ns)