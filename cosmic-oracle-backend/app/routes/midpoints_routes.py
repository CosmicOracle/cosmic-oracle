# app/routes/midpoints_routes.py
"""
Flask Blueprint for the Astrological Midpoints feature.

This script creates a blueprint that gathers all the related namespaces
from the midpoints controller and makes them available for registration
with the main Flask application under a consistent URL prefix.
"""

from flask import Blueprint
from flask_restx import Api

# Import the namespace we defined in the controller.
from app.controllers.midpoints_controller import midpoints_ns

# Create a blueprint. The url_prefix will be prepended to all routes
# defined in the namespaces added to this blueprint's API object.
# For example, a route '/tree' will become /api/v1/astrology/midpoints/tree
midpoints_bp = Blueprint('midpoints_api', __name__, url_prefix='/api/v1')

# Associate the blueprint with a new Api object. This allows us to manage
# documentation and routing for this feature set independently.
api = Api(midpoints_bp,
          title='Midpoints API',
          version='1.0',
          description='Endpoints for calculating astrological midpoint trees and their aspects.')

# Add the namespace from the controller to our API object.
# This registers all the routes defined within that namespace.
api.add_namespace(midpoints_ns)