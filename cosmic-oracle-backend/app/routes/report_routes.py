# app/routes/report_routes.py
"""
Flask Blueprint for the Report Generation feature.
"""
from flask import Blueprint
from flask_restx import Api
from app.controllers.report_controller import report_ns

report_bp = Blueprint('report_api', __name__, url_prefix='/api/v1')
api = Api(report_bp, title='Report Generation API', version='1.0')
api.add_namespace(report_ns)