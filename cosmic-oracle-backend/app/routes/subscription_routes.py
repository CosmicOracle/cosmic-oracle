# app/routes/subscription_routes.py
"""
Flask Blueprint for the Subscription and Billing feature.
"""
from flask import Blueprint
from flask_restx import Api
from app.controllers.subscription_controller import sub_ns

subscription_bp = Blueprint('subscription_api', __name__, url_prefix='/api/v1')
api = Api(subscription_bp, title='Subscription & Billing API', version='1.0')
api.add_namespace(sub_ns)