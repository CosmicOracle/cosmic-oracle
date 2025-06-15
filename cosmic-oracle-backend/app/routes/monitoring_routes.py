# app/routes/monitoring_routes.py
"""
Flask Blueprint for the Subscription Monitoring feature.
"""
from flask import Blueprint
from flask_restx import Api

from app.controllers.monitoring_controller import monitoring_ns

monitoring_bp = Blueprint('monitoring_api', __name__, url_prefix='/api/v1')

api = Api(monitoring_bp,
          title='Subscription Monitoring API',
          version='1.0',
          description='Endpoints for internal business intelligence and system health monitoring.')

api.add_namespace(monitoring_ns)