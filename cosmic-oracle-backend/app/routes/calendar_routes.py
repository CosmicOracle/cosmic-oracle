# app/routes/calendar_routes.py
"""
Flask Blueprint for the Astral Calendar and related features.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.calendar_controller import calendar_ns, antiscia_ns

# Note: Both namespaces are part of the same logical feature set, so they
# can share a blueprint and an API object.
calendar_bp = Blueprint('calendar_api', __name__, url_prefix='/api/v1')

api = Api(calendar_bp,
          title='Calendar & Traditional Techniques API',
          version='1.0',
          description='Endpoints for retrieving astral events and calculating traditional points.')

# Add both namespaces to the same API object
api.add_namespace(calendar_ns)
api.add_namespace(antiscia_ns)