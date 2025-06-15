# app/routes/dignities_routes.py

from flask import Blueprint
from flask_restx import Api

# --- Correctly import from sibling 'models' and 'controllers' directories ---
from app.models.dignities_model import ns as dignities_namespace
from app.controllers.dignities_controller import DignityController

# Create the Blueprint
dignities_bp = Blueprint(
    'dignities_api',
    __name__,
    url_prefix='/api/dignities'
)

# Create an API instance and associate it with the Blueprint
api = Api(
    dignities_bp,
    title='Astrological Dignities API',
    version='1.0',
    description='An API for calculating essential dignities in an astrological chart.'
)

# Add the Namespace to the API, which registers all routes from the controller
api.add_namespace(dignities_namespace, path='/')