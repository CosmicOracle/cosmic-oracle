# app/routes/immanuel_routes.py

from flask import Blueprint
from flask_restx import Api
from app.models.immanuel_model import ns as immanuel_namespace
from app.controllers.immanuel_controller import ImmanuelController

# Create the Blueprint with a URL prefix
immanuel_bp = Blueprint(
    'immanuel_api',
    __name__,
    url_prefix='/api/immanuel'
)

# Create an API instance and associate it with the Blueprint
api = Api(
    immanuel_bp,
    title='Immanuel Comprehensive Report API',
    version='1.0',
    description='An orchestration API to generate a complete spiritual and astrological profile.'
)

# Add the Namespace to the API
# This registers the '/generate-report' route from the controller
api.add_namespace(immanuel_namespace, path='/')